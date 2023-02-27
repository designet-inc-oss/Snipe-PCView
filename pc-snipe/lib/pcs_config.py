#
# pcs_config.py
#

"""
    pc-snipe
        A core program of Snipe-PCView software suit

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

from lib import common_defs as C

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
        C.CF_API_URL           : C.DEF_APIURL,
        C.CF_API_TIMEO         : C.DEF_APITIMEO,
        C.CF_KEYFILE           : C.DEF_API_KEY_FILE,
        C.CF_DNSADDR           : C.DEF_DNSADDR,
        C.CF_DEFAULT_COMM      : C.DEF_DEFAULTCOMM,
        C.CF_DNSDOMAIN         : C.DEF_DNSDOMAIN,
        C.CF_SIT_SEARCH_WINDOW : C.DEF_SITWINDOW,
        C.CF_TMPLPATH          : C.DEF_TMPL_DIR,
        C.CF_MAPPINGFILE       : C.DEF_MAPPING_FILE,
        C.CF_DNS_TIMEO         : C.DEF_DNS_TIMEO,
        C.CF_DISKSIZE_UNIT     : C.DEF_DISKSIZE_U,
        C.CF_MEMSIZE_UNIT      : C.DEF_MEMSIZE_U,
        C.CF_DISKSIZE_DIGITS   : C.DEF_DISKSIZE_D,
        C.CF_MEMSIZE_DIGITS    : C.DEF_MEMSIZE_D,
        C.CF_CPUTHDS_DIGITS    : C.DEF_CPUTHDS_D,
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
                if key == C.CF_API_URL:
                    # case CF_API_URL
                    url_ptn = 'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+'
                    if not re.match(url_ptn, value):
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_KEYFILE:
                    # case CF_KEYFILE
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isfile(value):
                        err_msg = f"{key}: file {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_DNSADDR:
                    # case CF_DNSADDR
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_DEFAULT_COMM:
                    # case CF_DEFAULT_COMM
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_DNSDOMAIN:
                    # case CF_DNSDOMAIN
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_SIT_SEARCH_WINDOW:
                    # case CF_SIT_SEARCH_WINDOW
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

                elif key == C.CF_DNS_TIMEO:
                    # case CF_DNS_TIMEO
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_TMPLPATH:
                    # case CF_TMPLPATH
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isdir(value):
                        err_msg = f"{key}: directory {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_MAPPINGFILE:
                    # case CF_MAPPINGFILE
                    if value == '':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue
                    elif not os.path.isfile(value):
                        err_msg = f"{key}: file {value} does not exist at line {line_num}"
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_DISKSIZE_UNIT:
                    # case CF_DISKSIZE_UNIT
                    if value != 'K' and value != 'M' and value != 'G':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_MEMSIZE_UNIT:
                    # case CF_MEMSIZE_UNIT
                    if value != 'K' and value != 'M' and value != 'G':
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_DISKSIZE_DIGITS:
                    # case CF_DISKSIZE_DIGITS
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_MEMSIZE_DIGITS:
                    # case CF_MEMSIZE_DIGITS
                    if value.isdecimal() is False or int(value) < 1:
                        err_msg = err_tmpl.format(line_num, key)
                        err_msgs.append(err_msg)
                        continue

                elif key == C.CF_CPUTHDS_DIGITS:
                    # case CF_CPUTHDS_DIGITS
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
| read_dmap(dmapfile):
|  read mapping file
|
| Parameters
| ----------
| dmapfile : str
|     Path to mapping file
|
| Return value
| ------------
| {dmap_code, dmap_list}
| dmap_code:
|     0: no error
|     1: config error
|     2: system error
| dmap_list : dict / array
|     dictionary of DMAP if no error
|     array of error messages if error detected
"""
def read_dmap(dmapfile):
    # initialize
    err_msgs = []
    dmap_list = {
        C.DMAP_COMPUTERNAME : False,
        C.DMAP_IPADDR       : '',
        C.DMAP_COMMUNITY    : '',
        C.DMAP_CPUTHREADS   : '',
        C.DMAP_MEMORYSIZE   : '',
        C.DMAP_DISKSIZE     : '',
        C.DMAP_DISKINFO     : '',
        C.DMAP_APPLI        : '',
        C.DMAP_COMPUTERINFO : '',
        C.DMAP_DEVICEINFO   : '',
        C.DMAP_NETWORKINFO  : ''
    }

    # read mapping file
    try:
        f = open(dmapfile, 'r')
    except:
        err_msg = 'Cannot open mapping file: ' + dmapfile
        err_msgs.append(err_msg)
        return [2, err_msgs]

    try:
        lines = f.readlines()
    except:
        err_msg = 'Cannot read mapping file: ' + dmapfile
        err_msgs.append(err_msg)
        return [2, err_msgs]

    f.close

    # define erorr message template
    err_tmpl = "Bad mapping file format at line {} ({})."

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
                if key not in dmap_list.keys():
                    err_msg = err_tmpl.format(line_num, key)
                    err_msgs.append(err_msg)
                    continue

                elif value == '':
                    err_msg = err_tmpl.format(line_num, key)
                    err_msgs.append(err_msg)
                    continue

                # case no error, store dmap dict
                dmap_list[key] = value

            else:
                # '=' not found
                err_msg = err_tmpl.format(line_num, "no '=' found")
                err_msgs.append(err_msg)

    # return if error detected
    if len(err_msgs) > 0:
        return [1, err_msgs]

    # check empty set
    for kn in dmap_list.keys():
        if dmap_list[kn] == False:
            err_msg = err_tmpl.format('--', 'no ' + kn + ' found')
            err_msgs.append(err_msg)

    # return if error detected
    if len(err_msgs) > 0:
        return [1, err_msgs]

    # return success
    return [0, dmap_list]

# END OF read_conf()

