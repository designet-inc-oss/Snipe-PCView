#
# pcs_snmp.py
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

from pysnmp.hlapi import *
import sys
import os
import re
import datetime
import time
import binascii
import chardet

#
# import from our library
#
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

from lib import common_defs as C
from lib import pcs_tmpl as T
from lib import mibmap as M

#
# functions
#

"""
| mb_conv(gen)
|  Convert from hexadecimal string to binary, then decode to UTF-8 string
|
| Parameters
| ----------
| gen : str
|     hexadecimal string to be decoded
|
| Return value
| ------------
| ret_str : str
|     decoded string in UTF-8
"""
def mb_conv(gen):
    # sanity check
    if len(gen) > 2 and gen[0:2] == '0x':
        # case this is hexadecimal string
        # go next process
        pass
    else:
        # case ascii string
        return gen

    # try to decode
    gens = gen[2:]
    try:
        # decode to binary
        bin_str = binascii.unhexlify(gens)
        # detect charactor encoding
        cd = chardet.detect(bin_str)
        myenc = cd['encoding']
        # convert from original encoding to UTF-8
        ret_str = bin_str.decode(myenc)
    except:
        # failed to decode ; return original string
        ret_str = gen

    return ret_str

# END OF mb_conv()
 
"""
| snmp_walk(ret_arr, modName, symName, router_ip, community)
|  Get asset data from appropriate WindowsPC by SNMP
|  This can get only one modName::symName data set
|
| Parameters
| ----------
| ret_arr : dict
|     To store data that is got by SNMP
|     This dict will be accumulated
| modName : str
| symName : str
|     OID to get by SNMP
| router_ip : str
|     IP address of WindowsPC
| community : str
|     Community name of WindowsPC
|
| Return value
| ------------
| ret_arr : dict
|     Success
| err_msg : str
|     error message
"""
def snmp_walk(ret_arr, modName, symName, router_ip, community):
    g = nextCmd(SnmpEngine(),
           CommunityData(community),
           UdpTransportTarget((router_ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(modName, symName)),
           lexicographicMode=False)
 
    while True:
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(g)
            if errorIndication:
                err_msg = str(errorIndication)
                return [1, err_msg]
            elif errorStatus:
                err_msg = '%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
                return [1, err_msg]
            else:
                for varBind in varBinds:
                    k = varBind[0].prettyPrint()
                    vp = varBind[1].prettyPrint()
                    try:
                        M.m[vp]
                        vp = M.m[vp]
                    except:
                        vp = vp
                    v = varBind[1]
                    k1, k2 = k.split('.')
                    try:
                        ret_arr[str(k1)][k2] = mb_conv(vp)
                    except:
                        ret_arr[str(k1)] = {} 
                        ret_arr[str(k1)][str(k2)] = mb_conv(vp)
        except StopIteration:
            # all done
            break
        except:
            # unknown error
            err_msg = 'Unknown error'
            return [2, err_msg]

    return [0, ret_arr]

# END OF snmp_walk()

"""
| get_snmp(conf, dmap, ip, comm)
|  Get asset data from WindowsPC by SNMP
|
| Parameters
| ----------
| conf : dict
|     pc_snipe config data
| dmap : dict
|     Snipe-IT data map
| ip : str
|     IP address of WindowsPC
| comm : str
|     Community
|
| Return value
| ------------
| snmp_data : dict
|     Success
| err_msg : str
|     error message
"""
def get_snmp(conf, dmap, ip, comm):
    # intialize return array
    ret_arr = {}

    # mandatory data get
    # ComputerName
    mod = C.SMOD_SNMPV2
    sym = C.SSYM_SYSNAME
    code, arr = snmp_walk(ret_arr, mod, sym, ip, comm)
    if code == 1:
        return [1, arr]
    if code == 2:
        return [2, arr]

    # ComputerInfo
    mod = C.SMOD_SNMPV2
    sym = C.SSYM_SYSDESCR
    code, arr = snmp_walk(ret_arr, mod, sym, ip, comm)
    if code == 1:
        return [1, arr]
    if code == 2:
        return [2, arr]

    # do snmpwalk for each field type
    # assets data accumulates to ret_arr
    sym_arr = {
        C.SMOD_SNMPV2 : {},
        C.SMOD_HOSTR  : {},
        C.SMOD_IFMIB  : {}
    }
    for elem in dmap:
        if dmap[elem] == '':
            # not set
            continue

        if elem == C.DMAP_COMPUTERNAME:
            # already got
            continue
        elif elem == C.DMAP_IPADDR:
            continue
        elif elem == C.DMAP_COMMUNITY:
            mod = C.SMOD_SNMPV2
            sym_arr[mod][C.SSYM_SYSNAME] = '1'
        elif elem == C.DMAP_CPUTHREADS:
            mod = C.SMOD_HOSTR
            sym_arr[mod][C.SSYM_PROC_FRWID] = '1'
        elif elem == C.DMAP_MEMORYSIZE:
            mod = C.SMOD_HOSTR
            sym_arr[mod][C.SSYM_MEMSIZE] = '1'
        elif elem == C.DMAP_DISKSIZE:
            mod = C.SMOD_HOSTR
            sym_arr[mod][C.SSYM_STA_TYPE] = '1'
            sym_arr[mod][C.SSYM_STA_DESCR] = '1'
            sym_arr[mod][C.SSYM_STA_AUNITS] = '1'
            sym_arr[mod][C.SSYM_STA_SIZE] = '1'
        elif elem == C.DMAP_DISKINFO:
            mod = C.SMOD_HOSTR
            """
            sym_arr[mod][C.SSYM_DEVTYPE] = '1'
            sym_arr[mod][C.SSYM_DEVDESCR] = '1'
            sym_arr[mod][C.SSYM_DISK_ACCESS] = '1'
            sym_arr[mod][C.SSYM_DISK_MEDIA] = '1'
            sym_arr[mod][C.SSYM_DISK_REMOVEBLE] = '1'
            sym_arr[mod][C.SSYM_DISK_CAPACITY] = '1'
            """
            sym_arr[mod][C.SSYM_STA_TYPE] = '1'
            sym_arr[mod][C.SSYM_STA_DESCR] = '1'
            sym_arr[mod][C.SSYM_STA_AUNITS] = '1'
            sym_arr[mod][C.SSYM_STA_SIZE] = '1'
        elif elem == C.DMAP_APPLI:
            mod = C.SMOD_HOSTR
            sym_arr[mod][C.SSYM_SW_CHANGE] = '1'
            sym_arr[mod][C.SSYM_SW_UPDATE] = '1'
            sym_arr[mod][C.SSYM_SW_NAME] = '1'
            sym_arr[mod][C.SSYM_SW_TYPE] = '1'
            sym_arr[mod][C.SSYM_SW_DATE] = '1'
        elif elem == C.DMAP_COMPUTERINFO:
            # already got
            continue
        elif elem == C.DMAP_DEVICEINFO:
            mod = C.SMOD_HOSTR
            sym_arr[mod][C.SSYM_DEVTYPE] = '1'
            sym_arr[mod][C.SSYM_DEVDESCR] = '1'
        elif elem == C.DMAP_NETWORKINFO:
            mod = C.SMOD_IFMIB
            sym_arr[mod][C.SSYM_IFDSCR] = '1'
            sym_arr[mod][C.SSYM_IFTYPE] = '1'
            sym_arr[mod][C.SSYM_IFPHYSADDR] = '1'
            sym_arr[mod][C.SSYM_IFNAME] = '1'
            sym_arr[mod][C.SSYM_IFPRESENT] = '1'
            sym_arr[mod][C.SSYM_IFALIAS] = '1'
        else:
            continue

    # do snmp_walk
    for mod, syms in sym_arr.items():
        for sym, val in syms.items():
            code, arr = snmp_walk(ret_arr, mod, sym, ip, comm)

            # error handling
            if code == 1:
                return [1, arr]
            if code == 2:
                return [2, arr]

        # end of one field type

    # return results
    return [0, ret_arr]

# END OF get_snmp()


"""
| proc_computername()
|  process ComputerName to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| org_name : str
|     ComputerName got from Snipe-IT
|
| Return value
| ------------
| (This function always returns 0)
"""
def proc_computername(after_data, snmp_data, org_name, domain):
    new_name = snmp_data[C.SMOD_SNMPV2 + '::' + C.SSYM_SYSNAME]['0']
    o_name1 = org_name
    o_name2 = org_name + '.' + domain
    o_name1c = o_name1.casefold()
    o_name2c = o_name2.casefold()
    new_namec = new_name.casefold()
    if (o_name1c != new_namec) and (o_name2c != new_namec):
        # if different ComputerName detected
        after_data[C.JSON_DIFF][C.JDIF_COMPUTERNAME] = True
    after_data[C.JSON_CFIELD][C.JSON_COMPUTERNAME] = new_name
    return 0

# END OF proc_computername()

"""
| proc_computerinfo(after_data, snmp_data, fnfmt)
|  process ComputerInfo to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_computerinfo(after_data, snmp_data, fnfmt):
    new_name = snmp_data[C.SMOD_SNMPV2 + '::' + C.SSYM_SYSDESCR]['0']

    # replace TAGs
    tag = {
        C.TAG_COMPUTERINFO : new_name
    }
    tags = {
        'one': tag,
        'loop': None,
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_COMPUTERINFO), True)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_COMPUTERINFO] = val
    if re.search(C.PTN_OSNAME, new_name) == None:
        # if difference ComputerName detected
        after_data[C.JSON_DIFF][C.JDIF_OSNAME] = True
    return 0

# END OF proc_computerinfo()

"""
| proc_cputhreads(after_data, snmp_data, fnfmt)
|  process CpuThreads to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
|     Note: Add leading spaces if digits of threads not enough
|           to CONF['CPUThreadsDigits']
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_cputhreads(after_data, snmp_data, fnfmt, conf):
    topstr = C.SMOD_HOSTR + '::' + C.SSYM_PROC_FRWID
    digits = conf[C.CF_CPUTHDS_DIGITS]
    dfmt = '{: >' + digits + '}'

    # count CPU threads
    threads = 0
    for a in snmp_data[topstr]:
        threads += 1

    # replace TAGs
    tag = {
        C.TAG_CPUTHREADS : dfmt.format(threads)
    }
    tags = {
        'one': tag,
        'loop': None,
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_CPUTHREADS), True)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_CPUTHREADS] = str(val)

    return 0
