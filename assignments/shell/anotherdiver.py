#!/usr/bin/env python

import sys, os, re, optparse

LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

def ParseCmd(raw_cmd):
    # split the command into a list
    parsed_cmd = raw_cmd.split()

    # Define the options/args
    parser = optparse.OptionParser('usage %prog -a<bool> list all show hidden'+\
            'files -l<bool>long listing -h<bool> human readable sizes',
            version="%prog 1.0")

    parser.add_option('-a', '-A', '--all', dest='isAll', action='store_true',
            default=False, help='<bool> show hidden files')
    parser.add_option('-l', '-L', '--long', dest='isLong', action='store_true',
            default=False, help='<bool> long listing')
    parser.add_option('-r', '-R', '--readable', dest='isRead', action='store_true',
            default=False, help='<bool> show human readable sizes')
    # parser.add_option('>', dest='toFile', action='store_true',
    #         default=False, help='<bool> sends output to file')
    # parser.add_option('<', dest='fromFile', action='store_true',
    #         default=False, help='<bool> input is redirected from a file ')

    return parser.parse_args(parsed_cmd)

def Run_Cmd(raw_cmd):
#   make a child process
    pid = os.fork()
    if pid == 0:
#       parse the new command
        (options, args) = ParseCmd(raw_cmd)
        print('Options: {}\nArgs: {}\n')

# #      if self is a child process
#         if options. == 'ls':
# #           runs the specified cmd
#             ary = List_Dir(command)
#             for i in ary:
#                 print (i)
#         elif command.cmd == 'mkdir':
#             Mk_Dir(command)
#         elif command.cmd == 'cd':
#             Chg_Dir(command)
#         elif command.cmd == 'pwd':
#             Print_Dir(command)

#   if self is parent process
    elif pid > 0:
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
        raw_cmd = sys.stdin.readline()
        command = ParseCmd(raw_cmd)

        #   Run command
        status = Run_Cmd(command)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
