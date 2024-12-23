import warnings

# 모든 경고 무시
warnings.filterwarnings('ignore')

import torch
from transformers import AutoImageProcessor, AutoModel, CLIPProcessor, CLIPModel
from pinecone import Pinecone
from PIL import Image
import cv2
import numpy as np
import pandas as pd
from openai import OpenAI
from cafe_LLM import cafe_LLM
import json



class cafe_rec_agent():

    def __init__(self, PINECONE_API_KEY, PINECONE_ENV, OPENAI_API_KEY, namespace, total_csv_path):

        self.PINECONE_API_KEY = PINECONE_API_KEY
        self.PINECONE_ENV = PINECONE_ENV
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.dino_processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
        self.dino_model = AutoModel.from_pretrained('facebook/dinov2-base').to(self.device)

        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)

        self.namespace = namespace
        temp_df = pd.read_csv("review_summary/location_count.csv")
        self.top_k = list(temp_df[temp_df['location'] == namespace]['count'])[0]
        self.total_csv_path = total_csv_path

    def img_retrieval(self, img_path, filtering_count):
        """
        이미지를 업로드하고 DINOv2, CLIP, 색상 기반 특징을 추출하여 결합하고
        db와 비교하여 검색 결과를 반환
        """
        pc = Pinecone(
            api_key=self.PINECONE_API_KEY,  # Or use PINECONE_API_KEY directly
            environment=self.PINECONE_ENV   # Or use PINECONE_ENV directly
        )

        index = pc.Index('aikudm', host = "https://aikudm-ry1dv08.svc.aped-4627-b74a.pinecone.io")

        ## 이미지 업로드
        
        image = Image.open(img_path)
        # image.show()

        # Dino
        dino_inputs = self.dino_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            dino_features = self.dino_model(**dino_inputs).last_hidden_state.mean(dim=1).cpu().numpy().flatten()

        # CLIP
        clip_inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            clip_features = self.clip_model.get_image_features(**clip_inputs).cpu().numpy().flatten()

        ## color based
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        hist_r = cv2.calcHist([image_cv], [0], None, [480], [0, 256]).flatten()
        hist_g = cv2.calcHist([image_cv], [1], None, [480], [0, 256]).flatten()
        hist_b = cv2.calcHist([image_cv], [2], None, [480], [0, 256]).flatten()
        color_features = np.concatenate((hist_r, hist_g, hist_b))

        ## concat
        combined_features = np.concatenate((clip_features, color_features, dino_features)).tolist()

        ## pinecone 비교해 내놓기
        query_results = index.query(
            vector=combined_features,
            namespace=self.namespace,
            top_k=self.top_k,
            include_metadata=True
        )
        
        df = pd.DataFrame([(match['id'], match['score']) for match in query_results['matches']], columns=['id', 'img_score'])
        df_filtered = df.head(filtering_count)

        return df_filtered
    
    def review_retrieval(self, query):

        """
        쿼리를 임베딩하고 db와 비교하여 검색 결과를 반환
        """
        pc = Pinecone(
            api_key=self.PINECONE_API_KEY,  # Or use PINECONE_API_KEY directly
            environment=self.PINECONE_ENV   # Or use PINECONE_ENV directly
        )
        
        client = OpenAI(api_key=self.OPENAI_API_KEY)

        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query,
            encoding_format="float"
        )

        output = np.array(response.data[0].embedding)

        index = pc.Index('aikudmreview', host = "https://aikudmreview-ry1dv08.svc.aped-4627-b74a.pinecone.io")

        # Query Pinecone for top-k similar vectors
        results = index.query(
            vector=output.tolist(),
            top_k=self.top_k,
            include_metadata=True,
            namespace = self.namespace
        )

        df = pd.DataFrame([(match['id'], match['score']) for match in results['matches']], columns=['id', 'query_score'])

        return df



    def merge_score(self, df_filtered, df_new):
        """
        두 DataFrame을 병합하고 새로운 query_score를 추가.
        
        Args:
            df_filtered (pd.DataFrame): 기존의 병합된 DataFrame.
            df_new (pd.DataFrame): 새로운 query_score가 포함된 DataFrame.
            
        Returns:
            pd.DataFrame: 병합 및 평균 점수가 포함된 DataFrame.
        """
        # 새로운 query_score의 열 이름을 생성
        query_score_col = f"query_score_{len([col for col in df_filtered.columns if 'query_score' in col]) + 1}"
        
        # df_new의 score 열을 새로운 query_score_x로 이름 변경
        df_new = df_new.rename(columns={'query_score': query_score_col})
        
        # 'id'를 기준으로 병합
        merged_df = pd.merge(df_filtered, df_new, on='id', how='inner')
        
        # 평균 점수 계산 (img_score 제외)
        score_columns = [col for col in merged_df.columns if 'query_score' in col]
        merged_df['average_score'] = merged_df[score_columns].mean(axis=1)

        columns_order = ['id', 'img_score'] + score_columns + ['average_score']
        merged_df = merged_df[columns_order]
        
        # 평균 점수를 기준으로 정렬
        df = merged_df.sort_values(by='average_score', ascending=False)
        
        return df


        
    def get_candidate(self, merged_df, count):

        review_csv = pd.read_csv(self.total_csv_path)
        candidate_id_list = list(merged_df['id'])[:count]

        input_dict = {}

        for i in range(len(candidate_id_list)):

            row = review_csv[review_csv['store_id'] == int(candidate_id_list[i])]
            input_dict[f"candidate_{i}"] = {"id": candidate_id_list[i], "store_name": row['store_name'], "menu": row['menu'], "review": row['summurized_review']}

        return input_dict
    
    def get_LLM_output(self, query, candidate):

        LLM_output = cafe_LLM(query, candidate)
        output_dict = json.loads(LLM_output)

        return output_dict
    
    def print_ranked_cafes(self, output_dict):
        """
        주어진 JSON 딕셔너리를 순위별로 포맷팅하여 출력합니다.
        Args:
            output_dict (dict): JSON 딕셔너리 형태의 카페 랭킹 데이터.
        """
        top5 = output_dict.get('ranking', [])[:5]  # 상위 5개 항목만 선택

        for idx, item in enumerate(top5, start=1):
            rank_prefix = f"# Rank {idx}" if idx == 1 else f"## Rank {idx}"
            print(rank_prefix)
            print(f"-- store_id: {item.get('store_id', 'N/A')}")
            print(f"-- store_name: {item.get('store_name', 'N/A')}")
            print(f"-- score: {item.get('score', 'N/A')}")
            print(f"-- reason: {item.get('reason', 'N/A')}")
            print()



if __name__ == "__main__":
    agent = cafe_rec_agent(PINECONE_API_KEY= "pcsk_69gv72_51gzDz84ieYxxPM27antjmxKNPeB1pY2gh82bEw1R6NWKMEGhSpFqDUXKGz3J4c",
                           PINECONE_ENV = "gcp_starter",
                           OPENAI_API_KEY = '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',
                           namespace='gangnam',
                           total_csv_path = 'review_summary/total_review_summary.csv')
    
    img_retrieval_output = agent.img_retrieval(img_path = 'experiment/hyeongyu_img.png',
                                               filtering_count = 30)    
    
    query = "조용히 공부할 수 있는 공간이 있었으면 좋겠어. 딸기케이크가 먹고싶어."

    review_output = agent.review_retrieval(query)
    merged_output = agent.merge_score(img_retrieval_output, review_output)
    LLM_input = agent.get_candidate(merged_output, 10)
    LLM_output = agent.get_LLM_output(query, LLM_input)
    print(LLM_output)
    agent.print_ranked_cafes(LLM_output)


    
