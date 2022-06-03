import argparse
import pandas as pd
from itertools import product

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--csv", required=True)
parser.add_argument("-e", "--extension", required=True)

args = parser.parse_args()
csv = args.csv
extension = args.extension

csv_df = pd.read_csv(csv, sep = ",", header = None)
print(csv_df)

#def rename(cell):
#    return str(cell + '.fasta')

#csv_df.applymap(rename)

#csv_df.apply(lambda x: rename(x))

#csv_df['col'] = csv_df['col'].astype(str) + '.fasta'

for row, col in product(csv_df.index, csv_df.columns):
    csv_df.loc[row, col] = csv_df.loc[row, col] + ".fasta"

print(csv_df)

csv_df.to_csv("renamed_" + csv, sep=",", index=False, header = False)
