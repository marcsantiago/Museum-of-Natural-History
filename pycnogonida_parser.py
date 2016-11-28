import argparse
import string
import re
from os import listdir, makedirs, getcwd
from os.path import isfile, join, exists

parser = argparse.ArgumentParser(description='Pycnogonida Parser')
parser.add_argument('-peptide_folder',  '--peptide_folder',   help='Path to peptide folder',      required=True)
parser.add_argument('-anoplo_file',     '--anoplo_file',      help='Path to anoplo fasta file',   required=True)
parser.add_argument('-pycno_file',      '--pycno_file',       help='Path to pycno fasta file',    required=True)
parser.add_argument('-dmel_file',       '--dmel_file',        help='Path to dmel fasta file',   required=True)
parser.add_argument('-smar_file',       '--smar_file',        help='Path to smar fasta file',    required=True)
parser.add_argument('-output_folder',   '--output_folder',    help='where output will be stored', required=False, default='parsed_data')
args = vars(parser.parse_args())

peptide_files = [join(args['peptide_folder'], f) for f in listdir(args['peptide_folder']) if isfile(join(args['peptide_folder'], f))]

target_taxa = re.compile(r'Anoplo|Pycno[^\]]+|Dmel[^\]]+|Smar[^\]]+', re.IGNORECASE)
peptide_name_regex = re.compile(r'(comp[^:]+).+(\(.\))') #anoplo/pycno
peptide_name_regex2 = re.compile(r'>([^\s]+)') # dmel/smar
nuc_map = string.maketrans("ACGT","TGCA")

# I load all the files into memory before iterating
# so that I don't have to load into memory each
# iteration
anoplo_file = None
pycno_file  = None
smar_file   = None
dmel_file   = None
with open(args['anoplo_file'], 'r') as afile, open(args['pycno_file'], 'r') as pfile, open(args['dmel_file'], 'r') as dfile, open(args['smar_file'], 'r') as sfile:
  anoplo_file = afile.read().split('>')
  pycno_file  = pfile.read().split('>')
  smar_file   = sfile.read().split('>')
  dmel_file   = dfile.read().split('>')

out_folder = args['output_folder']
if out_folder == 'parsed_data':
  out_folder = join(getcwd(), out_folder)
  if not exists(out_folder):
      makedirs(out_folder)
else:
  if not exists(out_folder):
      makedirs(out_folder)

for peptide_file in peptide_files:
  file_data = []
  file_name = join(args['output_folder'], peptide_file.replace(args['peptide_folder'], '').replace('/', ''))
  with open(peptide_file, 'r') as cin:
    chunks = cin.read().split('\n')
    for chunk in chunks:
      m = target_taxa.search(chunk)
      if m:
        target = m.group(0)
        if target[0] in ['a', 'A']:
            m = peptide_name_regex.search(chunk)
            if m:
              comp, rev = m.group(1), m.group(2)
              reverse_comp = False
              if rev.find('-') > -1:
                reverse_comp = True
              for anoplo_file_chunk in anoplo_file:
                if anoplo_file_chunk.find(comp) > -1:
                  if rev:
                    parts = anoplo_file_chunk.split('\n')
                    taxa = parts[0]
                    dna = ''.join(parts[1:])
                    dna = dna.translate(nuc_map)[::-1]
                    dna = '\n'.join([dna[i:i+60] for i in xrange(0, len(dna), 60)])
                    file_data.append('>Anoplo_' + taxa + '\n' + dna)
                  else:
                    file_data.append('>Anoplo_' + anoplo_file_chunk.rstrip())
                  break
        elif target[0] in ['p', 'P']:
          m = peptide_name_regex.search(chunk)
          if m:
            comp, rev = m.group(1), m.group(2)
            reverse_comp = False
            if rev.find('-') > -1:
              reverse_comp = True
            for pycno_file_chunk in pycno_file:
              if pycno_file_chunk.find(comp) > -1:
                if rev:
                  parts = pycno_file_chunk.split('\n')
                  taxa = parts[0]
                  dna = ''.join(parts[1:])
                  dna = dna.translate(nuc_map)[::-1]
                  dna = '\n'.join([dna[i:i+60] for i in xrange(0, len(dna), 60)])
                  file_data.append('>Pycno_' + taxa + '\n' + dna)
                else:
                  file_data.append('>Pycno_' + pycno_file_chunk.rstrip())
                break
        elif target[0] in ['s', 'S']:
          m = peptide_name_regex2.search(chunk)
          if m:
            comp = m.group(1)
            for smar_file_chunk in smar_file:
              if smar_file_chunk.find(comp) > -1:
                file_data.append('>Smar_' + smar_file_chunk.rstrip())
                break
        elif target[0] in ['d', 'D']:
          m = peptide_name_regex2.search(chunk)
          if m:
            comp = m.group(1)
            for dmel_file_chunk in dmel_file:
              if dmel_file_chunk.find(comp) > -1:
                file_data.append('>Dmel_' + dmel_file_chunk.rstrip())
                break

  if len(file_data) > 0:
    with open(file_name + '_out.fa', 'w') as cout:
      for data in file_data:
        cout.write(data+'\n')

  else:
    with open(file_name + '_blank.fa', 'w') as cout:
        cout.write('')
