#! /usr/bin/python3

##############################################################################
## Copyright 2019 Christopher Bickhaus										##
##																			##
## Licensed under the Apache License, Version 2.0 (the "License");			##
## you may not use this file except in compliance with the License.			##
## You may obtain a copy of the License at									##
##																			##
##     http://www.apache.org/licenses/LICENSE-2.0 							##
##																			##
## Unless required by applicable law or agreed to in writing, software		##
## distributed under the License is distributed on an "AS IS" BASIS,		##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.	##
## See the License for the specific language governing permissions and		##
## limitations under the License.											##
##############################################################################


import os
import argparse
import subprocess
from pathlib import Path
from sys import exit
from shlex import quote

###############
## CONSTANTS ##
###############

CMD_FILE_LOC = '/home/{0}/.cmdCache'.format(os.getlogin())
EMPTY_FILE_MSG = ("\nYou have not yet stored any favorite commands."
				 + "  Add your favorite commands to: \n\n\t{0}\n\n".format(CMD_FILE_LOC)
				 + "Each command should be on its own line with no other text or formatting.")


##########################
## Create CLI interface ##
##########################

parser = argparse.ArgumentParser()
options = parser.add_mutually_exclusive_group()
options.add_argument('-a', '--append', action='store_true', help='appends specified command to list')
options.add_argument('-r', '--remove', action='store_true', help='removes specified command from list')
parser.add_argument('command', nargs='?', default=None, 
					help='leave blank to print saved command list, specify number to retrieve command')
args = parser.parse_args()        


########################
## Helper Function(s) ##
########################

def create_cmd_obj(file_loc, msg):
	'''
	Input: file containing stored commands, message to print if file not found
	Return: If a populated file is found at file_loc, returns commandCache object, 
	otherwise exits program
	'''
	try: 
		cmd_dict = {}
		cmd_num = -1

		with open(file_loc, 'r') as f:
			for line in f:
				cmd_num += 1
				cmd_dict[cmd_num] = line.rstrip()
		
		# Makes sure at least one command was saved in file_loc, unless user trying to add command
		if cmd_num == -1 and not args.append:
			raise ValueError

	# If file not found or empty: touch file, direct user to populate, exit
	except (FileNotFoundError, ValueError):
		Path(file_loc).touch()
		print(msg)
		exit()

	return commandCache(cmd_dict, cmd_num, file_loc)


###############
## Class(es) ##
###############

class commandCache():
	''' Facilitates viewing stored commands, as well as adding, deleting or running a command
	'''
	def __init__(self, cmd_dict, highest_cmd, file_loc):

		self.cmd_dict = cmd_dict        
		self.highest_cmd = highest_cmd
		self.file_loc = file_loc

	def valid_cmd(self, command):
		''' Input: command number
			Return: True if given a valid command number
			Checks to see whether a proper command number was given
		'''
		try:
			command = int(command)
			if command < 0 or command > self.highest_cmd:
				raise ValueError
		except (TypeError, ValueError):
			print("You must enter the number of a valid command (0-{0})".format(self.highest_cmd))
			exit()

		return True

	def appendCommand(self, to_append):
		''' Input: command (string) to append to file
			Return: None
			Appends given string to CMD_FILE_LOC
		'''
		print("Appending command {0}: {1}".format((self.highest_cmd + 1), to_append))

		with open(self.file_loc, 'a') as f:
			f.write(to_append + "\n")		

	def removeCommand(self, to_delete):
		''' Input: number of command to delete
			Return: None
			Deletes the specified command
		'''		
		if self.valid_cmd(to_delete):
			to_delete = int(to_delete)

		print("Deleting command {0}: {1}...".format(to_delete, self.cmd_dict[to_delete]))
		
		idx = 0
		with open(self.file_loc, 'r') as f:
			with open('tmp', 'w') as new_f:
				for line in f:
					if idx != to_delete:
						new_f.write(line)
					idx += 1
		os.replace('tmp', self.file_loc)			
				
	def runCommand(self, to_run):
		''' Input: number of command to run 
			Return: None
			Runs the specified command and prints STDOUT to terminal
		'''

		if self.valid_cmd(to_run):
			to_run = int(to_run)

		cmd = self.cmd_dict[to_run]

		print('Running command {0}: {1}...\n'.format(to_run, cmd))
		out = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
		print(out.stdout)
	
	def __str__(self):
		'''Return: formatted string representation of commands in CMD_FILE_LOC: Command#    Command
		'''
		cmd_list_str = "\n\nCommand#\tCommand\n-------------------------------\n"
		
		for key, value in sorted(self.cmd_dict.items()):
			cmd_list_str += str(key) + "\t\t" + value + "\n"
			
		return cmd_list_str + "\n"


#######################
## Main Script Logic ##
#######################

cmd_cache = create_cmd_obj(CMD_FILE_LOC, EMPTY_FILE_MSG)

# Run appropriate method based on CLI positional arg and flags
if args.append:
	cmd_cache.appendCommand(args.command)
elif args.remove:
	cmd_cache.removeCommand(args.command)
elif args.command is None:
	print(cmd_cache)
else:
	cmd_cache.runCommand(args.command)
