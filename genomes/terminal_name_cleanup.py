#!/usr/bin/env python
__author__ = 'marc santiago'
import re
import os
import argparse


def check_folder_exist(folder):
  if os.path.exists(folder):
    return True
  else:
    return False

parser = argparse.ArgumentParser(description='clean up select files')
parser.add_argument('-f',  '--file', help='cleans up one file')
parser.add_argument('-d',  '--directory', help='cleans up a directory of files')

args = vars(parser.parse_args())


if args['file']:
  new_file = []
  with open(args['file'], 'r') as indata:
    for line in indata.readlines():
      if line.startswith('>'):
        m = re.search(r'>[^ | \n]+(.*)', line)
        if m:
          #terminal_name = re.sub(m.group(1), '', line)
          terminal_name = line.replace(m.group(1), '')
        else:
          terminal_name = line
        new_file.append(terminal_name)
      else:
        new_file.append(line)
  with open(args['file'], 'w') as out:
     out.write(''.join(new_file))

if args['directory']:
  file_paths = []
  assert check_folder_exist(args['directory']),\
  '''The Folder Entered Was Not Found, check spelling or path, usage: python clean_fas_seq.py folder_name'''
  for files in os.listdir(args['directory']):
    path = args['directory'] + "/" + files
    file_paths.append(path)

  for file in file_paths:
    new_file = []
    with open(file, 'r') as indata:
      for line in indata.readlines():
        if line.startswith('>'):
          m = re.search(r'>[^ | \n]+(.*)', line)
          if m:
            #terminal_name = re.sub(m.group(1), '', line)
            terminal_name = line.replace(m.group(1), '')
          else:
            terminal_name = line
          new_file.append(terminal_name)
        else:
          new_file.append(line)
    with open(file, 'w') as out:
       out.write(''.join(new_file))
