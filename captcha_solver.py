import requests


from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import Select
import ctypes
from PIL import Image, ImageFilter,ImageEnhance, ImageChops
from pytesseract import *
from io import BytesIO
import os
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import openpyxl
import sys
import re


SCALE_PERCENT = 300
URL_BASE = r'\\images'
FIREFOX = '\\geckodriver'
TESSERACT_BIN = r"\\Tesseract-OCR\\tesseract.exe"
IMG_BASE = os.path.join(URL_BASE, 'imagem_to_break.png')
IMG_TRANSF_1 = os.path.join(URL_BASE, 'img_transf_001.png')  
IMG_TRANSF_2 = os.path.join(URL_BASE, 'img_transf_002.png')   
IMG_TRANSF_3 = os.path.join(URL_BASE, 'img_transf_003.png')  



class BreakCaptcha:
    
    def __init__(self):
        pass

    # transforma a imagem de colorida (RGB) em tons de cinza
    def first_transformation(self):
        img = cv2.imread(IMG_BASE, 0)
        obj = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        cv2.imwrite(IMG_TRANSF_1, obj)
        
    # ajusta a imagem 
    def second_transformation(self):
        im = p.Image.open(IMG_TRANSF_1)
        bg = p.Image.new(im.mode, im.size, im.getpixel((0,0)))
        diff = p.ImageChops.difference(im, bg)
        diff = p.ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            im.crop(bbox)
            im.save(IMG_TRANSF_2) 
        
    # redimensiona a imagem em 300%
    def third_transformation(self):
        img = cv2.imread(IMG_TRANSF_2, cv2.IMREAD_UNCHANGED) 
        width = int(img.shape[1] * SCALE_PERCENT / 100)
        height = int(img.shape[0] * SCALE_PERCENT / 100)
        dim = (width, height)
        
        # aumenta o tamanho da imagem
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite(IMG_TRANSF_3, resized) 
        
    # retorna os caracteres impressos na imagem
    def forth_transformation(self):
        # converte a imagem para o formato RGB
        imagem = p.Image.open(IMG_TRANSF_3).convert('RGB')
        
        # convertendo em um array editável de numpy[x, y, CANALS]
        npimagem = np.asarray(imagem).astype(np.uint8)  
        
        # diminuição dos ruidos antes da binarização
        npimagem[:, :, 0] = 0 # zerando o canal R (RED)
        npimagem[:, :, 2] = 0 # zerando o canal B (BLUE)
        
        # atribuição em escala de cinza
        im = cv2.cvtColor(npimagem, cv2.COLOR_RGB2GRAY) 
        
        # aplicação da truncagem binária para a intensidade
        # pixels de intensidade de cor abaixo de 127 serão convertidos para 0 (PRETO)
        # pixels de intensidade de cor acima de 127 serão convertidos para 255 (BRANCO)
        # A atrubição do THRESH_OTSU incrementa uma análise inteligente dos nivels de truncagem
        ret, thresh = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
        
        # reconvertendo o retorno do threshold em um objeto do tipo PIL.Image
        binimagem = p.Image.fromarray(thresh) 
        
        # inicializa o tesseract e converte a imagem em texto
        pytesseract.tesseract_cmd = TESSERACT_BIN
        text = pytesseract.image_to_string(binimagem)
        
        # retorna o captcha
        return text
    
 
def main():
    captcha = BreakCaptcha()
    # inicio das etapas de quebra
    captcha.first_transformation()
    # segunda transformacao
    captcha.second_transformation()
    # aumenta a imagem
    captcha.third_transformation()
    # quebra a imagem
    captcha_text = captcha.forth_transformation()

    print(captcha_text)
   
   
if __name__ == "__main__":
    main()
    
