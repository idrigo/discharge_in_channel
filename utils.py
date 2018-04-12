# -*- coding: utf-8 -*-
import glob
import os

import numpy as np
from geopy.distance import vincenty
import pandas as pd

import config

abspath = os.path.dirname(os.path.abspath(__file__))


def coord_conv(s):
    """Конвертаця координат из градусов в десятичные"""
    try:
        degrees = float(s.split(' ')[0][:-2])
        minutes = (s.split(' ')[1][:-1])
        minutes = float(minutes) / 60
    except:
        degrees = float(s.split(' ')[0][:-2])
        minutes = (s.split(' ')[2][:-1])
        minutes = float(minutes) / 60
    res = degrees + minutes
    return res


def ladcp_df_of_dir(path, extension, read_coords):
    """
    Функция создает датафрейм из файлов измерений LADCP заданой папке с заданым расширением
    Если read_coords = TRUE, то функция считывает из файла ladcp координаты и переводит в нормальный вид
    """
    all_files = glob.glob(os.path.join(path, "*.{}".format(extension)))  # создаем список файлов в директории
    list_ = []
    for file_ in all_files:
        # Getting the file name without extension
        file_name = os.path.splitext(os.path.basename(file_))[0]  # получаем название файла
        df = pd.read_fwf(file_,
                         index_col=None,
                         header=None,
                         skiprows=7,
                         widths=[6, 7, 7, 7],
                         sep=' ')  # считываем в датафрейм из файла с фиксированной шириной столбца

        if read_coords == True:  # считываем координаты если нужно
            lat = str(pd.read_fwf(file_,
                                  nrows=1,
                                  skiprows=3,
                                  header=None).values[0][1])
            lon = str(pd.read_fwf(file_,
                                  nrows=1,
                                  skiprows=4,
                                  header=None).values[0][1])
            lat = coord_conv(lat)
            lon = coord_conv(lon)
            df['Lat'] = lat
            df['Lon'] = lon

        df['Station'] = file_name
        list_.append(df)

    dfn = pd.concat(list_, ignore_index=True)
    if read_coords == True:
        dfn.columns = ['Depth', 'U', 'V', 'W', 'Lat', 'Lon', 'Station']
        dfn = dfn[['Lat', 'Lon', 'Station', 'Depth', 'U', 'V', 'W']]
    else:
        dfn.columns = ['Depth', 'U', 'V', 'W', 'Station']
    return dfn


def dist_calc(df):
    """
    Рассчитываем расстояние между каждыми двумя станциями на разрезе.
    Подразумеваем, что первые две колонки - широта и долгота. Функция работает с pandas_df
    TODO - починить, чтобы нормально запсиывалась dist при одинаковых станциях
    """
    columns = df.columns.values
    columns = np.append(columns, 'Dist')
    columns = np.append(columns, 'Dist_Abs')  # формируем список названий колонок
    array = df.values  # переводим в массив numpy
    dist = [0]
    dist_abs = [0]
    for i in range(len(array) - 1):
        coord1 = array[i][0:2]
        coord2 = array[i + 1][0:2]
        distance = vincenty(coord1, coord2).meters  # считаем расстояние
        dist.append(distance)
        dist_abs.append(distance + dist_abs[i])  # считаем абсолютное расстояние от начала разреза
    razrez = np.column_stack((array, dist, dist_abs))
    df = pd.DataFrame(razrez)
    df.columns = columns
    return df


