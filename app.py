from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token 
from flask_jwt_extended import jwt_required,get_jwt_identity
import pymysql
from datetime import timedelta
from dotenv import load_dotenv
import os

from validation import *

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# jsonify 한글 인코딩이 변경되어 비정상 출력 문제 해결 코드
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
# JWT 암호화에 사용할 키 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
# JWT 토큰의 만료 시간 설정
app.config['BCRYPT_LEVEL'] = 10 # 기본값
# Bcrypt 사용 시 해시 함수 작업량 10 설정하여 비밀번호 보안 강화 역할

HOST = os.environ.get('HOST')
USER = os.environ.get('USER')
PASSWD = os.environ.get('PASSWD')
DATABASE = os.environ.get('DB')
CHARSET = os.environ.get('CHARSET')
PORT = 3306
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

default_image = './default_image.png'

# 퀴즈 풀면 사전에 저장하는 기능
@app.route('/quiz/save', methods=['GET','POST'])
@jwt_required()
def quiz_save():
    word_data = request.get_json()
    print(word_data)
    save_word =  [item['WORD_NUM'] for item in word_data]
    print(save_word)
    current_user = get_jwt_identity()
    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)      
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    dict_sql = f'SELECT USER_DICT FROM USER_ACT WHERE USER_NUM={current_user}'
    cursor.execute(dict_sql)
    dict_data = cursor.fetchall()

    if dict_data[0]['USER_DICT'] == None:
        save_sql = f'UPDATE USER_ACT SET USER_DICT = "{save_word}" WHERE USER_NUM={current_user}'
        cursor.execute(save_sql)
        connection.commit()
        connection.close()     
        return jsonify({"message": "정답입니다~"})   
    else:
        print(dict_data[0])
        print(dict_data[0]['USER_DICT'])
        list_dict = dict_data[0]['USER_DICT']
        print(list_dict)
        print(save_word)
        add_data = eval(list_dict) + save_word
        add_sql = f'UPDATE USER_ACT SET USER_DICT = "{add_data}" WHERE USER_NUM={current_user}'  
        cursor.execute(add_sql)
        connection.commit()
        connection.close()
        return jsonify({"message": "정답입니다~~"})    

# 뉴스 스크랩 하면 스크랩에 저장하는 기능
@app.route('/news/save', methods=['GET','POST'])
@jwt_required()
def news_save():
    news_data = request.get_json()
    save_news=  news_data[0]['NEWS_NUM']
    current_user = get_jwt_identity()
    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)      
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    dict_sql = f'SELECT USER_SCRAP FROM USER_ACT WHERE USER_NUM={current_user}'
    cursor.execute(dict_sql)
    dict_data = cursor.fetchall()

    if dict_data[0]['USER_SCRAP'] == None:
        save_sql = f'UPDATE USER_ACT SET USER_SCRAP = "{save_news}" WHERE USER_NUM={current_user}'
        cursor.execute(save_sql)
        connection.commit()
        connection.close()     
        return jsonify({"message": "뉴스가 스크랩 되었습니다."})   
    else:
        add_data = [dict_data[0]['USER_SCRAP']] + save_news
        add_sql = f'UPDATE USER_ACT SET USER_SCRAP = "{add_data}" WHERE USER_NUM={current_user}'  
        cursor.execute(add_sql)
        connection.commit()
        connection.close()
        return jsonify({"message": "뉴스가 스크랩 되었습니다."})   

