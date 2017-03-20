#!/usr/bin/env python

import sys, os, re, optparse, tempfile, stat
from os import path

LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

history = []
# holds the previously entered commands

argspec = \
# specifies the required arguments for commands
    {'ls': {'min':1,'max':2}, 'mkdir': {'min':2,'max':2},
   'cd': {'min':1,'max':2}, 'pwd': {'min':1,'max':1},
   'cp': {'min':2,'max':3}, 'mv': {'min':2,'max':3},
   'rm': {'min':2,'max':2}, 'rmdir': {'min':2,'max':2},
   'cat': {'min':2,'max':5}, 'less': {'min':2,'max':2},
   'head': {'min':2,'max':2}, 'tail': {'min':2,'max':2},
   'grep': {'min':3,'max':3}, 'wc': {'min':2,'max':2},
   'sort': {'min':1,'max':1}, 'who': {'min':1,'max':1},
   'history': {'min':1,'max':1}, '!':{'min':2,'max':2},
   'chmod': {'min':3,'max':3}}

permissions = \
# specifies the availible options for chmod command
    {'setID' : stat.S_ISUID,
    'setGRP' : stat.S_ISGID,
    'rcrdLOK': stat.S_ENFMT,
    'savTXT' : stat.S_ISVTX,
    'rOWN' : stat.S_IREAD,
    'wOWN' : stat.S_IWRITE,
    'xOWN' : stat.S_IEXEC,
    'rwxOWN' : stat.S_IRWXU,
    'rOWN' : stat.S_IRUSR,
    'wUSR' : stat.S_IWUSR,
    'xUSR' : stat.S_IXUSR,
    'rwxGRP' : stat.S_IRWXG,
    'rGRP' : stat.S_IRGRP,
    'wGRP' : stat.S_IWGRP,
    'xGRP' : stat.S_IXGRP,
    'rwxOTH' : stat.S_IRWXO,
    'rOTH' : stat.S_IROTH,
    'wOTH' : stat.S_IWOTH,
    'xOTH' : stat.S_IXOTH}

def ParseCmd(raw_cmd):
    ''' This method will parse the raw command into 2 lists ( args, options)'''
    # helper string for gen usage of function
    parser = optparse.OptionParser('usage %prog -a<bool> list all show hidden'+\
            'files -l<bool> long listing -h<bool> human readable sizes',
            version="%prog 1.0")
    # Define the options/args
    parser.add_option('-a', '-A', '--all', dest='isAll', action='store_true',
            default=False, help='<bool> show hidden files')
    parser.add_option('-l', '-L', '--long', dest='isLong', action='store_true',
            default=False, help='<bool> long listing')
    parser.add_option('-r', '-R', '--readable', dest='isRead', action='store_true',
            default=False, help='<bool> show human readable sizes')
    return parser.parse_args(raw_cmd)


def ToFile(result, mode, dest):
    ''' This method will redirect output from a function to a file '''
    try:
        # open the file
        with open(dest, mode) as f:
            # write the line
            for line in result:
                f.write('\n'+line)
        f.close()
    except:
        # on exception print error
        print("Could not write file")
    return result

def FromFile(args):
    ''' This method will pass data from a file to a function '''
    # specifies option for opening file
    mode='r'
    # the new argument to be sent back to calling function
    sendback = []

    try:
        argindex = args.index('<')
        # get the index of the file arg
        source = args[argindex+1]
        with open(source, 'r') as f:
            # read the file and store it as lists of raw string
            sendback = f.read().splitlines()
        f.close()
    except:
        print("Could not open file")
    for line in sendback:
        # if not an empty line
        if line != '':
            # chop off args trailing the '<' as they are no longer needed
            newargs = args[:argindex]
            # parse the strings into arg form
            linesplit = line.split()
            # put the new args at end or calling arg list
            newargs.extend(linesplit)
            try:
                # Process the new command
                _WorkLoop(newargs)
            except:
                print("Error passing file to function")
    return sendback

