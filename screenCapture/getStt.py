from flask import jsonify
from . import api
import mysql.connector

# 정확도를 위해 이 부분을 아래로 내리고 활성화하여 높일수 있지만 성능에 문제가 생길 수 있음.
conn = mysql.connector.connect(user='K2020509', password='K2020513',
                              host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',
                              database='METAGENSERVICE')
conn.close()

# by micky, pentaworks
# 2021-02-05
# We show search results with search keywords and add the number of times to the search words in the dictionary. In addition, keywords can be specified as search terms if there are no search results.

# @api.route('/searchList/<searchKey>')
# def searchList(searchKey):
#     # 검색어 사전처리
#     import re
#     if searchKey:
#         strSearchKey = re.sub('[-=.#/?:$@!*&^)}]', '', searchKey)
#     else:
#         return jsonify('Wrong SearchKey : You cannot use punctuation marks.')
#
#     # 검색결과 추출
#     result = filterResult(selectedRow(strSearchKey))
#
#     # 검색된 카테고리와 아이템의 조회숫자를 올린다.
#     counter = updateSearchCount(result)
#
#     # 검색된 내용이 없을경우 키워드 등록 및 추가키워드 대기
#     if len(result) == 0:
#         adder = insertNewKeyword(searchKey)
#
#     # 결과만들기
#     resultList = []
#     resultList.append(['RESULT', ['SUCCESS']])
#     resultList.append(['DATA', result])
#     return jsonify(resultList)
#
# # 자동완성 검색결과 만들기
# def selectedRow(tempText):
#     if tempText:
#         try:
#             # 성능향상을 높이기 위해 이 구문을 상단으로 옮기고 대신 한번씩 리부팅하면서 커넥션을 갱신할 수 있음
#             # conn = pymysql.connect(host='localhost', user='seeker', password='penta1234', db='searchservice',charset='utf8')
#             curs = conn.cursor()
#             sql = "SELECT SEARCHKEY, CONCAT(CATEID,'^^',ITEMID) AS ITEMKEY, KEYNUM, SEARCHCOUNT, CLICKCOUNT, LENGTH(SEARCHKEY) AS KEYLENGTH " \
#                   "FROM SEARCHDATA " \
#                   "WHERE SEARCHKEY LIKE '%"+tempText+"%' " \
#                   "ORDER BY CLICKCOUNT DESC, SEARCHCOUNT DESC, KEYLENGTH DESC, MODIFIEDTIME DESC"
#             curs.execute(sql)
#             # data Fetch
#             rows = curs.fetchall()
#         except Exception as e:
#             return str(e)
#         finally:
#             conn.close
#     return rows
#
# # 검색결과 필터
# def filterResult(tempList):
#     resultList = []
#     # 조회결과를 가지고와서 하나씩 분해한다.
#     for data in tempList:
#         # 최초키워드면 바로 입력하고
#         if len(resultList) < 1:
#             checkFlag = True
#         else:
#             # 최초가 아닐경우 같은 아이템식별자를 가진 것은 중복해서 넣지 않도록 한다.
#             for row in resultList:
#                 if row[1] == data[1]:
#                     checkFlag = False
#                     break
#                 else:
#                     checkFlag = True
#         # 반환해야 할 내용이면 반환결과에 저장한다.
#         if checkFlag:
#             resultList.append([data[0], data[1], data[2]])
#
#     return resultList
#
# # 조회됬던 ITEM에 대한 검색카운트를 올린다.
# def updateSearchCount(tempList):
#
#     if tempList:
#         try:
#             conn = pymysql.connect(host='safere-dev-db.cluster-caacwbaeku0h.ap-northeast-2.rds.amazonaws.com', user='seeker', password='penta1234', db='searchservice',charset='utf8')
#             curs = conn.cursor()
#             sql = """UPDATE SEARCHSERVICE.SEARCHDATA
#                      SET SEARCHCOUNT = (SEARCHCOUNT + 1)
#                      WHERE CATEID = %s AND ITEMID = %s"""
#
#             for row in tempList:
#                 data = tuple(row)
#                 itemkey = tuple(data[1].split('^^'))
#                 curs.execute(sql, (itemkey[0], itemkey[1]))
#             conn.commit()
#         except Exception as e:
#             return str(e)
#         finally:
#             conn.close
#
#     return True
#
# def insertNewKeyword(tempText):
#     if tempText:
#         try:
#             conn = pymysql.connect(host='safere-dev-db.cluster-caacwbaeku0h.ap-northeast-2.rds.amazonaws.com', user='seeker', password='penta1234', db='searchservice', charset='utf8')
#             curs = conn.cursor()
#             sql = "INSERT INTO NEWKEYWORD(KEYWORD) VALUE ('"+tempText+"')"
#             curs.execute(sql)
#             conn.commit()
#         except Exception as e:
#             return str(e)
#         finally:
#             conn.close
#     return True