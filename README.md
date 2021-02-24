# Naver News Title Sentiment Analysis

## Environment
모든 작업이 Google Colab Notebooks에서 진행되었습니다.

## Dataset
**Crawler.ipynb**을 이용해서 검색어별 2019년 12월 뉴스부터 2021년 1월 뉴스의 제목들을 크롤링하였습니다.

## Setup
<code> Google Colab Notebooks</code> 에서 <code> git clone</code> 커맨드를 입력합니다.

    !git clone https://github.com/KKN18/Naver-News-Sentiment-Analysis.git

1. **model.ipynb** 을 실행해 saved_model 폴더에 감정분석 모델을 학습 및 저장합니다.
2. **eval.ipynb**을 실행해 저장한 모델로 월별 네이버 뉴스 제목을 감정분석합니다.

## Sentiment Analysis Model
[Naver sentiment movie corpus](https://github.com/e9t/nsmc/) 로 학습시킨 BERT 모델을 이용하였습니다.

## Analysis Result
그래프의 값이 높을수록 **긍정**적인 헤드라인의 비율이 높았다는 것을 의미합니다.

![Economy](https://github.com/KKN18/Naver-News-Sentiment-Analysis/blob/main/result/Economy.PNG)
![Health](https://github.com/KKN18/Naver-News-Sentiment-Analysis/blob/main/result/Health.PNG)
![Social](https://github.com/KKN18/Naver-News-Sentiment-Analysis/blob/main/result/Social.PNG)
![Stock](https://github.com/KKN18/Naver-News-Sentiment-Analysis/blob/main/result/Stock.PNG)

## Reference
[BERT Fine-Tuning Tutorial](https://medium.com/@aniruddha.choudhury94/part-2-bert-fine-tuning-tutorial-with-pytorch-for-text-classification-on-the-corpus-of-linguistic-18057ce330e1)
