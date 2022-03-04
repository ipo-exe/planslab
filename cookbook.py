


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
    import inout
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
    meta, twi = inout.inp_asc_raster(file=_ftwi, dtype='float32')
    # load basin map
    meta, basin = inout.inp_asc_raster(file=_fbasin, dtype='float32')
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


def demo_g2g_model():
    import pandas as pd
    import matplotlib.pyplot as plt
    import inout
    from model import sim_g2g

    # inform series dataset file
    fseries = './data/series_short.txt'

    # inform TWI map file
    ftwi = './data/twi.asc'

    # inform basin map file
    fbasin = './data/basin.asc'


    # load serie to dataframe
    df = pd.read_csv(fseries, sep=';', parse_dates=['Date'])

    # load twi map
    meta, twi = inout.inp_asc_raster(file=ftwi, dtype='float32')
    # load basin map
    meta, basin = inout.inp_asc_raster(file=fbasin, dtype='float32')

    # define parameter values
    cpmax = 15
    sfmax = 30
    roots = 40
    qo = 10
    m = 8
    lamb = 7
    ksat = 3
    qt0 = qo / 100  # a fraction of qo - very dry condition
    k = 1.5
    n = 2

    # scale factor for maps
    scale = 1000

    # call model function
    sim = sim_g2g(series_df=df,
                  twi=twi,
                  basin=basin,
                  cpmax=cpmax,
                  sfmax=sfmax,
                  roots=roots,
                  qo=qo,
                  m=m,
                  lamb=lamb,
                  ksat=ksat,
                  qt0=qt0,
                  k=k,
                  n=n,
                  tracevars=False,  # no map traceback
                  integrate=False,  # no map integration
                  scale=scale)

    # view dataframe
    print(sim['Series'].head(15).to_string())


    # plot some variables series:
    plt.plot(sim['Series']['Date'], sim['Series']['Prec'], 'lightgrey', label='Precipitation')
    plt.plot(sim['Series']['Date'], sim['Series']['Q'], 'black', label='Streamflow')
    plt.plot(sim['Series']['Date'], sim['Series']['Qb'], 'navy', label='Baseflow')
    plt.ylabel('mm/d')
    plt.legend()
    # show plot
    plt.show()

demo_g2g_model()