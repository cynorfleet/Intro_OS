#!/usr/bin/env python

import sys
import os


#   Loop flags
LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

def Parse_Cmd(string):
#   split the cmd and return array
    return str.split(string)

def Run_Cmd(cmd_parsed):
#   make a child process
    pid = os.fork()

    if pid == 0:
        #   if self is a child process
        #   runs the specified cmd
        os.execvp(cmd_parsed[0], cmd_parsed)
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
        sys.stdout.write(':> ')
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