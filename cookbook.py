
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


demo_sal_lamb()