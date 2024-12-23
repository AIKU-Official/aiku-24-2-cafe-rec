from openai import OpenAI
import tiktoken
import pandas as pd
from tqdm import tqdm
import os

OPENAI_API_KEY = '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' 
client = OpenAI(api_key=OPENAI_API_KEY)

def review_preprocess(review_list):
    
    input_review = {}
    for i, review in enumerate(review_list):
        input_review[f"review_{i}"] = review

    return input_review    


def summurize_LLM(user_input):

    system_prompt = """ 
    You are an AI system designed to summarize café reviews.

    ## Instruction

    1. Summarize the café's interior atmosphere and vibe.
    2. Summarize the purpose of the visit.
    3. If there are any particularly delicious menu items, include them in the summary.
    
    If a specific point is not mentioned in the reviews, it may be omitted. 
    Summarize the reviews in three sentences, one for each point, and respond in Korean.

    ## Example
    
    user_input: {
        review_1 : "가족식사하고 근처에 제일 넓은 카페같아서 왔어요:) 사장님께서 단체석 자리 만들어주셨어요ㅎㅎ 최고! 빙수시켜도 1인 1메뉴구요~넓고 분위기도 좋고 티도 빙수도 다 맛있어요!",
        review_2 : "이 집은 팥 들어간 메뉴가 최고 입니다. 아 치즈 케익도 맛있어요",
        review_3 : "카페만의 시그니처 커피가 있어요 근데 매장 벽면이 마감이 안 된 원 건물을 뜯은 그자체의 디자인이라 해당 부분이 불호인 분들은 참고하세요",
        review_4 : "분위기가 독특해요!실내는 아늑한 분위기에할 일 하러 오기 좋아요"
    }

    agent_output: 카페는 넓고 아늑하며 독특한 벽면 인테리어로 편안한 분위기를 제공합니다. 가족 단위 방문이나 단체 모임, 또는 조용히 할 일을 하기에도 적합합니다. 팥이 들어간 메뉴와 치즈케이크, 그리고 시그니처 커피가 특히 맛있다는 평이 많습니다.
    """

    tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4o compatible tokenizer

    # Convert user_input to tokenized format and check length
    user_input_tokens = tokenizer.encode(str(user_input))
    max_tokens = 27000

    # Truncate user_input if it exceeds the maximum token limit
    if len(user_input_tokens) > max_tokens:
        truncated_tokens = user_input_tokens[:max_tokens]
        user_input = tokenizer.decode(truncated_tokens)

    user_message = f"""
        user_input: {user_input}
        agent_output: ???
    """


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
        ]
    )

    output = response.choices[0].message.content
    
    return output


def review_summary(xlsx_path, output_path):

    df = pd.read_excel(xlsx_path, sheet_name='output', engine='openpyxl')
    store_id_list = list(set(df['store_id']))
    store_name_list = []
    menu_list = []
    summurized_review_list = []


    for i in tqdm(range(len(store_id_list))):

        id = store_id_list[i]
        #
        store_name = list(df[df['store_id'] == id]['store_name'])[0]
        store_name_list.append(store_name)
        #
        menu = list(df[df['store_id'] == id]['menu'])[0]
        menu_list.append(menu)
        #
        review_list = list(df[df['store_id'] == id]['content'])
        input_review = review_preprocess(review_list)
        summurized_review = summurize_LLM(input_review)
        summurized_review_list.append(summurized_review)

    output_df = pd.DataFrame({"store_id": store_id_list,
                              "store_name": store_name,
                              "menu": menu_list,
                              "summurized_review": summurized_review_list})
    
    output_df.to_csv(output_path, index=False)
    

if __name__ == "__main__":

    # location_name = ['guro', 'seongbuk', 'jongno', 'jungnang', 'mapo', 'dongjak', 'gangnam', 'yangcheon', 
    #              'yeongdeungpo', 'geumchun', 'gwanak', 'yongsan', 'seongdong', 'gwangjin', 'seodaemun', 
    #              'gangbuk', 'nowon', 'junggu', 'seocho', 'gangdong', 'eunpyeong', 'dongdaemun', 'songpa',
    #              'dobong', 'gangseo']
    location_name = ['dobong', 'gangseo']
    
    for location in location_name:

        print(f"--{location} processing --")

        file_list = os.listdir(f"data/{location}")
        prefix = "naver_review"
        xlsx_name = list(filter(lambda item: item.startswith(prefix), file_list))
        xlsx_path = f"data/{location}/{xlsx_name[0]}"

        review_summary(xlsx_path, output_path=f"review_summary/{location}.csv")