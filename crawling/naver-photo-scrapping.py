import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 엑셀 파일에서 store_id 불러오기
file_path = os.path.join('gwangjin', 'gwangjin_store_id_list.xlsx')
df = pd.read_excel(file_path, sheet_name='output', header=None)

print(df.head())
# 'store_id' 열에서 id 리스트 가져오기
store_ids = df[0].tolist()

# Webdriver 설정 (headless 모드 해제 -> 실제 창이 보이도록)
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# 크롬 드라이버 설정 및 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 'image' 폴더 확인 및 생성
base_dir = os.path.join('gwangjin','image')
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
    print(f"{base_dir} 폴더를 생성했습니다.")
    
i=0
# 각 store_id에 대한 이미지 긁어오기
for store_id in store_ids:
    store_id = str(store_id)
    print(f"현재 store_id: {store_id}")

    # # 저장할 폴더 설정
    # if not os.path.exists(store_id):
    #     os.makedirs(store_id)
    store_folder = os.path.join(base_dir, store_id)
    
    if os.path.exists(store_folder):
        print(f"{store_folder} 폴더가 이미 존재합니다. 다음 store_id로 넘어갑니다")
        i+=1
        continue
    
    os.makedirs(store_folder)

    # 스토어 페이지 URL 설정 (store_id 기반으로 실제 URL 생성 필요)
    url = f'https://m.place.naver.com/restaurant/{store_id}/photo?filterType=%EB%82%B4%EB%B6%80'  # 실제 URL 형식에 맞게 수정

    # 해당 URL로 접속
    driver.get(url)

    # 페이지 로드 대기
    time.sleep(5)
    
    ############## 맨 밑까지 스크롤 ##############
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 스크롤 완료 후 로드 대기
        time.sleep(3)

        # 새 스크롤 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 스크롤이 더 이상 진행되지 않으면 반복 종료
        if new_height == last_height:
            break

        last_height = new_height

    # 이미지 태그를 모두 찾기 (클래스명이 'K0PDV'인 이미지 태그, 내부 사진만 추출)
    try:
        img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.K0PDV')

        # 내부 사진 필터링 및 상위 5개 추출
        internal_images = [img for img in img_elements if "내부" in img.get_attribute('alt')][:5]

        # 이미지 URL 추출 및 저장
        for idx, img in enumerate(internal_images):
            img_url = img.get_attribute('src')
            print(f"내부 이미지 {idx+1} URL: {img_url}")

            # 이미지 다운로드
            img_data = requests.get(img_url).content

            # 이미지 파일 저장
            img_filename = os.path.join(store_folder, f"{store_id}_{idx+1}.jpg")
            with open(img_filename, 'wb') as img_file:
                img_file.write(img_data)
                print(f"내부 이미지 {idx+1} 저장 완료: {img_filename}")
    
    except Exception as e:
        print(f"{store_id}에서 이미지를 다운로드할 수 없습니다: {e}")

# 웹 드라이버 종료
driver.quit()
