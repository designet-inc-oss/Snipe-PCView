#
# pcs_tmpl.py
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
from lib import mibmap as M

#
# functions
#

"""
| read_tmpl(tmplfile, onemode = False):
|  read output template file
|
| Parameters
| ----------
| tmplfile : str
|     Path to template file
|
| Return value
| ------------
| {code, tmpl}
| code:
|     0: no error
|     1: config error
|     2: system error
| tmpl : str
|     template if no error
|     error messages if error detected
"""
def read_tmpl(tmplfile, onemode = False):
    # read template file
    try:
        f = open(tmplfile, 'r')
    except:
        err_msg = 'Cannot open template file: ' + tmplfile
        return [2, err_msg]

    if onemode == True:
        try:
            tmpl = f.readline()
            tmpl = tmpl.replace('\n', '')
        except:
            err_msg = 'Cannot read template file: ' + tmplfile
            return [2, err_msg]
    else:
        try:
            tmpl = f.read()
        except:
            err_msg = 'Cannot read template file: ' + tmplfile
            return [2, err_msg]

    f.close

    return [0, tmpl]

# END OF read_tmpl()

"""
| read_wlbl(listfile):
|  read blacklist/whitelist file
|
| Parameters
| ----------
| listfile : str
|     Path to blacklist/whitelist file
|
| Return value
| ------------
| {code, list}
| code:
|     0: no error
|     1: config error
|     2: system error
| list : array / str
|     array : blacklist/whitelist if no error
|     str   : error messages if error detected
"""
def read_wlbl(listfile):
    # read list file
    try:
        f = open(listfile, 'r')
    except:
        err_msg = 'Cannot open list file: ' + listfile
        return [2, err_msg]

    try:
        t_lines = f.readlines()
    except:
        err_msg = 'Cannot read list file: ' + listfile
        return [2, err_msg]

    f.close

    lines = []
    for line in t_lines:
        lines.append(line.replace('\n', ''))

    return [0, lines]

# END OF read_wlbl()

"""
| replace_tag(tmpl, tags)
|
| Parameters
| ----------
| tmpl : str
|     template to replace
| tags : dict array
|     format is as below
|      tags['one'] : regular tags
|       tags['one']['tagname'] : 'tagname' will be replaced to the value
|      tags['loop'] : loop tags
|       tags['loop']['start'] : start of loop tag
|       tags['loop']['end']   : end of loop tag
|       tags['loop']['rep']   : replace tags for each iteration
|        tags['loop']['rep'][N]['tagname'] :
|                  'tagname' will be replaced to the value of the iteration N
|     Note: All tagnames must be set in every iteration
|
| Return value
| ------------
| replaced : str
|     replaced string
"""
def replace_tag(tmpl, tags):
    replaced = tmpl

    # step.1 replace regular tags
    if tags['one'] != None:
        for t, r in tags['one'].items():
            replaced = replaced.replace(t, str(r))

    # step.2 process loop tag
    if tags['loop'] != None:
        # step.2.1 find loop tag
        s = tags['loop']['start']
        e = tags['loop']['end']
        ## ptn includes LF char
        ss = s.replace('[', '\[').replace(']', '\]')
        ee = e.replace('[', '\[').replace(']', '\]')
        ptn = ss + '(.*?)' + ee
        ## m is array of loop tmplate string
        m = re.findall(ptn, replaced, flags=re.DOTALL)

        # step.2.2 replace loop section to replaced string
        for lt in m:
            l_tmpl = lt
            rptn = s + l_tmpl + e
            rrr = ''
            for itr in tags['loop']['rep']:
                rr = l_tmpl
                for t, r in itr.items():
                    rr = rr.replace(t, r)
                rrr = rrr + rr
            replaced = replaced.replace(rptn, rrr)

    return replaced

# END OF replace_tag()

