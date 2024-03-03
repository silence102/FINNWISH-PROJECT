import pymysql

# 올바른 이메일 형식인지 확인
def email_validation(email):
    email = email
    if '@' in email and  5 < len(email) < 40:
        return True
    else:
        return False
    
# 중복 이메일 주소 가입 방지    
def email_overlap(email):
    connection = pymysql.connect(host='localhost', port=3306, db='finnwish', user='root', passwd='1807992102', charset='utf8')
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM USER_LOGIN WHERE EMAIL = %s"
    cursor.execute(sql, (email,))
    result = cursor.fetchone()

    connection.close()

    if result:
        return False 
    else:
        return True
    
# 최소 비밀번호 길이 확인
def pw_validation(password):
    if 4 <= len(password) <= 30:
        return True
    else: 
        return False 
    
# 유저 이름 입력 정보 확인
def name_validation(name):
    if 1 <= len(name) <= 20:
        return True 
    else:
        return False 

# 생일 6자리로 입력 확인
def birth_validation(birth):
    if len(birth) == 6:
        return True 
    else:
        return False 

# 전화번호 양식 확인
def phone_validation(phone):
    if 3 <= len(phone) <= 11:
        return True 
    else:
        return False 
    