# END OF proc_cputhreads():

"""
| proc_memorysize(after_data, snmp_data, fnfmt, conf)
|  process MemorySize to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
|     Note: Add leading spaces if digits of threads not enough
|           to CONF['MemorySizeDigits']
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_memorysize(after_data, snmp_data, fnfmt, conf):
    topstr = C.SMOD_HOSTR + '::' + C.SSYM_MEMSIZE
    unit = conf[C.CF_MEMSIZE_UNIT]
    digits = int(conf[C.CF_MEMSIZE_DIGITS]) + 2
    dfmt = '{: >' + str(digits) + '.1f}'
    # decide unit
    if unit == 'K':
        # case Kilo byte
        unit_div = 1
    elif unit == 'M':
        # case Mega byte
        unit_div = 1024
    elif unit == 'G':
        # case Giga byte
        unit_div = 1024 * 1024
    else:
        # not reached (set default value)
        unit_div = 1024

    # get memory size
    try:
        memsize = dfmt.format(round(int(snmp_data[topstr]['0']) / unit_div, 1))
    except:
        memsize = 'unknown'

    # replace TAGs
    tag = {
        C.TAG_MEMORYSIZE : memsize
    }
    tags = {
        'one': tag,
        'loop': None,
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_MEMORYSIZE), True)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_MEMORYSIZE] = str(val)

    return 0
# END OF proc_memorysize():

"""
| proc_disksize(after_data, snmp_data, fnfmt)
|  process DiskInfo to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
|     Note: Add leading spaces if digits of threads not enough
|           to CONF['DiskSizeDigits']
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_disksize(after_data, snmp_data, fnfmt, conf):
    unit = conf[C.CF_DISKSIZE_UNIT]
    digits = int(conf[C.CF_DISKSIZE_DIGITS]) + 2
    dfmt = '{: >' + str(digits) + '.1f}'
    # decide unit
    if unit == 'K':
        # case Kilo byte
        unit_div = 1024
    elif unit == 'M':
        # case Mega byte
        unit_div = 1024 * 1024
    elif unit == 'G':
        # case Giga byte
        unit_div = 1024 * 1024 * 1024
    else:
        # not reached (set default value)
        unit_div = 1024 * 1024 * 1024

    # process white/black list
    wl = fnfmt['white'].format(C.DMAP_DISKSIZE)
    bl = fnfmt['black'].format(C.DMAP_DISKSIZE)
    lsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_STA_TYPE,
        C.SMOD_HOSTR + '::' + C.SSYM_STA_DESCR
    ]
    code, idx = T.get_tmpl_idx(wl, bl, snmp_data, lsyms)
    if code != 0:
        return idx

    total_capa = 0
    i = 0
    for k, v in idx.items():
        letag = {}

        # build disk size
        try:
            # have disk size
            u = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_AUNITS][k]
            s = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_SIZE][k]
            us = round((int(u) * int(s)) / unit_div, 1)
            #letag[C.TAG_DISK_ONESIZE] = str(int(us))
            letag[C.TAG_DISK_ONESIZE] = dfmt.format(us)
            total_capa += float(us)
        except:
            # not have disk size
            pass

    #val = str(total_capa)
    val = dfmt.format(total_capa)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_DISKSIZE] = str(val)

    return 0
