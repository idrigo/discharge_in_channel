# -*- coding: utf-8 -*-
# tested on python 2.7
import pandas as pd
import numpy as np
from geopy.distance import vincenty

import config
import utils
import grads
import plotting

np.warnings.filterwarnings("ignore", category =RuntimeWarning)  # игнорирование некритичных ошибок numpy

# -----------------ТЕЧЕНИЯ-------------------
print 'Создание датафрейма течений...'
if config.data_type == 'model':  # если используем модельные данные, то переходим в функию pygrads
    if not config.shirotny:
        df_cc = grads.select_netcdf('u',
                                    grads.uu,
                                    config.mlat,
                                    config.mlong,
                                    config.m_z_lev,
                                    config.t)  # создаем датафрейм течений
    else:
        df_cc = grads.select_netcdf('v',
                                    grads.vv,
                                    config.mlat,
                                    config.mlong,
                                    config.m_z_lev,
                                    config.t)  # создаем датафрейм течений
# TODO отладка кода
#elif config.data_type == 'geostr':
#    df_cc = pd.read_csv(config.geostr_path,
#                        header=0,
#                        sep=' ')
#    df_cc['Lon'] = -df_cc['Lon']
else:
    df_c = utils.ladcp_df_of_dir(config.currents_dir,  # создаем датафрейм из файлов в директории
                                 'lad',
                                 read_coords=True)
    df_c['Lon'] = -(abs(df_c['Lon']))  # меняем координаты
    df_cc = utils.dist_calc(df_c)  # рассчитываем растояние по разрезу, основываясь на координатах станций

print 'Создание датафрейма течений завершено'

# -------------------------РЕЛЬЕФ---------------------------------
# #делаем датафрейм рельефа
print 'Считывание файла рельефа...'

try:
    # смотрим, заданы ли границы разреза
    start = config.r_start
    end = config.r_end
except:
    start = (min(df_cc['Lat']), min(df_cc['Lon']))
    end = (max(df_cc['Lat']), max(df_cc['Lon']))

if config.echo:  #если используется файл эхолота
    df_relief = pd.read_csv(config.echosounder,
                            sep=' ',
                            names=['Lon', 'Lat', 'Depth'])
    df_relief['Depth'] = abs(df_relief['Depth'])

else:  # если используется двумерный рельеф
    # TODO разобраться с разделителями
    df = pd.read_csv(config.relief,
                     names=['X', 'Y', 'Z'],
                     sep='\t',
                     skiprows=1)

    df_relief = utils.interpolate_to_section(df['X'].values,  # интерполяция данных с двумерной сетки на разрез
                                             df['Y'].values,
                                             df['Z'].values,
                                             start,
                                             end,
                                             config.r_points)

df_r = utils.dist_calc(df_relief)  # рассчитываем растояние по разрезу, основываясь на координатах станций
print 'Создание датафрейма рельефа завершено'

if config.shirotny:  # если считаем широтный разрез
    x_coord = 'Lon'
    component = 'V'
else:
    x_coord = 'Lat'
    component = 'U'


def grid(x_list, y_list, v_nodes):
    """
    :param x_list: список координат x
    :param y_list: список координат y
    :param v_nodes: количество узлов по вертикали
    :return: координаты по x и y, двумерную сетку координат для построения графиков
    """
    print 'Создание сетки рельефа...'
    xi = x_list
    yi = np.linspace(0, max(y_list), v_nodes)
    xx, yy = np.meshgrid(xi, yi)
    print 'Создание сетки рельефа завершено'
    return xi, yi, xx, yy


