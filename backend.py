'''

PLANS backend routines

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
import os


def timestamp_log():
    import datetime
    s_aux = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-4]
    return s_aux


def timestamp(s_sep='-'):
    """
    Generates a string timestamp
    :param s_sep: string separator
    :return: string timestamp
    """
    import datetime
    def_now = datetime.datetime.now()
    yr = def_now.strftime('%Y')
    mth = def_now.strftime('%m')
    dy = def_now.strftime('%d')
    hr = def_now.strftime('%H')
    mn = def_now.strftime('%M')
    sg = def_now.strftime('%S')
    fm = def_now.strftime('%f')[:-4]
    def_lst = [yr, mth, dy, hr, mn, sg, fm]
    def_s = str(s_sep.join(def_lst))
    return def_s


def get_seed():
    """
    Get seed from computer clock
    :return: int
    """
    import datetime
    def_now = datetime.datetime.now()
    hr = def_now.strftime('%H')
    mn = def_now.strftime('%M')
    sg = def_now.strftime('%S')
    return int(sg + mn + hr)


def create_rundir(label='', wkplc='C:'):
    dir_nm = wkplc + '/' + label + '_' + timestamp()
    os.mkdir(dir_nm)
    return dir_nm


def status(msg='Status message', process=False):
    if process:
        print('\t>>> {:60}...'.format(msg))
    else:
        print('\n\t>>> {:60}\n'.format(msg))