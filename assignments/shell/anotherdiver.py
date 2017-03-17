#!/usr/bin/env python

import sys, os, re, optparse
from os import path

LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

def ToFile(args, opts, source):
    argstop = args.index('>')
    f = open(args[argstop+1], 'w')
    for line in source:
        f.write('\n'+line)
    return source

def List_Dir(args, opts):
    output = []
    dirlist = os.listdir(args[1])

    if opts.isAll == False:
        for file in dirlist:
            if re.match(r'^\..*', file):
                del dirlist[dirlist.index(file)]

    if opts.isLong == True:
        parent = path.abspath(args[1])
        for file in dirlist:
            listindex = dirlist.index(file)
            dirlist[listindex] = parent + file

    if opts.isRead == True:
        for file in dirlist:
            listindex = dirlist.index(file)
            filesize = path.getsize(file) / 1024.0
            print('{:<20}{:>30.2f} kb'.format(file, filesize))
            dirlist[listindex] = filesize

    print("answer:\n".format(dirlist))
    return dirlist

def ParseCmd(raw_cmd):
    # split the command into a list
    print(type(raw_cmd))
    print("String {}".format(raw_cmd))
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
    # parser.add_option('<', dest='fromFile', action='store_true',
    #         default=False, help='<bool> input is redirected from a file ')

    return parser.parse_args(raw_cmd)

def Run_Loop(raw_cmd):
#   make a child process
    pid = os.fork()
    if pid == 0:
#       parse the new command
	split_cmd = raw_cmd.split()
	print("Run_CMD String {}".format(split_cmd))
        (options, args) = ParseCmd(split_cmd)
        print('Options: {}\nArgs: {}\n'.format(options, args))

#      if self is a child process
        if args[0] == 'ls':
#           runs the specified cmd
            dirlist = List_Dir(args, options)
            if any('>' in s for s in args):
                ToFile(args, options, dirlist)
            else:
                print("Listing:\n{}".format(dirlist))
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
        print("Main\nRawType: {}\nRaw Content: {}\n".format(type(raw_cmd), raw_cmd))

        #   Run command
        status = Run_Loop(raw_cmd)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