# 유저의 MYPAGE 데이터 모음 기능 구현 - USER_NAME, USER_POINT ...
@app.route('/mypage', methods=['POST'])
@jwt_required()
def mypage():
    current_user = get_jwt_identity()
    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    join_sql = f"""SELECT USER_LOGIN.*, USER_ACT.* FROM USER_LOGIN 
    INNER JOIN USER_ACT ON USER_LOGIN.USER_NUM = USER_ACT.USER_NUM WHERE USER_LOGIN.USER_NUM={current_user}"""
    cursor.execute(join_sql)
    join_data = cursor.fetchall()
    connection.close()

    if join_data[0] != None:
        return jsonify(join_data)
    else:
        return jsonify({'message':'다시 로그인 해주세요.'})
     
    # my_sql = f'SELECT USER_NAME FROM USER_LOGIN WHERE USER_NUM={current_user}'
    # cursor.execute(my_sql)
    # name_data = cursor.fetchone()

    # point_sql = f'SELECT USER_POINT FROM USER_ACT WHERE USER_NUM={current_user}'
    # cursor.execute(point_sql)
    # point_data = cursor.fetchone()

# 퀴즈 문제 던져주는 기능 구현
@app.route('/quiz', methods=['GET','POST'])
@jwt_required()
def send_quiz():
    current_user = get_jwt_identity()
    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    
    sql = f'SELECT USER_DICT FROM USER_ACT WHERE USER_NUM={current_user}'
    cursor.execute(sql)
    data = cursor.fetchall()
    
    if data[0]['USER_DICT'] == None:
        quiz_sql = 'SELECT WORD_NUM, QUIZ, ANSWER FROM DICTIONARY LIMIT 3;'
        cursor.execute(quiz_sql)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    else:
        max_quiz = data[0]['USER_DICT'][-2]
        quiz_sql2 = f"SELECT WORD_NUM, QUIZ, ANSWER FROM DICTIONARY WHERE WORD_NUM > {max_quiz} LIMIT 3;"
        cursor.execute(quiz_sql2)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    
    # 뉴스는 스크랩 버튼 누르면 아마 POST, 저장하여 스크랩 DB로
    # 단어랑 퀴즈는 문제 다 맞추면 DICT DB로

# 홈 뉴스보기 기능 구현
@app.route('/news', methods=['GET','POST'])
@jwt_required() # @jwt_required() 데코레이터 -> 해당 엔드포인트에 접근하려면 JWT 토큰이 필요
                # => 자동으로 인증 처리, 유효한 JWT 토큰이 요청 헤더에 포함되어 있는지 확인하고, 유효성 검사를 수행
def home_news():
    current_user = get_jwt_identity()

    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    news_sql = f'SELECT USER_SCRAP FROM USER_ACT WHERE USER_NUM={current_user};'
    cursor.execute(news_sql)
    news_data = cursor.fetchall()
    # print(news_data) # [{'USER_SCRAP': None}]
    if news_data[0]['USER_SCRAP'] == None:
        news_sql = 'SELECT NEWS_NUM, NEWS_TITLE, ARTICLE, NEWS_IMAGE FROM NEWS LIMIT 1;'
        cursor.execute(news_sql)
        result = cursor.fetchall()
        print(result)
        connection.close()
        return jsonify(result)
    else:
        max_word = news_data[0]['USER_SCRAP'][-2]
        add_sql = f"SELECT NEWS_NUM, NEWS_TITLE, ARTICLE, NEWS_IMAGE FROM NEWS WHERE NEWS_NUM > {max_word} LIMIT 1;"
        cursor.execute(add_sql)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)

# 홈 단어공부 기능 구현
@app.route('/word', methods=['GET','POST'])
@jwt_required() # @jwt_required() 데코레이터 -> 해당 엔드포인트에 접근하려면 JWT 토큰이 필요
                # => 자동으로 인증 처리, 유효한 JWT 토큰이 요청 헤더에 포함되어 있는지 확인하고, 유효성 검사를 수행
