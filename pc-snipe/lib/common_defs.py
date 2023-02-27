#
# common_defs.py
#  common constant definition
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
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

############
# error code
#

# software error
ERRCODE_SUCCESS  = 0
ERRCODE_ARG      = 1
ERRCODE_CONF     = 2
ERRCODE_DMAP     = 3
ERRCODE_NOTAG    = 4
ERRCODE_NOASSET  = 5
ERRCODE_NOIP     = 6
ERRCODE_NOSNMP   = 7
ERRCODE_NOTMPL   = 8
ERRCODE_DIFF     = 9
ERRCODE_OS       = 10

# system error
ERRCODE_SYS_CONF = 99
ERRCODE_SYS_DMAP = 98
ERRCODE_SYS_API  = 97
ERRCODE_SYS_DNS  = 96
ERRCODE_SYS_SNMP = 95
ERRCODE_SYS_TMPL = 94
ERRCODE_SYS_WL   = 93
ERRCODE_SYS_BL   = 92

#################
# config elements
#
CF_API_URL           = 'SnipeIT_API_URL'
CF_KEYFILE           = 'SnipeIT_API_KeyFile'
CF_API_TIMEO         = 'SnipeIT_API_Timeout'
CF_DNSADDR           = 'DNS_Address'
CF_DEFAULT_COMM      = 'DefaultCommunity'
CF_DNSDOMAIN         = 'DNS_Domain'
CF_SIT_SEARCH_WINDOW = 'SnipeIT_SearchWindow'
CF_TMPLPATH          = 'TemplatePath'
CF_MAPPINGFILE       = 'MappingFile'
CF_DNS_TIMEO         = 'DNS_Timeout'
CF_DISKSIZE_UNIT     = 'DiskSizeUnit'
CF_MEMSIZE_UNIT      = 'MemorySizeUnit'
CF_DISKSIZE_DIGITS   = 'DiskSizeDigits'
CF_MEMSIZE_DIGITS    = 'MemorySizeDigits'
CF_CPUTHDS_DIGITS    = 'CPUThreadsDigits'

##################
# mapping elements
#
DMAP_COMPUTERNAME = 'ComputerName'
DMAP_IPADDR       = 'IPaddr'
DMAP_COMMUNITY    = 'Community'
DMAP_CPUTHREADS   = 'CPUThreads'
DMAP_MEMORYSIZE   = 'MemorySize'
DMAP_DISKINFO     = 'DiskInfo'
DMAP_DISKSIZE     = 'DiskSize'
DMAP_APPLI        = 'Appli'
DMAP_COMPUTERINFO = 'ComputerInfo'
DMAP_DEVICEINFO   = 'DeviceInfo'
DMAP_NETWORKINFO  = 'NetworkInfo'

#######################
# config default values
#
DEF_CONFIG_FILE  = myprefix + '/etc/pc-snipe.conf'
DEF_API_KEY_FILE = myprefix + '/etc/api.key'
DEF_MAPPING_FILE = myprefix + '/etc/mapping.conf'
DEF_TMPL_DIR     = myprefix + '/tmpl'
DEF_SITWINDOW    = 100
DEF_APIURL       = False
DEF_APITIMEO     = 30
DEF_DNSADDR      = ''
DEF_DEFAULTCOMM  = False
DEF_DNSDOMAIN    = ''
DEF_DNS_TIMEO    = 2
DEF_DISKSIZE_U   = 'G'
DEF_MEMSIZE_U    = 'M'
DEF_DISKSIZE_D   = '4'
DEF_MEMSIZE_D    = '6'
DEF_CPUTHDS_D    = '2'

###########
# JSON keys
#
JSON_BEFORE       = 'before'
JSON_AFTER        = 'after'
JSON_TAG          = 'tag'
JSON_CFIELD       = 'custom_fields'
JSON_ID           = 'id'
JSON_ATAG         = 'asset_tag'
JSON_RAW          = 'raw'
JSON_COMPUTERNAME = 'ComputerName'
JSON_COMPUTERINFO = 'ComputerInfo'
JSON_COMMUNITY    = 'Community'
JSON_VALUE        = 'value'
JSON_STATUS       = 'status'
JSON_MSG          = 'messages'
JVAL_ERR          = 'error'
JVAL_SUCCESS      = 'success'
JSON_DIFF         = 'diffdata'
JSON_FIELD        = 'field'
JDIF_COMPUTERNAME = 'ComputerName'
JDIF_OSNAME       = 'OSName'
JSON_TOTAL        = 'total'
JSON_ROWS         = 'rows'

