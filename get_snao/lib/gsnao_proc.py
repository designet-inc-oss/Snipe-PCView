#
# gsnao_proc.py
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
import os
import sys
import time
import json

#
# import from our library
#
myprefix = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(myprefix)

from lib import gsnao_common_defs as C

#
# constant definision
#
ST_INPROGRESS=1
ST_DONE=2
MODE_ADD = 1
MODE_WAIT = 2
MODE_ERROR = 3

"""
| exec_proc(prog, arglist)
|  invoke pc-snipe as child process
|
| Parameters
| ----------
|
| Return value
| ------------
"""
def exec_proc(prog, arglist):
    try:
        rpipe, wpipe = os.pipe()
        pid = os.fork()
    except OSError as e:
        return [False, e, None]
    if not pid:
        try:
            os.close(rpipe)
            os.dup2(wpipe, 1)
            os.execv(prog, arglist)
        except OSError as e:
            return [False, e, None]
            os_exit(C.ERRCODE_SYS_OTHER)
    else:
        os.close(wpipe)
        # set read pipe non-blocking mode
        os.set_blocking(rpipe, False)

        rpipe = os.fdopen(rpipe, 'r')
        return [True, pid, rpipe]

# END OF exec_proc()

"""
| manage_proc(conf, arg_list, atags)
|  manage process with process pool
|
| Parameters
| ----------
| conf : dict
|     config data
| arg_list : dict
|     arguments information
| atags : list
|     asset tags
|
| Return value
| ------------
| [ret_code, ret_arr]
| ret_code : int
|     0 : success
|     1 : software error
|     2 : system error
| ret_arr : dict
|     results from pc-snipe for each invokation
"""
def manage_proc(conf, arg_list, atags):
    #
    # counter definision
    #

    # concurrency
    window = int(conf[C.CF_PCS_CONCURRENCY])
    # total assets
    limit = len(atags)
    # next process index number
    count = 0
    # process counter now invoked
    nowproc = 0
    # counter that was done
    done = 0
    # process pool dict
    procs = {}
    # mode
    mode = -1
    # stop mode
    smode = arg_list['stop_mode']
    # report mode
    rmode = arg_list['report_mode']
    # error flag
    eflag = 0

    ret_arr = {}
    prog = conf[C.CF_PCS_CMD]
    pcs_conf = conf[C.CF_PCS_CONF]

    while done < limit:
        # decide mode
        if mode == MODE_ERROR:
            if nowproc == 0:
                break
        elif nowproc < window:
            # make process
            mode = MODE_ADD
        else:
            mode = MODE_WAIT

        if mode == MODE_ADD:
            # invoke pc-snipe processes up to PcSnipeConcurrency

            # care window
            if count + window > limit:
                window = limit - count

            # invoke them
            while nowproc < window:
                # invoke one pc-snipe
                pcs_args = [
                    prog,
                    '-c',
                    pcs_conf,
                    '-t',
                    atags[count]['atag']
                ]
                ret, cpid, rpipe = exec_proc(prog, pcs_args)
                if ret == False:
                    # system error ; force return
                    msg = cpid.strerror()
                    return [2, msg]

                # create process pool
                procs[str(cpid)] = {
                    'serial' : count,
                    'status' : ST_INPROGRESS,
                    'pipe'   : rpipe,
                    'msg'    : ''
                }
                count += 1
                nowproc += 1
        elif mode == MODE_WAIT or mode == MODE_ERROR:
            # collect process
            epid, code = os.waitpid(-1, os.WNOHANG)
            if epid == 0:
                # if no process finished
                # wait one second
                time.sleep(1)
            else:
                # a process finished

                # get messages from stdout of pc-snipe
                procs[str(epid)]['msg'] += procs[str(epid)]['pipe'].read()

                # update process pool
                procs[str(epid)]['status'] = ST_DONE
                done += 1
                nowproc -= 1

                # store message if report mode is True
                myatag = atags[procs[str(epid)]['serial']]['atag']
                ecode = os.WEXITSTATUS(code)
                if os.WIFEXITED(code) == False:
                    efmt = 'The process was abnormal end (pid={})'
                    msg = efmt.format(epid)
                    ret_arr[myatag] = split_msg(procs[str(epid)]['msg'], rmode)
                    eflag = 1
                    if smode == True:
                        # stop mode
                        mode = MODE_ERROR
                elif not (
                          (ecode == C.ERRCODE_SUCCESS)
                          or (ecode == C.ERRCODE_DIFF)
                          or (ecode == C.ERRCODE_OS)
                         ):
                    # error status
                    ret_arr[myatag] = split_msg(procs[str(epid)]['msg'], rmode)
                    eflag = 1
                    if smode == True:
                        # stop mode
                        mode = MODE_ERROR
                else:
                    ret_arr[myatag] = split_msg(procs[str(epid)]['msg'], rmode)

                # cleanup process pool of this
                procs[str(epid)]['pipe'].close()
                procs.pop(str(epid))

        # care messages
        for k, v in procs.items():
            try:
                procs[k]['msg'] += v['pipe'].read()
            except TypeError as e:
                # No data in buffer
                pass
            except:
                # error
                msg = 'Failed to read outputs from pc-snipe'
                return [2, msg]

    if eflag == 1:
        ret_code = 1
    else:
        ret_code = 0
    return [ret_code, ret_arr]

# END OF manage_proc()

"""
| split_msg(msg, rmode)
|  Decode JSON message from pc-snipe to array
|  If rmode is False, supress 'before' and 'after' report
|
| Parameters
| ----------
| msg : str
|     JSON message from pc-snipe
| rmode : boolean
|     report mode
|
| Return value
| ------------
| data : dict
|     decoded data
"""
def split_msg(msg, rmode):
    data = json.loads(msg)
    if rmode == False:
        data['before'] = []
        data['after'] = []
    return data

# END OF split_msg()
