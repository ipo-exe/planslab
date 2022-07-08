'''

PLANS geoprocessing routines

Copyright (C) 2022 Iporã Brito Possantti

References:


************ GNU GENERAL PUBLIC LICENSE ************

https://www.gnu.org/licenses/gpl-3.0.en.html

Permissions:
 - Commercial use
 - Distribution
 - Modification
 - Patent use
 - Private use

Conditions:
 - Disclose source
 - License and copyright notice
 - Same license
 - State changes

Limitations:
 - Liability
 - Warranty

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''
import numpy as np


def areas(array, cellsize, values, factor=1):
    """
    derive a list of areas in array based on a list of values
    :param array: 2d array
    :param cellsize: cellsize float
    :param values: sequence of values to lookup
    :return: array of areas in cellsize squared units
    """
    areas = list()
    for i in range(len(values)):
        lcl_val = values[i]
        lcl_bool = (array == lcl_val) * 1
        lcl_pixsum = np.sum(lcl_bool)
        lcl_area = lcl_pixsum * cellsize * cellsize
        areas.append(lcl_area)
    return np.array(areas)/(factor * factor)


def xmap(map1, map2, map1ids, map2ids, map1f=100, map2f=1):
    """
    Generalized crossing map function
    :param map1: 2d array of map 1
    :param map2: 2d array of map 1
    :param map1ids: 1d array of map 1 ids
    :param map2ids: 1d array of map 2 ids
    :param map1f: int - factor of map 1 in map algebra
    :param map2f: int - factor of map 2 in map algebra
    :return: 2d array of crossed map
    """
    map1_values = map1ids * map1f
    map2_values = map2ids * map2f
    xmap = map1 * 0.0
    for i in range(len(map1_values)):
        for j in range(len(map2_values)):
            xmap_value = map1_values[i] + map2_values[j]
            lcl_xmap = (map1 == map1ids[i]) * (map2 == map2ids[j]) * xmap_value
            xmap = xmap + lcl_xmap
    return xmap


def fuzzy_transition(array, a, b, ascending=True, type='senoid'):
    """

    Fuzzify a numpy array by a transition from a to b values

    :param array: numpy array
    :param a: float initial threshold
    :param b: float terminal threshold
    :param ascending: boolean
    :param type: string type of fuzzy. options: 'senoid' and 'linear' (trapezoid)
    :return: numpy array
    """
    if ascending:
        if type == 'senoid':
            transition = (array >= b) + (array > a) * (array < b) * (-0.5 * np.cos(np.pi * (array - a)/(b - a)) + 0.5 )
        if type == 'linear':
            transition = (array >= b) + (array > a) * (array < b) * (( array / (b - a)) - (a / (b - a)))
    else:
        if type == 'senoid':
            transition = (array <= a) + (array > a) * (array < b) * (0.5 * np.cos(np.pi * (array - a)/(b - a)) + 0.5)
        if type == 'linear':
            transition = (array <= a) + (array > a) * (array < b) * ((- array / (b - a)) + (b / (b - a)))
    return transition


def htwi(twi, hand, h_max=15.0, hand_lo=0.0, h_w=1, twi_w=1):
    """

    HAND enhanced TWI map method. Short method.

    :param twi: 2d array - TWI - Topographical Wetness Index
    :param hand: 2d array - HAND - Height Above Nearest Drainage
    :param cellsize: float - cell size in meters
    :param h_max: float - HAND higher threshold
    :param hand_lo: float - HAND lower threshold
    :param h_w: float - HAND weight factor
    :param twi_w: float - TWI weight factor
    :return: 2d numpy array of HAND-enhanced TWI map
    """
    # fuzify twi
    twi_lo = np.min(twi)
    twi_hi = np.max(twi)
    twi_fuzz = fuzzy_transition(twi, a=twi_lo, b=twi_hi, ascending=True)
    #
    # fuzify hand
    hand_fuzz = fuzzy_transition(hand, a=hand_lo, b=h_max, ascending=False)
    #
    # compound twi:
    twi_comp = h_w * hand_fuzz + twi_w * twi_fuzz
    #
    # fuzify again to restore twi range
    twi_hand_map = twi_hi * fuzzy_transition(twi_comp, a=np.min(twi_comp), b=np.max(twi_comp))
    return twi_hand_map


def reclassify(array, upvalues, classes):
    """
    utility function -
    Reclassify array based on list of upper values and list of classes values

    :param array: 2d numpy array to reclassify
    :param upvalues: 1d numpy array of upper values
    :param classes: 1d array of classes values
    :return: 2d numpy array reclassified
    """
    new = array * 0.0
    for i in range(len(upvalues)):
        if i == 0:
            new = new + ((array <= upvalues[i]) * classes[i])
        else:
            new = new + ((array > upvalues[i - 1]) * (array <= upvalues[i]) * classes[i])
    return new


def rusle_l(slope, cellsize):
    """
    RUSLE L Factor (McCool et al. 1989; USDA, 1997)

    L = (x / 22.13) ^ m

    where:
    m = β / (1 + β)
    and:
    β = (sinθ ⁄ 0.0896) ⁄ (3.0⋅(sinθ)^0.8 + 0.56)

    x is the plot lenght taken as 1.4142 * cellsize  (diagonal length of cell)

    :param slope: slope in degrees of terrain 2d array
    :param cellsize: cell size in meters
    :return: RUSLE L factor 2d array
    """
    slope_rad = np.pi * 2 * slope / 360
    lcl_grad = np.sin(slope_rad)
    beta = (lcl_grad / 0.0896) / ((3 * np.power(lcl_grad, 0.8)) + 0.56)
    m = beta / (1.0 + beta)
    return np.power(np.sqrt(2) * cellsize / 22.13, m)


def rusle_s(slope):
    """
    RUSLE S Factor (McCool et al. 1987; USDA, 1997)

    S = 10.8 sinθ + 0.03     sinθ < 0.09
    S = 16.8 sinθ - 0.5      sinθ >= 0.09

    :param slope: slope in degrees of terrain 2d array
    :return: RUSLE S factor 2d array
    """
    slope_rad = np.pi * 2 * slope / 360
    lcl_grad = np.sin(slope_rad)
    lcl_s = ((10.8 * lcl_grad + 0.03 ) * (lcl_grad < 0.09)) + ((16.8 * lcl_grad - 0.5 ) * (lcl_grad >= 0.09))
    return lcl_s


def usle_l(slope, cellsize):
    """
    Wischmeier & Smith (1978) L factor

    L = (x / 22.13) ^ m

    where:

    m = 0.2 when sinθ < 0.01;
    m = 0.3 when 0.01 ≤ sinθ ≤ 0.03;
    m = 0.4 when 0.03 < sinθ < 0.05;
    m = 0.5 when sinθ ≥ 0.05

    x is the plot lenght taken as 1.4142 * cellsize  (diagonal length of cell)

    :param slope: slope in degrees of terrain 2d array
    :param cellsize: cell size in meters
    :return: Wischmeier & Smith (1978) L factor 2d array
    """
    slope_rad = np.pi * 2 * slope / 360
    lcl_grad = np.sin(slope_rad)
    m = reclassify(lcl_grad, upvalues=(0.01, 0.03, 0.05, np.max(lcl_grad)), classes=(0.2, 0.3, 0.4, 0.5))
    return np.power(np.sqrt(2) * cellsize / 22.13, m)


def usle_s(slope):
    """
    Wischmeier & Smith (1978) S factor

    S = 65.41(sinθ)^2 + 4.56sinθ + 0.065

    :param slope: slope in degrees of terrain 2d array
    :return:
    """
    slope_rad = np.pi * 2 * slope / 360
    lcl_grad = np.sin(slope_rad)
    return (65.41 * np.power(lcl_grad, 2)) + (4.56 * lcl_grad) + 0.065
