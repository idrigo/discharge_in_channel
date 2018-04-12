# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import config
import os
import utils


def section_plotting(x, y, z, save=False, lim=None, st_x=None, st_y=None, t = None, Q=None):
    # TODO доделать универсальность
    levels = np.linspace(-0.5, 0.5, 20)
    #CS = plt.contour(x, y, z, 5, colors='k', linewidths=0.1)
    #plt.clabel(CS, fontsize=9, inline=1)

    plt.contourf(x,
                 y,
                 z,
                 levels,
                 cmap=plt.get_cmap('coolwarm'))
    plt.colorbar()
    try:
        plt.scatter(st_x, st_y, marker = 'o', c = 'k', s = 0.5)
    except:
        pass

    if lim!=None:
        plt.ylim(lim, max(y))
    plt.gca().invert_yaxis()  # переворачиваем оси

    filename_w_ext = os.path.basename(config.relief)
    filename, file_extension = os.path.splitext(filename_w_ext)
    relief = filename

    if config.data_type == 'model':
        title = 't={}, Q={}\n{}'.format(t, Q, relief)
        filename = 'MODEL t{} lat={} lon={} z={}.png'.format(t, config.mlat, config.mlong, config.z_value)
    else:
        dirname = config.currents_dir.split('/')[-1]
        title = '{}\nQ={}\n{}'.format(dirname, Q, relief)
        # TODO изменить имя файла
        filename = 'LADCP {} {}.png'.format(dirname, relief)
    plt.title(title)

    if save:
        plt.savefig(os.path.join(utils.abspath, 'out', filename), dpi=300)

    plt.show()
    return


'''
def 
    plt.contourf(xi, yi, zz_cut_xy, levels, cmap = plt.get_cmap('coolwarm'))
    plt.ylim(z_value,max(y))
    plt.scatter(x, y, marker = 'o', c = 'k', s = 0.5) #рисуем станции
    plt.gca().invert_yaxis()
    return
'''