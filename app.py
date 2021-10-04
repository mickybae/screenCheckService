import json
import sys
from flask import Flask
from flask import request
import mysql.connector
import cv2
import numpy as np
import hashlib
from jsonify.convert import jsonify
import urllib.request
import matplotlib
from matplotlib import pyplot as plt



app = Flask(__name__)

def getList():
    global conn
    curs = conn.cursor()
    sql = "SELECT SEARCHKEY, CONCAT(CATEID,'^^',ITEMID) AS ITEMKEY, KEYNUM, SEARCHCOUNT, CLICKCOUNT, LENGTH(SEARCHKEY) AS KEYLENGTH " \
    "FROM SEARCHDATA " \
    "WHERE SEARCHKEY LIKE '%"+tempText+"%' " \
    "ORDER BY CLICKCOUNT DESC, SEARCHCOUNT DESC, KEYLENGTH DESC, MODIFIEDTIME DESC"
    curs.execute(sql)
    # data Fetch
    result = curs.fetchall()
    conn.close
    return result

def save_video(fileUrl, fileid):
    savename = "./workfiles/" + fileid + ".mp4"
    urllib.request.urlretrieve(fileUrl, savename)

#Feature point matching
def checker_FPM_ORB(src1, src2, optvalue):

    if src1 is None or src2 is None:
        print('Image load failed!')
        sys.exit()

    # 특징점 알고리즘 객체 생성 (KAZE, AKAZE, ORB 등)
    # feature = cv2.KAZE_create()
    # feature = cv2.AKAZE_create()
    feature = cv2.ORB_create() #1과 비교해서 크면 변화

    # 특징점 검출 및 기술자 계산
    kp1, desc1 = feature.detectAndCompute(src1, None)
    kp2, desc2 = feature.detectAndCompute(src2, None)

    # 특징점 매칭
    matcher = cv2.BFMatcher_create()
    # matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING) # 이진 기술자를 사용하는 알고리즘
    # matches = matcher.match(desc1, desc2)
    print('# of kp1:', len(kp1))
    print('# of kp2:', len(kp2))
    pt1 = len(kp1)
    pt2 = len(kp2)
    rate = 0
    if pt1 == pt2:
        rate = 100
        maxpt = 1
        pt = 0
    elif pt1 > pt2:
        pt = pt1 - pt2
        maxpt = pt1
    else:
        pt = pt2 - pt1
        maxpt = pt2

    if rate != 100:
        rate = ((maxpt * optvalue) * 100) / pt

    #print(rate/100)
    # print("maxpt :" + str(maxpt * 0.5))
    # print("pt :" + str(pt))

    #orb
    if (rate/100) < 10:
        result = True
    else:
        result = False

    # 특징점 매칭 결과 영상 생성 (연구자료 생성시 사용)
    # dst = cv2.drawMatches(src1, kp1, src2, kp2, matches, None)
    # cv2.imshow('dst', dst)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    #Draw first 10 matches

    return result

def checker_CS(src1, src2, optvalue):
    if src1 is None or src2 is None:
        print('Image load failed!')
        sys.exit()
    global pre_similarity
    vimg1 = np.array(src1)
    vimg2 = np.array(src2)
    vimg1 = np.ravel(vimg1, order='C')
    vimg2 = np.ravel(vimg2, order='C')
    dot_product = np.dot(vimg1, vimg2)
    l2_norm = (np.sqrt(sum(np.square(vimg1))) * np.sqrt(sum(np.square(vimg2))))
    similarity = (dot_product / l2_norm)*100000 #작은값보정
    #print(similarity)

    if similarity < 4:
        result = True
    else:
        result = False
    return result

def save_checker(obj1, obj2): #파일저장조건확인
    #이미지 특징벡터 추출
    #obj1 쿼리이미지
    #obj2 학습이미지
    # 영상 변조하기 (변조된 사이즈의 이미지와 흑백이미지를 비교에 사용
    src1 = cv2.cvtColor(obj1, cv2.COLOR_BGR2GRAY)
    src1 = cv2.resize(src1, dsize=(160, 120), interpolation=cv2.INTER_AREA)
    src2 = cv2.cvtColor(obj2, cv2.COLOR_BGR2GRAY)
    src2 = cv2.resize(src2, dsize=(160, 120), interpolation=cv2.INTER_AREA)

    checkPoint = 0
    result = False
    #여러가지 복합검사
    if checker_FPM_ORB(src1, src2, optvalue=0.5) == True:
        checkPoint += 1
    if checker_CS(src1, src2, optvalue=0.5) == True:
        checkPoint += 1
    if checkPoint == 2:
        result = True

    return result

@app.route('/')
def screenCapture():  # put application's code here
    return 'Hello World!'

