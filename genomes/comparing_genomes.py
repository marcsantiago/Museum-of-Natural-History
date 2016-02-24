#!/usr/bin/env python
__author__ = 'marc santiago'

import csv
import argparse
import re

from itertools import izip


def multiple_replacer(*key_values):
  replace_dict = dict(key_values)
  replacement_function = lambda match: replace_dict[match.group(0)]
  pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
  return lambda string: pattern.sub(replacement_function, string)

def multiple_replace(string, *key_values):
  return multiple_replacer(*key_values)(string)


parser = argparse.ArgumentParser(description='Comparing Genomes Out File Generator')
parser.add_argument('-f',  '--file', help='opens input file', required=True)
parser.add_argument('-v', '--verbose', help='Writes an outfile that Includes GeneID', default=False)
parser.add_argument('-x', '--filter', help='Filters file based on supplied orthologs, e.g. 1:2', default=False)
parser.add_argument('-a', '--all', help='Reformats file to show all orthologs e.g, 1:1, 1:2, 1:3. etc', default=False)


args = vars(parser.parse_args())

if args['file']:
  with open(args['file'], 'rU') as indata:
    spamreader = csv.reader(indata, delimiter='\t', quotechar='#')
    spam_to_list = list(spamreader)[2:]
    first_col = []
    second_col = []
    third_col = []
    forth_col = []
    for row in spam_to_list:
      first_col.append(row[0])
      second_col.append(row[1])
      third_col.append(row[2])
      forth_col.append(row[3])

  if len(first_col) != len(second_col):
    raise IndexError("Column 1 and Column 2 weren't the same length, please check the file.")

  mapped_data = []
  for index in xrange(len(first_col)):
    if (first_col[index], second_col.count(second_col[index]), first_col.count(first_col[index])) not in mapped_data:
      mapped_data.append((first_col[index], second_col.count(second_col[index]), first_col.count(first_col[index])))

  if args['verbose']:
    with open('out_verbose.txt', 'w') as outdata:
      for i in xrange(len(mapped_data)):
        outdata.write("Id={0}\t{1}: {2}".format(mapped_data[i][0], mapped_data[i][1], mapped_data[i][2]) + "\n")

  else:
    with open('out.txt', 'w') as outdata:
      for i in xrange(len(mapped_data)):
        outdata.write("{0}: {1}".format(mapped_data[i][1], mapped_data[i][2]) + "\n")

  if args['filter']:
    key = str(args['filter'])
    genemap = zip(third_col, forth_col)
    genemap = dict(izip(first_col, genemap))
    with open('filtered_data.txt', 'w') as filtered_data:
      for k, v in genemap.iteritems():
        for j in xrange(len(mapped_data)):
          if k == mapped_data[j][0]:
            num = "{0}:{1}".format(mapped_data[j][1], mapped_data[j][2])
            if key == num:
              filtered_data.write("{0}\t{1}\t{2}".format(mapped_data[j][0],
              multiple_replace(str(v), ["(", ""], [")", ""], ["'", ""], [", ", "\t"]), num + "\n"))

  if args['all']:
    genemap = zip(third_col, forth_col)
    genemap = dict(izip(first_col, genemap))
    with open('all_data.txt', 'w') as filtered_data:
      for k, v in genemap.iteritems():
        for j in xrange(len(mapped_data)):
          if k == mapped_data[j][0]:
            num = "{0}:{1}".format(mapped_data[j][1], mapped_data[j][2])
            filtered_data.write("{0}\t{1}\t{2}".format(mapped_data[j][0],
            multiple_replace(str(v), ["(", ""], [")", ""], ["'", ""], [", ", "\t"]), num + "\n"))