"""
| get_tmpl_idx(wl, bl, snmp_data, syms):
|
| Parameters
| ----------
| wl : str
|     white list filename
| bl : str
|     black list filename
| snmp_data : dict
|     SNMP data
| syms : array
|     OID names to evaluate
|
| Return value
| ------------
| {code, idx}
| code:
|     0: no error
|     1: config error
|     2: system error
| idx :
|     array : index list
|     str : error message if error detected
"""
def get_tmpl_idx(wl, bl, snmp_data, syms, msyms={}):
    # detect and read files
    if os.path.isfile(wl):
        wlmode = True
        code, white_list = read_wlbl(wl)
        if code != 0:
            return [code, white_list]
    else:
        wlmode = False
    if os.path.isfile(bl):
        blmode = True
        code, black_list = read_wlbl(bl)
        if code != 0:
            return [code, black_list]
    else:
        blmode = False

    # each mode
    t_idx = {}
    if wlmode == False and blmode == False:
        # get all mode
        syms.extend(msyms)
        for sym in syms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                t_idx[k] = int(k)
    elif wlmode == True and blmode == False:
        # white list only mode
        for sym in syms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                try:
                    if t_idx[k]:
                        # this index is already labeled
                        continue
                except:
                    pass
                for ptn in white_list:
                    if ptn in v:
                        # label this index white
                        t_idx[k] = int(k)
                        break
                    else:
                        continue
        for sym in msyms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                try:
                    if t_idx[k]:
                        # this index is already labeled
                        continue
                except:
                    pass
                try:
                    M.m[v]
                except:
                    # no match datamap
                    continue
                for ptn in white_list:
                    if ptn in M.m[v]:
                        # label this index white
                        t_idx[k] = int(k)
                        break
                    else:
                        continue
    elif wlmode == False and blmode == True:
        # black list only mode
        for sym in syms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                # omit if this key is already labeled black
                try:
                    if t_idx[k] == -1:
                        continue
                except:
                    pass
                for ptn in black_list:
                    if ptn in v:
                        # label this index black
                        t_idx[k] = -1
                        break
                    else:
                        continue
                try:
                    if t_idx[k] != -1:
                        # this index is not labeled black
                        t_idx[k] = int(k)
                except:
                    # this index is not labeled black
                    t_idx[k] = int(k)
        for sym in msyms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                # omit if this key is already labeled black
                try:
                    if t_idx[k] == -1:
                        continue
                except:
                    pass
                try:
                    M.m[v]
                except:
                    # no match datamap
                    continue
                for ptn in black_list:
                    if ptn in M.m[v]:
                        # label this index black
                        t_idx[k] = -1
                        break
                    else:
                        continue
                try:
                    if t_idx[k] != -1:
                        # this index is not labeled black
                        t_idx[k] = int(k)
                except:
                    # this index is not labeled black
                    t_idx[k] = int(k)
    elif wlmode == True and blmode == True:
        # both mode
        for sym in syms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                # omit if this key is already labeled black
                try:
                    if t_idx[k] == -1:
                        continue
                except:
                    pass

                # first, evaluate if this is in white list
                for wptn in white_list:
                    if wptn in v:
                        try:
                            if t_idx[k] == -1:
                                break
                        except:
                            t_idx[k] = int(k)
                    else:
                        continue

                # then evaluate if this is in black list
                for bptn in black_list:
                    if bptn in v:
                        t_idx[k] = -1
                        break
                    else:
                        continue
        for sym in msyms:
            try:
                snmp_data[sym]
            except:
                continue
            for k, v in snmp_data[sym].items():
                # omit if this key is already labeled black
                try:
                    if t_idx[k] == -1:
                        continue
                except:
                    pass
                try:
                    M.m[v]
                except:
                    # no match datamap
                    continue

                # first, evaluate if this is in white list
                for wptn in white_list:
                    if wptn in M.m[v]:
                        try:
                            if t_idx[k] == -1:
                                break
                        except:
                            t_idx[k] = int(k)
                    else:
                        continue

                # then evaluate if this is in black list
                for bptn in black_list:
                    if bptn in M.m[v]:
                        t_idx[k] = -1
                        break
                    else:
                        continue

    # relocate t_idx
    n_idx = {}
    for k, v in t_idx.items():
        if v != -1:
            n_idx[k] = v
    idx = sorted(n_idx.items(), key=lambda x:x[1])
    idx = dict((x, y) for x, y in idx)
    return [0, idx]

# END OF get_tmpl_idx()