@app.route('/makeScreenShot', methods=['GET', 'POST'])
def makeScreenShot():
    print("call to makeScreenShot")
    # target = getList()
    # for row in target:
    #     print(row)

    #파일 아이디와 URL을 받으면
    fUrl = "http://127.0.0.1/datas/test2.mp4"
    fId = "C000002"
    fSensetive = 3 #초당 프레임수
    fStt = True
    #
    #파일을 다운로드 하고
    save_video(fUrl, fId)
    vidcap = cv2.VideoCapture("./workfiles/" + fId + ".mp4")
    count = 0
    obj1 = None
    pre_filename = ""
    while vidcap.isOpened():
        ret, image = vidcap.read()
        filename = fId + "_" + str(int(vidcap.get(1))) + ".png"
        if pre_filename == filename:
            break
        else:
            pre_filename = filename
        if count == 0:
            obj1 = image
            cv2.imwrite('./pictures/' + filename, image)
        elif (int(vidcap.get(1)) % (fSensetive*30)) == 0:
            if image is None:
                break
            else:
                if (save_checker(obj1, image) == True):
                    print(filename)
                    cv2.imwrite('./pictures/' + filename, image)
                    obj1 = image #저장된 이미지로 변경

        count += 1
    vidcap.release()

    result = "Good job"
    return result

# 여기 이하로는 웹 API 및 서비스 API 구분
# 여기 이하로는 웹 API 및 서비스 API 구분
# 여기 이하로는 웹 API 및 서비스 API 구분
# 여기 이하로는 웹 API 및 서비스 API 구분
# 여기 이하로는 웹 API 및 서비스 API 구분
def get_hash_value(in_str, in_digest_bytes_size=64, in_return_type='digest'):
    assert 1 <= in_digest_bytes_size and in_digest_bytes_size <= 64
    blake  = hashlib.blake2b(in_str.encode('utf-8'), digest_size=in_digest_bytes_size)
    if in_return_type == 'hexdigest': return blake.hexdigest()
    elif in_return_type == 'number': return int(blake.hexdigest(), base=16)
    return blake.digest()

def checkSpace(arrObj): #빈 변수확인
    result = True
    for data in arrObj:
        if data == "":
            result = False
    return result

def valid_check(strUri, arrValue):
    result = False
    if strUri == "register": #벨리데이션 체크등록
        result = True

    return result

#회원가입
@app.route('/member/register', methods=['GET', 'POST'])
def register():
    arrValue = {} #dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'POST':
        arrValue['userId'] = request.form.get('userid')
        arrValue['userPasswd1'] = request.form.get('userpasswd1')
        arrValue['userPasswd2'] = request.form.get('userpasswd2')
        arrValue['userCompanyName'] = request.form.get('usercompanyname')
        arrValue['userName'] = request.form.get('username')
        arrValue['userEmail'] = request.form.get('useremail')
        arrValue['userTelno'] = request.form.get('usertelno')
        arrValue['apiToken'] = get_hash_value(arrValue['userId'], in_digest_bytes_size=64, in_return_type='hexdigest')
        if valid_check('register', arrValue) == True :
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "INSERT INTO METAGENSERVICE.MEMBER"
                strSql = strSql + "(MID, MPASSWD, MCOMPNAME, MUSERNAME, MCONTACTEMAIL, MCONTACTTELNO, CREATEDDATE)"
                strSql = strSql + " VALUES (%s, %s, %s, %s, %s, %s, now())"
                curs.execute(strSql, (arrValue['userId'], arrValue['userPasswd1'], arrValue['userCompanyName'], arrValue['userName'], arrValue['userEmail'], arrValue['userTelno']))
                conn.commit()
                curs = conn.cursor()
                strSql = "INSERT INTO METAGENSERVICE.OPENAPITOKEN"
                strSql = strSql + "(APITOKEN, MEMBER_MID, CREATEDDATE)"
                strSql = strSql + " VALUES (%s, %s, now())"
                curs.execute(strSql, (arrValue['apiToken'], arrValue['userId']))
                conn.commit()
            except Exception as e:
                return str(e)
            finally:
                conn.close()

            resultList['userId'] = arrValue['userId']
            resultList['apiToken'] = arrValue['apiToken']

            resultDict['code'] = "C0000"
            resultDict['message'] = 'SUCCESS'
            resultDict['data'] = resultList
            print(resultDict)
        else:
            resultDict['code'] = "E0000"
            resultDict['message'] = 'ERROR'

    return json.dumps(resultDict)

#로그인 전 ID 체크
@app.route('/member/idcheck/<userid>', methods=['GET', 'POST'])
def idcheck(userid):
    arrValue = {} #dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userId'] = userid

        if valid_check('register', arrValue) == True :
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT COUNT(MID) as MIDCOUNT FROM METAGENSERVICE.MEMBER"
                strSql = strSql + " WHERE MID = '" + arrValue['userId'] + "'"

                curs.execute(strSql)
                rows = curs.fetchall()
                print(rows[0][0])

                if rows[0][0] > 0:
                    resultList['result'] = False
                else:
                    resultList['result'] = True

                resultDict['code'] = "C0000"
                resultDict['message'] = 'SUCCESS'
                resultDict['data'] = resultList

                conn.commit()
            except Exception as e:
                return str(e)
            finally:
                conn.close()

        else:
            resultDict['code'] = "E0000"
            resultDict['message'] = 'ERROR'

    return json.dumps(resultDict)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9900, debug=True)


