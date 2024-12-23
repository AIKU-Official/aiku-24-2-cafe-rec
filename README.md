# 프로젝트명

📢 2024년 2/겨울학기 [AIKU](https://github.com/AIKU-Official) 활동으로 진행한 프로젝트입니다
🎉 2024년 2/겨울학기 AIKU Conference 열심히상 수상!

## 소개

내가 원하는 분위기의 카페를 찾으려면, 네이버지도에 들어가서, 카페 탭을 누르고, 광고 거르고, 
리뷰 보면서 내리다가, 좀 괜찮아보이는 카페 있으면 블로그 리뷰 들어가서 내부 사진 확인하고, 어쩌구저쩌구...

수 많은 정보들과 광고에 지친 이 시점, 내가 원하는 분위기의 카페를 누군가 추천해줬으면 좋겠다!는 생각에서 출발했습니다.

카페 내부 사진 및 리뷰 데이터를 임베딩하고, Semantic Search를 통해 사용자의 요구사항에 부합하는 카페를 추천하는 agent입니다.


## 방법론

### 파이프라인

 <img width="742" alt="pipeline" src="https://github.com/user-attachments/assets/d1d726fd-f499-404e-94b5-10738cfdb46d" />

### 1. 데이터셋 수집
관련 데이터셋의 부재로 네이버 플레이스에서 카페 내부 사진, 리뷰, 위치, 메뉴 데이터 크롤링
   
   서울시 각 구별(총 25개)로 대략 200개 내외의 카페
   
   하나의 카페 당 5개의 이미지, 15개의 리뷰 데이터 수집
    -> 총 4953개 카페, 24765개의 이미지, 74295개의 리뷰


 ### 2. 데이터셋 전처리

  크롤링 과정에서 카페 내부 분위기를 파악할 수 없는 이미지들이 다수 포함 -> BLIP을 이용하여 삭제
  
  15개의 리뷰를 카페의 분위기, 방문 목적, 특징적인 인테리어나 메뉴를 잘 나타내도록 요약 -> GPT-4o-mini에게 Instruction, Few-shot example 제공


 ### 3. 데이터 임베딩

 #### 3.1.이미지
  CLIP: 이미지-텍스트 쌍으로 학습 되어 개념적인 부분을 잘 포착
  
  DINO: Image Representation Learning이 목적이므로 디테일 한 색감 및 질감을 잘 포착

  Color feature: 색감이 분위기를 가장 잘 나타낸다고 판단하여 명도, 채도 등을 나타내는 feature 사용 
  
  -> 총 3개의 embedding을 concat

 #### 3.2.리뷰
  OPENAI에서 제공하는 "text-embedding-ada-002" 모델을 이용하여 요약된 리뷰에 대한 sentence embedding 추출


 ### 4. DB 구축
  빠르고 효율적인 semantic search를 위하여 Vector DB로 Pinecone 사용

 ### 5. 모델링
  1. 사용자가 제공하는 이미지를 기준으로 유사도가 높은 30개의 카페를 Candidate로 선정
  2. 이후 사용자와의 대화들과 리뷰 임베딩의 유사도의 평균값을 기준으로 Candiate Re-Ranking
     <img width="1031" alt="image" src="https://github.com/user-attachments/assets/5d924ae8-bd26-4893-b35a-f6d137d6a5b5" />
  3. 상위 10개 카페 정보 (메뉴, 요약된 리뷰)와 사용자의 쿼리를 LLM에게 제공
  4. LLM은 점수 및 순위를 매기고 이유와 함께 사용자에게 제공



 ## 환경 설정
  가상 환경을 만든 이후, requirements.txt 이용

  ```
  pip install -r requirements.txt
  ```


 ## 사용 방법
  좋아하는 분위기의 사진을 "experiment" 디렉토리에 추가

  카페 추천을 받고 싶은 지역을 선택

  ```
  locations = [
    "junggu", "gangdong", "seocho", "dongdaemun", "eunpyeong", "songpa", 
    "gangseo", "dobong", "seongdong", "yongsan", "gwangjin", "gangbuk", 
    "seodaemun", "nowon", "dongjak", "gangnam", "yeongdeungpo", "yangcheon", 
    "geumchun", "gwanak", "guro", "seongbuk", "jongno", "jungnang", "mapo"
  ]
  ```

  ```
  python main.py experiment/<YOUR_IMG> <YOUR_LOCATION>
  ```
  
 ## 예시 결과
  데모를 만들지 못해 터미널에서만 실행이 가능합니다 😢
  
  ```
  python main.py experiment/experiment_3.jpeg mapo
  ```
  
  실행 시 아래와 같은 화면이 나타납니다.
  
  <img width="799" alt="스크린샷 2024-12-23 오후 11 30 58" src="https://github.com/user-attachments/assets/7d9f315c-58a2-46da-9ff7-c47ddde45250" />

  자유롭게 원하는 카페에 대한 설명을 입력해주세요. 모델이 카페를 추천해줍니다.
  
  <img width="888" alt="스크린샷 2024-12-23 오후 11 36 21" src="https://github.com/user-attachments/assets/f40abfdc-c947-4f54-8048-dfb26dcbe1cb" />

  왼쪽 사진에 대한 모델의 inference 결과는 아래와 같습니다. 아직 데모가 없으니... 직접 네이버, 카맵에 카페 이름을 검색해보셔야.. 합니다 .. 😢
  
  <img width="1053" alt="스크린샷 2024-12-23 오후 11 34 34" src="https://github.com/user-attachments/assets/618d0175-54c6-4f44-807d-bfe714f6803f" />



## 팀원

- [강현규]: 문제 정의, 코드 작성
- [김은진]: CBIR, 실험 진행
- [이민하]: 데이터셋 수집 및 전처리 
- [전혜서]: 리뷰 요약 및 DB 구축