def List_Dir(target, opts):
    ''' lists the contents of a directory '''
    output = []
    dirlist = []
    convertsize = 1024.0
    try:
        # get a list of directories
        dirlist = os.listdir(target)
    except:
        return("Could not find file or dir")

    # if NOT showing hidden files
    if opts.isAll == False:
        for file in dirlist:
            # if pathname starts with a period
            if re.match(r'^\..*', file):
                # remove hidden path from list
                del dirlist[dirlist.index(file)]

    # if Long pathnames
    if opts.isLong == True:
        # get full path from filename
        parent = path.abspath(target)
        for file in dirlist:
            # get the index of path name
            listindex = dirlist.index(file)
            # change the path to full pathname
            dirlist[listindex] = parent + file

    # if human readable filesize
    if opts.isRead == True:
        for file in dirlist:
            # get the index of path name
            listindex = dirlist.index(file)
            # convert to kilob
            filesize = path.getsize(file) / convertsize
            print('{:<20}{:>30.2f} kb'.format(file, filesize))
            dirlist[listindex] = filesize
    return dirlist

def ListFactory(args, options):
    ''' adds current dir as arg if no arg present '''
    dirlist = []
    if len(args) < 1:
        args.append('.')
    dirlist = List_Dir(args[0], options)
    return dirlist

def Mk_Dir(args):
    ''' makes a directory '''
    path = args[0]
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def Change_Dir(args):
    ''' changes to a direct '''
    if len(args) == 0:
        return (Print_Dir())
    else:
        path = args[0]
        try:
            os.chdir(path)
            return (Print_Dir())
        except:
            return("Invalid path name")
    return

def Print_Dir():
    ''' Prints the current directory '''
    try:
        path = os.getcwd()
        return path
    except:
        return ("Invalid path")

def Remove_Dir(args):
    ''' Removes a directory '''
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
    ''' Removes a path '''
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
    ''' moves path to specified dir '''
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
    ''' copies file to specified path '''
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
    ''' display contents of file '''
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
    ''' display first few lines of file '''
    path = args[0]
    data = []
    try:
        if os.path.exists(path):
            with open(path, 'r') as temp:
                try:
                    rawdata = temp.read()
                    lines = rawdata.splitlines()
                    for i in range(0, 3):
                        data.append(lines[i])
                        print(lines[i])
                except:
                    pass
            temp.close()
            return data
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Tail_File(args):
    ''' display last few lines of file '''
    path = args[0]
    data = []
    try:
        if os.path.exists(path):
            with open(path, 'r') as temp:
                try:
                    rawdata = temp.read()
                    lines = rawdata.splitlines()
                    lastelm = len(lines)
                    for i in range(lastelm-3, lastelm):
                        data.append(lines[i])
                        print(lines[i])
                except:
                    pass
            temp.close()
            return data
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Less_File(args):
    ''' show contents of file at a page at a time '''
    path = args[0]
    try:
        if os.path.exists(path):
            with open(path, 'r') as temp:
                # try to display contents at 2048 bytes at a time
                try:
                    # http://stackoverflow.com/questions/1752107/how-to-loop-until-eof-in-python#1752208
                    for block in iter(lambda: temp.read(2048), ""):
                        print(block)
                        usrprompt = raw_input("Press 'enter' for next page ('q' to quit)")
                        if usrprompt == 'q':
                            return
                # if file is not bigger than 2048 bytes, just display whole file
                except:
                    View_File(path)
            temp.close()
            return
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Word_Count(args):
    ''' display number of lines/words/chars '''
    path = args[0]
    try:
        if os.path.exists(path):
            line_length = 0
            word_length = 0
            char_length = 0
            stats = []
            with open(path, 'r') as temp:
                # read file
                rawdata = temp.read()
                # make list of lines
                lines = rawdata.splitlines()
                # count lines
                line_length = len(lines)
                # make list of words
                words_split = rawdata.split()
                # count words
                word_length = len(words_split)
                # get number of chars then subtract carriage returns
                char_length = temp.tell() - (line_length) -1
            temp.close()
            stats = [line_length, word_length, char_length]
            return stats
        else:
            return("Source path does not exist")
    except:
        return("Could NOT read file")
    return

def Get_Who():
    ''' display current user '''
    try:
        # http://computer-programming-forum.com/56-python/3fc3d4036df2cc9a.htm
        user = os.environ["USER"]
        return user
    except:
        return("Totes being H@(ked")
    return

def GREP(args):
    ''' search path contents for keyword '''
    keyword = args[0]
    path = args[1]
    try:
        if os.path.exists(path):
            with open(path, 'r') as temp:
                filestream = temp.read()
                file_parsed = filestream.split()
                if keyword in file_parsed:
                    return True
                else:
                    return False
            temp.close()
        else:
            return ("Source path not found")
    except:
        return ("Could NOT read file")
    return

def Sort_List(args):
    ''' sort data in path '''
    unsorted_list = args
    try:
        return sorted(unsorted_list)
    except:
        return("Could NOT sort array")
    return

