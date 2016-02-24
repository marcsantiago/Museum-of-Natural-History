#!/usr/bin/env python2.7
__author__ = 'marc santiago'
import os
def main():
  from parse_outfiles import parse_dot_out_file
  from parse_targets import parse_targets
  from clean_fasta_files import clean_fasta_files
  """This file is intended to utilize functions located in imported files above.  For function documentation view source
  for individual files"""

  if not os.path.exists('fastafiles'):
    os.makedirs('fastafiles')

  if not os.path.exists('junkdata'):
    os.makedirs('junkdata')

  if not os.path.exists('uniquenames'):
    os.makedirs('uniquenames')

  print 'Have you placed all the files in the right folder?'
  print """You should have 2 directories, one named 'Targets' and one names 'outfiles', spelling is important!"""
  print 'Each of those folders should have the same number of items, whose names correspond to' \
      ' each other in alphabetical order'
  print 'Start Program [y, n]'
  start = raw_input()
  if start.lower() == 'y' or 'yes':
    print 'Parsing data from out files...'
    parse_dot_out_file()
    print 'Parsing out files complete.'
    print 'Grabbing sequences from target files.'
    print 'Please be patient, this process may take a few minutes...'
    parse_targets()
    print 'Cleaning up...'
    clean_fasta_files()
    print """Done, to view your files please check the 'fastafiles' directory"""
  elif start.lower() == 'no' or 'n':
    return 0
  else:
    print 'Invalid input'
    return 1

if __name__ in '__main__':
  main() 
