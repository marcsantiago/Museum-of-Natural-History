#!/usr/bin/env python
import csv
import argparse

__author__ = 'marcsantiago'

parser = argparse.ArgumentParser(description='Comparing Genomes Out File Generator')
parser.add_argument('-f',  '--file', help='opens input file', required=True)
parser.add_argument('-v', '--verbose', help='Writes an outfile that Includes GeneID', default=False)
args = vars(parser.parse_args())

if args['file']:
	with open(args['file'], 'rU') as indata:
		spamreader = csv.reader(indata, delimiter='\t', quotechar='#')
		spam_to_list = list(spamreader)[2:]
		first_col = []
		second_col = []
		for row in spam_to_list:
			first_col.append(row[0])
			second_col.append(row[1])

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
