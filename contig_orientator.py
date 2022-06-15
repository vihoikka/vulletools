"""
Takes a list of contigs, orders them as given and flips them as given.

Inputs:
 - info: tab-separated file with columns: contig name, orientation (+ or -), order (starting from 1)
 - fasta: a regular fasta file with matching contigs to info file
 
Pseudocode:

1. Take list of contigs with orientation and coordinate
2. Orders list based on order column
3. Loop through fasta to find matching contig
4. Flip if necessary
5. Do for all
6. Save as txt
"""

import pandas as pd
from Bio import SeqIO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fasta", required=True)
parser.add_argument("-i", "--info", required=True)
args = parser.parse_args()
fasta = args.fasta
info = args.info

records = SeqIO.parse(fasta, "fasta")
info_df = pd.read_csv(info, sep="\t", header=None)

#print(info_df)
info_df_sorted = info_df.sort_values([2])
#print(info_df_sorted)

newSeqs = []

for a,b in info_df_sorted.iterrows():
    contig = b[0]
    flip = b[1]
    print(flip)
    for record in records:
        print(record.id)
        if record.id == contig:
            if flip == "-":
                #newSeq = record.seq.reverse_complement()
                newSeq = record.seq[::-1] #reverse
            else:
                newSeq = record.seq
            print(newSeq)
            newSeqs.append(newSeq)
    records = SeqIO.parse(fasta, "fasta")

finalSeq = ""
n = 0
for seq in newSeqs:
    print(seq)
    finalSeq += seq
    if n < len(newSeqs)-1:
        finalSeq += "N" * 100
    n += 1

output = open("output.txt", "w")
output.write(str(finalSeq))
output.close()
