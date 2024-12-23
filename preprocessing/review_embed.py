from openai import OpenAI
import pandas as pd
import numpy as np
from tqdm import tqdm
import pickle

def make_review_embed(csv_path, output_path):

    df = pd.read_csv(csv_path)
    
    store_id_list = df['store_id'].to_list()
    review_list = df['summurized_review'].to_list()

    OPENAI_API_KEY = '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' 
    client = OpenAI(api_key=OPENAI_API_KEY)

    embedding_store = {}

    for i in tqdm(range(len(store_id_list))):

        store_id = store_id_list[i]
        response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=review_list[i],
                encoding_format="float"
                )

        embedding_store[store_id] = np.array(response.data[0].embedding)

    with open(output_path, 'wb') as f:  # 'wb': 쓰기 모드(바이너리)
        pickle.dump(embedding_store, f)

location_name = ['guro', 'seongbuk', 'jongno', 'jungnang', 'mapo', 'dongjak', 'gangnam', 'yangcheon', 
                 'yeongdeungpo', 'geumchun', 'gwanak', 'yongsan', 'seongdong', 'gwangjin', 'seodaemun', 
                 'gangbuk', 'nowon', 'junggu', 'seocho', 'gangdong', 'eunpyeong', 'dongdaemun', 'songpa',
                 'dobong', 'gangseo']

    
for location in location_name:

    print(f"--{location} processing --")

    make_review_embed(csv_path = f"review_summary/{location}.csv" , output_path = f"features/review-features/{location}_review_embed.pkl")
    
    
