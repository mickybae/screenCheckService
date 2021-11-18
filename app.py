import json
import os
import sys
from flask import Flask
from flask import request
from flask_cors import CORS
import mysql.connector
import cv2
import numpy as np
import hashlib
import random
from datetime import datetime
from jsonify.convert import jsonify
import urllib.request
import matplotlib
from matplotlib import pyplot as plt

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)



app = Flask(__name__)
CORS(app)

#대상영상 저장
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
    # print('# of kp1:', len(kp1))
    # print('# of kp2:', len(kp2))
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

#화면변환 확인
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

#변환된 화면저장
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

#Object정보저장
def fnSaveObjectList(tempList):

    insertValue = ""
    for file in tempList:
        fileObject = open("./output/" + file, "r", encoding='UTF8')
        data = fileObject.read().replace("'", "").replace('"', '').replace(",", "^^")
        arrTemp = file.split('_')
        if data is None:
            data = "Empty"
        if data.strip() is not None:
            if insertValue == "":
                insertValue = "('" + arrTemp[0] + '_' + arrTemp[1] + "', " + arrTemp[0] + ", '" + data + "', now())"
            else:
                insertValue = insertValue + ",('" + arrTemp[0] + '_' + arrTemp[1] + "', " + arrTemp[
                    0] + ",'" + data + "', now())"

    # Conn 열고 업데이트 수행 후
    try:
        conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                       host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                       database='METAGENSERVICE')
        curs = conn.cursor()
        strSqlInsert = "INSERT INTO METAGENSERVICE.CONTENTMETADATA_OBJECTDETECTION (CMSCENE_SCENE, CMSCENE_CONTENTMASTER_CID, NAME, CREATEDDATE) VALUES "
        strSqlInsert = strSqlInsert + insertValue
        print(strSqlInsert)
        curs.execute(strSqlInsert)
        conn.commit()
    except Exception as e:
        return str(e)
    finally:
        conn.close()
    return True

#Text 정보저장
def fnSaveTextList(tempList):
    insertValue = ""
    for file in tempList:
        fileObject = open("./output/"+file, "r", encoding='UTF8')
        data = fileObject.read().replace("'","").replace('"','').replace(",","^^")
        arrTemp = file.split('_')
        if data is None:
            data = "Empty"
        if data.strip() is not None:
            if insertValue == "":
                insertValue = "('" + arrTemp[0] + '_' + arrTemp[1] + "', " + arrTemp[0] + ", '" + data + "', now())"
            else:
                insertValue = insertValue + ",('" + arrTemp[0] + '_' + arrTemp[1] + "', " + arrTemp[0] + ",'" + data + "', now())"


    # Conn 열고 업데이트 수행 후
    try:
        conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                           host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                           database='METAGENSERVICE')
        curs = conn.cursor()
        strSqlInsert = "INSERT INTO METAGENSERVICE.CONTENTMETADATA_OCR (CMSCENE_SCENE, CMSCENE_CONTENTMASTER_CID, TEXTDATA, CREATEDDATE) VALUES "
        strSqlInsert = strSqlInsert + insertValue
        print(strSqlInsert)
        curs.execute(strSqlInsert)
        conn.commit()
    except Exception as e:
        return str(e)
    finally:
        conn.close()
    return True



