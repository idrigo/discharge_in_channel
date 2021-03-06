# -*- coding: utf-8 -*-


# ***************** ОСНОВНЫЕ НАСТРОЙКИ ***************

data_type = 'model'  # вид данных
#data_type = 'LADCP'

echo = False  # если рельеф по эхолоту, то TRUE

# если вы не хотите, чтобы границы разреза совпадали с границами данных (например в случае LADCP), раскомментируйте
# в случае модельных данных, лучше оставить закомментированными
#r_start = (10.75, -41.01)  # начало разреза (широта, долгота)
#r_end = (10.835, -41.01)  # конец разреза (широта, долгота)

# заготовка настроек для долготного разреза
shirotny = False  # ставим True если разрез широтный
t = 8  # момент модельного времени
z_value = 3850  # верхняя граница расчета течений
mlat = (-1.15, -0.95)  # широта
mlong = -22.6  # долгота

'''
# заготовка настроек для широтного разреза
z_value = 3920
mlat = -1.09
mlong = (-22.55, -22.35)
t = 8
shirotny = True  # True если наш разрез широтный, False если меридиональный TODO автоматизировать это
'''


# ***************** ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ***************
#  если вы хотите, можно заменить пути к папкам на абсолютные
#  необходимо помнить что в windows разделитель "\", что является экранирующим символом, так что будьте аккуратны

import os
import glob
path = os.path.dirname(os.path.abspath(__file__))

method = 'linear'   # метод интерполяции
n_nodes = 500  # определяем количество узлов сетки по вертикали

echosounder = glob.glob(os.path.join(path, 'relief', '*'))  # TODO убрать дубликат
relief = glob.glob(os.path.join(path, 'relief', '*'))[0]  # получаем файл рельефа из директории рельефа
r_points = 200  # количество точек на разрезе рельефа

currents_dir = os.path.join(path, 'ladcp')  # папка с файлами измерений ladcp (.lad)
model_path = os.path.join(path, 'model')  # папка с файлами модели
m_z_lev = (0, 5000)  # верхняя и нижняя граница выборки из модели