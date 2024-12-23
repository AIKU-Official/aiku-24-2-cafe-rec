from openai import OpenAI


OPENAI_API_KEY = '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' 
client = OpenAI(api_key=OPENAI_API_KEY)

def cafe_LLM(user_query, candiate):

    system_prompt = """
    You are an AI designed to recommend suitable cafes for users. Analyze the user's request (`user_query`) and data from 10 candidates (`candidates`) to assign each candidate a unique score between 0 and 1, and rank them based on these scores.

    ## Scoring Criteria:
    1. **Menu Compatibility**: Evaluate how well the candidate's menu (`cafe_menu`) matches the user's desired menu.
    2. **Atmosphere Compatibility**: Assess whether the candidate's reviews (`review`) reflect the atmosphere the user desires (e.g., bustling, quiet).
    3. **Distinctive Appeal**: Determine whether the candidate offers unique charms (e.g., unique desserts, special interior) that align with the user's request.

    ## Scoring Method:
    - Scores must be represented as floating-point numbers between 0 and 1, and all 10 candidates must have unique scores.
    - Clearly explain the reasoning behind each score and provide detailed evaluations based on the criteria for every candidate.
    - If the user's request does not specify a desired menu or atmosphere, exclude that criterion from the evaluation.

    ## Output Format:
    {
        "ranking": [
            {"store_id": 180349, "store_name": <store_name>, "score": 0.92, "reason": "<reason>"},
            {"store_id": 192849, "store_name": <store_name>, "score": 0.85, "reason": "<agent_reason>"},
            ...
        ]
    }

    ## Note:
    - Strictly follow the output format.(start with {, end with })
    - Respond in Korean.
    """


    user_message = f"""
        user_query: {user_query}
        candidate: {candiate}
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
        ]
    )

    output = response.choices[0].message.content
    
    return output