# END OF proc_disksize()

"""
| proc_disksize(after_data, snmp_data, fnfmt)
|  process DiskInfo to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_diskinfo(after_data, snmp_data, fnfmt, conf):
    unit = conf[C.CF_DISKSIZE_UNIT]
    digits = int(conf[C.CF_DISKSIZE_DIGITS]) + 2
    dfmt = '{:0>' + str(digits) + '.1f}'
    # decide unit
    if unit == 'K':
        # case Kilo byte
        unit_div = 1024
    elif unit == 'M':
        # case Mega byte
        unit_div = 1024 * 1024
    elif unit == 'G':
        # case Giga byte
        unit_div = 1024 * 1024 * 1024
    else:
        # not reached (set default value)
        unit_div = 1024 * 1024 * 1024

    # process white/black list
    wl = fnfmt['white'].format(C.DMAP_DISKINFO)
    bl = fnfmt['black'].format(C.DMAP_DISKINFO)
    """
    lsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_DEVTYPE,
        C.SMOD_HOSTR + '::' + C.SSYM_DEVDESCR,
        C.SMOD_HOSTR + '::' + C.SSYM_DISK_ACCESS,
        C.SMOD_HOSTR + '::' + C.SSYM_DISK_MEDIA
    ]
    """
    lsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_STA_TYPE,
        C.SMOD_HOSTR + '::' + C.SSYM_STA_DESCR
    ]
    code, idx = T.get_tmpl_idx(wl, bl, snmp_data, lsyms)
    if code != 0:
        return idx

    # build loop tags
    tsyms = {
        C.TAG_DISK_MEDIA     : C.SMOD_HOSTR + '::' + C.SSYM_DISK_MEDIA,
        C.TAG_DISK_ONESIZE   : C.SMOD_HOSTR + '::' + C.SSYM_DISK_CAPACITY,
        C.TAG_DISK_ACCESS    : C.SMOD_HOSTR + '::' + C.SSYM_DISK_ACCESS,
        C.TAG_DISK_REMOVEBLE : C.SMOD_HOSTR + '::' + C.SSYM_DISK_REMOVEBLE,
        C.TAG_DISK_DESCR     : C.SMOD_HOSTR + '::' + C.SSYM_DEVDESCR
    }
    total_capa = 0
    ltag = []
    i = 0
    """
    for k, v in idx.items():
        # is this a disk device?
        try:
            snmp_data[tsyms[C.TAG_DISK_MEDIA]][k]
        except:
            # this is not a disk device ; skip
            continue

        # this is a disk device
        letag = {}
        for tn, sym in tsyms.items():
            try:
                snmp_data[sym][k]
                letag[tn] = snmp_data[sym][k]
            except:
                continue
        ltag.append(letag)

        # calculate total capacity
        try:
            snmp_data[tsyms[C.TAG_DISK_ONESIZE]][k]
            total_capa += int(snmp_data[tsyms[C.TAG_DISK_ONESIZE]][k])
        except:
            pass
    """
    for k, v in idx.items():
        letag = {}

        # build disk size
        try:
            # have disk size
            u = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_AUNITS][k]
            s = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_SIZE][k]
            us = round((int(u) * int(s)) / unit_div, 1)
            #letag[C.TAG_DISK_ONESIZE] = str(int(us))
            letag[C.TAG_DISK_ONESIZE] = str(us)
            total_capa += float(us)
        except:
            # not have disk size
            letag[C.TAG_DISK_ONESIZE] = 0

        # get storage descr
        try:
            # have hrStorageDescr
            d = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_DESCR][k]
            letag[C.TAG_DISK_DESCR] = d
        except:
            letag[C.TAG_DISK_DESCR] = ''

        # get storage type
        try:
            # have hrStorageDescr
            t = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_STA_TYPE][k]
            letag[C.TAG_DISK_MEDIA] = t
        except:
            letag[C.TAG_DISK_MEDIA] = ''

        ltag.append(letag)

    # Replace TAGs
    tag = {
        C.TAG_DISK_TOTALSIZE : total_capa
    }
    tags = {
        'one': tag,
        'loop': {
            'start': C.LTAG_DISK_S,
            'end'  : C.LTAG_DISK_E,
            'rep'  : ltag
        },
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_DISKINFO), False)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_DISKINFO] = val

    
    return 0
# END OF proc_diskinfo():

"""
| proc_appli(after_data, snmp_data)
|  process Appli to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_appli(after_data, snmp_data, fnfmt):
    # process white/black list
    wl = fnfmt['white'].format(C.DMAP_APPLI)
    bl = fnfmt['black'].format(C.DMAP_APPLI)
    lsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_SW_NAME
    ]
    code, idx = T.get_tmpl_idx(wl, bl, snmp_data, lsyms)
    if code != 0:
        return idx

    # build loop tags
    tsyms = {
        C.TAG_APPLI_NAME     : C.SMOD_HOSTR + '::' + C.SSYM_SW_NAME,
        C.TAG_APPLI_INSTDATE : C.SMOD_HOSTR + '::' + C.SSYM_SW_DATE
    }
    ltag = []
    i = 0
    for k, v in idx.items():
        letag = {}
        for tn, sym in tsyms.items():
            try:
                snmp_data[sym][k]
                letag[tn] = snmp_data[sym][k]
            except:
                continue
        ltag.append(letag)

    # build LastChange and LastUpdate
    nowtime = int(time.time())
    try:
        raw_lc = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_SW_CHANGE]['0']
        raw_lctime = int(int(raw_lc) / 100)
        lc_time = nowtime - raw_lctime
        lc = datetime.datetime.fromtimestamp(lc_time)
    except:
        lc = 'XXXX-XX-XX XX:XX:XX'
    try:
        raw_lu = snmp_data[C.SMOD_HOSTR + '::' + C.SSYM_SW_UPDATE]['0']
        raw_lutime = int(int(raw_lu) / 100)
        lu_time = nowtime - raw_lutime
        lu = datetime.datetime.fromtimestamp(lu_time)
    except:
        lu = 'XXXX-XX-XX XX:XX:XX'

    # Replace TAGs
    tag = {
        C.TAG_APPLI_LASTCHANGE : lc,
        C.TAG_APPLI_LASTUPDATE : lu
    }
    tags = {
        'one': tag,
        'loop': {
            'start': C.LTAG_APPLI_S,
            'end'  : C.LTAG_APPLI_E,
            'rep'  : ltag
        },
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_APPLI), False)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_APPLI] = val

    return 0
