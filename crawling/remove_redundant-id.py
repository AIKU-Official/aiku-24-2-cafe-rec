import pandas as pd
import os

# 파일 경로 설정
file_path = os.path.join('gwangjin', 'naver_review_2024-11-29_19-13-39.xlsx')

# 엑셀 파일에서 store_id 목록 읽기
df = pd.read_excel(file_path, sheet_name='output', header=None)

# 중복을 제거한 store_id 목록 만들기
unique_df = df[0].drop_duplicates()
print(unique_df.head())

# 중복 제거 후 저장할 파일 경로 설정 (#덮어쓰기)
unique_file_path = os.path.join('gwangjin', 'gwangjin_store_id_list.xlsx')

# 중복 제거된 결과를 새로운 엑셀 파일에 저장
unique_df.to_excel(unique_file_path, index=False, header=False, sheet_name="output")

print(f"중복이 제거된 store_id 리스트가 {unique_file_path}에 저장되었습니다.")