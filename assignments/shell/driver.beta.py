#!/usr/bin/env python

import sys
import os
import re

#==========================================================================

class CMD:

    def __init__(self, cmd_raw):
    #   holds the command string
        self.cmd = ''
    #   holds all the user requested options in an array
        self.options = []
    #   holds the entire string of commands partitiond in an array
        self.args = []
    #   finds the target arg
        self.target = ''
    #   a flag that specifies if the command is valid (default = False)
        self.cmd_valid = False
    #   a flag that specifies if command is being piped
        self.piped = False
        self._isPiped()

    #   split the raw string into array
        self.args = str.split(cmd_raw)

    #   set the command var by grabbing 1st element of args
        self.cmd = self.args[0]
    #   find all options in the argument array
        self.options = re.findall(r'(-[lsh]+)+', cmd_raw)

    #   finds the target arg by finding the difference between sets
        self.__target_set = (set(self.args) - set([self.cmd] + self.options))
    #   converts the set to a list
        self.target = list(self.__target_set)

    #   **DEBUG**
        print ('Target = {}'.format(self.target))
    #   validate the command
        self.Validate()
        return

    def _isPiped(self):
        if '|' in self.args:
            self.piped = True
            # DEBUG
            print ('Its PIPED')
        matches = [i for i, x in enumerate(self.args) if x == '|']
        return len(matches) - 1

    def Validate(self):
        if ((self.cmd == 'ls') or (self.cmd == 'mkdir') or (self.cmd == 'cd')):
    #       after ommiting the options, we still have a command and a path
            if ( (len(self.args) - len(self.options)) == 2 ):
                self.cmd_valid = True
    #           **DEBUG**
                print (self.ToString())
    #       if no options or target specefied
            elif ((len(self.options) + len(self.target) == 0) and (self.cmd == 'ls')):
                self.cmd_valid = True
    #           **DEBUG**
                print (self.ToString())

            else:
                self.cmd_valid = False
    #           **DEBUG**
                print ('INVALID SYNTAX')
        else:
    #       **DEBUG**
            print ('COMMAND NOT VALID')
            return

    def ToString(self):
    #   return data dump
        return ('\nCOMMAND STASTICIS:\ncommand = {}\noptions = {}\nargs count = {}\nargs = {}\nisValid = {}\n'.format(self.cmd,self.options,len(self.args),self.args, self.cmd_valid))

#==========================================================================

#   Loop flags
LOOP_STATUS_GO = 1
LOOP_STATUS_STOP = 0

def List_Dir(cmd):
    output = []
    # if no target make current dir default target
    if len(cmd.target) == 0:
        dirlist = os.listdir('.')
    # if index 1 is an option param
    elif len(cmd.options) > 0:
        dirlist = os.listdir( cmd.target[0] )
    # if no option params
    else:
        dirlist = os.listdir( cmd.target[0] )

    # print list of files and directories
    print ("\nThe listing for specified directory is: ")
    for file in dirlist:
        output.append(file)
    return output

def Mk_Dir(cmd):
    # if one target make one dir
    if len(cmd.target) == 1:
        os.mkdir(cmd.target[0])
    else:
        print('TARGET DESTINATION ERROR')
    return

def Chg_Dir(cmd):
    if len(cmd.options) == 0:
        if len(cmd.target) == 0:
            os.chdir('~/')
        elif len(cmd.target) == 1:
            if cmd.target[0] == '..':
                os.chdir('..')
            else:
                os.chdir(cmd.target[0])
        else:
            print('TARGET DESTINATION ERROR')
    else:
        print('SYNTAX ERROR')
    return

def Print_Dir(cmd):
    if len(cmd.args) == 1 and len(cmd.cmd) > 0:
        return os.curdir
    else:
        print('SYNTAX ERROR')
    return 'SYNTAX ERROR'

def Run_Cmd(command):
#   make a child process
    pid = os.fork()
    if pid == 0:
#       if self is a child process
        if command.cmd == 'ls':
#           runs the specified cmd
            ary = List_Dir(command)
            for i in ary:
                print (i)
        elif command.cmd == 'mkdir':
            Mk_Dir(command)
        elif command.cmd == 'cd':
            Chg_Dir(command)
        elif command.cmd == 'pwd':
            Print_Dir(command)

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
        command = sys.stdin.readline()
        command = CMD(command)

        #   Run command
        status = Run_Cmd(command)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
