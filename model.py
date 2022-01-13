import matplotlib.pyplot as plt
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


def topmodel_qv(d, unz, ksat, threshold=0.001):
    """
    Global and local vertical recharge rate function (Beven and Woods.. )

    :param d: deficit in mm
    :param unz: usaturated zone water in mm
    :param ksat: velocity parameter in mm/d
    :return: vertical recharge rate
    """
    return ksat * (unz / (d + threshold)) * (d > 0)  # threshold to avoid division by zero


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


def sim_g2g(series_df, basin, twi, qt0, cpmax, sfmax, roots, qo, m, lamb, ksat, n=2, k=1,
            scale=1000,
            trace=True,
            tracevars='D-Cpy',
            integrate=False,
            integratevars='D-Qv'):
    from sys import getsizeof
    #import matplotlib.pyplot as plt
    # stock variables
    simvars = ['D',    # saturated water stock deficit
               'Unz',  # unsaturated zone water stock
               'Sfs',  # surface water stock
               'Cpy',  # canopy water stock
               'VSA',  # variable source area
               'Prec', # precipitation
               'PET',  # potential evapotranspiration
               'Intc', # interceptation in canopy
               'Ints', # interceptation in surface
               'TF',   # throughfall
               'R',    # runoff
               'RIE',  # infiltration excess runoff (Hortonian)
               'RSE',  # saturation excess runoff (Dunnean)
               'RC',   # runofff coeficient (%)
               'Inf',  # infiltration
               'Qv',   # recharge
               'Evc',  # evaporation from the canopy
               'Evs',  # evaporation from the surface
               'Tpun', # transpiration from the unsaturated zone
               'Tpgw', # transpiration from the saturated zone
               'ET',   # evapotranspiration
               'Qb',   # baseflow
               'Qs',   # stormflow
               'Q']    # streamflow

    #
    # append global variables fields
    ts = series_df.copy()
    for v in simvars:
        if v == 'Prec' or v == 'PET':
            pass
        else:
            ts[v] = 0.0
    #
    #
    # get map shape
    shape = np.shape(twi)
    rows = shape[0]
    cols = shape[1]
    tlen = len(ts)
    #
    # deploy simulation maps
    mps = dict()
    mem_size = 0
    for v in simvars:
        if v == 'Qb' or v == 'Qs' or v == 'Q':
            pass
        else:
            mps[v] = np.zeros(shape=shape, dtype='int32')
            mem_size = getsizeof(mps[v]) + mem_size
    #print('Sim size : {} MB'.format(mem_size / 1000000))
    mps_trace = dict()
    if trace:
        tracevars = tracevars.split('-')
        mem_size = 0
        for v in tracevars:
            mps_trace[v] = np.zeros(shape=(tlen, rows, cols), dtype='int32')
            mem_size = getsizeof(mps_trace[v]) + mem_size
    #print('Trace size : {} MB'.format(mem_size / 1000000))
    mps_integrate = dict()
    if integrate:
        integratevars = integratevars.split('-')
        for v in integratevars:
            mps_integrate[v] = np.zeros(shape=(rows, cols), dtype='int32')
    #
    # get initial local deficits
    ts['D'].values[0] = topmodel_d0(qt0=qt0, qo=qo, m=m)
    mps['D'] = scale * topmodel_di(d=ts['D'].values[0], twi=twi, m=m, lamb=lamb)
    mps['VSA'] = topmodel_vsai(di=mps['D'])
    #
    #
    # ESMA loop
    for t in range(tlen):
        # INPUT define Prec and PET
        mps['Prec'] = ts['Prec'].values[t] * scale * np.ones(shape=shape, dtype='int32')
        mps['PET'] = ts['PET'].values[t] * scale * np.ones(shape=shape, dtype='int32')

        # STOCKS WATER BALANCE (backward looking)
        if t > 0:
            # Canopy water balance
            mps['Cpy'] = mps['Cpy'] + mps['Intc'] - mps['Evc']
            ts['Cpy'].values[t] = avg_2d(var2d=mps['Cpy'], weight=basin) / scale  # compute basin-wide avg
            #
            # Vadose zone water balance
            mps['Unz'] = mps['Unz'] + mps['Inf'] - mps['Qv'] - mps['Tpun']
            ts['Unz'].values[t] = avg_2d(var2d=mps['Unz'], weight=basin) / scale  # compute basin-wide avg
            #
            # Surface water balance
            mps['Sfs'] = mps['Sfs'] + mps['Ints'] - mps['Inf'] - mps['Evs']
            ts['Sfs'].values[t] = avg_2d(var2d=mps['Sfs'], weight=basin) / scale  # compute basin-wide avg
            #
            # Deficit water balance
            ts['D'].values[t] = ts['D'].values[t - 1] + ts['Qb'].values[t - 1] + ts['Tpgw'].values[t - 1] - \
                                ts['Qv'].values[t - 1]
            # update Deficit
            mps['D'] = scale * topmodel_di(d=ts['D'].values[t], twi=twi, m=m, lamb=lamb)
            # update VSA
            mps['VSA'] = topmodel_vsai(di=mps['D'])
            ts['VSA'].values[t] = 100 * avg_2d(var2d=mps['VSA'], weight=basin) / scale  # compute basin-wide avg

        # FLOWS COMPUTATION

        # --- Canopy flows

        # potential interceptation on canopy
        p_intc = (scale * cpmax) - mps['Cpy']
        #
        # Interceptation in the canopy
        mps['Intc'] = (p_intc * (mps['Prec'] > p_intc)) + (mps['Prec'] * (mps['Prec'] <= p_intc))
        ts['Intc'].values[t] = avg_2d(var2d=mps['Intc'], weight=basin) / scale  # compute basin-wide avg
        #
        # Evaporation in the canopy
        mps['Evc'] = (mps['PET'] * (mps['Cpy'] > mps['PET'])) + (mps['Cpy'] * (mps['Cpy'] <= mps['PET']))
        ts['Evc'].values[t] = avg_2d(var2d=mps['Evc'], weight=basin) / scale  # compute basin-wide avg
        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Evc'])
        #
        # Throughfall
        mps['TF'] = mps['Prec'] - mps['Intc']
        ts['TF'].values[t] = avg_2d(var2d=mps['TF'], weight=basin) / scale  # compute basin-wide avg


        # --- Transpiration from groundwater

        # potential tp from gw:
        p_tpgw = (roots * scale) - mps['D']
        p_tpgw = p_tpgw * (p_tpgw >= 0) # remove negative values
        #
        # Transpiration from groundwater
        mps['Tpgw'] = (mps['PET'] * (p_tpgw > mps['PET'])) + (p_tpgw * (p_tpgw <= mps['PET']))
        ts['Tpgw'].values[t] = avg_2d(var2d=mps['Tpgw'], weight=basin) / scale  # compute basin-wide avg
        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Tpgw'])

        # ---- Interceptation on the surface

        # potential Infs
        p_ints = (sfmax * scale) - mps['Sfs']
        #
        # Interceptation on the surface
        mps['Ints'] = (p_ints * (mps['TF'] > p_ints)) + (mps['TF'] * (mps['TF'] <= p_ints))
        ts['Ints'].values[t] = avg_2d(var2d=mps['Ints'], weight=basin) / scale  # compute basin-wide avg

        # ---- Runoff

        # Runoff
        mps['R'] = mps['TF'] - mps['Ints']
        ts['R'].values[t] = avg_2d(var2d=mps['R'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff component -  RIE
        mps['RIE'] = mps['R'] * (mps['VSA'] != 1)
        ts['RIE'].values[t] = avg_2d(var2d=mps['RIE'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff components -  RSE
        mps['RSE'] = mps['R'] * (mps['VSA'] == 1)
        ts['RSE'].values[t] = avg_2d(var2d=mps['RSE'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff components -  RC
        if ts['Prec'].values[t] > 0:  # avoid division by zero
            mps['RC'] = 100 * mps['R'] / mps['Prec']
        else:
            mps['RC'] = mps['RC'] * 0
        ts['RC'].values[t] = avg_2d(var2d=mps['RC'], weight=basin) # compute basin-wide avg

        # ---- Infiltration
        # potential infiltration allowed by surface water
        p_infs = ((ksat * scale) * (mps['Sfs'] > (ksat * scale))) + (mps['Sfs'] * (mps['Sfs'] <= (ksat * scale)))
        #
        # potential infiltration allowed by the vadose zone
        p_infu = (mps['D'] - mps['Unz']) * ((mps['D'] - mps['Unz']) > 0)  # ensure positive values only - Deficit update
        #
        # Infiltration
        mps['Inf'] = (p_infu * (p_infs > p_infu)) + (p_infs * (p_infs <= p_infu))
        ts['Inf'].values[t] = avg_2d(var2d=mps['Inf'], weight=basin) / scale  # compute basin-wide avg

        # ---- Recharge

        # Vadose zone saturation
        unz_sat = mps['Unz'] / mps['D']
        unz_sat = np.nan_to_num(unz_sat, nan=0)
        unz_sat = (unz_sat * (unz_sat <= 1)) + (1 * (unz_sat > 1))
        #
        # potential recharge
        p_qv = (ksat * scale) * unz_sat
        #
        # Recharge
        mps['Qv'] = (p_qv * (mps['Unz'] > p_qv)) + (mps['Unz'] * (mps['Unz'] <= p_qv))
        ts['Qv'].values[t] = avg_2d(var2d=mps['Qv'], weight=basin) / scale  # compute basin-wide avg

        # ---- Transpiration from vadose zone
        #
        # transpiration factor for accounting root depth in the vadoze zone
        tp_factor = ((roots * scale) / (mps['D']))
        tp_factor = np.nan_to_num(tp_factor, nan=1, posinf=1) # avoid nan values where D is 0
        tp_factor = (tp_factor * (tp_factor < 1)) + (1 * (tp_factor >= 1))
        #
        # potential tp
        p_tpun_1 = (mps['Unz'] - mps['Qv'])
        p_tpun = (p_tpun_1 * ((roots * scale) > mps['D'])) + (p_tpun_1 * tp_factor * ((roots * scale) <= mps['D']))
        #
        # Transpiration from vadose zone
        mps['Tpun'] = (mps['PET'] * (p_tpun > mps['PET'])) + (p_tpun * (p_tpun <= mps['PET']))
        ts['Tpun'].values[t] = avg_2d(var2d=mps['Tpun'], weight=basin) / scale  # compute basin-wide avg
        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Tpun'])

        # Evaporation from the surface
        # potential Evs
        p_evs = mps['Sfs'] - mps['Inf']
        # Evs
        mps['Evs'] = (mps['PET'] * (p_evs > mps['PET'])) + (p_evs * (p_evs <= mps['PET']))
        ts['Evs'].values[t] = avg_2d(var2d=mps['Evs'], weight=basin) / scale  # compute basin-wide avg

        # --- Baseflow
        ts['Qb'].values[t] = topmodel_qb(d=ts['D'].values[t], qo=qo, m=m)

        # --- ET
        mps['ET'] = mps['Evc'] + mps['Evs'] + mps['Tpgw'] + mps['Tpun']
        ts['ET'].values[t] = avg_2d(var2d=mps['ET'], weight=basin) / scale  # compute basin-wide avg
        #
        # append to trace and integration
        if trace:
            for v in tracevars:
                mps_trace[v][t] = mps[v]
        if integrate:
            for v in integratevars:
                mps_integrate[v] = mps_integrate[v] + mps[v]
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

    # fix stocks in integration:
    if integrate:
        for v in integratevars:
            if v in ['D', 'Cpy', 'Sfs', 'Unz', 'VSA', 'RC']:
                mps_integrate[v] = mps_integrate[v] / tlen
    # return
    return {'Series': ts, 'Trace': mps_trace, 'Integration': mps_integrate}
