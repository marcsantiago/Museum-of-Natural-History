#!/usr/bin/env python3
__author__ = 'marcsantiago'
import os
import sys
import gc


def gene_position_list(charset_file):
    with open(charset_file, "r") as gene_file:
        gene_data = list(gene_file)

    position_list = []
    master_position_list = []
    for line in gene_data:
        gene_line = str(line).strip()
        find_equal_sign = gene_line.find("=")
        find_minus_sign = gene_line.find("-")
        position_list.append(gene_line[find_equal_sign + 2:find_minus_sign])
        position_list.append(gene_line[find_minus_sign + 2:-1])
        master_position_list.append(position_list)
        position_list = []
    del position_list
    return master_position_list


def format_fasta_file(file_name):
    taxa_list = file_name
    with open(taxa_list, "r") as taxa_file:
        taxa_data = list(taxa_file)

    with open("reformatted_fasta_file.txt", "w") as newFile:
        for line in taxa_data:
            if str(line).startswith('>'):
                newFile.write("\n" + str(line))
            else:
                newFile.write(str(line).strip())
    taxa_file.close()
    newFile.close()

print("Enter the file name containing the character set followed by taxa fasta file.")
print("See example below for proper usage.")
print("python gene_splicer.py SOS_set13_181g_55t.charset SOS_set13_181g_55t.fas")


charset = sys.argv[1]
taxa_file = sys.argv[2]

if not os.path.isfile(charset):
    print("The character set file you have entered was not found.  "
          "Check spelling and or make sure the file is in the same directory as the script")
    sys.exit(1)

if not os.path.isfile(taxa_file):
    print("The taxa file you have entered was not found.  "
          "Check spelling and or make sure the file is in the same directory as the script")
    sys.exit(1)


gene_positions = gene_position_list(charset)
format_fasta_file(taxa_file)
taxa_list = "reformatted_fasta_file.txt"


if not os.path.exists('Taxa_Splice_Files'):
    os.makedirs('Taxa_Splice_Files')


with open(taxa_list, "r") as taxa_list:
    taxa_data = list(taxa_list)
    taxa_data = [i for i in taxa_data if i != '\n']


taxa_names = []
taxa_sequence = []
for lines in taxa_data:
    taxa_line = str(lines).strip()
    if taxa_line.startswith(">"):
        taxa_names.append(taxa_line[1:])
    else:
        taxa_sequence.append(taxa_line)

#get splice (first and second number)
first_num = []
second_num = []
for gene in gene_positions:
    first_num.append(gene[0])
    second_num.append(gene[1])
gene_positions = []

del gene_positions
gc.collect()

#fix ranges
for taxa in range(len(taxa_names)):
    count = 0
    with open("Taxa_Splice_Files/" + taxa_names[taxa] + ".fas", "w") as myfile:
        for postion in range(len(first_num)):
            count += 1
            myfile.write(">" + taxa_names[taxa] + str(count) + "\n")
            seq_item = taxa_sequence[taxa]
            myfile.write(seq_item[int(first_num[postion]) - 1:int(second_num[postion]) - 1] + "\n")