#주기적으로 웹 호출하여 동작시킴
@app.route('/makeScreenShot')
def makeScreenShot():
    #print("call to makeScreenShot")
    # target = getList()
    # for row in target:
    #     print(row)
    resultDict = {}
    resultList = []
    try:
        conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                       host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                       database='METAGENSERVICE')
        curs = conn.cursor()
        strSql = "SELECT CID, CONTENTURL, SENSETIVESECOND, OPTIONOCR, OPTIONOBJDETECT, CONTENTLANGUAGE FROM METAGENSERVICE.CONTENTMASTER WHERE STATUS = 'STAY' ORDER BY CID DESC"
        curs.execute(strSql)
        rows = curs.fetchall()
        #print(rows)
        conn.commit()
    except Exception as e:
        return str(e)

    finally:
        conn.close()

    for i in rows:
        fId = str(i[0])
        fUrl = i[1]
        fSensetive = i[2]
        # 파일 아이디와 URL을 받으면
        #print(fId)
        # print(fUrl)
        # print(fSensetive)
        #파일 아이디와 URL을 받으면
        #fUrl = "http://127.0.0.1/datas/test2.mp4"
        #fId = "C000002"
        #fSensetive = 3 #초당 프레임수

        # 파일을 다운로드 하고
        save_video(fUrl, fId)
        vidcap = cv2.VideoCapture("./workfiles/" + fId + ".mp4")
        count = 0
        obj1 = None
        pre_filename = ""
        while vidcap.isOpened():
            #print(fId)
            ret, image = vidcap.read()
            filename = fId + "_" + str(int(vidcap.get(1))) + ".png"
            if pre_filename == filename:
                break
            else:
                pre_filename = filename
            #print("count : " + str(count))
            if count == 0:
                obj1 = image
                cv2.imwrite('./pictures/' + filename, image)
                resultList.append(fId + "_" + str(int(vidcap.get(1))) + "^^" + str(fId) + "^^" + str(int(vidcap.get(1))))
            elif (int(vidcap.get(1)) % (fSensetive*30)) == 0: #동영상 프레임수 업그레이드 필요
                if image is None:
                    break
                else:
                    if (save_checker(obj1, image) == True):
                        #print(filename)
                        cv2.imwrite('./pictures/' + filename, image)
                        obj1 = image #저장된 이미지로 변경
                        resultList.append(fId + "_" + str(int(vidcap.get(1))) + "^^" + str(fId) + "^^" + str(int(vidcap.get(1))))
            count += 1
        vidcap.release()

    # contentmaster Table의 "STAY" 를 "PROC" 로 변경한후
    condition = ""
    insertValue = ""
    counter = 0
    for rows in resultList:
        row = rows.split("^^")
        cid = row[0]
        contentmaster_cid = row[1]
        time = row[2]
        if condition == "":
            condition = str(contentmaster_cid)
        else:
            condition = condition + ", " + str(contentmaster_cid)

        if insertValue == "":
            insertValue = "('" + cid + "', " + str(contentmaster_cid) + ", " + str(time) + ")"
        else:
            insertValue = insertValue + ", ('" + cid + "', " + str(contentmaster_cid) + ", " + str(time) + ")"
        counter += 1

    #바뀔께 있으면
    if condition != "":
        #Conn 열고 업데이트 수행 후
        try:
            conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                           host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                           database='METAGENSERVICE')
            curs = conn.cursor()
            strSqlUpdate = "UPDATE METAGENSERVICE.CONTENTMASTER SET STATUS = 'PROC' WHERE CID in (" + condition +")"
            print(strSqlUpdate)
            curs.execute(strSqlUpdate)
            strSqlInsert = "INSERT INTO METAGENSERVICE.CMSCENE (SCENE, CONTENTMASTER_CID, TIME) VALUES "
            strSqlInsert = strSqlInsert + insertValue
            print(strSqlInsert)
            curs.execute(strSqlInsert)
            conn.commit()
        except Exception as e:
            return str(e)
        finally:
            conn.close()

    resultDict['code'] = "C0000"
    resultDict['message'] = 'SUCCESS'
    resultDict['data'] = counter
    return json.dumps(resultDict)

#요청 및 완료된 목록 조회
@app.route('/makeMetaData')
def makeMetaData():
    resultDict = {}
    resultList = []
    saveObjectList = []
    saveTextList = []
    path_dir = './output'
    filelist = os.listdir(path_dir)
    for file in filelist:
        arrtemp = file.split('_',2)
        if (arrtemp[2].split('.')[0]) == 'OBJECT':
            #print('Object : ' + file)
            saveObjectList.append(file)
        else:
            #print('TEXT : ' + file)
            saveTextList.append(file)

    # print(saveObjectList)
    # print(saveTextList)

    if fnSaveObjectList(saveObjectList) == True:
        result = True

    if fnSaveTextList(saveTextList) == True:
        result = True




    resultDict['code'] = "C0000"
    resultDict['message'] = 'SUCCESS'
    resultDict['data'] =json.dumps(result)
    return json.dumps(resultDict)





