from flask import Flask
import mysql.connector
import cv2
import numpy
import matplotlib
import urllib.request

app = Flask(__name__)
global conn
conn = mysql.connector.connect(user='K2020509', password='K2020513',host='dbscs.cf0f2mdds5gb.ap-northeast-2.rds.amazonaws.com',database='METAGENSERVICE')


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

def save_checker(obj1, obj2): #파일저장조건확인
    return True

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
    fUrl = "http://127.0.0.1/datas/test1.mp4"
    fId = "C000001"
    fSensetive = 3
    fStt = True
    #
    #파일을 다운로드 하고
    save_video(fUrl, fId)
    vidcap = cv2.VideoCapture("./workfiles/" + fId + ".mp4")
    count = 0
    while(True):
        ret, image = vidcap.read()
        if (int(vidcap.get(1)) % (fSensetive*30)) == 0:
            filename = fId + "_" + str(int(vidcap.get(1))) + ".png"
            if image is None:
                break
            else:
                if (save_checker(obj1, obj2) == True):
                    cv2.imwrite('./pictures/' + filename, image)

        count += 1



    #
    # #파일을 지정된 프레임수로 돌리면서
    #
    # #90프레임마다. 화면을 발췌하여
    #
    # #이전에 저장된 화면과 유사도를 비교하고
    #
    # #3가지 유사도의 비교가 완료되어 3점을 얻으면
    #
    # #해당 이미지는 이전이미지와 다른것으로 간주하고 저장한다.
    result = "Good job"
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9900, debug=True)
