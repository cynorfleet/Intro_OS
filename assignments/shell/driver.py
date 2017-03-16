#!/usr/bin/env python

import sys
import os
import re

class CommandStat:
    cmd = ''
    option = {[]}
    optcount = 0
    fields = 0

    def ToString(self):
        return 'command = {}\noption = {}\nfields = {}\noption_flag = {}'.format(cmd,option,fields,option_flag)
        

#   Loop flags
LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0
CmdConfig = CommandStat()

def List_Dir(cmd_parsed):
    # if index 1 is an option param
    if re.findall(r'(-[lsh]+)+', cmd_parsed[1]):
        dirlist = os.listdir( cmd_parsed[2] )
    # if no option params
    else:
        dirlist = os.listdir( cmd_parsed[1] )

    # print list of files and directories
    print ("\nThe listing for specified directory is: ")
    for file in dirlist:
        print (file)
    return

def Parse_Cmd(string):
    searchObj = re.findall(r'(-[lsh]+)+', string)
#   split the cmd and return array
#    searchObj = re.split(r'(-[lsh]+)+', string, re.I)
    if searchObj:
        print ('\nOption Params = {}' .format(searchObj))
        for option in searchObj:
            CmdConfig.option.add(option)
            print ('Option = {}' .format(CmdConfig.option[CmdConfig.optcount])
            CmdConfig.optcount += 1
    else:
        print ('Nothing!!!')

    string = str.split(string)
    CmdConfig.cmd = string[0]
    return CmdConfig

def Run_Cmd(cmd_parsed):
#   make a child process
    pid = os.fork()
    if pid == 0:
        #   if self is a child process
        #   runs the specified cmd
        if cmd_parsed[0] == 'ls':
            List_Dir(cmd_parsed)
        # else:
            #os.execvp(cmd_parsed[0], cmd_parsed)
    elif pid > 0:
        #   if self is parent process
        while True:
            wpid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break

    return LOOP_STATUS_GO

def shell_loop():
    #   Start looping
    status = LOOP_STATUS_GO

    while status == LOOP_STATUS_GO:
        #   Display a cmd
        sys.stdout.write('BAD A$$ SHELL:> ')
        sys.stdout.flush()

        #   Get user command
        cmd = sys.stdin.readline()

        #   Parse comand
        cmd_parsed = Parse_Cmd(cmd)

        #   Run command
        status = Run_Cmd(cmd_parsed)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
