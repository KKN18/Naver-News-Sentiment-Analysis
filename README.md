# 네이버 뉴스 제목 감정분석

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

