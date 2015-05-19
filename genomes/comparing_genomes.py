#!/usr/bin/env python
__author__ = 'marc santiago'
import csv
import argparse
import re

from itertools import izip


# methods for quick string replacements vs replace().replace()... 
def multiple_replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)


parser = argparse.ArgumentParser(description='Comparing Genomes Out File Generator')
parser.add_argument('-f', '--file', help='opens input file', required=True)
parser.add_argument('-v', '--verbose', help='Writes an outfile that Includes GeneID', default=False)
parser.add_argument('-x', '--filter', help='Filters file based on supplied orthologs, e.g. 1:2', default=False)
args = vars(parser.parse_args())

if args['file']:
    with open(args['file'], 'rU') as in_data:
        spam_reader = csv.reader(in_data, delimiter='\t', quotechar='#')
        spam_to_list = list(spam_reader)[2:]
        first_col = []  # protein 1 / ID
        second_col = []  # protein 2
        third_col = []  # gene name data
        forth_col = []  # gene name data

        for row in spam_to_list:
            first_col.append(row[0])
            second_col.append(row[1])
            third_col.append(row[2])
            forth_col.append(row[3])

    # if len(first_col) != len(second_col): # Error check to make sure list lengths are the same ###Redundant 
    # raise IndexError("Column 1 and Column 2 weren't the same length, please check the file.")
    # [(ID, number of protein2 duplicates), number of ID duplicates] --> 
    # index[i]0 = ID, index[i][1] = protein2 duplicates, index[i][2] = protein1 duplicates
    mapped_data = []
    for index in xrange(len(first_col)):
        if (
                first_col[index], second_col.count(second_col[index]), first_col.count(first_col[index])) not in mapped_data:
            mapped_data.append((first_col[index], second_col.count(second_col[index]),
                                first_col.count(first_col[index])))

    # returns a file with id number and protein duplicate ratio
    if args['verbose']:
        with open('out_verbose.txt', 'w') as out_data:
            for i in xrange(len(mapped_data)):
                out_data.write(
                    "Id={0}\t{1}: {2}".format(mapped_data[i][0], mapped_data[i][1], mapped_data[i][2]) + "\n")

    # returns a file with the protein duplicate ratio
    else:
        with open('out.txt', 'w') as out_data:
            for i in xrange(len(mapped_data)):
                out_data.write("{0}: {1}".format(mapped_data[i][1], mapped_data[i][2]) + "\n")

    # returns a file with containing 3 columns, [Protein1/ID, gene name 1, gene name 2, protein1:protein2 ratio]
    if args['filter']:
        key = str(args['filter'])
        gene_map = zip(third_col, forth_col)
        gene_map = dict(izip(first_col, gene_map))
        with open('filtered_data.txt', 'w') as filtered_data:
            for k, v in gene_map.items():
                for j in xrange(len(mapped_data)):
                    if k == mapped_data[j][0]:
                        num = "{0}:{1}".format(mapped_data[j][1], mapped_data[j][2])
                        if key == num:
                            filtered_data.write("{0}\t{1}\t{2}".format(mapped_data[j][0],
                                                                       multiple_replace(str(v), ["(", ""], [")", ""],
                                                                                        ["'", ""], [", ", "\t"]),
                                                                       num + "\n"))
