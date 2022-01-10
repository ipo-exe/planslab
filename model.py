import numpy as np


def avg_2d(var2d, weight):
    """
    average raster value based on weight mask
    :param var2d: 2d numpy array of raster values
    :param weight: 2d numpy array of weight mask
    :return: float average value
    """
    lcl_avg = np.sum(var2d * weight) / np.sum(weight)  # avg
    return lcl_avg


def nash_cascade(q, k, n):
    """
    Runoff routing model of multiple linear reservoirs (Nash Cascade)
    :param q: 1d numpy array of runoff
    :param k: float of residence time in time step units
    :param n: float of equivalent number of reservoirs in Nash Cascade
    :return: 1d numpy array of routed runoff
    """
    from scipy.special import gamma
    size = len(q)
    time = np.arange(0, size)
    nash = np.power((time / k), (n - 1)) * np.exp(- time / k) / (k * gamma(n))  # the Nash Cascade time function
    for t in range(0, len(time)):
        lcl_q = q[t]
        if t == 0:
            qs = lcl_q * nash
        else:
            qs[t:] = qs[t:] + lcl_q * nash[:size - t]
    return qs


def topmodel_d0(qt0, qo, m):
    """
    TOPMODEL Deficit as a function of baseflow (Beven and Kirkby, 1979)
    :param qt0: flow at t=0 in mm/d
    :param qo: max baseflow when d=0 in mm/d
    :param m: decay parameter in mm
    :return: basin global deficit in mm
    """
    return - m * np.log(qt0/qo)


def topmodel_qb(d, qo, m):
    """
    TOPMODEL baseflow as a function of global deficit (Beven and Kirkby, 1979)
    :param d: basin global deficit in mm
    :param qo: max baseflow when d=0 in mm/d
    :param m: decay parameter in mm
    :return: baseflow in mm/d
    """
    return qo * np.exp(-d/m)


def topmodel_qv(d, unz, ksat):
    """
    Global and local vertical recharge rate function (Beven and Woods.. )

    :param d: deficit in mm
    :param unz: usaturated zone water in mm
    :param ksat: velocity parameter in mm/d
    :return: vertical recharge rate
    """
    return ksat * (unz / (d + 0.001)) * (d > 0)  # + 0.001 to avoid division by zero


def topmodel_di(d, twi, m, lamb):
    """
    local deficit di (Beven and Kirkby, 1979)
    :param d: global deficit float
    :param twi: TWI 1d bins array
    :param m: float
    :param lamb: average value of TWIi
    :return: 1d bins array of local deficit
    """
    lcl_di = d + m * (lamb - twi)
    #avg_di = avg_2d(lcl_di, aoi)
    mask = 1.0 * (lcl_di > 0)
    lcl_di2 =  np.abs(lcl_di * mask)  # set negative deficit to zero
    return lcl_di2


def topmodel_vsai(di):
    """
    Variable Source Area
    :param di: float or nd array of local deficit in mm
    :return: float or nd array of pseudo boolean of saturated areas
    """
    return ((di == 0) * 1)


def sim_g2g(series_df, basin, twi, qt0, cpmax, sfmax, roots, qo, m, lamb, ksat, n=2, k=1, scale=1000):
    from sys import getsizeof
    import matplotlib.pyplot as plt
    stocks_lbls = ['D', 'Unz', 'Sfs', 'Cpy', 'VSA']
    flows_lbls = ['Prec', 'PET', 'Int', 'TF', 'R', 'Inf', 'Qv', 'Evc', 'Evs', 'Tpun', 'Tpgw', 'ET', 'Qb', 'Qs', 'Q']

    #
    # append global variables fields
    series = series_df.copy()
    for lbl  in stocks_lbls:
        series[lbl] = 0.0
    for lbl in flows_lbls:
        if lbl == 'Prec' or lbl == 'PET':
            pass
        else:
            series[lbl] = 0.0
    #
    # set global deficit initial conditions
    series['D'].values[0] = topmodel_d0(qt0=qt0, qo=qo, m=m)
    #
    # get map shape
    shape = np.shape(twi)
    rows = shape[0]
    cols = shape[1]
    tlen = len(series)
    #
    # deploy map series
    mps = dict()
    mem_size = 0
    for lbl  in stocks_lbls:
        mps[lbl] = np.zeros(shape=(tlen, rows, cols), dtype='int32')
        mem_size = getsizeof(mps[lbl]) + mem_size
    for lbl in flows_lbls:
        mps[lbl] = np.zeros(shape=(tlen, rows, cols), dtype='int32')
        mem_size = getsizeof(mps[lbl]) + mem_size
    # insert Prec and PET maps
    for t in range(tlen):
        mps['Prec'][t] = scale * series['Prec'].values[t] * (mps['Prec'][t] + 1)
        mps['PET'][t] = scale * series['PET'].values[t] * (mps['PET'][t] + 1)
    print('Size : {} MB'.format(mem_size / 1000000))
    #
    #
    # ESMA loop
    for t in range(1, tlen):
        #
        # Canopy water balance
        mps['Cpy'][t] = mps['Cpy'][t - 1] + mps['Int'][t - 1] - mps['Evc'][t - 1]
        series['Cpy'].values[t] = avg_2d(var2d=mps['Cpy'][t], weight=basin) / scale  # compute basin-wide avg
        #
        #
        # potential Cpy
        p_int = (cpmax * scale) - mps['Cpy'][t]
        #
        # Interceptation
        mps['Int'][t] = (mps['Prec'][t] * (mps['Prec'][t] <= p_int)) + (p_int * ((mps['Prec'][t] > p_int)))
        series['Int'].values[t] = avg_2d(var2d=mps['Int'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Throughfall
        mps['TF'][t] = mps['Prec'][t] - mps['Int'][t]
        series['TF'].values[t] = avg_2d(var2d=mps['TF'][t], weight=basin) / scale
        #
        # Evaporation from the canopy
        mps['Evc'][t] = (mps['Cpy'][t] * (mps['Cpy'][t] <= mps['PET'][t])) + (mps['PET'][t] * (mps['Cpy'][t] > mps['PET'][t]))
        series['Evc'].values[t] = avg_2d(var2d=mps['Evc'][t], weight=basin) / scale  # compute basin-wide avg

        # todo keep going here

    # return
    return series