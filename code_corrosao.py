"""
Created on Thu Nov 21 16:47:32 2019

@author: Mariana
"""
from os import listdir
from os.path import isfile, join
from PIL import Image
import numpy as np
import os

MYPATH = 'Brodatz_128x128'
NEWPATH = 'Brodatz_128x128_corrosao2'
ONLYFILES = [f for f in listdir(MYPATH) if isfile(join(MYPATH, f))]
IMAGES = np.empty(len(ONLYFILES), dtype=object)

V = 2
GAMMA = 0.05
INT = 100

for n in range(730, 1778):
    IMAGES[n] = Image.open(join(MYPATH, ONLYFILES[n]))
    c = IMAGES[n]

#Add linhas e colunas imaginarias
    b = np.insert(c, 0, values=0, axis=1)
    f = np.insert(b, b.shape[1], values=0, axis=1)
    e = np.insert(f, 0, values=0, axis=0)
    c = np.insert(e, e.shape[0], values=0, axis=0)

    row, col = c.shape
    s = np.zeros((row, col, INT+1))
    d = np.zeros((row, col))
    Q = np.zeros((row, col))
    matrizcorrosao = np.zeros((row, col))

#Associação da imagem original aos estados no t=0
    for i in range(row):
        for j in range(col):
            s[i, j, 0] = c[i, j]

    for t in range(INT):

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


                if (d[i, j] < V or d[i, j] >= 255):
                    s[i, j, t+1] = s[i, j, t]
                else:
                    Q[i, j] = int((255 - d[i, j]) * GAMMA)
                    s[i, j, t+1] = s[i, j, t] + Q[i, j]
                    matrizcorrosao[i, j] += Q[i, j]
                    
    y = 255/np.amax(matrizcorrosao)
    corrosaofinal = matrizcorrosao*y
    img = Image.fromarray((corrosaofinal).astype(np.uint8))
    file_path = os.path.join(NEWPATH, ONLYFILES[n])
    img.save(file_path)