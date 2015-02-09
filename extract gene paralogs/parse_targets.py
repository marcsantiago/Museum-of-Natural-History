#!/usr/bin/env
__author__ = 'marcsantago'
import os
import re


def target_exist():
    """Ensures that the Targets folder exist"""
    if os.path.exists('Targets'):
        return True
    else:
        return False


def get_uniquenames():
    """Yields a file from the uniquenames folder"""
    for i in os.listdir('uniquenames'):
        if i.endswith('.txt'):
            yield i


def get_targets():
    """Yields a file from the Targets folder"""
    assert target_exist(),\
        '''The directory 'Targets' does not exist or is not in the same directory as python script'''
    for i in os.listdir('Targets'):
        if i.endswith('.fasta'):
            yield i


def parse_targets():
    """Compares like files from the uniquenames folder with the data located within the Targets folder"""

    #Creates a list from the file within the Targets folder
    target_file_list = list()
    for targets in get_targets():
        target_file_list.append(targets)

    #Creates a list from the file within the uniquenames folder
    sequence_file_list = list()
    for sequences in get_uniquenames():
        sequence_file_list.append(sequences)

    #Iterates over the number of elements within the target_file_list
    #For each item a file is opened from both the Targets and uniquenames folder and two new list are created
    for index in xrange(len(target_file_list)):
        target_file_path = 'Targets/' + target_file_list[index]
        with open(target_file_path, 'r') as target_file:
            target_list = target_file.read().split('>')
        sequence_file_path = 'uniquenames/' + sequence_file_list[index]
        with open(sequence_file_path, 'r') as sequence_file:
            sequence_list = sequence_file.read().split()

        #If there is a match between an item within the target_list and sequence_list that target item is appended
        #to the file created below
        output_file_name = 'fastafiles/' + str(target_file_list[index]).replace('Trinity', 'Done')
        with open(output_file_name, 'w') as output:
            for tar in target_list:
                for seq in sequence_list:
                    match = re.match(seq, tar)
                    if match:
                        output.write(tar)