def interpolate(x, y, z, v_nodes, df_r, method):
    """
    x,y,z - значения, которые нужно проинтерполировать
    создает регулярную сетку значений на основе данных рельефа
    df_r - датафрейм рельефа, на основании которого будет проводиться интерполяция
    v_nodes - разрешение по вертикали
    """
    print 'Интерполяция разреза скоростей...'
    xi, yi, xx, yy = grid(df_r[x_coord].values,
                          df_r['Depth'].values,
                          v_nodes)

    from scipy.interpolate import griddata
    # интерполируем двумя методами на сетку: между измерениями интерполируем кубическим сплайном
    # вне измерений используем приближение ближайшей точки измерения, т.к. этот метод умеет экстраполировать
    zi = griddata((x, y),  # внутренняя сетка
                  z,
                  (xx, yy),
                  method=method)
    zi1 = griddata((x, y),  # внешняя сетка
                   z,
                   (xx, yy),
                   method='nearest')

    zi1[~np.isnan(zi)] = 0  # зануляем внешлюю сетку, там где внутренняя сетка НЕ равна nan
    zz = np.nansum(np.dstack((zi, zi1)), 2) # складываем две сетки, получаем комбинировнанное поле

    print 'Интерполяция разреза скоростей завершена'
    return zz


x = pd.to_numeric(df_cc[x_coord]).values.flatten()  # создаем список координат для интерполяции
y = pd.to_numeric(df_cc['Depth']).values.flatten()
z = pd.to_numeric(df_cc[component]).values.flatten()

zz = interpolate(x,  # интерполируем значения на двумерную сетку
                 y,
                 z,
                 config.n_nodes,
                 df_r,
                 config.method)


# выясняем шаг сетки по глубине TODO - сделать наоборот, т.е. от шага сетки зависит количество узлов
depth_step = max(df_r['Depth'].values) / config.n_nodes


def cut_array(bottom_list,
              array,
              depth_step,
              top):
    print 'Обрезка разреза скоростей по рельефу...'
    '''
    обрезает 2-мерный массив снизу по списку значений, например глубины.
    длина списка должна быть равна колчеству колонок в массиве
    также задается верхняя граница
    '''
    top_cut_list = [top] * np.shape(array)[1]  # создаем список, по которому обрезать. в будущем - неровная граница
    a = array
    for i in range(np.shape(a)[1]):  # итерация по оси x, то есть по колонкам
        # "обрезаем" то количество узлов, которое равно глубине в данной точке, деленное на шаг сетки
        cut_top = int(top_cut_list[i] / depth_step)
        a[:, i][:cut_top] = np.nan

        cut_bottom = int(bottom_list[i] / depth_step)
        # "обрезаем" то количество узлов, которое равно глубине в данной точке, деленное на шаг сетки
        a[:, i][cut_bottom:] = np.nan
    print 'Обрезка разреза скоростей по рельефу завершена'
    return a


zz_cut = cut_array(bottom_list=df_r['Depth'].values,
                   array=zz,
                   depth_step=depth_step,
                   top=config.z_value)

# Считаем площадь для каждого из узлов сетки как шаг по глубине умноженный на шаг по оси X
xstep = vincenty((0, df_r[x_coord][0]), (0, df_r[x_coord][1])).meters
node_weight = depth_step * xstep

Q_cut = np.nansum(zz_cut) * node_weight

zz_plus = zz_cut[np.where(zz_cut > 0.)]
zz_minus = zz_cut[np.where(zz_cut < 0.)]

Q_plus = np.nansum(zz_plus) * node_weight
Q_minus = np.nansum(zz_minus) * node_weight

xi, yi, xx, yy = grid(df_r[x_coord].values,
                      df_r['Depth'],
                      config.n_nodes)

plotting.section_plotting(xi,
                          yi,
                          zz_cut,
                          save=True,
                          lim=config.z_value,
                          st_x=x,
                          st_y=y,
                          t=config.t,
                          Q=round((Q_cut / 1e6), 3))


utils.print_to_console(Q_cut, Q_plus, Q_minus)

utils.results_out(df_cc,
                  Q_cut,
                  Q_plus,
                  Q_minus)

#utils.grid_to_df(zz_cut, xi, yi, save=True)