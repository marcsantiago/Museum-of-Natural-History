#!/usr/bin/env python
__author__ = 'marcsantiago'
from os import remove
from itertools import izip

import argparse

parser = argparse.ArgumentParser(description='Amino Acid Threshold Setter')
parser.add_argument('-f',  '--file_path', help='Reads the contents of the supplied file', required=True)
parser.add_argument('-t',  '--threshold_value', type=int,  help='Set the upper limit of amino acids in the seqeunce', required=True)
args = vars(parser.parse_args())

junkfilename = 'junk_output.txt'
with open(junkfilename, 'w') as junk_output:
	with open(args['file_path'], 'r') as data: 
		for line in data.readlines():
			if line.startswith('>'):
				junk_output.write('\n'+line)
				continue
			else:
				junk_output.write(line.strip())

with open(junkfilename, 'r') as input_data:
	sequences_id = []
	sequences = []
	for line in input_data.readlines():
		if line.startswith('\n'):
			continue
		elif line.startswith('>'):
			sequences_id.append(line.strip())
		else:
			sequences.append(line.strip())
			
if len(sequences_id) != len(seqeunce):
	raise IndexError

mapped_id_with_seq = dict(izip(sequences_id, sequences))

with open('amino_acid_threshold_is_'+str(args['threshold_value'])+'.fasta', 'w') as outdata: # will be the arg value  
	for k, v in mapped_id_with_seq.items():
		if len(v) <= int(args['threshold_value']): # 
			outdata.write(k+'\n'+v+'\n')
remove(junkfilename)
