#!/usr/bin/env python2.7
__author__ = 'marcsantiago'
from taxa_class import taxa_list
from taxa_class import gene_folder
import sys
import os

'''Usage python main.py [full_taxon_list.txt] the file between the brackets can have any name.txt'''
#assign the second parameter to the filename

try:
    from prettytable import PrettyTable
except:
    print("PrettyTable package is missing from your python installation")
    install = raw_input("To install package type [c]\t")
    if install.lower() == 'c':
        os.system("sudo easy_install prettytable")
        print("Re-run python script after installation")
        raw_input("Press any key to exit")
        sys.exit(1)
    else:
        print("Cannot continue with installing the program")
        print("Here is the package source \n https://code.google.com/p/prettytable/")
        os.system("open https://code.google.com/p/prettytable/")
        print("Re-run python script after installation")
        raw_input("Press any key to exit")
        sys.exit(1)


full_taxa_list_file = sys.argv[1]

#instantiate full taxon list object
full_taxa_list = taxa_list(full_taxa_list_file)
full_taxa_list = full_taxa_list.returnlist()
full_taxa_list = sorted(full_taxa_list)

#list of files from the Gene_Folder
files_from_gene_folder = gene_folder()
files_from_gene_folder = files_from_gene_folder.returnlist()
copy_files_from_gene_folder = [str(i).replace('.txt', '') for i in files_from_gene_folder]  #names without path for column headers
files_from_gene_folder = ['Gene_Folder/' + str(i) for i in files_from_gene_folder]

#create table object
table = PrettyTable(['Taxa'])

#master list holds the gene matrix data file in order of gene file input
master_character_list = list()
for file in files_from_gene_folder:
    character = list()
    with open(file, 'r') as genefile:
        taxon = genefile.readlines()
        taxa = [str(i).strip() for i in taxon]
        taxa = sorted(taxa)
        for org in full_taxa_list:
            if org in taxa:
                character.append(1)
            else:
                character.append(0)
    master_character_list.append(character)

#create taxa column
for num in xrange(len(full_taxa_list)):
    table.add_row([full_taxa_list[num]])

#create columns for each gene
for col in xrange(len(master_character_list)):
    table.add_column(copy_files_from_gene_folder[col], master_character_list[col])

#table.set_style(PLAIN_COLUMNS)
table.align = "l"

#create table with borders
############################################################
with open('table_matrix_dirty.txt', 'w') as outfile:
    outfile.write(str(table))
with open('table_matrix_dirty.txt', 'r') as dirty_matrix:
    dirty_file = dirty_matrix.read()
dirty_file = str(dirty_file)
############################################################

#reformat bordered file for tab delimited and csv file types
############################################################
dirty_file = dirty_file.replace("+", '').replace(' ', '').replace("|", "\t").replace("-", "")
with open("table_matrix_clean.txt", 'w') as clean:
    clean.write(dirty_file)
with open("table_matrix_clean.txt", 'r') as cleand:
    f = list()
    for lin in cleand.readlines():
        f.append(lin.lstrip())
############################################################

#create tab delimited file
############################################################
with open("table_matrix_tab.txt", 'w') as w:
    for i in f:
        w.write(str(i))
############################################################

os.remove('table_matrix_clean.txt')  #remove unformatted matrix file

#create cvs file
############################################################
with open("table_matrix_tab.txt", 'r') as r:
    dirty_file = r.read().replace('\t', ",")

with open("table_matrix_clean.csv", 'w') as cleancvs:
    cleancvs.write(dirty_file)
############################################################
