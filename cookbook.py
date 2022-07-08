


def demo_sal_m():
    # import tool:
    from tools import sal_d_by_m

    # define TWI raster file:
    _ftwi = './data/twi.asc'

    # define TWI raster file:
    _fbasin = './data/basin.asc'

    # define output folder:
    _outfolder = 'C:/bin'

    # call tool and parameters:
    sal_d_by_m(ftwi=_ftwi,
               fbasin=_fbasin,
               m1=1,
               m2=5,
               dmax=50,
               size=30,
               label='lab',
               wkpl=True,
               folder=_outfolder)


def demo_sal_lamb():
    import inp
    import numpy as np

    # import tool:
    from tools import sal_d_by_lamb

    # define TWI raster file:
    _ftwi = './data/twi.asc'

    # define Basin map file
    _fbasin = './data/basin.asc'

    # define output folder:
    _outfolder = 'C:/bin'

    # compute the standard lambda
    # load twi map
    meta, twi = inp.asc_raster(file=_ftwi, dtype='float32')
    # load basin map
    meta, basin = inp.asc_raster(file=_fbasin, dtype='float32')
    # standard lambda:
    lamb_mean = np.sum(twi * basin) / np.sum(basin)
    lamb_1 = lamb_mean
    lamb_2 = lamb_1 * 2

    # call tool and parameters:
    sal_d_by_lamb(ftwi=_ftwi,
                  m=4,
                  lamb1=lamb_1,
                  lamb2=lamb_2,
                  dmax=50,
                  size=30,
                  label='lab',
                  wkpl=True,
                  folder=_outfolder)


def demo_sal_twi():
    # import tool:
    from tools import sal_d_by_twi

    # define TWI1 raster file:
    _ftwi1 = './data/twi.asc'

    # define TWI2 raster file:
    _ftwi2 = './data/htwi.asc'

    # define Basin map file
    _fbasin = './data/basin.asc'

    # define output folder:
    _outfolder = 'C:/bin'

    # call tool and set parameters:
    sal_d_by_twi(ftwi1=_ftwi1,
                 ftwi2=_ftwi2,
                 fbasin=_fbasin,
                 m=4,
                 dmax=50,
                 size=30,
                 label='lab',
                 wkpl=True,
                 folder=_outfolder)


def demo_plot_scalar_map():
    from tools import plot_scalar_map
    # define parameters
    s_dirout = '/home/ipora/Documents/bin'
    s_mapfile = './samples/map_ksat.asc'
    s_name = s_mapfile.split('_')[-1].split('.')[0].lower()
    # call tool
    plot_scalar_map(
        s_mapfile=s_mapfile,
        s_mapid=s_name,
        s_ttl='{}'.format(s_name.upper()),
        s_filename='view_{}'.format(s_name),
        s_folder_out=s_dirout,
        b_wkpl=True,
        s_label='',
        b_tui=True,
    )

def demo_plot_scalar_map_batch():
    import os
    from tools import plot_scalar_map
    # define folder
    s_folder = './samples'
    # select files
    lst_files_all = os.listdir(s_folder)
    lst_files = list()
    for f in lst_files_all:
        if '.asc' in f:
            lst_files.append('{}/{}'.format(s_folder, f))
    # main loop:
    for f in lst_files:
        if 'lulc' in f or 'soils' in f or 'shru' in f:
            pass
        else:
            # define parameters
            s_dirout = s_folder
            s_mapfile = f
            s_name = s_mapfile.split('_')[-1].split('.')[0].lower()
            # call tool
            plot_scalar_map(
                s_mapfile=s_mapfile,
                s_mapid=s_name,
                s_ttl='{}'.format(s_name.upper()),
                s_filename='view_map_{}'.format(s_name),
                s_folder_out=s_dirout,
                b_wkpl=False,
                s_label='',
                b_tui=True,
            )

def demo_g2g_model():
    import pandas as pd
    import matplotlib.pyplot as plt
    import inp, geo
    from model import simulation

    # inform series dataset file
    fseries = './samples/series_obs.txt'

    # inform TWI map file
    ftwi = './samples/map_twi.asc'

    # inform HAND map file
    fhand = './samples/map_hand.asc'

    # inform basin map file
    fbasin = './samples/map_basin.asc'

    # load serie to dataframe
    df = pd.read_csv(fseries, sep=';', parse_dates=['Date'])
    # filter
    df = df.query('Date >= "2017-01-01"')

    # load twi map
    meta, twi = inp.asc_raster(file=ftwi, dtype='float32')

    # load hand map
    meta, hand = inp.asc_raster(file=fhand, dtype='float32')

    # load basin map
    meta, basin = inp.asc_raster(file=fbasin, dtype='float32')

    # define parameter values
    hmax = 5
    w = 0.3
    cpmax = 20
    sfmax = 20
    roots = 20
    qo = 10
    m = 10
    lamb = 10
    ksat = 20
    rho = 0.2
    c = 80
    k = 2
    n = 1

    # inital conditions
    qt0 = qo / 100  # a fraction of qo - very dry condition

    # boundary conditions:
    lat = -10

    # scale factor for maps
    scale = 1000

    # compute HTWI
    htwi = geo.htwi(twi=twi, hand=hand, h_max=hmax, h_w=w)
    #plt.imshow(htwi)
    #plt.show()

    # call model function
    sim = simulation(series_df=df,
                     htwi=htwi,
                     basin=basin,
                     cpmax=cpmax,
                     sfmax=sfmax,
                     roots=roots,
                     qo=qo,
                     m=m,
                     lamb=lamb,
                     ksat=ksat,
                     rho=rho,
                     qt0=qt0,
                     c=c,
                     k=k,
                     n=n,
                     lat=lat,
                     trace=False,  # map traceback
                     tracevars='D-Qv',
                     integrate=True,  # map integration
                     integratevars='D-RC-VSA',
                     scale=scale)

    # view dataframe
    print(sim['Series'].head(15).to_string())
    print(sim['Series']['Tp'].sum())
    print(sim['Integration']['D'].dtype)
    plt.imshow(sim['Integration']['RC'])
    plt.show()

    # plot some variables series:
    plt.plot(sim['Series']['Date'], sim['Series']['P'], 'lightgrey', label='P')
    plt.plot(sim['Series']['Date'], sim['Series']['Q_obs'], 'tab:red', label='Qobs')
    #plt.plot(sim['Series']['Date'], sim['Series']['Ev'], 'red', label='Evap.')
    plt.plot(sim['Series']['Date'], sim['Series']['Tp'], 'green', label='Transp.')
    plt.plot(sim['Series']['Date'], sim['Series']['Q'], 'black', label='Streamflow')
    plt.plot(sim['Series']['Date'], sim['Series']['Qb'], 'navy', label='Baseflow')
    plt.ylabel('mm/d')
    plt.legend()
    # show plot
    plt.show()


demo_plot_scalar_map_batch()

#demo_g2g_model()