# END OF proc_appli():

"""
| proc_deviceinfo(after_data, snmp_data, fnfmt)
|  process DeviceInfo to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_deviceinfo(after_data, snmp_data, fnfmt):
    # process white/black list
    wl = fnfmt['white'].format(C.DMAP_DEVICEINFO)
    bl = fnfmt['black'].format(C.DMAP_DEVICEINFO)
    lsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_DEVDESCR
    ]
    mlsyms = [
        C.SMOD_HOSTR + '::' + C.SSYM_DEVTYPE
    ]
    code, idx = T.get_tmpl_idx(wl, bl, snmp_data, lsyms, mlsyms)
    if code != 0:
        return idx

    # build loop tags
    tsyms = {
        C.TAG_DEVINFO_DESCR : C.SMOD_HOSTR + '::' + C.SSYM_DEVDESCR
    }
    mtsyms = {
        C.TAG_DEVINFO_TYPE : C.SMOD_HOSTR + '::' + C.SSYM_DEVTYPE
    }
    ltag = []
    i = 0
    for k, v in idx.items():
        letag = {}
        for tn, sym in tsyms.items():
            try:
                snmp_data[sym][k]
                letag[tn] = snmp_data[sym][k]
            except:
                continue
        for tn, sym in mtsyms.items():
            try:
                snmp_data[sym][k]
                try:
                    letag[tn] = M.m[snmp_data[sym][k]]
                except:
                    letag[tn] = snmp_data[sym][k]
            except:
                continue
        ltag.append(letag)

    # Replace TAGs
    tag = {}
    tags = {
        'one': None,
        'loop': {
            'start': C.LTAG_DEVINFO_S,
            'end'  : C.LTAG_DEVINFO_E,
            'rep'  : ltag
        },
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_DEVICEINFO), False)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_DEVICEINFO] = val
    return 0
# END OF proc_deviceinfo():

"""
| proc_networkinfo(after_data, snmp_data, fnfmt)
|  process NetworkInfo to output format
|
| Parameters
| ----------
| after_data : dict
|     Return data structure to be stored
| snmp_data : dict
|     SNMP data
| fnfmt : str
|     Template filename format string
|
| Return value
| ------------
| 0 : if no error
| str : if error
"""
def proc_networkinfo(after_data, snmp_data, fnfmt):
    # process white/black list
    wl = fnfmt['white'].format(C.DMAP_NETWORKINFO)
    bl = fnfmt['black'].format(C.DMAP_NETWORKINFO)
    lsyms = [
        C.SMOD_IFMIB + '::' + C.SSYM_IFTYPE,
        C.SMOD_IFMIB + '::' + C.SSYM_IFDSCR
    ]
    code, idx = T.get_tmpl_idx(wl, bl, snmp_data, lsyms)
    if code != 0:
        return idx

    # build loop tags
    tsyms = {
        C.TAG_NETINFO_TYPE  : C.SMOD_IFMIB + '::' + C.SSYM_IFTYPE,
        C.TAG_NETINFO_DESCR : C.SMOD_IFMIB + '::' + C.SSYM_IFDSCR,
        C.TAG_NETINFO_MAC   : C.SMOD_IFMIB + '::' + C.SSYM_IFPHYSADDR
    }
    ltag = []
    i = 0
    for k, v in idx.items():
        letag = {}
        for tn, sym in tsyms.items():
            try:
                snmp_data[sym][k]
                letag[tn] = snmp_data[sym][k]
            except:
                continue
        ltag.append(letag)

    # Replace TAGs
    tag = {}
    tags = {
        'one': None,
        'loop': {
            'start': C.LTAG_NETINFO_S,
            'end'  : C.LTAG_NETINFO_E,
            'rep'  : ltag
        },
        'cond': None
    }
    code, tmpl = T.read_tmpl(fnfmt['tmpl'].format(C.DMAP_NETWORKINFO), False)
    if code != 0:
        return tmpl
    val = T.replace_tag(tmpl, tags)

    # store data
    after_data[C.JSON_CFIELD][C.DMAP_NETWORKINFO] = val

    return 0

# END OF proc_networkinfo():

"""
| accumulate_after(conf, dmap, computer_name, snmp_data)
|  Analyze SNMP data and shape them to 'after' structure
|
| Parameters
| ----------
| conf : dict
|     pc_snipe config data
| dmap : dict
|     Snipe-IT data map
| computer_name : str
|     Computer name which is used to search
| snmp_data : dict
|     Asset data got by SNMP
|
| Return value
| ------------
| after_data : dict
|     Success
| err_msg : str
|     error message
"""
def accumulate_after(conf, dmap, computer_name, ipaddr, snmp_data):
    after_data = {
        C.JSON_CFIELD : {},
        C.JSON_DIFF   : {
            C.JDIF_COMPUTERNAME : False,
            C.JDIF_OSNAME       : False
        }
    }
    fn_fmt = {
        'tmpl'  : conf[C.CF_TMPLPATH] + '/{}/template.conf',
        'white' : conf[C.CF_TMPLPATH] + '/{}/whitelist.conf',
        'black' : conf[C.CF_TMPLPATH] + '/{}/blacklist.conf'
    }

    for elem in dmap:
        if dmap[elem] == '':
            # not set
            continue

        if elem == C.DMAP_COMPUTERNAME:
            code = proc_computername(after_data, snmp_data,
                                     computer_name, conf[C.CF_DNSDOMAIN]
                                    )
        elif elem == C.DMAP_IPADDR:
            after_data[C.JSON_CFIELD][C.DMAP_IPADDR] = ipaddr
        elif elem == C.DMAP_COMMUNITY:
            continue
        elif elem == C.DMAP_CPUTHREADS:
            code = proc_cputhreads(after_data, snmp_data, fn_fmt, conf)
        elif elem == C.DMAP_MEMORYSIZE:
            code = proc_memorysize(after_data, snmp_data, fn_fmt, conf)
        elif elem == C.DMAP_DISKSIZE:
            code = proc_disksize(after_data, snmp_data, fn_fmt, conf)
        elif elem == C.DMAP_DISKINFO:
            code = proc_diskinfo(after_data, snmp_data, fn_fmt, conf)
        elif elem == C.DMAP_APPLI:
            code = proc_appli(after_data, snmp_data, fn_fmt)
        elif elem == C.DMAP_COMPUTERINFO:
            code = proc_computerinfo(after_data, snmp_data, fn_fmt)
        elif elem == C.DMAP_DEVICEINFO:
            code = proc_deviceinfo(after_data, snmp_data, fn_fmt)
        elif elem == C.DMAP_NETWORKINFO:
            code = proc_networkinfo(after_data, snmp_data, fn_fmt)
        else:
            continue

        if code != 0:
            return [2, code]

    return [0, after_data]

# END OF accumulate_after()