# 여기 이하로는 웹 API 및 서비스 API 구분
# 여기 이하로는 웹 API 및 서비스 API 구분

#Root 디렉토리
@app.route('/')
def screenCapture():  # put application's code here
    return 'Welcome to System!'

# Key(Token) 만드는곳
def get_hash_value(in_str, in_digest_bytes_size=64, in_return_type='digest'):
    assert 1 <= in_digest_bytes_size and in_digest_bytes_size <= 64
    blake = hashlib.blake2b(in_str.encode('utf-8'), digest_size=in_digest_bytes_size)
    if in_return_type == 'hexdigest': return blake.hexdigest()
    elif in_return_type == 'number': return int(blake.hexdigest(), base=16)
    return blake.digest()

#변수내용이 비었는지 확인
def checkSpace(arrObj):
    result = True
    for data in arrObj:
        if data == "":
            result = False
    return result

#각 API별 필수 입력사항 확인하는 부분 - 추가개발 필요
def valid_check(strUri, arrValue):
    result = False
    if strUri == "register": #벨리데이션 체크등록
        result = True

    return result

#사용가능한 토큰인지 확인
def check_usertoken(target, userid, token):
    result = False
    if target == "web":
        try:
            conn_inner = mysql.connector.connect(user='K2020509', password='K2020513',
                                           host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                           database='METAGENSERVICE')
            curs = conn_inner.cursor()
            strSql = "SELECT WEBTOKEN.WEBTOKEN FROM METAGENSERVICE.WEBTOKEN "
            strSql = strSql + " WHERE WEBTOKEN.MEMBER_MID = '" + userid + "' order by LASTUSEDATE DESC LIMIT 1"
            print(strSql)
            curs.execute(strSql)
            rows = curs.fetchall()
            if not rows:
                result = False
            elif rows[0][0].strip() == token.strip():
                result = True
            else:
                result = False
            conn_inner.commit()
        except Exception as e:
            return str(e)
        finally:
            conn_inner.close()

    elif target == "openapi":
        try:
            conn_inner = mysql.connector.connect(user='K2020509', password='K2020513',
                                           host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                           database='METAGENSERVICE')
            curs = conn_inner.cursor()
            strSql = "SELECT OPENAPITOKEN.APITOKEN FROM METAGENSERVICE.OPENAPITOKEN "
            strSql = strSql + " WHERE OPENAPITOKEN.MEMBER_MID = '" + userid + "' order by CREATEDDATE ASC LIMIT 1"
            curs.execute(strSql)
            rows = curs.fetchall()
            if not rows:
                result = False
            elif rows[0][0] == token:
                result = True
            else:
                result = False
            conn_inner.commit()
        except Exception as e:
            return str(e)
        finally:
            conn_inner.close()
    print(result)
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
            # print(resultDict)
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
                # print(rows[0][0])
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

#로그인
@app.route('/member/login', methods=['GET', 'POST'])
def login():
    arrValue = {} #dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'POST':
        arrValue['userId'] = request.form.get("userid")
        arrValue['userPasswd'] = request.form.get("userpasswd")

        if valid_check('register', arrValue) == True :
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT COUNT(MID) as MIDCOUNT FROM METAGENSERVICE.MEMBER"
                strSql = strSql + " WHERE MID = '" + arrValue['userId'] + "' and MPASSWD = '" + arrValue['userPasswd'] + "' "

                curs.execute(strSql)
                rows = curs.fetchall()
                # print(rows[0][0])

                if rows[0][0] > 0:
                    arrValue['webToken'] = get_hash_value(arrValue['userId'] + str(random.uniform(1000, 9999)), in_digest_bytes_size=64, in_return_type='hexdigest')
                    strSql = "INSERT INTO METAGENSERVICE.WEBTOKEN"
                    strSql = strSql + "(WEBTOKEN, MEMBER_MID, LASTUSEDATE)"
                    strSql = strSql + " VALUES (%s, %s, now())"
                    curs.execute(strSql, (arrValue['webToken'], arrValue['userId']))
                    conn.commit()
                    resultList['web_token'] = arrValue['webToken']
                else:
                    resultList['result'] = "No id or password"

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

