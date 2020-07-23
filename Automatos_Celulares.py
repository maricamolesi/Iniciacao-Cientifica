"""
Created on Thu Nov 21 16:47:32 2019

@author: Mariana
"""
from os import listdir
from os.path import isfile, join
from PIL import Image
import numpy as np
import os

#Entrada do banco de imagens de interesse, no caso do trabalho foi utilizado o banco de imagens Brodatz.
MYPATH = 'Brodatz_128x128'
NEWPATH = '(caminho da pasta para salvar as imagens corroídas)'
ONLYFILES = [f for f in listdir(MYPATH) if isfile(join(MYPATH, f))]
IMAGES = np.empty(len(ONLYFILES), dtype=object)

#Entrada dos parâmetros
V = int(input('Surface roughness v: '))
GAMMA = float(input('Pitting power γ: '))
INT = int(input('Number of iterations: '))

#Matriz dos vetores característicos
FEATURE_MATRIX = np.zeros((len(ONLYFILES), (INT)))

#Acesso a cada imagem da pasta
for n in range(len(ONLYFILES)):
    IMAGES[n] = Image.open(join(MYPATH, ONLYFILES[n]))
    c = IMAGES[n]

    #Add linhas e colunas imaginarias
    b = np.insert(c, 0, values=0, axis=1)
    f = np.insert(b, b.shape[1], values=0, axis=1)
    e = np.insert(f, 0, values=0, axis=0)
    c = np.insert(e, e.shape[0], values=0, axis=0)

    row, col = c.shape
    s = np.zeros((row, col, INT+1))  #Matriz dos estados das células
    d = np.zeros((row, col))         #Matriz da diferença do estado e o menor valor da vizinhança
    Q = np.zeros((row, col))         #Matriz das corrosões
    matrizcorrosao = np.zeros((row, col))   #Matriz da massa total corroída

    #Associação da imagem original aos estados no t=0
    for i in range(row):
        for j in range(col):
            s[i, j, 0] = c[i, j]
    
    #Corrosao da imagem
    for t in range(INT):
        
        #Condição de contorno
        for i in range(col):
            s[0, i, t] = s[1, i, t]
            s[row-1, i, t] = s[row-2, i, t]
        for i in range(row):
            s[i, 0, t] = s[i, 1, t]
            s[i, col-1, t] = s[i, col-2, t]
        
        for i in range(1, row-1):
            for j in range(1, col-1):
                smin = s[i-1, j-1, t]
                for k in range(i-1, i+2):
                    for m in range(j-1, j+2):
                        if (s[k, m, t] <= smin):
                            smin = s[k, m, t]
                d[i, j] = s[i, j, t] - smin

                if (d[i, j] < V or d[i, j] > 255):
                    s[i, j, t+1] = s[i, j, t]
                else:
                    Q[i, j] = int((255 - d[i, j]) * GAMMA)
                    s[i, j, t+1] = s[i, j, t] + Q[i, j]
                    matrizcorrosao[i, j] += Q[i, j]
                    
        FEATURE_MATRIX[n, t] = (np.sum(matrizcorrosao)/(row*col))            
    
    #Normalizar e salvar imagens corroídas em nova pasta
    corrosaofinal = matrizcorrosao*255/np.amax(matrizcorrosao)
    img = Image.fromarray((corrosaofinal).astype(np.uint8))
    file_path = os.path.join(NEWPATH, ONLYFILES[n])
    img.save(file_path)