def CHMOD(args):
    ''' changes permission of file '''
    global permissions
    path = args[0]
    mode = args[1]
    try:
        perm = permissions[mode]
        if os.path.exists(path):
            os.chmod(path, perm)
            return ("Permission change succesful")
        else:
            return("Path Does Not Exist")
    except:
        return("Invalid permission mode. See permission dictionary at line 23")
    return

def _WorkLoop(split_cmd):
    ''' the main loop which processes the command '''
    (options, args) = ParseCmd(split_cmd)
    result = None
    mode = None
    dest = None
    try:
        spec = argspec[args[0]]
    except:
        print("Not a valid command")
        return
    if '<' in args:
            args = FromFile(args)
    if '>>' in args:
        dest = args[args.index('>>')+1]
        mode = ('a')
        args = args[:args.index('>>')]
    elif '>' in args:
        dest = args[args.index('>')+1]
        mode = ('w')
        args = args[:args.index('>')]

    arglen = len(args)
    if args[0] == 'ls':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = ListFactory(args[1:], options)
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'mkdir':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Mk_Dir(args[1:])
        else:
            print('ERROR: invalid args {}'.format(args))
            return
    if args[0] == 'cd':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Change_Dir(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'pwd':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Print_Dir()
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'rmdir':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Remove_Dir(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'rm':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Remove_Path(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'cp':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Copy_Path(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'mv':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Move_Path(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'cat':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = View_File(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'head':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Head_File(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'tail':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Tail_File(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'less':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Less_File(args[1:])
            return
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'wc':
        if arglen >= spec['min'] and arglen <= spec['max']:
            stats = Word_Count(args[1:])
            print("Lines = {:>30}\nWords = {:>30}\nChars = {:>30}".format(stats[0], stats[1], stats[2]))
            return
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'grep':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = GREP(args[1:])
            result = ("{} matched: {}".format(args[1], result))
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'who':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = Get_Who()
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'sort':
        if arglen >= spec['min']:
            result = Sort_List(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if args[0] == 'history':
        for i, command in enumerate(history):
            result.append(command)
            print('{}. {}'.format(i, command))
    if args[0] == 'chmod':
        if arglen >= spec['min'] and arglen <= spec['max']:
            result = CHMOD(args[1:])
        else:
            print('ERROR: invalid args')
            return
    if mode != None:
        ToFile(result, mode, dest)
    elif result != None:
        print(result)
    return result

def Replay(raw_cmd):
    ''' re-executes a previously entered command '''
    match = re.match(r'^!', raw_cmd)
    # if there is a ! replay the command
    if match != None:
        hist = raw_cmd.split()
        hist_cmd = hist[0].split('!')
        hist_index = hist_cmd[1]
        hist_index = int(hist_index)
        replay = history[hist_index]
        print(replay)
        return replay
    else:
        return raw_cmd

def Run_Loop(raw_cmd):
    ''' prepares the command for execution '''
    status = LOOP_STATUS_GO
#   make a child process
    pid = os.fork()
    if pid == 0:
        if '|' in raw_cmd:
            try:
                newcmd = []
                pipedcmd = raw_cmd.split('|')
                split_cmd = pipedcmd[0].split()
                nextcmd = _WorkLoop(split_cmd)
                del pipedcmd[0]
                newcmd = nextcmd.split()
                print("piped is {}".format(pipedcmd))
                pipedcmd.extend[newcmd]
                Run_Loop(pipedcmd)
            except:
                print("function does not support piping")

        elif 'exit' in raw_cmd:
            status = LOOP_STATUS_STOP
        else:
                # if list of commands (ie from piped or file)
                if type(raw_cmd) == list:
                    for item in raw_cmd:
                        cmd = Replay(item)
                        split_cmd = cmd.split()
                        _WorkLoop(split_cmd)
                # if single command
                else:
                    cmd = Replay(raw_cmd)
                    split_cmd = cmd.split()
                    _WorkLoop(split_cmd)
    elif pid > 0:
        while True:
            wpid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break
    return status

def shell_loop():
    #   Start looping
    status = LOOP_STATUS_GO

    while status == LOOP_STATUS_GO:
        #   Display a cmd
        sys.stdout.write('BAD A$$ SHELL:> ')
        sys.stdout.flush()
        #   Get user command
        raw_cmd = sys.stdin.readline()
        #   store in history
        history.append(raw_cmd)
        #   Run command
        status = Run_Loop(raw_cmd)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