def interpolate_to_section(x, y, z, start, end, n_points):
    """
    Функция интерполирует данные с некоторого поля на разрез, который задается
    координатами начала и конца (переменные start, end). Start, end должны задаваться в виде кортежей
    Поле задается в виде переменных x,y,z; где все эти переменные - списки одинаковой длины
    (например широта, долгота, глубина)
    """
    print 'Интерполяция рельефа на разрез...'
    raz_lat = np.linspace(start[0], end[0], n_points)  # создаем координаты широты и долготы на разрезе
    raz_lon = np.linspace(start[1], end[1], n_points)
    razrez_cords = np.column_stack((raz_lat, raz_lon))  # np массив широты и долготы точек разреза

    # интерполируем значения из сетки на линию и объединяем в один массив
    # method = 'cubic'
    # method = 'nearest'
    method = 'cubic'

    from scipy.interpolate import griddata

    razrez_z = griddata((x, y),
                        z,
                        (raz_lon, raz_lat),
                        method=method)

    razrez = np.column_stack((razrez_cords, razrez_z))
    # Рассчитываем расстояние между каждыми двумя станциями на разрезе рельефа
    dist = [0]
    dist_abs = [0]
    for i in range(len(razrez) - 1):
        coord1 = razrez[i][0:2]
        coord2 = razrez[i + 1][0:2]
        distance = vincenty(coord1, coord2).meters
        dist.append(distance)
        dist_abs.append(distance + dist_abs[i])

    razrez = np.column_stack((razrez, dist))  # конструируем массив разреза, глубина и расстояние

    df = pd.DataFrame(razrez, columns=['Lat', 'Lon', 'Depth', 'Dist'])
    df['Dist_Abs'] = dist_abs
    if df['Depth'].mean() < 0:
        df['Depth'] = abs(df['Depth'])
    print 'Интерполяция рельефа на разрез завершена'
    return df


def value_idx(df, colname, input_):
    # хитрейшим образом получаем индекс, ближайший к интересующей нас величине в датафрейме
    val = df.iloc[(df[colname] - input_).abs().argsort()[:2]].index[0]
    return val


def print_to_console(Q_cut, Q_plus, Q_minus):
    print 'Суммарный расход в слое ниже {0} м равен {1} м^3/c или {2} Св'.format(config.z_value,
                                                                                 round(Q_cut, 1),
                                                                                 round(Q_cut / 1e6, 5))

    print 'Расход для положительной компоненты в слое ниже {0} м равен {1} м^3/c или {2} Св'.format(config.z_value,
                                                                                                    round(Q_plus, 1),
                                                                                                    round(Q_plus / 1e6,
                                                                                                          5))

    print 'Расход для отрицательной компоненты в слое ниже {0} м равен {1} м^3/c или {2} Св'.format(config.z_value,
                                                                                                    round(Q_minus, 1),
                                                                                                    round(Q_minus / 1e6,
                                                                                                          5))


def results_out(df, Q_cut, Q_plus, Q_minus):  # TODO доделать универсальность построения строки
    import csv
    type_ = config.data_type
    fname = os.path.join(abspath, 'out', 'result.txt')

    if type_ == 'model':
        data = ['None',
                config.method,
                config.z_value,
                round(Q_cut / 1e6, 5),
                round(Q_plus / 1e6, 5),
                round(Q_minus / 1e6, 5),
                type_,
                config.mlat,
                config.mlong]
    elif type_ == 'LADCP':
        stations = ''
        for item in pd.unique(df['Station']):
            stations += item + '-'
        stations = stations[:-1]
        data = [stations,
                config.method,
                config.z_value,
                round(Q_cut / 1e6, 5),
                round(Q_plus / 1e6, 5),
                round(Q_minus / 1e6, 5),
                type_]

    if os.path.exists(fname):
        with open(fname, "w") as myfile:
            w = csv.writer(myfile)
            w.writerow(data)
    else:
        print data
        with open(fname, "a+") as myfile:
            w = csv.writer(myfile)
            w.writerow(['Stations',
                        'Method',
                        'Z_Value',
                        'Q',
                        'Q+',
                        'Q-',
                        'Type',
                        'Lat',
                        'Lon'])
            w.writerow(data)

        return


def grid_to_df(array, x, y, save=None):
    '''
    Принимает на вход двумерный массив значений, x, y. На выходе - датафрейм
    '''
    x_ = []
    y_ = []
    for j in range(len(x)):
        for k in range(len(y)):
            x_.append(x[j])
            y_.append(y[k])

    data = np.column_stack((x_, y_, array.ravel()))
    df = pd.DataFrame(data=data,
                      columns=['X', 'Y', 'Z'])
    df = df.dropna(axis=0)
    df = df.reindex()

    if save:
        if config.model_data:
            df.to_csv('model_t:{}_z:{}.dat'.format(config.t,
                                                   config.z_value),
                      sep='\t')
        else:
            df.to_csv('LADCP_{}_z_{}.dat'.format(config.currents_dir.split(os.sep)[-1],
                                                 config.z_value),
                      sep='\t')
    return df


def path_util(dir, fname=None):
    import os
    abspath = os.getcwd()
    try:
        return os.path.join(abspath, dir, fname)
    except:
        return os.path.join(abspath, dir)
