import inout
import numpy as np
import pandas as pd


def sal_d_by_m(ftwi,
               m1=10,
               m2=500,
               dmax=100,
               size=100,
               label='',
               wkpl=False,
               folder='C:/bin'):
    """
    SAL of deficit by changing m
    :param ftwi: string filepath to .asc raster map of TWI
    :param m1: float of m parameter 1
    :param m2: float of m parameter 2
    :param dmax: int of max deficit
    :param size: int size of SAL
    :param label: string file label
    :param wkpl: boolen to set the output folder as workplace
    :param folder: string file path to output folder
    :return: none
    """
    from model import topmodel_di, topmodel_vsai
    from visuals import sal_deficit_frame
    from backend import create_rundir
    import imageio
    import os

    def id_label(id):
        if id < 10:
            return '000' + str(id)
        elif id >= 10 and id < 100:
            return '00' + str(id)
        elif id >= 100 and id < 1000:
            return '0' + str(id)
        elif id >= 1000 and id < 10000:
            return  str(id)

    # folder setup
    if wkpl:  # if the passed folder is a workplace, create a sub folder
        if label != '':
            label = label + '_'
        folder = create_rundir(label=label + 'SAL_D_by_m__{}_{}'.format(str(int(m1)), str(int(m1))), wkplc=folder)
    # load twi maps
    meta, twi = inout.inp_asc_raster(file=ftwi, dtype='float32')
    # standard lambda:
    lamb_mean = np.mean(twi)
    d = np.linspace(0, dmax, size)
    for i in range(len(d)):
        lcl_d = d[i]
        print(i)
        lcl_di_1 = topmodel_di(d=lcl_d, twi=twi, m=m1, lamb=lamb_mean)
        lcl_di_2 = topmodel_di(d=lcl_d, twi=twi, m=m2, lamb=lamb_mean)
        lcl_vsai_1 = topmodel_vsai(di=lcl_di_1)
        lcl_vsai_2 = topmodel_vsai(di=lcl_di_2)
        # plot frame
        lcl_flnm = 'sal_d_by_m__{}'.format(id_label(id=i))
        sal_deficit_frame(dgbl=lcl_d,
                          d1=lcl_di_1,
                          d2=lcl_di_2,
                          p1=m1,
                          p2=m2,
                          p_lbl='m',
                          vsa1=lcl_vsai_1,
                          vsa2=lcl_vsai_2,
                          dgbl_max=dmax,
                          vmin=0,
                          vmax=dmax,
                          filename=lcl_flnm,
                          folder=folder,
                          supttl='Sensitivity to m | lamb={}'.format(round(lamb_mean, 2)))
        #
        # export gif animation
        png_dir = folder
        gifname = png_dir + '/animation.gif'
        images = []
        for file_name in sorted(os.listdir(png_dir)):
            if file_name.endswith('.png'):
                file_path = os.path.join(png_dir, file_name)
                images.append(imageio.imread(file_path))
        imageio.mimsave(gifname, images)