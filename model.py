#import matplotlib.pyplot as plt
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
    return np.round(lcl_avg, decimals=4)


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


#
#
#
# PET model silent functions
def pet_gsc():
    """
    PET model Solar Constant
    :return: float solar constant in [W/m2]
    """
    return 1360.0  # W/m2


def pet_g(day):
    """
    PET model Solar Radiation as a function of Julian Day
    :param day: int - julian day
    :return: solar radiation (float or array) in [W/m2]
    """
    return pet_gsc() * (1 + 0.033 * np.cos(2 * np.pi * day / 365))


def pet_declination(day):
    """
    PET model - Earth declination angle
    :param day: int - julian day
    :return: Earth declination angle in [radians]
    """
    return (2 * np.pi * 23.45 / 360) * np.sin(2 * np.pi * (284 + day) / 365)


def pet_zenital_angle(day, latitude, hour):
    """
    Zenital incidence angle in radians on a horizontal plane
    :param day: int julian day
    :param latitude: latitude angle in [radians]
    :param hour: hour angle in [radians]
    :return: zenital incidence angle in radians
    """
    dcl = pet_declination(day=day)
    return np.arccos((np.cos(latitude) * np.cos(dcl) * np.cos(hour)) + (np.sin(latitude) * np.sin(dcl)))


def pet_altitude_angle(day, latitude, hour):
    """
    Altitude incidence angle in radians on a horizontal plane
    :param day: int julian day
    :param latitude: latitude angle in [radians]
    :param hour: hour angle in [radians]
    :return: zenital incidence angle in radians
    """
    zenit = pet_zenital_angle(day=day, latitude=latitude, hour=hour)
    return (np.pi / 2) - zenit


def pet_hss(declination, latitude):
    """
    PET model - Sun Set Hour angle in radians
    :param declination: declination angle in [radians]
    :param latitude: latitude angle in [radians]
    :return: Sun Set Hour angle in [radians]
    """
    return np.arccos(-np.tan(latitude) * np.tan(declination))


def pet_daily_hetrad(day, latitude):
    """
    PET model - Daily integration of the instant Horizontal Extraterrestrial Radiation Equations
    :param day: int - Julian day
    :param latitude: float - latitude in [radians]
    :return: Horizontal Daily Extraterrestrial Radiation in [MJ/(d * m2)]
    """
    g = pet_g(day)  # Get instant solar radiation in W/m2
    declination = pet_declination(day)  # Get declination in radians
    hss = pet_hss(declination=declination, latitude=latitude)  # get sun set hour angle in radians
    het = (24 * 3600 / np.pi) * g * ((np.cos(latitude) * np.cos(declination) * np.sin(hss))
                                     + (hss * np.sin(latitude) * np.sin(declination)))  # J/(d * m2)
    return het / (1000000)  # MJ/(d * m2)


def pet_latent_heat_flux():
    """
    PET model - Latent Heat Flux of water in MJ/kg
    :return: float -  Latent Heat Flux of water in MJ/kg
    """
    return 2.45  # MJ/kg


def pet_water_spmass():
    """
    PET model - Water specific mass in kg/m3
    :return: float - Water specific mass in kg/m3
    """
    return 1000.0  # kg/m3


def pet_oudin(temperature, day, latitude, k1=100, k2=5):
    """
    PET Oudin Model - Radiation and Temperature based PET model of  Ref: Oudin et al (2005b)
    :param temperature: float or array of daily average temperature in [C]
    :param day: int or array of Julian day
    :param latitude: latitude angle in [radians]
    :param k1: Scalar parameter in [C * m/mm]
    :param k2: Minimum air temperature [C]
    :return: Potential Evapotranspiration in [mm/d]
    """
    het = pet_daily_hetrad(day, latitude)
    pet = (1000 * het / (pet_latent_heat_flux() * pet_water_spmass() * k1)) * (temperature + k2) * ((temperature + k2) > 0) * 1.0
    return pet


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


