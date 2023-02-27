#
# gsnao_snipeit_api.py
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

import sys
import os
import re
import datetime
import requests
import json

myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)
from lib import gsnao_common_defs as C

URL_TOTAL = '{}/hardware?search={}&limit=0'
URL_SEARCH = '{}/hardware?search={}&limit={}&offset={}'

"""
| get_apikey(keyfile):
|  Get apikey from keyfile
|  (private function)
|
| Parameters
| ----------
| keyfile : str
|     Path to API key file
|
| Return value
| ------------
| {code, api_key}
| code:
|     0: no error
|     2: system error
| api_key : str
|     API key string if no error (code=0)
|     error message if error detected (code=2)
"""
def get_apikey(keyfile):
    try:
        f = open(keyfile, 'r')
    except:
        err_msg = 'Cannot open API key file: ' + keyfile
        return [2, err_msg]
    try:
        lines = f.readlines()
    except:
        err_msg = 'Cannot read API key file: ' + keyfile
        return [2, err_msg]
    api_key = lines[0].rstrip()
    return [0, api_key]

# END OF get_apikey()

"""
| search_by_col(conf)
|  Search assets that set auto-update flag
|
| Parameters
| ----------
| conf : dict
|     configuration dictionary
|
| Return value
| ------------
| [code, resp_data]
| code:
|     0: no error
|     1: error from API expressly
|     2: system error
| resp_data : dict / str
|     dictionary of asset data if the asset found
|     str of error message if error detected
"""
def search_by_col(conf):
    url_top = conf[C.CF_API_URL]
    search_val = conf[C.CF_AUTOCOL_VAL]
    search_key = conf[C.CF_AUTOCOL_KEY]
    window = int(conf[C.CF_SEARCH_W])
    cname = conf[C.CF_COMPUTERNAME]
    timeo = int(conf[C.CF_API_TIMEO])

    # setup API key
    api_ret = get_apikey(conf[C.CF_KEYFILE])
    if api_ret[0] != 0:
        # error state
        return api_ret
    api_key = api_ret[1]

    # setup URL and parameters
    url_total = URL_TOTAL.format(url_top, search_val)

    # setup header
    hdr = {
        'Accept'        : 'application/json',
        'Authorization' : 'Bearer ' + api_key,
        'Content-Type'  : 'application/json'
    }

    # do search
    try:
        tmp_syserr = sys.stderr
        sys.stderr = None
        resp = requests.get(url_total, headers=hdr,
                            timeout=float(timeo), verify=False)
        sys.stderr = tmp_syserr
    except:
        # error status
        err_msg = 'Cannot connect Snipe-IT API ' + url_total
        return [2, err_msg]

    if resp.status_code != 200:
        err_msg = 'Cannot get data from Snipe-IT API ' + url_total
        return [2, err_msg]

    data = json.loads(resp.text)

    # check if error occurred
    try:
        if data[C.JSON_STATUS] == C.JVAL_ERR:
            err_msg = data[C.JSON_MSG]
            return [1, err_msg]
        else:
            err_msg = 'Unknown error'
            return [2, err_msg]
    except KeyError:
        # do nothing
        err_msg = ''

    resp_data = {
        C.JSON_TOTAL         : '',
    }

    try:
        if data[C.JSON_TOTAL]:
            resp_data[C.JSON_TOTAL] = data[C.JSON_TOTAL]
    except KeyError:
        resp_data[C.JSON_TOTAL] = ''

    if resp_data[C.JSON_TOTAL] == '':
        resp_data[C.JSON_TOTAL] = 0

    total = int(resp_data[C.JSON_TOTAL])
    offset = 0
    atags = []

    while offset < total:
        url_search = URL_SEARCH.format(url_top, search_val, window, offset)
        # do search
        try:
            tmp_syserr = sys.stderr
            sys.stderr = None
            resp = requests.get(url_search, headers=hdr,
                                timeout=float(timeo), verify=False)
            sys.stderr = tmp_syserr
        except:
            # error status
            err_msg = 'Cannot connect Snipe-IT API ' + url_search
            return [2, err_msg]

        if resp.status_code != 200:
            err_msg = 'Cannot get data from Snipe-IT API ' + url_search
            return [2, err_msg]

        data = json.loads(resp.text)

        # check if error occurred
        try:
            if data[C.JSON_STATUS] == C.JVAL_ERR:
                err_msg = data[C.JSON_MSG]
                return [1, err_msg]
            else:
                err_msg = 'Unknown error'
                return [2, err_msg]
        except KeyError:
            # do nothing
            err_msg = ''

        rtop = data[C.JSON_ROWS]
        for adata in rtop:
            ainfo = {
                'atag': '',
                'cname': '',
                'id': ''
            }
            try:
                adata[C.JSON_CFIELD][search_key][C.JSON_VALUE]
            except:
                continue
            if adata[C.JSON_CFIELD][search_key][C.JSON_VALUE] == search_val:
                myatag = adata[C.JSON_ATAG]
                ainfo['atag'] = myatag
            else:
                continue

            try:
                mycname = adata[C.JSON_CFIELD][cname][C.JSON_VALUE]
                ainfo['cname'] = mycname
            except:
                pass

            try:
                myid = adata[C.JSON_ID]
                ainfo['id'] = myid
            except:
                pass

            atags.append(ainfo)

        offset += window

    return [0,atags]

# END OF search_by_col()

