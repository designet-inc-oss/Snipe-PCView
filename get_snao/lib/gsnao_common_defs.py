#
# gsnao_common_defs.py
#  common constant definition
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
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

############
# error code
#

# software error
ERRCODE_SUCCESS   = 0
ERRCODE_ARG       = 1
ERRCODE_CONF      = 2
ERRCODE_DMAP      = 3
ERRCODE_NOASSET   = 5
ERRCODE_DIFF      = 9
ERRCODE_OS        = 10

# system error
ERRCODE_SYS_CONF  = 99
ERRCODE_SYS_DMAP  = 98
ERRCODE_SYS_API   = 97
ERRCODE_SYS_PCS   = 91
ERRCODE_SYS_OTHER = 90

##################
# mapping elements
#
DMAP_COMPUTERNAME = 'ComputerName'

#################
# config elements
#
CF_PCS_CMD = 'PcSnipeCmd'
CF_PCS_CONF = 'PcSnipeConf'
CF_AUTOCOL_KEY = 'AutoCollectKey'
CF_AUTOCOL_VAL = 'AutoCollectValue'
CF_SEARCH_W = 'SnipeIT_SearchWindow'
CF_PCS_PREFIX = 'PcSnipePrefix'
CF_API_URL = 'SnipeIT_API_URL'
CF_KEYFILE           = 'SnipeIT_API_KeyFile'
CF_COMPUTERNAME = DMAP_COMPUTERNAME
CF_MAPPINGFILE = 'MappingFile'
CF_PCS_CONCURRENCY = 'PcSnipeConcurrency'
CF_API_TIMEO = 'SnipeIT_API_Timeout'

#######################
# config default values
#
DEF_CONFIG_FILE  = myprefix + '/etc/get_snao.conf'
DEF_SITWINDOW    = 100
DEF_PCS_PREFIX   = '/usr/local/pc-snipe'
DEF_PCS_CMD      = DEF_PCS_PREFIX + '/bin/pc-snipe'
DEF_PCS_CONF     = DEF_PCS_PREFIX + '/etc/pc-snipe.conf'
DEF_AUTOCOL_KEY  = False
DEF_AUTOCOL_VAL  = False
DEF_PCS_CONCURRENCY = 5
DEF_API_TIMEO    = 30

###########
# JSON keys
#
JSON_TAG          = 'tag'
JSON_ID           = 'id'
JSON_CFIELD       = 'custom_fields'
JSON_ATAG         = 'asset_tag'
JSON_VALUE        = 'value'
JSON_STATUS       = 'status'
JSON_MSG          = 'messages'
JSON_ROWS         = 'rows'
JSON_TOTAL        = 'total'
JVAL_ERR          = 'error'
JVAL_SUCCESS      = 'success'