def home_word():
    current_user = get_jwt_identity()

    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    word_sql = f'SELECT USER_DICT FROM USER_ACT WHERE USER_NUM={current_user};'
    cursor.execute(word_sql)
    word_data = cursor.fetchall()
    
    if word_data[0]['USER_DICT'] == None:
        dict_sql = 'SELECT WORD_NUM, WORD_NUM, WORD, EXPLAINATION FROM DICTIONARY LIMIT 3;'
        cursor.execute(dict_sql)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    else:
        max_word = word_data[0]['USER_DICT'][-2]
        add_sql = f"SELECT WORD_NUM, WORD, EXPLAINATION FROM DICTIONARY WHERE WORD_NUM > {max_word} LIMIT 3;"
        cursor.execute(add_sql)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)

# 회원가입 API 엔드포인트
@app.route('/signup', methods=['POST']) ## POST 방식으로 오는 입력만 받음
def signup():
    # POST 요청으로부터 필요한 정보를 get_json으로 받아옴
    data = request.get_json() 
    user_id = data['EMAIL']
    user_pw = data['PASSWORD']
    user_birth = data['USER_BIRTH']
    user_name = data['USER_NAME']
    user_phone = data['PHONE_NUM']
    hashed_pw = bcrypt.generate_password_hash(user_pw)
    # hashed_pw = bcrypt.hashpw(str(user_pw).encode('utf8'), bcrypt.gensalt())
    # generate_password_hash(): 주어진 비밀번호를 안전하게 해시화된 문자열로 변환 
    # -> 해시화된 비밀번호는 안전한 저장을 위해 데이터베이스에 저장됨
    
    # 유효성 검사 
    if email_validation(user_id) and email_overlap(user_id) and pw_validation(user_pw) and name_validation(user_name) and birth_validation(user_birth) and phone_validation(user_phone):
        connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
        # pymysql.connect : MySQL 데이터베이스에 연결
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        # connection.cursor : 연결된 데이터베이스에 대한 커서 객체 생성
        # pymysql.cursors.DictCursor : 딕셔너리 형태로 결과를 반환

        sql = "INSERT INTO USER_LOGIN (EMAIL, PASSWORD, USER_BIRTH, USER_NAME, PHONE_NUM) VALUES (%s, %s, %s, %s, %s);" 
        sql_act = "INSERT INTO USER_ACT (USER_POINT, USER_IMAGE) values (%s,%s);"
        # %s : 플레이스홀더, SQL 쿼리 실행 시 동적으로 값을 대체하는 데 사용 
        # sql : 삽일할 데이터를 포함하는 SQL 쿼리문 정의
        # INSERT INTO TABLE () : USER_LOGIN 테이블에 (각 컬럼) 해당되는 값을 삽입
        cursor.execute(sql, (user_id, hashed_pw, user_birth, user_name, user_phone))
        cursor.execute(sql_act,(0, default_image))
        # cursor.execute : 커서를 사용하여 SQL 쿼리문을 실행, 두 번째 매개변수에는 쿼리문의 플레이스홀더에 해당하는 값들 전달
        
        connection.commit()
        # 데이터베이스에 대한 변경 사항을 커밋(변경된 내용을 적용하는 작업)
        connection.close()
        # 데이터베이스 연결 닫기

        return jsonify({'message': '회원가입이 완료되었습니다.'})
        # 작업 완료 후 메시지를 JSON 형식으로 반환
    
    elif email_validation(user_id) == False:
        return jsonify({'message':'이메일 양식에 맞게 입력해주세요'})
    elif email_overlap(user_id) == False:
        return jsonify({'message': '이미 사용 중인 이메일 주소입니다.'})
    elif pw_validation(user_pw) == False:
        return jsonify({'message': '비밀번호를 4자 이상 입력해 주세요.'})
    elif name_validation(user_name) == False:
         return jsonify({'message':'이름을 입력해 주세요.'})
    elif birth_validation(user_birth) == False:
         return jsonify({'message':'생일을 6자리 숫자로 입력해 주세요.'})
    elif phone_validation(user_phone) == False:
         return jsonify({'message':'( - ) 기호 없이 전화번호만 입력해 주세요'})
    else:
        return jsonify({'message': '양식에 맞게 다시 입력해 주세요.'})
    
