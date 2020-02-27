import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta                      # 'dbsparta'라는 이름의 db를 만듭니다.


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('project_fake review_200226.html')


# URL을 읽어서 HTML를 받아오고,
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


# 영화의 리뷰 페이지별로 자료를 크롤링해서 mongodb에 추가한다.

iterations = 3
rank = 1

for page_num in range(1, iterations):
    print(page_num)

    website = 'http://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=186821&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page={}'.format(page_num)
    data = requests.get(website, headers=headers)


# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup = BeautifulSoup(data.text, 'html.parser')

# select를 이용해서, li들을 불러오기
    contents = soup.select('body > div > div > div.score_result > ul > li')

# reviews (li들) 의 반복문을 돌리기

    for content in contents:
    # movie 안에 a 가 있으면,
        li_1 = content.select_one('div.star_score')
        if li_1 is not None:
            score = li_1.text.strip()
            review = content.select_one(' li > div.score_reple > p').text.strip()
            review = review.strip('관람객').strip()
            print(rank, score, review)

            doc = {
                'rank': rank,
                'score': score,
                'review': review
            }
            db.contents.insert_one(doc)

            rank += 1






if __name__ == '__main__':
   app.run('localhost',port=5000,debug=True)
