#!/usr/bin/env
__author__ = 'marcsantiago'
import os

def fastafiles_exist():
    """Ensures that the folder fastafiles has been created of exists"""
    if os.path.exists('fastafiles'):
        return True
    else:
        return False


def get_file_names():
    """Grabs each file from the folder fastafiles and yields one at a time (generator)"""
    assert fastafiles_exist(),\
        '''The directory 'fastafile' does not exist or is not in the same directory as python script'''
    for i in os.listdir('fastafiles'):
        if i.endswith('.fasta'):
            yield i


def clean_fasta_files():
    """Appends the associated name of the organism to the comp output file name and adds a > to the front for a proper
    fasta file"""
    for files in get_file_names():
        path = 'fastafiles/' + files
        with open(path, 'r') as fasta_read:
            file = fasta_read.read().replace('comp', '>' + files + '_comp')

        finish_path = 'fastafiles/' + files.replace('Done', 'Clean')
        with open(finish_path, 'w') as fasta_write:
            fasta_write.write(file)
        os.remove(path)

