#!/usr/bin/env python

import sys, os, re, optparse, tempfile
from os import path

LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

argspec = {'ls': {'min':1,'max':2}, 'mkdir': {'min':2,'max':2},
       'cd': {'min':1,'max':2}, 'pwd': {'min':1,'max':1},
       'cp': {'min':2,'max':3}, 'mv': {'min':2,'max':3},
       'rm': {'min':2,'max':2}, 'rmdir': {'min':2,'max':2},
       'cat': {'min':2,'max':5}, 'less': {'min':2,'max':2},
       'head': {'min':2,'max':2}, 'tail': {'min':2,'max':2},
       'grep': {'min':3,'max':3}, 'wc': {'min':2,'max':2},
       'sort': {'min':1,'max':1}, 'who': {'min':1,'max':1},
       'history': {'min':1,'max':1}, '!':{'min':2,'max':2},
       'chmod': {'min':2,'max':2}}

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

def Mk_Dir(args):
    path = args[0]
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def Change_Dir(args):
    if len(args) == 0:
        return
    else:
        path = args[0]
        try:
            os.chdir(path)
        except:
            return("Invalid path name")
    return path

def Print_Dir(args):
    path = os.getcwd()
    return path

def Remove_Dir(args):
    path = args[0]
    try:
        if os.path.exists(path):
            os.removedirs(path)
        else:
            return("Directory Does Not Exist")
    except:
        return("Could NOT remove path")
    return

def Remove_Path(args):
    path = args[0]
    try:
        if os.path.exists(path):
            os.remove(path)
        else:
            return("Path Does Not Exist")
    except:
        return("Could NOT remove path")
    return

def Move_Path(args):
    source = args[0]
    destination = args[1]
    try:
        if os.path.exists(source):
            os.rename(source, destination)
            return destination
        else:
            return("Source Path Does Not Exist")
    except:
        return("Could NOT copy path")
    return

def Copy_Path(args):
    source = args[0]
    destination = args[1]
    try:
        if os.path.exists(source):
            data = ''
            with open(source, 'r') as tempsource:
                data = tempsource.readlines()
            tempsource.close()
            with open(destination, 'w') as tempwrite:
                tempwrite.writelines(data)
            tempwrite.close()
            return destination
        else:
            return("Path Does Not Exist")
    except:
        return("Could NOT copy path")

def View_File(args):
    path = args[0]
    try:
        if os.path.exists(path):
            data = ''
            with open(path, 'r') as temp:
                data = temp.read()
            temp.close()
            return data
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Head_File(args):
    path = args[0]
    try:
        if os.path.exists(path):
            data = ''
            with open(path, 'r') as temp:
                data = temp.read(1024)
            temp.close()
            return data
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Tail_File(args):
    path = args[0]
    try:
        if os.path.exists(path):
            data = ''
            with open(path, 'r') as temp:
                temp.seek(-1024, 2)
                data = temp.read()
            temp.close()
            return data
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Less_File(args):
    path = args[0]
    try:
        if os.path.exists(path):
            data = ''
            usrprompt = None
            with open(path, 'r') as temp:
                while temp.tell() < temp.__sizeof__() and usrprompt != 'q':
                    data = temp.read(4096)
                    print(data)
                    usrprompt = raw_input("Hit 'enter' to continue ('q' to quit)")
            temp.close()
            return
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return
def _WorkLoop(split_cmd):
    (options, args) = ParseCmd(split_cmd)
    result = []
    arglen = len(args)
    spec = argspec[args[0]]
    if args[0] == 'ls':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = ListFactory(args[1:], options)
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'mkdir':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Mk_Dir(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'cd':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Change_Dir(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'pwd':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Print_Dir(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'rmdir':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Remove_Dir(args[1:])
        else:
            print('ERROR: invalid args')
    if args[0] == 'rm':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Remove_Path(args[1:])
        else:
            print('ERROR: invalid args')
    if args[0] == 'cp':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Copy_Path(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'mv':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Move_Path(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'cat':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = View_File(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'head':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Head_File(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'tail':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Tail_File(args[1:])
            print (result)
        else:
            print('ERROR: invalid args')
    if args[0] == 'less':
        print("Arglen={}\nMin={}\nMax={}\n".format(arglen,spec['min'], spec['max']))
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Less_File(args[1:])
        else:
            print('ERROR: invalid args')


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
            del pipedcmd[0]
            Run_Loop(pipedcmd)
        else:
                # if list of commands (ie from piped or file)
                if type(raw_cmd) == list:
                    for item in raw_cmd:
                        split_cmd = item.split()
                        print("NOT PIPED. Contains: {}. Type: {}".format(item, type(item)))
                        _WorkLoop(split_cmd)
                # if single command
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