###########
# SNMP defs
#
SMOD_SNMPV2         = 'SNMPv2-MIB'
SSYM_SYSNAME        = 'sysName'
SSYM_SYSDESCR       = 'sysDescr'

SMOD_HOSTR          = 'HOST-RESOURCES-MIB'
SSYM_PROC_FRWID     = 'hrProcessorFrwID'
SSYM_MEMSIZE        = 'hrMemorySize'
SSYM_DISK_ACCESS    = 'hrDiskStorageAccess'
SSYM_DISK_MEDIA     = 'hrDiskStorageMedia'
SSYM_DISK_REMOVEBLE = 'hrDiskStorageRemoveble'
SSYM_DISK_CAPACITY  = 'hrDiskStorageCapacity'
SSYM_DEVTYPE        = 'hrDeviceType'
SSYM_DEVDESCR       = 'hrDeviceDescr'
SSYM_SW_CHANGE      = 'hrSWInstalledLastChange'
SSYM_SW_UPDATE      = 'hrSWInstalledLastUpdateTime'
SSYM_SW_NAME        = 'hrSWInstalledName'
SSYM_SW_TYPE        = 'hrSWInstalledType'
SSYM_SW_DATE        = 'hrSWInstalledDate'
SSYM_STA_TYPE       = 'hrStorageType'
SSYM_STA_DESCR      = 'hrStorageDescr'
SSYM_STA_AUNITS     = 'hrStorageAllocationUnits'
SSYM_STA_SIZE       = 'hrStorageSize'

SMOD_IFMIB          = 'IF-MIB'
SSYM_IFDSCR         = 'ifDescr'
SSYM_IFTYPE         = 'ifType'
SSYM_IFPHYSADDR     = 'ifPhysAddress'
SSYM_IFNAME         = 'ifName'
SSYM_IFPRESENT      = 'ifConnectorPresent'
SSYM_IFALIAS        = 'ifAlias'

###################
# pattern constants
#
PTN_OSNAME = 'Software: Windows'

##############
# replace tags
#

# CPUThreads
TAG_CPUTHREADS = '[[CPUThreads]]'

# MemorySize
TAG_MEMORYSIZE = '[[MemorySize]]'

# DiskInfo
TAG_DISK_TOTALSIZE = '[[TotalCapacity]]'
LTAG_DISK_S        = '[[DiskInfoBegin]]'
LTAG_DISK_E        = '[[DiskInfoEnd]]'
TAG_DISK_DESCR     = '[[DeviceDescr]]'
TAG_DISK_ACCESS    = '[[Access]]'
TAG_DISK_REMOVEBLE = '[[Removeble]]'
TAG_DISK_ONESIZE   = '[[Capacity]]'
TAG_DISK_MEDIA     = '[[Media]]'

# Appli
TAG_APPLI_LASTCHANGE = '[[LastChange]]'
TAG_APPLI_LASTUPDATE = '[[LastUpdate]]'
LTAG_APPLI_S         = '[[AppliBegin]]'
LTAG_APPLI_E         = '[[AppliEnd]]'
TAG_APPLI_NAME       = '[[AppliName]]'
TAG_APPLI_INSTDATE   = '[[InstalledDate]]'

# ComputerInfo
TAG_COMPUTERINFO = '[[ComputerInfo]]'

# DeviceInfo
LTAG_DEVINFO_S    = '[[DeviceInfoBegin]]'
LTAG_DEVINFO_E    = '[[DeviceInfoEnd]]'
TAG_DEVINFO_TYPE  = '[[DeviceType]]'
TAG_DEVINFO_DESCR = '[[DeviceDescr]]'

# NetworkInfo
LTAG_NETINFO_S    = '[[NetworkInfoBegin]]'
LTAG_NETINFO_E    = '[[NetworkInfoEnd]]'
TAG_NETINFO_TYPE  = '[[IFType]]'
TAG_NETINFO_DESCR = '[[IFDescr]]'
TAG_NETINFO_MAC   = '[[IFMac]]'