#사용자 웹토큰과 아이디를 받아 유효하면 OPENAPI TOKEN 조회
@app.route('/member/getapitoken', methods=['GET', 'POST'])
def getapitoken():
    arrValue = {} #dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT APITOKEN FROM METAGENSERVICE.OPENAPITOKEN "
                strSql = strSql + " WHERE MEMBER_MID = '" + arrValue['userid'] + "' order by CREATEDDATE ASC LIMIT 1"
                curs.execute(strSql)
                rows = curs.fetchall()
                if not rows:
                    resultList['api_token'] = "no have"

                else:
                    resultList['api_token'] = rows[0][0].strip()

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

#요청내용등록
@app.route('/content/req_register', methods=['GET', 'POST'])
def req_register():
    arrValue = {} #dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'POST':
        arrValue['contentTitle'] = request.form.get('contenttitle')
        arrValue['contentUrl'] = request.form.get('contenturl')
        arrValue['sensetiveSecond'] = int(request.form.get('senstivesecond'))
        # arrValue['option_STT'] = request.form.get('option_stt')
        arrValue['option_OCR'] = request.form.get('option_OCR')
        arrValue['option_ObjDetect'] = request.form.get('option_ObjDetect')
        arrValue['contentLanguage'] = request.form.get('contentLanguage')
        arrValue['api_token'] = request.form.get('api_token')
        arrValue['userId'] = request.form.get('userid')
        arrValue['status'] = 'STAY'
        print(arrValue)

        if (valid_check('register', arrValue)) and (check_usertoken('web', arrValue['userId'], arrValue['api_token'])):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "INSERT INTO `METAGENSERVICE`.`CONTENTMASTER`"
                strSql = strSql + "(MEMBER_MID, CONTENTTITLE, CONTENTURL, SENSETIVESECOND, OPTIONOCR, OPTIONOBJDETECT, CONTENTLANGUAGE, STATUS, MODIFIEDDATE, CREATEDDATE )"
                strSql = strSql + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())"
                curs.execute(strSql, (arrValue['userId'], arrValue['contentTitle'], arrValue['contentUrl'], arrValue['sensetiveSecond'], arrValue['option_OCR'], arrValue['option_ObjDetect'], arrValue['contentLanguage'], arrValue['status']))
                conn.commit()
            except Exception as e:
                return str(e)
            finally:
                conn.close()

            resultList['result'] = True

            resultDict['code'] = "C0000"
            resultDict['message'] = 'SUCCESS'
            resultDict['data'] = resultList
            # print(resultDict)
        else:
            resultDict['code'] = "E0000"
            resultDict['message'] = 'ERROR'

    return json.dumps(resultDict)

#요청카운트 조회
@app.route('/content/req_count', methods=['GET', 'POST'])
def req_count():
    arrValue = {}  # dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT COUNT(*) FROM METAGENSERVICE.CONTENTMASTER "
                strSql = strSql + " WHERE MEMBER_MID = '" + arrValue['userid'] + "' "
                curs.execute(strSql)
                rows = curs.fetchall()
                print(strSql)
                if not rows:
                    resultList['api_token'] = "no have"

                else:
                    resultList['count'] = rows[0][0]

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

#완료카운트 조회
@app.route('/content/fin_count', methods=['GET', 'POST'])
def fin_count():
    arrValue = {}  # dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT COUNT(*) FROM METAGENSERVICE.CONTENTMASTER "
                strSql = strSql + " WHERE MEMBER_MID = '" + arrValue['userid'] + "' AND STATUS = 'FINISH' "
                curs.execute(strSql)
                rows = curs.fetchall()
                print(strSql)
                if not rows:
                    resultList['count'] = 0

                else:
                    resultList['count'] = rows[0][0]

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

