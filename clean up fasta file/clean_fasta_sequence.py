#! /urs/bin/env python2.7
__author__ = 'marcsantiago'
import os
import sys

start_folder = sys.argv[1]


if not os.path.exists('Cleaned Fasta Files'):
    os.makedirs('Cleaned Fasta Files')


def check_folder_exist(folder):
    if os.path.exists(folder):
        return True
    else:
        return False


def get_files():
    """Grabs files from input folder"""
    file_path_list = []
    assert check_folder_exist(start_folder),\
    '''The Folder Entered Was Not Found, check spelling or path, usage: python clean_fas_seq.py folder_name'''
    for files in os.listdir(start_folder):
        path = start_folder + "/" + files
        file_path_list.append(path)
    return file_path_list

old_files = get_files()

for f in old_files:
    taxa = []
    protein_seq = []
    with open(f) as data:
        lines = data.readlines()
    for l in lines:
        if l.startswith(">"):
            taxa.append(l)
        else:
            protein_seq.append(l)
    my_dict = dict(zip(taxa, protein_seq))
    new_taxa = []
    new_protein_seq = []
    for k, v in my_dict.items():
        if not v == "\n":
            new_taxa.append(k)
            new_protein_seq.append(v)

    new_file_name = str(f).find("/") + 1

    with open("Cleaned Fasta Files/" + str(f)[new_file_name:], "w") as clean_data:
        for i in xrange(len(new_taxa)):
            clean_data.write(new_taxa[i])
            clean_data.write(new_protein_seq[i])
print("Done, check Cleaned Fasta Files folder")