def simulation(series_df, basin, htwi, qt0, cpmax, sfmax, roots, qo, m, lamb, ksat, rho, c, n, k,
               scale=1000,
               lat=-30,
               trace=False,
               tracevars='D-Cp',
               integrate=False,
               integratevars='D-Qv'):
    """

    g2g simulation model

    Simulated variables:

    'D',    # saturated water stock deficit
    'Vz',   # vadose (unsaturated) zone water stock
    'Sf',   # surface water stock
    'Cp',   # canopy water stock
    'VSA',  # variable source area
    'P',    # precipitation
    'PET',  # potential evapotranspiration
    'Inc',  # interceptation in canopy
    'Ins',  # interceptation in surface
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

    :param series_df: pandas dataframe of timeseries
    :param basin: 2d numpy array of basin area
    :param htwi: numpy array of HTWI map (positive values only)
    :param qt0: float of initial condition of baseflow in mm/d
    :param cpmax: float or 2d numpy array of canopy water stock capacity in mm
    :param sfmax: float or 2d numpy array of surface water stock capacity in mm
    :param roots: float or 2d numpy array of effective root zone depth in mm
    :param qo: float of full saturation baseflow in mm/d
    :param m: float of the scaling parameter in mm
    :param lamb: float the TWI threshold
    :param ksat: float or 2d numpy array of daily hydraulic conductivity in mm/d
    :param n: float of number of linear reservoirs (n >= 1)
    :param k: float of detention time of linear reservoirs (k >= 1)
    :param scale: int value to scale maps to integer format (recommended scale >= 1000)
    :param trace: boolean to trace back daily maps of variables
    :param tracevars: string of variables to trace back. Variables must be concatenated by `-`.
    Example: D-Cp-VSA
    :param integrate: boolean to integrate back maps of variables
    :param integratevars: string of variables to integrate back. Variables must be concatenated by `-`.
    Example: D-Cp-VSA
    :return: python dict containing:

    {'Series': simulated time series pandas dataframe,
     'Trace': dict of 3d numpy arrays of traced variables,
     'Integration': dict of 2d numpy arrays of integrated variables}

    """
    from sys import getsizeof

    # simulation variables
    simvars = [
               'D',   # saturated water stock deficit
               'Vz',  # unsaturated zone water stock
               'Sf',  # surface water stock
               'Cp',  # canopy water stock
               'VSA', # variable source area
               'P',   # precipitation [input]
               'PET', # potential evapotranspiration
               'IRI', # irrigation dripping or inundation
               'IRA', # irrigation by aspersion
               'Inc', # interceptation in canopy
               'Ins', # interceptation in surface
               'TF',  # throughfall
               'R',   # runoff
               'RIE', # infiltration excess runoff (Hortonian)
               'RSE', # saturation excess runoff (Dunnean)
               'RC',  # runofff coeficient (%)
               'Inf', # infiltration
               'Qv',  # recharge
               'Evc', # evaporation from the canopy
               'Evs', # evaporation from the surface
               'Ev',  # evaporation Evc + Evs
               'Tpv', # transpiration from the vadose zone
               'Tps', # transpiration from the saturated zone
               'Tp',  # transpiration Tpu + Tps
               'ET',  # evapotranspiration (Ev + Tp)
               'Qb',  # baseflow
               'Qs',  # stormflow
               'Q'    # streamflow
               ]
    #
    # copy input series
    df_ts = series_df.copy()

    # compute PET by Oudin model
    days = df_ts['Date'].dt.dayofyear
    ts_days = days.values
    lat = lat * np.pi / 180  # convet lat from degrees to radians
    df_ts['PET'] = pet_oudin(temperature=df_ts['T'].values, day=ts_days, latitude=lat, k1=c)  # Oudin model

    # append global variables fields to simulation series
    for v in simvars:
        if v in ['P', 'T', 'IRI', 'IRA', 'PET']:
            pass
        else:
            df_ts[v] = 0.0 # set as zero
    #
    #
    # get map shape using basin mask
    shape = np.shape(basin)
    rows = shape[0]
    cols = shape[1]
    tlen = len(df_ts)
    #
    # deploy simulation maps
    mps = dict()
    mem_size = 0
    for v in simvars:
        if v == 'Qb' or v == 'Qs' or v == 'Q':
            pass
        else:
            # store as uint16 (unsigned 16-bit integer)
            mps[v] = np.zeros(shape=shape, dtype='uint16')
            mem_size = getsizeof(mps[v]) + mem_size
    print('Sim size : {} MB'.format(mem_size / 1000000))

    # deploy trace and integration maps
    mps_trace = dict()
    if trace:
        tracevars = tracevars.split('-')
        mem_size = 0
        for v in tracevars:
            # store as uint16 (unsigned 16-bit integer)
            mps_trace[v] = np.zeros(shape=(tlen, rows, cols), dtype='uint16')
            mem_size = getsizeof(mps_trace[v]) + mem_size
        print('Trace size : {} MB'.format(mem_size / 1000000))
    mps_integrate = dict()
    if integrate:
        integratevars = integratevars.split('-')
        for v in integratevars:
            # store as uint16 (unsigned 16-bit integer)
            mps_integrate[v] = np.zeros(shape=(rows, cols), dtype='uint16')
    #
    # get initial local deficits
    df_ts['D'].values[0] = topmodel_d0(qt0=qt0, qo=qo, m=m)

    # todo adapt to twi vector
    mps['D'] = scale * topmodel_di(d=df_ts['D'].values[0], twi=htwi, m=m, lamb=lamb)
    mps['VSA'] = topmodel_vsai(di=mps['D'])

    # get root zone depth:
    rzd = roots * rho

    # ESMA loop
    for t in range(tlen):
        # INPUT define P and PET
        mps['P'] = df_ts['P'].values[t] * scale * np.ones(shape=shape, dtype='uint32')
        mps['PET'] = df_ts['PET'].values[t] * scale * np.ones(shape=shape, dtype='uint32')

        # STOCKS WATER BALANCE (backward looking)
        if t > 0:
            # Canopy water balance
            mps['Cp'] = mps['Cp'] + mps['Inc'] - mps['Evc']
            df_ts['Cp'].values[t] = avg_2d(var2d=mps['Cp'], weight=basin) / scale  # compute basin-wide avg
            #
            # Vadose zone water balance
            mps['Vz'] = mps['Vz'] + mps['Inf'] - mps['Qv'] - mps['Tpv']
            df_ts['Vz'].values[t] = avg_2d(var2d=mps['Vz'], weight=basin) / scale  # compute basin-wide avg
            #
            # Surface water balance
            mps['Sf'] = mps['Sf'] + mps['Ins'] - mps['Inf'] - mps['Evs']
            df_ts['Sf'].values[t] = avg_2d(var2d=mps['Sf'], weight=basin) / scale  # compute basin-wide avg
            #
            # Deficit water balance
            df_ts['D'].values[t] = df_ts['D'].values[t - 1] + df_ts['Qb'].values[t - 1] + df_ts['Tps'].values[t - 1] - \
                                df_ts['Qv'].values[t - 1]
            # update Deficit
            # todo adapt to twi vector
            mps['D'] = scale * topmodel_di(d=df_ts['D'].values[t], twi=htwi, m=m, lamb=lamb)
            # update VSA
            mps['VSA'] = topmodel_vsai(di=mps['D'])
            df_ts['VSA'].values[t] = 100 * avg_2d(var2d=mps['VSA'], weight=basin) / scale  # compute basin-wide avg

        # FLOWS COMPUTATION

        # --- Canopy flows

        # potential interceptation on canopy
        p_intc = (scale * cpmax) - mps['Cp']
        #
        # Interceptation in the canopy
        mps['Inc'] = (p_intc * (mps['P'] > p_intc)) + (mps['P'] * (mps['P'] <= p_intc))
        df_ts['Inc'].values[t] = avg_2d(var2d=mps['Inc'], weight=basin) / scale  # compute basin-wide avg
        #
        # Evaporation in the canopy
        mps['Evc'] = (mps['PET'] * (mps['Cp'] > mps['PET'])) + (mps['Cp'] * (mps['Cp'] <= mps['PET']))
        df_ts['Evc'].values[t] = avg_2d(var2d=mps['Evc'], weight=basin) / scale  # compute basin-wide avg
        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Evc'])
        #
        # Throughfall
        mps['TF'] = mps['P'] - mps['Inc']
        df_ts['TF'].values[t] = avg_2d(var2d=mps['TF'], weight=basin) / scale  # compute basin-wide avg


        # --- Transpiration from groundwater

        # potential tp from gw:
        p_tpgw = (rzd * scale) - mps['D']
        p_tpgw = p_tpgw * (p_tpgw >= 0) # remove negative values
        #
        # Transpiration from groundwater
        mps['Tps'] = (mps['PET'] * (p_tpgw > mps['PET'])) + (p_tpgw * (p_tpgw <= mps['PET']))
        df_ts['Tps'].values[t] = avg_2d(var2d=mps['Tps'], weight=basin) / scale  # compute basin-wide avg

        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Tps'])

        # ---- Interceptation on the surface

        # potential Infs
        p_ints = (sfmax * scale) - mps['Sf']
        #
        # Interceptation on the surface
        mps['Ins'] = (p_ints * (mps['TF'] > p_ints)) + (mps['TF'] * (mps['TF'] <= p_ints))
        df_ts['Ins'].values[t] = avg_2d(var2d=mps['Ins'], weight=basin) / scale  # compute basin-wide avg

        # ---- Runoff

        # Runoff
        mps['R'] = mps['TF'] - mps['Ins']
        df_ts['R'].values[t] = avg_2d(var2d=mps['R'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff component -  RIE
        mps['RIE'] = mps['R'] * (mps['VSA'] != 1)
        df_ts['RIE'].values[t] = avg_2d(var2d=mps['RIE'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff components -  RSE
        mps['RSE'] = mps['R'] * (mps['VSA'] == 1)
        df_ts['RSE'].values[t] = avg_2d(var2d=mps['RSE'], weight=basin) / scale  # compute basin-wide avg
        #
        # Runoff components -  RC
        if df_ts['P'].values[t] > 0:  # avoid division by zero
            mps['RC'] = 100 * mps['R'] / mps['P']
        else:
            mps['RC'] = mps['RC'] * 0
        df_ts['RC'].values[t] = avg_2d(var2d=mps['RC'], weight=basin) # compute basin-wide avg

        # ---- Infiltration
        # potential infiltration allowed by surface water
        p_infs = ((ksat * scale) * (mps['Sf'] > (ksat * scale))) + (mps['Sf'] * (mps['Sf'] <= (ksat * scale)))
        #
        # potential infiltration allowed by the vadose zone
        p_infu = (mps['D'] - mps['Vz']) * ((mps['D'] - mps['Vz']) > 0)  # ensure positive values only - Deficit update
        #
        # Infiltration
        mps['Inf'] = (p_infu * (p_infs > p_infu)) + (p_infs * (p_infs <= p_infu))
        df_ts['Inf'].values[t] = avg_2d(var2d=mps['Inf'], weight=basin) / scale  # compute basin-wide avg

        # ---- Recharge

        # Vadose zone saturation
        unz_sat = mps['Vz'] / (mps['D'] + (scale / 1000))
        unz_sat = np.nan_to_num(unz_sat, nan=0)
        unz_sat = (unz_sat * (unz_sat <= 1)) + (1 * (unz_sat > 1))
        #
        # potential recharge
        p_qv = (ksat * scale) * unz_sat
        #
        # Recharge
        mps['Qv'] = (p_qv * (mps['Vz'] > p_qv)) + (mps['Vz'] * (mps['Vz'] <= p_qv))
        df_ts['Qv'].values[t] = avg_2d(var2d=mps['Qv'], weight=basin) / scale  # compute basin-wide avg

        # ---- Transpiration from vadose zone
        #
        # transpiration factor for accounting root depth in the vadoze zone
        tp_factor = ((rzd * scale) / (mps['D'] + (scale / 1000)))
        tp_factor = np.nan_to_num(tp_factor, nan=1, posinf=1) # avoid nan values where D is 0
        tp_factor = (tp_factor * (tp_factor < 1)) + (1 * (tp_factor >= 1))
        #
        # potential tp
        p_tpun_1 = (mps['Vz'] - mps['Qv'])
        p_tpun = (p_tpun_1 * ((rzd * scale) > mps['D'])) + (p_tpun_1 * tp_factor * ((rzd * scale) <= mps['D']))
        #
        # Transpiration from vadose zone
        mps['Tpv'] = (mps['PET'] * (p_tpun > mps['PET'])) + (p_tpun * (p_tpun <= mps['PET']))
        df_ts['Tpv'].values[t] = avg_2d(var2d=mps['Tpv'], weight=basin) / scale  # compute basin-wide avg
        #
        # update PET
        mps['PET'] = mps['PET'] - np.mean(mps['Tpv'])

        # Evaporation from the surface
        # potential Evs
        p_evs = mps['Sf'] - mps['Inf']
        # Evs
        mps['Evs'] = (mps['PET'] * (p_evs > mps['PET'])) + (p_evs * (p_evs <= mps['PET']))
        df_ts['Evs'].values[t] = avg_2d(var2d=mps['Evs'], weight=basin) / scale  # compute basin-wide avg

        # --- Baseflow
        df_ts['Qb'].values[t] = topmodel_qb(d=df_ts['D'].values[t], qo=qo, m=m)

        # --- ET
        mps['Tp'] = mps['Tps'] + mps['Tpv']  # Tp
        mps['Ev'] = mps['Evc'] + mps['Evs']  # Ev
        mps['ET'] = mps['Evc'] + mps['Evs'] + mps['Tps'] + mps['Tpv']
        df_ts['ET'].values[t] = avg_2d(var2d=mps['ET'], weight=basin) / scale  # compute basin-wide avg
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
    df_ts['Qs'] = nash_cascade(df_ts['R'].values, k=k, n=n)
    #
    #
    # Compute full discharge Q = Qb + Qs
    df_ts['Q'] = df_ts['Qb'] + df_ts['Qs']

    # compute global Tp and Ev
    df_ts['Tp'] = df_ts['Tpv'] + df_ts['Tps']
    df_ts['Ev'] = df_ts['Evc'] + df_ts['Evs']

    # average stocks in integration:
    if integrate:
        for v in integratevars:
            if v in ['D', 'Cp', 'Sf', 'Vz', 'VSA', 'RC']:
                mps_integrate[v] = mps_integrate[v] / tlen
    # return
    return {'Series': df_ts, 'Trace': mps_trace, 'Integration': mps_integrate}
