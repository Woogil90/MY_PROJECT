import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만듭니다.


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('project_fake review_200226_rev2.html')


# URL을 읽어서 HTML를 받아오고,
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

positive_word = ['최고다','인정','뻔한','억지연기','억지','빈약','별로','돈아까운','떨어진','아깝다','엉망','속았다','쪽팔린다'
'거짓','후회','피식','알바','노잼','억지','아쉽','욕','엉망진창','속음','뻔한','짜증','삼류영화','재미없','뻔한','지겹다','졸려','별로','아깝다','아까운','억지스러','어처구니','상술','지루','엉성','재미없다','딱히']
negative_word = ['손색','엄청','유쾌','상쾌','통쾌','잘봤습니다','오졌다','ㅋㅋ','레알','존잼','완전','스트레스','웰메이드','케미','다한,영화','믿고보는','빵빵','오진다','두마리','두마리','토끼','능청'
'대박','원탑','킬링타임','스크린','오져','ㅎㅎ','믿고','정통','연기','재밌','감동','다했','꿀잼','경지','매력','코믹','배꼽','몰입','강추','존잼']


## keyword를 받아와서 처리 후, DB에 데이터를 넣는다.
@app.route('/keyword', methods=['POST'])
def find_moviecode():
    ##keyword가 출력되어야 한다.

    keyword_receive = request.form['keyword_give']

    website1 = 'https://movie.naver.com/movie/search/result.nhn?query={}&section=all&ie=utf8'.format(keyword_receive)
    data1 = requests.get(website1, headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup1 = BeautifulSoup(data1.text, 'html.parser')

    # select를 이용해서, li들을 불러오기
    moviecode = soup1.select_one('#old_content > ul.search_list_1 > li > dl > dt > a')['href'].split('code=')[1]

    ##keyword를 통해 moviecode를 얻어내야 한다.

    ## 1. moviecode 획득 완료


    website3 = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code={}'.format(moviecode)
    data3 = requests.get(website3, headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup3 = BeautifulSoup(data3.text, 'html.parser')

    # select를 이용해서, img들을 불러오기
    # print(soup3)
    picture = soup3.select_one('#content > div.article > div.mv_info_area > div.poster > a > img')['src']
    ## 2. moviecode에 해당하는 사진을 불러온다.

    print(picture)


    reviews = list(db.fakereview.find({'code': moviecode}, {'_id': 0}))

    ##2-1 기존에 있는 moviecode가 있으면, for loop를 돌리지 않고 기존 것을 활용해 return한다..

    if len(reviews) == 0:
        iterations = 11  ## 몇 페이지까지 볼 것인지 기재한다.
        rank = 1

        ##2-2 moviecode가 없으면 for loop를 돌려서 구하고, 값을 return한다.

        for page_num in range(1, iterations):
            print(page_num)

            website2 = 'http://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code={}&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page={}'.format(
                moviecode, page_num)
            data2 = requests.get(website2, headers=headers)

            # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
            soup2 = BeautifulSoup(data2.text, 'html.parser')

            # select를 이용해서, li들을 불러오기
            contents = soup2.select('body > div > div > div.score_result > ul > li')

            # reviews (li들) 의 반복문을 돌리기

            for content in contents:
                # movie 안에 a 가 있으면,
                li_1 = content.select_one('div.star_score')
                if li_1 is not None:
                    score = li_1.text.strip()
                    review = content.select_one(' li > div.score_reple > p').text.strip()
                    review = review.strip('관람객').strip()
                    print(rank, score, review, moviecode)

                    doc = {
                        'rank': rank,
                        'score': score,
                        'review': review,
                        'code': moviecode
                    }

                    db.fakereview.insert_one(doc)

                    rank += 1

        reviews = list(db.fakereview.find({'code': moviecode}, {'_id': 0}))
    for idx, r in enumerate(reviews):
        review = reviews[idx]['review']
        for word in positive_word:
            if word in review:
                reviews[idx]['review'] = reviews[idx]['review'].replace(word, '<span class="blue">{}</span>'.format(word))
        for word in negative_word:
            if word in review:
                reviews[idx]['review'] = reviews[idx]['review'].replace(word, '<span class="red">{}</span>'.format(word))
    return jsonify({'result': 'success', 'reviews': reviews, 'picture': picture})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
