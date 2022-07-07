import inp
import numpy as np
import pandas as pd


def slh_sim_g2g(fseries, ftwi, fbasin,
                fparams='none',
                fcpmax='none',
                fsfmax='none',
                froots='none',
                fksat='none',
                pannel=True,
                trace=True,
                tracevars='Cpy-D',
                integrate=True,
                integratevars='Cpy-D',
                animate=True,
                folder='C:/bin',
                wkpl=True,
                label='',
                scale=1000,
                tui=True):
    """

    Stable LULC Hydrology - g2g mode

    Simulated variables:

    'D',    # saturated water stock deficit
    'Unz',  # unsaturated zone water stock
    'Sfs',  # surface water stock
    'Cpy',  # canopy water stock
    'VSA',  # variable source area
    'Prec', # precipitation
    'PET',  # potential evapotranspiration
    'Inc', # interceptation in canopy
    'Ins', # interceptation in surface
    'TF',   # throughfall
    'R',    # runoff
    'RIE',  # infiltration excess runoff (Hortonian)
    'RSE',  # saturation excess runoff (Dunnean)
    'RC',   # runofff coeficient (%)
    'Inf',  # infiltration
    'Qv',   # recharge
    'Evc',  # evaporation from the canopy
    'Evs',  # evaporation from the surface
    'Tpu', # transpiration from the unsaturated zone
    'Tps', # transpiration from the saturated zone
    'ET',   # evapotranspiration
    'Qb',   # baseflow
    'Qs',   # stormflow
    'Q'     # streamflow

    :param fseries: string path to series .txt file
    :param ftwi: string path to twi .asc file
    :param fbasin: string path to basin .asc file
    :param fparams: string path to parameters dataframe .txt file
    :param fcpmax: string 'none' or path to cpmax .asc file
    :param fsfmax: string 'none' or path to sfmax .asc file
    :param froots: string 'none' or path to roots .asc file
    :param fksat: string 'none' or path to ksat .asc file
    :param pannel: boolean to export pannel file
    :param trace: boolean to trace back daily maps of variables
    :param tracevars: string of variables to trace back. Variables must be concatenated by `-`.
    Example: D-Cpy-VSA
    :param integrate: boolean to integrate back maps of variables
    :param integratevars: string of variables to integrate back. Variables must be concatenated by `-`.
    Example: D-Cpy-VSA
    :param animate: boolean to create .gif animation of traced maps
    :param folder: string path to output folder
    :param wkpl: boolean to use folder as workplace
    :param label: string label to output folder
    :param scale: int value to scale maps to integer format (recommended scale >= 1000)
    :param tui: boolean to screen printouts
    :return:
    """
    import model
    from backend import create_rundir, status
    from visuals import pannel_global
    import os
    # folder setup
    if wkpl:  # if the passed folder is a workplace, create a sub folder
        if label != '':
            label = label + '_'
        folder = create_rundir(label=label + 'SLH', wkplc=folder)
    #
    # import data
    if tui:
        status('importing time series')
    df_series = pd.read_csv(fseries, sep=';', parse_dates=['Date'])
    if tui:
        status('importing twi map')
    meta, twi = inp.asc_raster(file=ftwi, dtype='float32')
    if tui:
        status('importing basin map')
    meta, basin = inp.asc_raster(file=fbasin, dtype='float32')
    if tui:
        status('importing parameters')
    param_dct, param_df = inp.hydroparams(fhydroparam=fparams)
    cpmax = param_dct['cpmax']['Set']
    sfmax = param_dct['sfmax']['Set']
    roots = param_dct['roots']['Set']
    qo = param_dct['qo']['Set']
    m = param_dct['m']['Set']
    lamb = param_dct['lambda']['Set']
    ksat = param_dct['ksat']['Set']
    rho = param_dct['rho']['Set']
    c = param_dct['c']['Set']
    k = param_dct['k']['Set']
    n = param_dct['n']['Set']
    qt0 = param_dct['qo']['Set'] / 100
    if fcpmax != 'none':
        if tui:
            status('importing canopy index map')
        meta, cpmax_map = inp.asc_raster(file=fcpmax, dtype='float32')
        cpmax = cpmax_map * cpmax
    if fsfmax != 'none':
        if tui:
            status('importing surface index map')
        meta, sfmax_map = inp.asc_raster(file=fsfmax, dtype='float32')
        sfmax = sfmax_map * sfmax
    if froots != 'none':
        if tui:
            status('importing roots index map')
        meta, roots_map = inp.asc_raster(file=froots, dtype='float32')
        roots = roots_map * roots
    if fksat != 'none':
        if tui:
            status('importing ksat index map')
        meta, ksat_map = inp.asc_raster(file=fksat, dtype='float32')
        ksat = ksat_map * ksat
    if tui:
        status('running model')
    sim = model.simulation(series_df=df_series,
                           twi=twi,
                           basin=basin,
                           cpmax=cpmax,
                           sfmax=sfmax,
                           roots=roots,
                           qo=qo,
                           m=m,
                           lamb=lamb,
                           ksat=ksat,
                           rho=rho,
                           c=c,
                           k=k,
                           n=n,
                           qt0=qt0,
                           lat=-20,
                           tracevars=tracevars,
                           trace=trace,
                           integrate=integrate,
                           integratevars=integratevars,
                           scale=scale)
    sim_df = sim['Series']
    if tui:
        status('exporting series')
    sim_df.to_csv('{}/sim_series.txt'.format(folder), sep=';', index=False)
    if tui:
        status('exporting parameters')
    param_df.to_csv('{}/sim_params.txt'.format(folder), sep=';', index=False)
    if pannel:
        if tui:
            status('exporting series pannel')
        pannel_global(series_df=sim_df, folder=folder, show=False)
    if trace:
        from visuals import export_map_views
        tracevars = tracevars.split('-')
        trace_folder = folder + '/trace'
        os.mkdir(trace_folder)
        for v in tracevars:
            if tui:
                status('exporting {} frames'.format(v))
            lcl_dir = trace_folder + '/{}_frames'.format(v)
            os.mkdir(lcl_dir)
            # get mapid
            if v in ['Cpy', 'Sfs', 'Unz']:
                mapid = 'stock'
            elif v == 'VSA':
                mapid = 'VSA'
            elif v == 'D':
                mapid = 'deficit'
            elif v in ['Evc', 'Evs', 'Tpu', 'Tps', 'ET']:
                mapid = 'flow_v'
            else:
                mapid = 'flow'

            if v == 'VSA':
                ranges = (0, 1)
                v_scale = 1
            else:
                ranges = (np.min(sim['Trace'][v]) / scale, np.max(sim['Trace'][v]) / scale)
                v_scale = scale
            export_map_views(map3d=sim['Trace'][v],
                             series=sim['Series'],
                             meta=meta,
                             ranges=ranges,
                             mapid=mapid,
                             mapttl=v,
                             folder=lcl_dir,
                             filename=v,
                             metadata=True,
                             integration=False,
                             png=True,
                             nodata=-1,
                             scale=v_scale,
                             tui=tui)
            if animate:
                import imageio
                if tui:
                    status('exporting {} gif animation'.format(v))
                png_dir = lcl_dir
                gifname = folder + '/{}_animation.gif'.format(v)
                images = [] # empty list
                for file_name in sorted(os.listdir(png_dir)):
                    if file_name.endswith('.png'):
                        file_path = os.path.join(png_dir, file_name)
                        images.append(imageio.imread(file_path))
                imageio.mimsave(uri=gifname, ims=images)
    if integrate:
        from visuals import plot_map_view
        integratevars = integratevars.split('-')
        integrate_folder = folder + '/integration'
        os.mkdir(integrate_folder)
        for v in integratevars:
            if tui:
                status('exporting {} integration'.format(v))
            # get mapid
            if v in ['Cpy', 'Sfs', 'Unz']:
                mapid = 'stock'
            elif v == 'VSA' or v == 'RC':
                mapid = 'VSA'
            elif v == 'D':
                mapid = 'deficit'
            elif v in ['Evc', 'Evs', 'Tpun', 'Tpgw', 'ET']:
                mapid = 'flow_v'
            else:
                mapid = 'flow'
            # get ranges and scale
            if v == 'VSA':
                ranges = (0, 100)
                v_scale = 1 / 100
            elif v == 'RC':
                ranges = (0, np.max(sim['Integration'][v]))
                v_scale = 1
            else:
                ranges = (np.min(sim['Integration'][v]) / scale, np.max(sim['Integration'][v]) / scale)
                v_scale = scale
            kind = 'accumulation'
            if v in ['D', 'Cpy', 'Sfs', 'Unz', 'VSA', 'RC']:
                kind = 'average'
            # export map
            inp.out_asc_raster(array=sim['Integration'][v] / v_scale,
                                 meta=meta,
                                 folder=integrate_folder,
                                 filename='{}_integration'.format(v))
            # plot view
            plot_map_view(map2d=sim['Integration'][v] / v_scale,
                          ranges=ranges,
                          meta=meta,
                          metadata=True,
                          mapid=mapid,
                          mapttl='{} {} in {} days'.format(v, kind, str(int(len(df_series)))),
                          filename='{}_integration'.format(v),
                          folder=integrate_folder,
                          integration=True)


