#
# gsnao_config.py
#

"""
    get_snao
        One of pc-snipe driver of Snipe-PCView software suit

    Copyright (C) 2023  DesigNET, INC.

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
"""

#
# import from system library
#
import sys
import os
import re
import datetime

#
# import from our library
#
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

from lib import gsnao_common_defs as C

#
# functions
#

"""
| read_conf(conf):
|  read configuration file
|
| Parameters
| ----------
| conf : str
|     Path to configuration file
|
| Return value
| ------------
| {conf_code, config_list}
| conf_code:
|     0: no error
|     1: config error
|     2: system error
| config_list : dict / array
|     dictionary of configurations if no error
|     array of error messages if error detected
"""
def read_conf(conf):
    # initialize
    err_msgs = []
    config_list = {
        C.CF_PCS_CMD         : C.DEF_PCS_CMD,
        C.CF_PCS_CONF        : C.DEF_PCS_CONF,
        C.CF_AUTOCOL_KEY     : C.DEF_AUTOCOL_KEY,
        C.CF_AUTOCOL_VAL     : C.DEF_AUTOCOL_VAL,
        C.CF_SEARCH_W        : C.DEF_SITWINDOW,
        C.CF_PCS_CONCURRENCY : C.DEF_PCS_CONCURRENCY,
        C.CF_API_TIMEO       : C.DEF_API_TIMEO,
        C.CF_PCS_PREFIX      : C.DEF_PCS_PREFIX,
    }

    # read configuration file
    try:
        f = open(conf, 'r')
    except:
        err_msg = 'Cannot open configuration file: ' + conf
        err_msgs.append(err_msg)
        return [2, err_msgs]

    try:
        lines = f.readlines()
    except:
        err_msg = 'Cannot read configuration file: ' + conf
        err_msgs.append(err_msg)
        return [2, err_msgs]

    f.close

    # define erorr message template
    err_tmpl = "Bad configuration format at line {} ({})."

    # store configuration values
    line_num = 0
    for line in lines:
        line_num += 1
        # skip comment and blank line
        if line[0] != '#' and line[0] != '\n':
            l_arr = re.search(r"(^[^=]+)=(.*$)\n", line)
            if l_arr:
                # split key and value
                key = l_arr.group(1)
                value = l_arr.group(2)

                # check keys and values
                if key == C.CF_PCS_CONF:
                    # case CF_PCS_CONF
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isfile(value):
                        err_msg = f"{key}: file {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_PCS_PREFIX:
                    # case CF_PCS_PREFIX
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isdir(value):
                        err_msg = f"{key}: directory {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_PCS_CMD:
                    # case CF_PCS_CMD
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isfile(value):
                        err_msg = f"{key}: file {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_AUTOCOL_KEY:
                    # case CF_AUTOCOL_KEY
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_AUTOCOL_VAL:
                    # case CF_AUTOCOL_VAL
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_SEARCH_W:
                    # case CF_SEARCH_W
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_PCS_CONCURRENCY:
                    # case CF_PCS_CONCURRENCY
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_API_TIMEO:
                    # case CF_API_TIMEO
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                else:
                    # not a config element
                    err_msg = err_tmpl.format(line_num, key)
                    err_msgs.append(err_msg)
                    continue

                # case no error, store config dict
                config_list[key] = value

            else:
                # '=' not found
                err_msg = err_tmpl.format(line_num, "no '=' found")
                err_msgs.append(err_msg)

    # return if error detected
    if len(err_msgs) > 0:
        return [1, err_msgs]

    # check empty set
    for kn in config_list.keys():
        if config_list[kn] == False:
            err_msg = err_tmpl.format('--', 'no ' + kn + ' found')
            err_msgs.append(err_msg)

    # return if error detected
    if len(err_msgs) > 0:
        return [1, err_msgs]

    # return success
    return [0, config_list]

# END OF read_conf()

"""
| merge_config(gsconf, psconf, dmap)
|  Merge get_snao config and pc-snipe config
|
| Parameters
| ----------
| gsconf : dict
|     config data of get_snao to be merged with pc-snipe config
| psconf : dict
|     config data of pc-snipe
| dmap : dict
|     DMAP data
|
| Return value
| ------------
| (void)
"""
def merge_config(gsconf, psconf, dmap):

    # merge from psconf
    merge_ps = [
        C.CF_API_URL,
        C.CF_KEYFILE
    ]
    for x in merge_ps:
        gsconf[x] = psconf[x]

    # merge from dmap
    merge_dm = [
        C.CF_COMPUTERNAME
    ]
    for x in merge_dm:
        gsconf[x] = dmap[x]

    return

# END OF merge_conf()

