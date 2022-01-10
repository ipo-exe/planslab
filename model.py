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
    stocks_lbls = ['D',  # saturated water stock deficit
                   'Unz',  # unsaturated zone water stock
                   'Sfs',  # surface water stock
                   'Cpy',  # canopy water stock
                   'VSA']  # variable source area
    flows_lbls = ['Prec',  # precipitation
                  'PET',  # potential evapotranspiration
                  'Intc',  # interceptation in canopy
                  'Ints',  # interceptation in surface
                  'TF',  # throughfall
                  'R',  # runoff
                  'Inf',  # infiltration
                  'Qv',  # recharge
                  'Evc',  # evaporation from the canopy
                  'Evs',  # evaporation from the surface
                  'Tpun',  # transpiration from the unsaturated zone
                  'Tpgw',  # transpiration from the saturated zone
                  'ET',  # evapotranspiration
                  'Qb',  # baseflow
                  'Qs',  # stormflow
                  'Q']  # streamflow

    #
    # append global variables fields
    ts = series_df.copy()
    for lbl  in stocks_lbls:
        ts[lbl] = 0.0
    for lbl in flows_lbls:
        if lbl == 'Prec' or lbl == 'PET':
            pass
        else:
            ts[lbl] = 0.0
    #
    # set global deficit initial conditions
    ts['D'].values[0] = topmodel_d0(qt0=qt0, qo=qo, m=m)
    #
    # get map shape
    shape = np.shape(twi)
    rows = shape[0]
    cols = shape[1]
    tlen = len(ts)
    #
    # deploy map series
    mps = dict()
    mem_size = 0
    for lbl  in stocks_lbls:
        mps[lbl] = np.zeros(shape=(tlen, rows, cols), dtype='int32')
        mem_size = getsizeof(mps[lbl]) + mem_size
    for lbl in flows_lbls:
        if lbl == 'Qb' or lbl == 'Qs' or lbl == 'Q':
            pass
        else:
            mps[lbl] = np.zeros(shape=(tlen, rows, cols), dtype='int32')
            mem_size = getsizeof(mps[lbl]) + mem_size
    # insert Prec and PET maps
    for t in range(tlen):
        mps['Prec'][t] = scale * ts['Prec'].values[t] * (mps['Prec'][t] + 1)
        mps['PET'][t] = scale * ts['PET'].values[t] * (mps['PET'][t] + 1)
    print('Size : {} MB'.format(mem_size / 1000000))
    #
    # get initial local deficits
    mps['D'][0] = topmodel_di(d=ts['D'].values[0], twi=twi, m=m, lamb=lamb)
    #
    #
    # ESMA loop
    for t in range(1, tlen):
        #
        # Canopy water balance
        mps['Cpy'][t] = mps['Cpy'][t - 1] + mps['Intc'][t - 1] - mps['Evc'][t - 1]
        ts['Cpy'].values[t] = avg_2d(var2d=mps['Cpy'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Surface water balance
        mps['Sfs'][t] = mps['Sfs'][t - 1] + mps['Ints'][t - 1] - mps['Inf'][t - 1] - mps['Evs'][t - 1]
        ts['Sfs'].values[t] = avg_2d(var2d=mps['Sfs'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Unsaturated zone water balance
        mps['Unz'][t] = mps['Unz'][t - 1] + mps['Inf'][t - 1] - mps['Qv'][t - 1] - mps['Tpun'][t - 1]
        ts['Unz'].values[t] = avg_2d(var2d=mps['Unz'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Deficit update:
        ts['D'].values[t] = ts['D'].values[t - 1] - ts['Qv'].values[t - 1] + ts['Qb'].values[t - 1] + ts['Tpgw'].values[t - 1]
        mps['D'][t] = scale * topmodel_di(d=ts['D'].values[t], twi=twi, m=m, lamb=lamb)
        #
        # VSA update
        mps['VSA'][t] = topmodel_vsai(di=mps['D'][t])
        ts['VSA'].values[t] = 100 * np.sum(mps['VSA'][t] * basin) / np.sum(basin) # in %
        #
        # Baseflow
        ts['Qb'].values[t] = topmodel_qb(d=ts['D'].values[t], qo=qo, m=m)



        # ---- Canopy

        # potential interceptation
        p_intc = (cpmax * scale) - mps['Cpy'][t]
        #
        # Interceptation in the canopy
        mps['Intc'][t] = (mps['Prec'][t] * (mps['Prec'][t] <= p_intc)) + (p_intc * ((mps['Prec'][t] > p_intc)))
        ts['Intc'].values[t] = avg_2d(var2d=mps['Intc'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Throughfall
        mps['TF'][t] = mps['Prec'][t] - mps['Intc'][t]
        ts['TF'].values[t] = avg_2d(var2d=mps['TF'][t], weight=basin) / scale
        #
        # Evaporation from the canopy
        mps['Evc'][t] = (mps['Cpy'][t] * (mps['Cpy'][t] <= mps['PET'][t])) + (mps['PET'][t] * (mps['Cpy'][t] > mps['PET'][t]))
        ts['Evc'].values[t] = avg_2d(var2d=mps['Evc'][t], weight=basin) / scale  # compute basin-wide avg
        pet_update = mps['PET'][t] - mps['Evc'][t]  # update PET

        # ---- Saturated Root Zone - transpiration

        p_tpgw = ((roots * scale) - mps['D'][t]) * (((roots * scale) - mps['D'][t]) > 0)
        mps['Tpgw'][t] = (pet_update * (p_tpgw >= pet_update)) + (p_tpgw * (p_tpgw < pet_update))
        ts['Tpgw'].values[t] = avg_2d(var2d=mps['Tpgw'][t], weight=basin) / scale  # compute basin-wide avg
        pet_update = pet_update - mps['Tpgw'][t]  # update PET


        # ---- Surface (runoff and inf)


        # potential Sfs
        p_ints = (sfmax * scale) - mps['Sfs'][t]
        #
        # Interceptation in the surface
        mps['Ints'][t] = (mps['TF'][t] * (mps['TF'][t] <= p_ints)) + (p_ints * ((mps['TF'][t] > p_ints)))
        ts['Ints'].values[t] = avg_2d(var2d=mps['Ints'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff
        mps['R'][t] = mps['TF'][t] - mps['Ints'][t]
        ts['R'].values[t] = avg_2d(var2d=mps['R'][t], weight=basin) / scale # compute basin-wide avg
        #
        # surface top-down potential inf
        p_inf_sfs = (mps['Sfs'][t] * (mps['Sfs'][t] < (ksat * scale))) + ((ksat * scale) * (mps['Sfs'][t] < (ksat * scale)))
        #
        # potential infiltration allowed by the usaturated zone water content:
        p_inf_unz = (mps['D'][t] - mps['Unz'][t]) * ((mps['D'][t] - mps['Unz'][t])> 0)
        #
        # Infiltration
        mps['Inf'][t] = (p_inf_sfs * (p_inf_sfs < p_inf_unz)) + (p_inf_unz * (p_inf_sfs >= p_inf_unz))
        ts['Inf'].values[t] = avg_2d(var2d=mps['Inf'][t], weight=basin) / scale # compute basin-wide avg


        # ----- Unsat zone


        # potential qv recharge rate without PET:
        p_qv = topmodel_qv(d=mps['D'][t], unz=mps['Unz'][t], ksat=(ksat * scale))
        #
        # actual qv recharge rate with PET (proportional to ratio):
        mps['Qv'][t] = mps['Unz'][t] * (p_qv / (pet_update + p_qv + 1)) * ((pet_update + p_qv) > 0)  # + 1 to avoid division by zero
        ts['Qv'].values[t] = avg_2d(var2d=mps['Qv'][t], weight=basin) / scale  # compute basin-wide avg
        #
        # compute potential tpun transpiration rate (gated by roots and proportional to ratio):
        p_tpun = mps['Unz'][t] * (mps['Unz'][t] <= (roots * scale)) + (roots * scale) * (mps['Unz'][t] > (roots * scale))
        p_tpun = p_tpun * (pet_update / (pet_update + p_qv + 1)) * ((pet_update + p_qv) > 0)  # + 1 to avoid division by zero
        #
        # transpiration from the unsaturated zone
        tpun_i = (pet_update * (p_tpun >= pet_update)) + (p_tpun * (p_tpun < pet_update))
        ts['Tpun'].values[t] = avg_2d(var2d=mps['Tpun'][t], weight=basin) / scale  # compute basin-wide avg
        pet_update = pet_update - mps['Tpun'][t]  # update PET


        # ---- Surface (evaporation)

        # potential evap
        p_evs = mps['Sfs'][t] - mps['Inf'][t]

        # Evaporation from the surface
        # todo fix negative values
        mps['Evs'][t] = (p_evs * (p_evs <= pet_update)) + (pet_update * (p_evs > pet_update))
        ts['Evs'].values[t] = avg_2d(var2d=mps['Evs'][t], weight=basin) / scale  # compute basin-wide avg
        #
        #
        # compute full ET signal
        mps['ET'][t] = mps['Evc'][t] + mps['Evs'][t] + mps['Tpun'][t] + mps['Tpgw'][t]
        ts['ET'].values[t] = avg_2d(var2d=mps['ET'][t], weight=basin) / scale  # compute basin-wide avg
    #
    #
    # RUNOFF ROUTING by Nash Cascade of linear reservoirs
    if n < 1:
        n = 1.0
    ts['Qs'] = nash_cascade(ts['R'].values, k=k, n=n)
    #
    #
    # Compute full discharge Q = Qb + Qs
    ts['Q'] = ts['Qb'] + ts['Qs']

    # return
    return ts