def sal_d_by_m(ftwi,
               fbasin='none',
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
    from backend import create_rundir, status
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
        folder = create_rundir(label=label + 'SAL_D_by_m__{}_{}'.format(str(int(m1)), str(int(m2))), wkplc=folder)
    # load twi map
    meta, twi = inp.asc_raster(file=ftwi, dtype='float32')
    # load basin map
    if fbasin == 'none':
        basin = (twi.copy() * 0) + 1
    else:
        meta, basin = inp.asc_raster(file=fbasin, dtype='float32')
    # standard lambda:
    lamb_mean = np.sum(twi * basin) / np.sum(basin)
    d = np.linspace(0, dmax, size)
    for i in range(len(d)):
        lcl_d = d[i]
        status('computing frame {} of {}'.format(i + 1, size))
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
                          vmax=dmax * 1.5,
                          filename=lcl_flnm,
                          folder=folder,
                          supttl='Sensitivity to m | lamb={}'.format(str(np.round(lamb_mean, 2))))
    #
    # export gif animation
    status('exporting gif animation')
    png_dir = folder
    gifname = png_dir + '/animation.gif'
    images = []
    for file_name in sorted(os.listdir(png_dir)):
        if file_name.endswith('.png'):
            file_path = os.path.join(png_dir, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(gifname, images)


def sal_d_by_lamb(ftwi,
                  m=10,
                  lamb1=5,
                  lamb2=15,
                  dmax=100,
                  size=100,
                  label='',
                  wkpl=False,
                  folder='C:/bin'):
    """
    SAL of deficit by changing Lambda
    :param ftwi: string filepath to .asc raster map of TWI
    :param lamb1: float of lamb parameter 1
    :param lamb2: float of lamb parameter 2
    :param dmax: int of max deficit
    :param size: int size of SAL
    :param label: string file label
    :param wkpl: boolen to set the output folder as workplace
    :param folder: string file path to output folder
    :return: none
    """
    from model import topmodel_di, topmodel_vsai
    from visuals import sal_deficit_frame
    from backend import create_rundir, status
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
        folder = create_rundir(label=label + 'SAL_D_by_lamb__{}_{}'.format(str(int(lamb1)), str(int(lamb2))), wkplc=folder)
    # load twi maps
    meta, twi = inp.asc_raster(file=ftwi, dtype='float32')
    d = np.linspace(0, dmax, size)
    for i in range(len(d)):
        lcl_d = d[i]
        status('computing frame {} of {}'.format(i + 1, size))
        lcl_di_1 = topmodel_di(d=lcl_d, twi=twi, m=m, lamb=lamb1)
        lcl_di_2 = topmodel_di(d=lcl_d, twi=twi, m=m, lamb=lamb2)
        lcl_vsai_1 = topmodel_vsai(di=lcl_di_1)
        lcl_vsai_2 = topmodel_vsai(di=lcl_di_2)
        # plot frame
        lcl_flnm = 'sal_d_by_lamb__{}'.format(id_label(id=i))
        sal_deficit_frame(dgbl=lcl_d,
                          d1=lcl_di_1,
                          d2=lcl_di_2,
                          p1=lamb1,
                          p2=lamb2,
                          p_lbl='lamb',
                          vsa1=lcl_vsai_1,
                          vsa2=lcl_vsai_2,
                          dgbl_max=dmax,
                          vmax=dmax * 1.5,
                          filename=lcl_flnm,
                          folder=folder,
                          supttl='Sensitivity to lambda | m={}'.format(m))
    #
    # export gif animation
    status('exporting gif animation')
    png_dir = folder
    gifname = png_dir + '/animation.gif'
    images = []
    for file_name in sorted(os.listdir(png_dir)):
        if file_name.endswith('.png'):
            file_path = os.path.join(png_dir, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(gifname, images)


def sal_d_by_twi(ftwi1, ftwi2,
                 fbasin='none',
                 m=10,
                 dmax=100,
                 size=100,
                 label='',
                 wkpl=False,
                 folder='C:/bin'):
    """
    SAL of deficit by changing TWI map
    :param ftwi1: string filepath to .asc raster map of TWI 1
    :param ftwi2: string filepath to .asc raster map of TWI 2
    :param m: int of m parameter
    :param dmax: int of max deficit
    :param size: int size of SAL
    :param label: string file label
    :param wkpl: boolen to set the output folder as workplace
    :param folder: string file path to output folder
    :return: none
    """
    from model import topmodel_di, topmodel_vsai
    from visuals import sal_deficit_frame
    from backend import create_rundir, status
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
        folder = create_rundir(label=label + 'SAL_D_by_TWI', wkplc=folder)

    # load twi maps
    meta, twi1 = inp.asc_raster(file=ftwi1, dtype='float32')
    meta, twi2 = inp.asc_raster(file=ftwi2, dtype='float32')
    # load basin map
    if fbasin == 'none':
        basin = (twi1.copy() * 0) + 1
    else:
        meta, basin = inp.asc_raster(file=fbasin, dtype='float32')
    # compute standard lambdas:
    lamb1 = np.sum(twi1 * basin) / np.sum(basin)
    lamb2 = np.sum(twi2 * basin) / np.sum(basin)
    d = np.linspace(0, dmax, size)
    for i in range(len(d)):
        lcl_d = d[i]
        status('computing frame {} of {}'.format(i + 1, size))
        lcl_di_1 = topmodel_di(d=lcl_d, twi=twi1, m=m, lamb=lamb1)
        lcl_di_2 = topmodel_di(d=lcl_d, twi=twi2, m=m, lamb=lamb2)
        lcl_vsai_1 = topmodel_vsai(di=lcl_di_1)
        lcl_vsai_2 = topmodel_vsai(di=lcl_di_2)
        # plot frame
        lcl_flnm = 'sal_d_by_twi__{}'.format(id_label(id=i))
        sal_deficit_frame(dgbl=lcl_d,
                          d1=lcl_di_1,
                          d2=lcl_di_2,
                          p_lbl='m',
                          p1=m,
                          p2=m,
                          vsa1=lcl_vsai_1,
                          vsa2=lcl_vsai_2,
                          dgbl_max=dmax,
                          vmax=dmax * 1.5,
                          filename=lcl_flnm,
                          folder=folder,
                          supttl='Sensitivity to TWI')
    #
    # export gif animation
    status('exporting gif animation')
    png_dir = folder
    gifname = png_dir + '/animation.gif'
    images = []
    for file_name in sorted(os.listdir(png_dir)):
        if file_name.endswith('.png'):
            file_path = os.path.join(png_dir, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(gifname, images)




