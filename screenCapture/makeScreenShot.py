# from flask import jsonify
from . import api
import mysql.connector
import cv2
import urllib.request

@api.route('/makeScreenShot', methods=['GET', 'POST'])
def makeScreenShot():
    print("call to makeScreenShot")
    target = getList()
    for row in target:
        print(row)

    #파일 아이디와 URL을 받으면
    fUrl = "http://127.0.0.1/datas/test1.mp4"
    fID = "C000001"
    fSensetive = 3
    fStt = True

    #파일을 다운로드 하고
    capture = cv2.VideoCapture(fUrl)
    while capture.isOpened():
        run, frame = capture.read()
        if not run:
            lastReturn = "프레임추출종료"
            break
        img = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        cv2.imshow('video', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

    #파일을 지정된 프레임수로 돌리면서

    #90프레임마다. 화면을 발췌하여

    #이전에 저장된 화면과 유사도를 비교하고

    #3가지 유사도의 비교가 완료되어 3점을 얻으면

    #해당 이미지는 이전이미지와 다른것으로 간주하고 저장한다.


def getList():
    conn = mysql.connector.connect(user='K2020509', password='K2020513',
                                   host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                                   database='METAGENSERVICE')

    result = []



    conn.close
    return result









# @api.route('/insertSearchKey', methods=['GET', 'POST'])
# def insertSearchKey():
#     if request.method =='POST':
#         insertkey = request.form.get('insertkey')
#         keywordList = makeKeyword(insertkey)
#         result = insertSearchServiceRow(keywordList, request.form.get('linkedcate'),request.form.get('linkeditem'))
#         resultList = []
#         resultList.append(['RESULT',['SUCCESS']])
#         resultList.append(['DATA',result])
#     return jsonify(resultList)
#
# # by micky, pentaworks
# # 2021-02-02
#
# # simple keywords maker for searching title in shopping-mall
# def makeKeyword(tempText):
#     from konlpy.tag import Okt
#     from collections import OrderedDict
#     from itertools import repeat
#     okt = Okt()
#     tempList = []
#     # 어절분리 및 중복제거를 하지만 순서는 유지할 것 python3.X 기준으로 개발 zip(o) izip(x)
#     # 분리된 어절에서 필요없는 품사는 분류 및 제거 (형용사, 알파벳, 관형사, 외국어 및 한자등 기호, 명사, 숫자, 미등록어, 동사 기록)
#     for word in list(OrderedDict(zip(tempText.split(), repeat(None)))):
#         for token in okt.pos(word):
#             if token[1] in ['Adjective','Alpha','Determiner','Foreign','Noun','Number','Unknown','Verb']:
#                 # Number의 경우 후방 연속되는 단어와 띄어쓰기가 없음.
#                 if token[1] == "Number":
#                     tempList.append(token[0])
#                 else:
#                     tempList.append(token[0] + " ")
#
#
#     # 키워드 생성하기 전체제목 unigram, bigram, trigram 으로 키워드 생서으 숫자가 있을 경우 후방단어와 띄어쓰기 없음
#     resultList = []
#     resultList.append(tempText)
#     resultList.extend(makeUnigram(tempList)) # merge List
#     resultList.extend(makeBigram(tempList)) # merge List
#     resultList.extend(makeTrigram(tempList)) # merge List
#
#     return resultList
#
# # unigram maker
# def makeUnigram(tempList):
#     resultList = []
#     for word in tempList:
#         resultList.append(word.replace(" ","")) #공백제거 후 사용
#     return resultList
#
# # bigram maker
# def makeBigram(tempList):
#     resultList = []
#     for i in range(0, len(tempList)-1):
#         resultList.append(tempList[i] + tempList[i+1].replace(" ","")) #후방단어만 공백제거 후 사용
#     return resultList
#
# # trigram maker
# def makeTrigram(tempList):
#     resultList = []
#     for i in range(0, len(tempList)-2):
#         resultList.append(tempList[i] + tempList[i+1] + tempList[i+2].replace(" ","")) #후방단어만 공백제거 후 사용
#     return resultList
#
# def insertSearchServiceRow(tempList, cateid, itemid):
#
#     if tempList:
#         try:
#             curs = conn.cursor()
#             sql = """INSERT INTO searchdata (`SEARCHKEY`,`CATEID`,`ITEMID`,`SEARCHCOUNT`,`CLICKCOUNT`,`CREATEDTIME`,`MODIFIEDTIME`)
#                      VALUES (%s, %s, %s, 0, 0, now(), now())"""
#             resultList=[]
#             for keyword in tempList:
#                 # 생성된 검색키워드가 2어절이라일때는 키워드로 입력하지 않음.
#                 if len(keyword) > 2:
#                     curs.execute(sql, (keyword,cateid, itemid))
#                     resultList.append([keyword])
#             conn.commit()
#         except Exception as e:
#             return str(e)
#         finally:
#             conn.close
#
#     return resultList




