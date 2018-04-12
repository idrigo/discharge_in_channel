# -*- coding: utf-8 -*-

import glob
import config
import os
import subprocess
import numpy as np
import pandas as pd
from netCDF4 import Dataset

# проверка, есть ли в директории файлы u.nc и v.nc
# если нет, то запуск скрипта grads -bpcx grads-netcdf.gs, если да - то все норм и можно работать
u = os.path.join(config.model_path, 'u.nc')
v = os.path.join(config.model_path, 'v.nc')

if not (os.path.isfile(u) and os.path.isfile(v)):
    print('Cоздание netcdf массивов')
    dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(config.model_path)
    subprocess.call(['grads', '-bpcx', 'grads-netcdf.gs'])
    os.chdir(dir)

uu = Dataset(u, mode='r')
vv = Dataset(v, mode='r')




def select_netcdf(var, array, latbounds, lonbounds, levbounds, timebound):
    """
    :param var: (str) переменная компоненты вектора скорости ('u' или 'v')
    :param array: (str) путь к nc - массиву, который необходимо обработать
    :param latbounds: [array] границы по широте
    :param lonbounds: [array] границы по долготе
    :param levbounds: [array] границы по глубине
    :param timebound: [int] модельное время
    :return: (df) датафрейм течений
    """
#    array = Dataset(array, mode='r')

    lats = array.variables['lat'][:]
    lons = array.variables['lon'][:]
    times = array.variables['time'][:]
    levs = array.variables['lev'][:]

    timei = np.argmin(np.abs(times - timebound))

    levli = np.argmin(np.abs(levs - levbounds[0]))
    levui = np.argmin(np.abs(levs - levbounds[1]))

    if len(latbounds) == 2:
        # latitude lower and upper index
        latli = np.argmin(np.abs(lats - latbounds[0]))
        latui = np.argmin(np.abs(lats - latbounds[1]))
        lonli = lons[np.argmin(np.abs(lons - lonbounds))]
        subset = array.variables[var][timei, levli:levui, latli:latui, lonli]
        subset = np.ma.getdata(subset)
        subset[subset == -999000000.0] = np.nan

        lev_subset = levs[levli:levui]
        lat_subset = lats[latli:latui]

        depth = []
        lat_ = []
        lon_ = []
        for i in range(len(lev_subset)):
            for j in range(len(lat_subset)):
                depth.append(lev_subset[i])
                lat_.append(lat_subset[j])
                lon_.append(lonli)

    else:
        # latitude lower and upper index
        latli = lats[np.argmin(np.abs(lats - latbounds))]
        lonli = np.argmin(np.abs(lons - lonbounds[0]))
        lonui = np.argmin(np.abs(lons - lonbounds[1]))
        subset = array.variables[var][timei, levli:levui, latli, lonli:lonui]
        subset = np.ma.getdata(subset)
        subset[subset == -999000000.0] = np.nan

        lev_subset = levs[levli:levui]
        lon_subset = lons[lonli:lonui]

        depth = []
        lat_ = []
        lon_ = []

        for i in range(len(lev_subset)):
            for j in range(len(lon_subset)):
                depth.append(lev_subset[i])
                lon_.append(lon_subset[j])
                lat_.append(latli)

    data = np.column_stack((lat_, lon_, depth, subset.ravel()))
    df = pd.DataFrame(data=data,
                      columns=['Lat', 'Lon', 'Depth', var.upper()])
    df[var.upper()] = df[var.upper()] / 100

    return df

