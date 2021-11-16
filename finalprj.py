# -*- coding: utf-8 -*-

# install..

#pip install imageio-ffmpeg
#pip install opencv-python
#pip install easyocr
# Install detectron2 that matches the above pytorch version
# See https://detectron2.readthedocs.io/tutorials/install.html for instructions
#pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.9/index.html


"""## EasyOCR을 이용한 이미지내 텍스트 인식

https://github.com/JaidedAI/EasyOCR/blob/master/custom_model.md 
"""



import pandas as pd
from PIL import Image
from pathlib import Path
import glob
import easyocr

import torch, torchvision
import sys
import torch
import detectron2
from detectron2.utils.logger import setup_logger
import numpy as np
import os, json, cv2, random
from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog


#print(torch.__version__, torch.cuda.is_available())
#assert torch.__version__.startswith("1.9")


#settings
BASE_PATH = "/content/drive/MyDrive/finalprj"
TEXT_COUNT = 5 #한 화면에서 추출할 텍스트 갯수

#Text Detecting
reader = easyocr.Reader(['en','ko']) # this needs to run only once to load the model into memory

def get_data(df):
  if(len(df) > 0):
    df = df.query('confident > 0.5')
    df['left'] = 0
    df['right'] = 0
    df['top'] = 0
    df['bottom'] = 0
    df['size'] = 0
    for i in df.index:
      #print(df['coord'][i])
      codf = pd.DataFrame(df['coord'][i])
      #print(codf)
      if len(codf) > 3 :
        df.loc[i,'left'] = codf.loc[0,0]
        df.loc[i,'right'] = codf.loc[1,0]
        df.loc[i,'top'] = codf.loc[0,1]
        df.loc[i,'bottom'] = codf.loc[2,1]
        df.loc[i,'size'] = (codf.loc[2,1] - codf.loc[0,1])
    df = df[['txt','left','right','top','bottom','size']] 
    df = df.sort_values(by=['size'],ascending=False).head(TEXT_COUNT)    #텍스트 사이즈에 따라 상위N개만 추출.

  return df

def write_text_result(img_path, resultdf):
  file_path = img_path.replace("/src/", "/target/result/").replace(".png","_text.txt")
  f = open(file_path,'w')
  #f.write('[Text] \n')
  for j in resultdf.index:
    f.write( f'[{resultdf.loc[j,"left"]},{resultdf.loc[j,"top"]}][{resultdf.loc[j,"right"]},{resultdf.loc[j,"bottom"]}]{resultdf.loc[j,"txt"]} ')
    f.write('\n')
  f.close()




srcimgs = glob.glob(f'{BASE_PATH}/src/*')

for img_path in srcimgs:
  result = reader.readtext(img_path)
  resultdf = pd.DataFrame(result);
  if(len(resultdf) > 0):
    resultdf.columns = ['coord','txt','confident']
    resultdf = get_data(resultdf)
    write_text_result(img_path, resultdf)
  print(f'%s --------------------', img_path)
  print(resultdf)


#Object Detecting

# Setup detectron2 logger
setup_logger()


def write_object_result(img_path, outputs):
  file_path = img_path.replace("/src/", "/target/result/").replace(".png",".txt")
  print(file_path)
  f = open(file_path,'a')
  f.write('[OBJECT] \n')
  #classnmlist = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes
  classnmlist = ['사람', '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '배', '신호등', '소화기', '정지신호', '주차기', '벤치', '새', '고양이', '개', '말', '양', '소', '코끼리', '곰', '얼룩말', '기린', '배낭', '우산', '가방', '타이', '가방', '프리스비', '스키', '스노보드', '공', '연', '야구배트', '글러브', '스케이드보드', '서핑보드', '라켓', '병', '잔', '컵', '포크', '칼', '숟가락', '보울', '바나나', '사과', '샌드위치', '오렌지', '브로콜리', '당근', '핫도그', '피자', '도넛', '케이크', '의자', '쇼파', '화분', '침대', '식탁', '변기', '모니터', '노트북', '마우스', '리모콘', '키보드', '휴대폰', '전자렌지', '오븐', '토스터', '씽크대', '냉장고', '책', '시계', '꽃병', '가위', '곰인형', '드라이어', '치솔']
  classlist = outputs["instances"].pred_classes.tolist()
  boxlist = outputs["instances"].pred_boxes.tensor.cpu().tolist()


  for i in range(len(classlist)):
    f.write( f'[{int(boxlist[i][0])},{int(boxlist[i][1])}][{int(boxlist[i][2])},{int(boxlist[i][3])}]{classnmlist[classlist[i]]} ')
    f.write('\n')
  f.close()

def write_img_result(img_path, img):
  tar_img_path = img_path.replace('/src/','/target/img/').replace('.png','_marked.png')
  cv2.imwrite(tar_img_path,img)


cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)

srcimgs = glob.glob(f'{BASE_PATH}/src/*')

for img_path in srcimgs:
  im = cv2.imread(img_path)
  #cv2_imshow(im)
  outputs = predictor(im)
  write_object_result(img_path, outputs)
  v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
  out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
  write_img_result(img_path, out.get_image()[:, :, ::-1])
  cv2_imshow(out.get_image()[:, :, ::-1])

#img 삭제

if os.path.exists(BASE_PATH + "/src"):
  for file in os.scandir(BASE_PATH + "/src"):
    os.remove(file.path)




