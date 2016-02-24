#!/usr/bin/env python2.7
__author__ = 'marc santiago'
import sys
import os


class taxa_list:
  '''Creates a list of taxa from a file containing the full list of taxa in question.'''
  taxalist = list()
  def __init__(self, taxa_list_file):
    self.taxa_list_file = taxa_list_file
    if os.path.isfile(taxa_list_file):
      try:
        with open(self.taxa_list_file, 'r') as taxa:
          self.taxalist = taxa.readlines()
      except EOFError:
        print("Error Has Occured")
    else:
      print("The file entered does not exist")
      print('List is empty, either the file name is wrong or there is no data in the file')
      raw_input('press any key to exit')
      sys.exit(1)

  def returnlist(self):
    print("Full Taxa List Uploaded")
    tlist = [str(i).strip() for i in self.taxalist]
    return tlist


class gene_folder:
  file_list = list()
  def __init__(self):
    if not os.path.exists('Gene_Folder'):
      os.makedirs('Gene_Folder')
    print("Please Place all Gene Files into Gene_Folder, which was created if it didn't exist already")
    self.ready = raw_input("When you are ready type [c] to continue or [q] to quit \t")
    while self.ready == 'c' or self.ready == 'q':
      if self.ready == 'q':
        break
      for i in os.listdir('Gene_Folder'):
        if i != '.DS_Store':
          self.file_list.append(i)
      break

  def returnlist(self):
    return self.file_list

