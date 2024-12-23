import argparse
from agent import cafe_rec_agent


def main(YOUR_IMG_PATH, YOUR_NAMESPACE):
    print("###### 모델 로드 중입니다... ######\n")

    agent = cafe_rec_agent(
        PINECONE_API_KEY="pcsk_69gv72_51gzDz84ieYxxPM27antjmxKNPeB1pY2gh82bEw1R6NWKMEGhSpFqDUXKGz3J4c",
        PINECONE_ENV="gcp_starter",
        OPENAI_API_KEY="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",
        namespace=YOUR_NAMESPACE,
        total_csv_path="review_summary/total_review_summary.csv",
    )

    print("###### 제시한 이미지와 유사한 카페를 선정 중입니다... ######\n")

    img_retrieval_output = agent.img_retrieval(
        img_path=YOUR_IMG_PATH, filtering_count=30
    )

    user_query_list = []
    i = 0
    merged_output = img_retrieval_output

    while True:
        user_query = input("\033[92mUser\033[0m: ")
        if user_query.lower() == "exit":
            print("\033[93mChatbot\033[0m: 안녕히 가세요!")
            break

        user_query_list.append(user_query)
        combined_query = ",".join(user_query_list)

        review_output = agent.review_retrieval(user_query)

        # merge_score 함수 호출
        merged_output = agent.merge_score(merged_output, review_output)

        candidate = agent.get_candidate(merged_output, 10)
        LLM_output = agent.get_LLM_output(combined_query, candidate)

        print("\033[93mChatbot\033[0m:")
        agent.print_ranked_cafes(LLM_output)
        print()

        i += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cafe Recommendation Agent")
    parser.add_argument("img_path", type=str, help="Path to the image file")
    parser.add_argument("namespace", type=str, help="Namespace for the agent")

    args = parser.parse_args()
    main(args.img_path, args.namespace)
