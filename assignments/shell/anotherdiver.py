#!/usr/bin/env python

import sys, os, re, optparse
from os import path

LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

def ToFile(args, aORw, source, mode):
    argstop = args.index(aORw)
    argtarget = args[argstop+1]
    f = open(argtarget, mode)

    if mode == 'a':
        print("APPEND MODE")
    elif mode == 'w':
        print("WRITE MODE")

    for line in source:
        f.write('\n'+line)
    return source

def FromFile(args):
    mode='r'
    print("READ MODE")

    sendback = []
    argindex = args.index('<')
    source = args[argindex+1]
    print("source: {}".format(source))
    f = open(source, 'r')
    sendback = f.read().splitlines()
    f.close()
    print('LINE: {}\n'.format(sendback))
    # for line in f:
        # sendback.append(line)


    return sendback

def List_Dir(target, opts):
    output = []
    convertsize = 1024.0
    dirlist = os.listdir(target)

    if opts.isAll == False:
        for file in dirlist:
            if re.match(r'^\..*', file):
                del dirlist[dirlist.index(file)]

    if opts.isLong == True:
        parent = path.abspath(target)
        for file in dirlist:
            listindex = dirlist.index(file)
            dirlist[listindex] = parent + file

    if opts.isRead == True:
        for file in dirlist:
            listindex = dirlist.index(file)
            filesize = path.getsize(file) / convertsize
            print('{:<20}{:>30.2f} kb'.format(file, filesize))
            dirlist[listindex] = filesize

    return dirlist


def ParseCmd(raw_cmd):
    # split the command into a list
    print("\nString {}".format(raw_cmd))
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

def ListFactory(args, options):

    print('Options: {}\nArgs: {}\n'.format(options, args))

    dirlist = []

    if any('<' in s for s in args):
        result = []
        argindex = args.index('<')
        source = args[argindex+1]
        data = FromFile(args)
        for line in data:
            if line == '':
                del data[data.index(line)]
            else:
                result.append(List_Dir(line, options))
                dirlist = result
                print("Result:\n{}".format(result))
        return result

    else:
        if len(args) < 1:
            args.append('.')

        dirlist = List_Dir(args[0], options)

        if any('>>' in s for s in args):
            mode = 'a'
            dirlist = ToFile(args, '>>', dirlist, mode)
            return dirlist

        elif any('>' in s for s in args):
            mode = 'w'
            dirlist = ToFile(args, '>', dirlist, mode)
            return dirlist

        else:
            return dirlist
    return

def _WorkLoop(split_cmd):
    (options, args) = ParseCmd(split_cmd)
    result = []

    if args[0] == 'ls':
        result = ListFactory(args[1:], options)
        print (result)
    return result

def Run_Loop(raw_cmd):
#   make a child process
    pid = os.fork()
    if pid == 0:
        if '|' in raw_cmd:
            print("PIPED")
            pipedcmd = raw_cmd.split('|')
    #       parse the new command
            split_cmd = pipedcmd[0].split()
            _WorkLoop(split_cmd)

    #           runs the specified cmd

    #                 print (i)
    #         elif command.cmd == 'mkdir':
#             Mk_Dir(command)
    #         elif command.cmd == 'cd':
    #             Chg_Dir(command)
    #         elif command.cmd == 'pwd':
    #             Print_Dir(command)

            #   if self is parent process
            del pipedcmd[0]
            Run_Loop(pipedcmd)
        else:
                if type(raw_cmd) == list:
                    for item in raw_cmd:
                        split_cmd = item.split()
                        print("NOT PIPED. Contains: {}. Type: {}".format(item, type(item)))
                        _WorkLoop(split_cmd)
                else:
                    split_cmd = raw_cmd.split()
                    _WorkLoop(split_cmd)

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

        #   Run command
        status = Run_Loop(raw_cmd)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