# 로그인 API 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    connection = pymysql.connect(host=HOST, port=PORT, db=DATABASE, user=USER, passwd=PASSWD, charset=CHARSET)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    user_id = data['EMAIL']
    user_pw = data['PASSWORD']
    
    ## encoded_pw = str(user_pw).encode('utf8')
    # str 객체 내 메소드인 encode()를 이용하여 UTF-8 방식으로 인코딩 해준 값을 넣어줌
    # hashed_password = bcrypt.hashpw('password'.encode('utf8'), bcrypt.gensalt())
    ## hashed_pw = bcrypt.check_password_hash(encoded_pw, bcrypt.gensalt())
    # bcrypt.hashpw(): 인코딩 실시
    # 두번 째 파라미터 bcrypt.gensalt(): salt 값 설정
    
    # sql = f'SELECT * FROM USER_LOGIN WHERE EMAIL = "{user_id}"'
    sql = "SELECT * FROM USER_LOGIN WHERE EMAIL = %s"
    # SELECT *는 검색 결과로 모든 열을 반환하라는 의미
    # 이메일과 비밀번호가 일치하는 사용자의 모든 정보를 가져옴
    
    # cursor.execute(sql)
    cursor.execute(sql, (user_id,))
    db_data = cursor.fetchall()
    # 커서를 통해 실행된 쿼리결과에서 행(row)을 가져오는 메서드
    # 호출될 때마다 결과 집합에서 한 번에 하나의 행을 가져옴
    
    connection.close()

    ## encoded = jwt.encode(json, 'Secret Key', algorithm='HS256')
    # 인코딩 하고자 하는 dict 객체, 시크릿 키, 알고리즘 방식 삽입
    ## decoded = jwt.decode(encoded, 'Secret Key', algorithm='HS256')
    # 디코딩 하고자 하는 str 객체, 시크릿 키, 알고리즘 방식 삽입

    # 사용자 정보를 데이터베이스에서 검증
    if len(db_data) > 0: 
        result = bcrypt.check_password_hash(db_data[0]['PASSWORD'], user_pw)
        # 암호 일치 확인 방법 bcrypt.checkpw(): 첫번째 파라미터와 두번째 파라미터로 비교하고자 하는 bytes-string 입력
        # check_password_hash(pwhash, password): 사용자가 제출한 비밀번호를 확인할 때
        if result:
            user_name = db_data[0]['USER_NAME']
            return jsonify({'message': f"{user_name}님 반갑습니다.", 'access_token' : create_access_token(identity=db_data[0]['USER_NUM']),"token_type":"bearer", "expires_in": 7200})
                                                                    # JWT 토큰을 생성하여 access_token 키 값에 입력 
                                                                    # # identity 는 db_data의 user_num을 고유 값으로 사용
        else:
            return jsonify({'message': '비밀번호를 다시 입력해주세요.'})
    else:
        return jsonify({'message': '아이디를 다시 입력해주세요.'})
    # jsonify 함수는 키-값 쌍을 가진 딕셔너리를 인자로 받아 JSON 형식으로 반환해주는 함수
if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
## 이거는 마지막에서만 선언

# 코드를 작성한 파일을 실행하거나 flask run 명령을 사용하여 Flask 애플리케이션을 실행합니다.
# Postman, cURL 또는 웹 브라우저와 같은 도구를 사용하여 회원가입과 로그인 API 엔드포인트를 호출합니다.
# 회원가입에는 POST 요청을 /signup 엔드포인트로 보내고 필요한 데이터를 JSON 형식으로 전송합니다.
# 로그인에는 POST 요청을 /login 엔드포인트로 보내고 필요한 데이터를 JSON 형식으로 전송합니다.
# 각 API 엔드포인트는 요청을 받아 처리하고 응답으로 JSON 데이터를 반환합니다. 응답을 확인하여 예상된 메시지가 올바르게 반환되는지 확인할 수 있습니다.