#요청 및 완료된 목록 조회
@app.route('/content/list_content', methods=['GET', 'POST'])
def list_content():
    arrValue = {}  # dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        arrValue['fromdate'] = request.args['fromdate']
        arrValue['enddate'] = request.args['enddate']
        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT CID, CONTENTTITLE, CONTENTURL, PLAYTIME, STATUS FROM CONTENTMASTER"
                strSql = strSql + " WHERE MEMBER_MID = '" + arrValue['userid'] +"' "
                strSql = strSql + " AND CREATEDDATE BETWEEN '" + arrValue['fromdate'] + "' AND  '"+arrValue['enddate']+"' "
                strSql = strSql + " ORDER BY STATUS DESC"

                curs.execute(strSql)
                rows = curs.fetchall()
                print(strSql)
                print(json.dumps(rows))

                if not rows:
                    resultList['api_token'] = "no have"
                else:
                    resultList['count'] = rows[0][0]

                resultDict['code'] = "C0000"
                resultDict['message'] = 'SUCCESS'
                resultDict['data'] = json.dumps(rows)

                conn.commit()
            except Exception as e:
                return str(e)
            finally:
                conn.close()

        else:
            resultDict['code'] = "E0000"
            resultDict['message'] = 'ERROR'

    return json.dumps(resultDict)

#요청건의 상세조회
@app.route('/content/detail', methods=['GET', 'POST'])
def detail():
    arrValue = {}  # dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        arrValue['cid'] = request.args['cid']

        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT CID, CONTENTTITLE, CONTENTURL, PLAYTIME, SENSETIVESECOND, OPTIONSTT, OPTIONOCR, OPTIONOBJDETECT, STATUS, MODIFIEDDATE, CREATEDDATE FROM METAGENSERVICE.CONTENTMASTER"
                strSql = strSql + " WHERE MEMBER_MID = '" + arrValue['userid'] +"' "
                strSql = strSql + " AND CID = " + arrValue['cid']

                curs.execute(strSql)
                rows = curs.fetchall()
                print(strSql)

                if not rows:
                    rows = "Have not Data"

                resultDict['code'] = "C0000"
                resultDict['message'] = 'SUCCESS'
                resultDict['data'] = json.dumps(rows, cls=DateTimeEncoder)

                conn.commit()
            except Exception as e:
                return str(e)
            finally:
                conn.close()

        else:
            resultDict['code'] = "E0000"
            resultDict['message'] = 'ERROR'
    return json.dumps(resultDict)


#JSON DATA조회
@app.route('/openAPIs/contentMetaData', methods=['GET', 'POST'])
def contentMetaData():
    arrValue = {}  # dict구조체 사용
    resultDict = {}
    resultList = {}
    if request.method == 'GET':
        arrValue['userid'] = request.args['userid']
        arrValue['api_token'] = request.args['api_token']
        arrValue['cid'] = request.args['cid']

        if check_usertoken('web', arrValue['userid'], arrValue['api_token']):
            try:
                conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                               host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                               database='METAGENSERVICE')
                curs = conn.cursor()
                strSql = "SELECT CS.SCENE, CM.CONTENTLANGUAGE"
                strSql = strSql + ", (SELECT NAME FROM METAGENSERVICE.CONTENTMETADATA_OBJECTDETECTION WHERE CMSCENE_SCENE = CS.SCENE ) AS NAME "
                strSql = strSql + ", (SELECT TEXTDATA FROM METAGENSERVICE.CONTENTMETADATA_OCR WHERE CMSCENE_SCENE = CS.SCENE ) AS TEXTDATA "
                strSql = strSql + " FROM METAGENSERVICE.CONTENTMASTER AS CM "
                strSql = strSql + " INNER JOIN CMSCENE AS CS ON CM.CID = CS.CONTENTMASTER_CID "
                strSql = strSql + " WHERE CM.CID = " + arrValue['cid']
                strSql = strSql + " GROUP BY CS.SCENE, CM.CONTENTLANGUAGE, NAME, TEXTDATA "
                strSql = strSql + " ORDER BY CS.TIME ASC "

                curs.execute(strSql)
                rows = curs.fetchall()
                print(strSql)
                print(json.dumps(rows))

                if not rows:
                    resultList['api_token'] = "no have"
                else:
                    resultList['count'] = rows[0][0]

                resultDict['code'] = "C0000"
                resultDict['message'] = 'SUCCESS'
                resultDict['data'] = json.dumps(rows)

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


