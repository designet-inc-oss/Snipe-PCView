#
# pcs_dns.py
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

import socket
import os
import sys
import dns.resolver
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

from lib import common_defs as C


"""
| get_ipaddr_by_sys(host)
|  get IP address by gethostbyname()
|
| Parameters
| ----------
| host : str
|  hostname to query
|
| Return value
| ------------
| code:
|  0: no error
|  1: software error
|  2: system error
| ip: str
|  ip address if no error
|  error message if error
"""
def get_ipaddr_by_sys(host):
    try:
        ip = socket.gethostbyname(host)
        code = 0
    except BaseException as e:
        ip = e
        code = 1
    return [code, ip]

# END OF get_ipaddr_by_sys()

"""
| get_ipaddr_by_dns(nameserver, host)
|  get IP address by gethostbyname()
|
| Parameters
| ----------
| nameserver : str
|  DNS resolver IP address
| host : str
|  hostname to query
|
| Return value
| ------------
| code:
|  0: no error
|  1: software error
|  2: system error
"""
def get_ipaddr_by_dns(conf, host):
    nameserver = conf[C.CF_DNSADDR]
    dnstimeo = conf[C.CF_DNS_TIMEO]

    # setup Resolver instance without system default configuration
    resolver = dns.resolver.Resolver(configure=False)

    # set parameters
    resolver.nameservers = [nameserver]
    resolver.timeout = dnstimeo
    resolver.lifetime = dnstimeo

    # do query
    try:
        answers = resolver.query(host, 'A')
    except dns.resolver.NXDOMAIN as e:
        # NXDOMAIN
        return [1, e]
    except dns.resolver.Timeout as e:
        # timeout
        return [2, e]
    except Exception as e:
        # other system error
        return [2, e]

    return [0, str(answers[0])]

# END OF get_ipaddr_by_dns()

"""
| get_ipaddr(conf, host):
|  Get IP address of WindowsPC
|   system mode: by gethostbyname()
|   DNS mode: by myself from DNS
|
| Parameters
| ----------
| conf : dict
|     configuration data
| host : str
|     hostname to search
|
| Return value
| ------------
| {code, ip_addr}
| code:
|     0: no error
|     1: config error
|     2: system error
| ip_addr : str
|     IP address if no error
|     error message if error detected
"""
def get_ipaddr(conf, host):
    # split DNS_Address setting condition
    if conf[C.CF_DNSADDR] == '':
        # system mode
        code, ip_addr = get_ipaddr_by_sys(host)
    else:
        # DNS mode
        code, ip_addr = get_ipaddr_by_dns(conf, host)

    if code == 1:
        return [1, ip_addr]
    if code == 2:
        return [2, ip_addr]

    return [0, ip_addr]

# END OF get_ipaddr()
