#!/usr/bin/env python
__author__ = 'marc santiago'
import csv
import argparse

from datetime import datetime
from os import listdir, getcwd, path, makedirs
from itertools import izip


# this method checks to see what column the reference data is
# the method also assumes that your looking at a file that isn't 1:1 orthology
def check_filtered_file(filtered_data_file):
  print('Checking to see which column the reference data is in')
  with open(filtered_data_file) as filtered_data:
    filtered_data_to_list = []
    for col in filtered_data.readlines():
      row_split = col.split('\t')
      filtered_data_to_list.append(row_split)

  col2 = 0
  col3 = 0 
  ref2 = filtered_data_to_list[0][1]
  ref3 = filtered_data_to_list[0][2]
  for i in xrange(len(filtered_data_to_list)):
    if filtered_data_to_list[i][1] == ref2:
      col2 += 1
    if filtered_data_to_list[i][2] == ref3:
      col3 += 1

  if col2 > col3:
    print('Check complete, column found')
    return False

  print('Check complete, column found')
  return True

# this method retrieves the reference gene and the other genes
# paired with the reference gene from the filtered.txt file 
def retrieve_filtered_file_data(filtered_data_file):
  with open(filtered_data_file) as filtered_data:
    print('Filtered_data.txt file open')
    print('Creating base list...please wait')
    
    filtered_data_to_list = []
    for col in filtered_data.readlines():
      row_split = col.split('\t')
      filtered_data_to_list.append(row_split)

    reference_names = []
    reference_names_list = []
    if check_filtered_file(filtered_data_file):
      for i in filtered_data_to_list:
        reference = i[2]
        reference_names.append(reference)
        for j in filtered_data_to_list:
          if j[2] == reference:
            reference_names.append(j[1])
        reference_names_list.append(reference_names)
        reference_names = []
    else:
      for i in filtered_data_to_list:
        reference = i[1]
        reference_names.append(reference)
        for j in filtered_data_to_list:
          if j[1] == reference:
            reference_names.append(j[2])
        reference_names_list.append(reference_names)
        reference_names = []
    print('Base list create')
    return reference_names_list

# returns a list of file names from the working directory
def retrieve_pairwise_files():
  print('Retrieving pairwise file names')
  f = listdir(getcwd())
  f = [i for i in f if str(i).endswith('txt') and i != 'filtered_data.txt' and i != 'out.txt' and i != 'all_data.txt' and i != 'out_verbose.txt']
  print('Pairwise file names retrieved')
  return f

# returns a list of file names from the Genomes directory
def retrieve_genome_files():
  print('Retrieving genome file names')
  try:
    f = listdir(getcwd() + "/Genomes")
  except IOError:
    print('Please make sure that the genome/fasta files are in a directory labeled Genomes')
  
  print('Genomes file names retrieved')
  return ['Genomes/' + str(i) for i in f]


# goes through each pairwise file and grabs the rest of the genes based on the reference gene
# the reference gene is the first element in the 2d list created with the open_filtered_file method
# note, the genes are appended to the list. The format is taxa not >taxa
def generate_master_reference_list(filtered_data_file):
  base_list = retrieve_filtered_file_data(filtered_data_file)
  pairwise_files = retrieve_pairwise_files()
  print('Creating master list, this step will take a while, please wait...')
  for i in xrange(len(base_list)):
    reference = base_list[i][0]
    
    for f in pairwise_files:
      with open(f, 'rU') as file_data:
        spam_reader = csv.reader(file_data, delimiter='\t', quotechar='#') 
        spam_to_list = list(spam_reader)[2:]  # skip commented lines in file
        
        for row in spam_to_list:  
          if reference in row[2]:
            if row[3] not in base_list[i]:
              base_list[i].append(row[3].strip())
          elif reference in row[3]:
            if row[2] not in base_list[i]:
              base_list[i].append(row[2].strip())

  base_list = set(tuple(element) for element in base_list)  
  base_list = [list(t) for t in set(tuple(element) for element in base_list)]
  print('Master list created')
  return base_list


# goes through each fasta file inside the Genomes directory and maps gene names sequences
def generate_master_sequence_dictionary():
  ids = []
  sequences = []
  genome_files = retrieve_genome_files()
  print('Creating a dictionary of genes and their sequences')
  for f in genome_files:
    with open(f, 'r') as genome:
      for line in genome.readlines():
        if line.startswith('>'):
          ids.append(line[1:].strip())
        else:
          sequences.append(line.strip())
  print('Gene dictionary created')
  return dict(izip(ids, sequences))   


# using both the master reference list and gene dictionary a file is written for each reference
def generate_sequence_files(filtered_data_file):
  master_list = generate_master_reference_list(filtered_data_file)
  gene_dictionary = generate_master_sequence_dictionary()

  time_stamp = str(datetime.now().strftime("%y%m%d_%H%M%S"))
  folder_name = "_".join(['Genomes_Out_Files', time_stamp])

  if not path.exists(folder_name):
    makedirs(folder_name)
   
  print('Creating sequences files, this may take a while, please wait...')
  count = 0
  for filename in master_list:
    with open(folder_name + '/' + str(filename[0]) + '.fa', 'w') as seq_data:
      for k, v in gene_dictionary.items():
        for i in master_list[count]:
          if k == i:
            seq_data.write('>' + str(k) + '\n' + str(v) + '\n')
    count += 1

  print 'Done, check the {0} folder'.format(folder_name)


parser = argparse.ArgumentParser(description='Pairwise to Fasta File Generator, '
                       'Note the program does not work with pairwise 1:1')
parser.add_argument('-f',  '--file', help='Opens a filter_data.txt file, which is generated using'
                      ' comparing_genomes.py', required=True)
args = vars(parser.parse_args())

if args['file']:
  generate_sequence_files(args['file'])
