#
# snipeit_api.py
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

import sys
import os
import re
import datetime
import requests
import json

myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)
from lib import common_defs as C

URL_HW_BYTAG = '{}/hardware/bytag/{}'
URL_HW = '{}/hardware'
URL_HW_BYID = '{}/hardware/{}'
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
| search_by_tag(conf, tag, DMAP):
|  Search asset by tag from Snipe-IT
|
| Parameters
| ----------
| conf : dict
|     configuration dictionary
| tag : str
|     asset tag for serarch
| DMAP : dict
|     custom filed definision map
|
| Return value
| ------------
| {code, resp_data}
| code:
|     0: no error
|     1: error from API expressly
|     2: system error
| resp_data : dict / str
|     dictionary of asset data if the asset found
|     str of error message if error detected
"""
def search_by_tag(conf, tag, DMAP):
    url_top = conf[C.CF_API_URL]
    timeo = conf[C.CF_API_TIMEO]

    # setup API key
    api_ret = get_apikey(conf[C.CF_KEYFILE])
    if api_ret[0] != 0:
        # error state
        return api_ret
    api_key = api_ret[1]

    # setup URL and parameters
    url = URL_HW_BYTAG.format(url_top, tag)

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
        resp = requests.get(url, headers=hdr,
                            timeout=float(timeo), verify=False)
        sys.stderr = tmp_syserr
    except:
        # error status
        err_msg = 'Cannot connect Snipe-IT API ' + url
        return [2, err_msg]

    if resp.status_code != 200:
        err_msg = 'Cannot get data from Snipe-IT API ' + url
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
        C.JSON_ID           : '',
        C.JSON_ATAG         : '',
        C.JSON_COMPUTERNAME : '',
        C.JSON_COMMUNITY    : conf[C.CF_DEFAULT_COMM],
        C.JSON_CFIELD       : {}
    }
    try:
        if data[C.JSON_ID]:
            resp_data[C.JSON_ID] = data[C.JSON_ID]
    except KeyError:
        resp_data[C.JSON_ID] = ''

    try:
        if data[C.JSON_ATAG]:
            resp_data[C.JSON_ATAG] = data[C.JSON_ATAG]
    except KeyError:
        resp_data[C.JSON_ATAG] = ''

    for k, v in DMAP.items():
        try:
            resp_data[C.JSON_CFIELD][k] = data[C.JSON_CFIELD][v][C.JSON_VALUE]
        except KeyError:
            resp_data[C.JSON_CFIELD][k] = ''
            continue

        if k == C.DMAP_COMPUTERNAME:
            resp_data[C.JSON_COMPUTERNAME] = data[C.JSON_CFIELD][v][C.JSON_VALUE]
        elif k == C.JSON_COMMUNITY:
            resp_data[C.JSON_COMMUNITY] = data[C.JSON_CFIELD][v][C.JSON_VALUE]

    # store raw data
    resp_data[C.JSON_RAW] = data

    return [0,resp_data]

# END OF search_by_tag()

"""
| search_by_name():
|  Search asset by computer name from Snipe-IT
|
| Parameters
| ----------
| conf : dict
|     configuration dictionary
| computer_name : str
|     computer name for serarch
| DMAP : dict
|     custom filed definision map
|
| Return value
| ------------
| {code, resp_data}
| code:
|     0: no error
|     1: error from API expressly
|     2: system error
| resp_data : dict / str
|     dictionary of asset data if the asset found
|     str of error message if error detected
"""
def search_by_name(conf, computer_name, DMAP):
    url_top = conf[C.CF_API_URL]
    timeo = conf[C.CF_API_TIMEO]
    window = int(conf[C.CF_SIT_SEARCH_WINDOW])
    search_key = DMAP[C.DMAP_COMPUTERNAME]

    # setup API key
    api_ret = get_apikey(conf[C.CF_KEYFILE])
    if api_ret[0] != 0:
        # error state
        return api_ret
    api_key = api_ret[1]

    # setup URL of total number of search result
    url_total = URL_TOTAL.format(url_top, computer_name)

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
            return [2, err_msg]
        else:
            err_msg = 'Unknown error'
            return [2, err_msg]
    except KeyError:
        # do nothing
        err_msg = ''

    resp_data = {
        C.JSON_TOTAL : 0,
    }

    try:
        if data[C.JSON_TOTAL]:
            resp_data[C.JSON_TOTAL] = int(data[C.JSON_TOTAL])
    except KeyError:
        resp_data[C.JSON_TOTAL] = 0

    total = resp_data[C.JSON_TOTAL]
    offset = 0

    resp_data = {
        C.JSON_ID           : '',
        C.JSON_ATAG         : '',
        C.JSON_COMPUTERNAME : '',
        C.JSON_COMMUNITY    : conf[C.CF_DEFAULT_COMM],
        C.JSON_CFIELD       : {}
    }
    found_flg = 0

    while offset < total:
        url_search = URL_SEARCH.format(url_top, computer_name, window, offset)

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

        # search computer_name from candidate
        for adata in rtop:
            try:
                mycn = adata[C.JSON_CFIELD][search_key][C.JSON_VALUE]
                if mycn == computer_name:
                    # found it
                    found_flg = 1
                    try:
                        if adata[C.JSON_ID]:
                            resp_data[C.JSON_ID] = adata[C.JSON_ID]
                    except KeyError:
                        resp_data[C.JSON_ID] = ''

                    try:
                        if adata[C.JSON_ATAG]:
                            resp_data[C.JSON_ATAG] = adata[C.JSON_ATAG]
                    except KeyError:
                        resp_data[C.JSON_ATAG] = ''

                    for k, v in DMAP.items():
                        try:
                            resp_data[C.JSON_CFIELD][k] = \
                                    adata[C.JSON_CFIELD][v][C.JSON_VALUE]
                        except KeyError:
                            resp_data[C.JSON_CFIELD][k] = ''
                            continue

                        if k == C.DMAP_COMPUTERNAME:
                            resp_data[C.JSON_COMPUTERNAME] = \
                                    adata[C.JSON_CFIELD][v][C.JSON_VALUE]

                        elif k == C.JSON_COMMUNITY:
                            resp_data[C.JSON_COMMUNITY] = \
                                    adata[C.JSON_CFIELD][v][C.JSON_VALUE]

                    resp_data[C.JSON_RAW] = adata
                    break

            except:
                # no custom_filed or DMAP_COMPUTERNAME; ignore this
                pass

        if found_flg == 1:
            break

        offset += window

    if found_flg == 1:
        # found asset
        return [0, resp_data]
    else:
        # no asset found
        return [1, 'Asset not found']

# END OF search_by_name()

"""
| make_snipeit_json()
|  Build dictionary data to make JSON to update Snipe-IT
|
| Parameters
| ----------
| dmap : dict
| before : dict
| after : dict
|
| Return value
| ------------
| patch_data : dict
|     to make JSON data
| False : if the asset has no custom field
"""
def make_snipeit_json(dmap, before, after):
    try:
        btop = before[C.JSON_RAW][C.JSON_CFIELD]
    except:
        # no custom field
        return False

    skip_list = [
        C.DMAP_COMPUTERNAME,
        C.DMAP_COMMUNITY
    ]
    patch_data = {}
    for elem, sit_fname in dmap.items():
        skip_f = 0
        for skip in skip_list:
            if elem == skip:
                skip_f = 1
                break
        if skip_f == 1:
            continue

        # get DB Field
        try:
            field = btop[sit_fname][C.JSON_FIELD]
        except:
            # no data found from before
            continue

        # get new data
        try:
            patch_data[field] = after[C.JSON_CFIELD][elem]
        except:
            # no data found from after
            continue

    return patch_data

# END OF make_snipeit_json()

"""
| update_snipeit()
|  Update Snipe-IT
|
| Parameters
| ----------
| conf : dict
|     pc_snipe config data
| id : str
|     ID of the asset to be updated
| put_arr : dict
|     dict data from make_snipeit_json()
|
| Return value
| ------------
| [code, message]
| code : int
|     0 : success
|     1 : software error
|     2 : system error
| message : str
|     error message
"""
def update_snipeit(conf, id, put_arr):
    url_top = conf[C.CF_API_URL]
    timeo = conf[C.CF_API_TIMEO]

    # product JSON
    put_json = json.dumps(put_arr)

    # setup API key
    api_ret = get_apikey(conf[C.CF_KEYFILE])
    if api_ret[0] != 0:
        # error state
        return api_ret
    api_key = api_ret[1]

    # setup URL and parameters
    url = URL_HW_BYID.format(url_top, id)

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
        resp = requests.patch(url, headers=hdr, data=put_json,
                              timeout=float(timeo), verify=False)
        sys.stderr = tmp_syserr
    except:
        # error status
        err_msg = 'Cannot connect Snipe-IT API ' + url
        return [2, err_msg]

    if resp.status_code != 200:
        err_msg = 'Cannot patch data from Snipe-IT API ' + url
        return [2, err_msg]

    data = json.loads(resp.text)

    # check if error occurred
    try:
        if data[C.JSON_STATUS] == C.JVAL_SUCCESS:
            pass
        elif data[C.JSON_STATUS] == C.JVAL_ERR:
            err_msg = data[C.JSON_MSG]
            return [1, err_msg]
        else:
            err_msg = 'Unknown error (' + data[C.JSON_STATUS] + ')'
            return [2, err_msg]
    except KeyError:
        # do nothing
        err_msg = ''

    return [0, '']

# END OF update_snipeit()
