import json
import argparse
import os

#### Blobber ####

""" 
Blobtools organizes its results in a .json. The blobs are stored in a dictionary dict_of_blobs in order, where
the first entry is longest. Since we are looking for phages, we can assume a longer contig than any other with a
dramatically higher coverage than any other contig. The pseudocode is:

Load txt file with one sample name per row. These names are used to find blobplots that contain the name in full. Phages are loaded to list.

Per phage in the list
1. Take longest and second longest contig
2. Check if longest contig is a virus
3. Check if longest contig is over a preset minimum length (default: 10 kb)
4. Check if longest contig is X times longest than second longest (default: 5x)
5. Check if longest contig has X times higher coverage than second longest (default: 10x)

The program outputs a single line: phage_name,success
Where phage_name is the sample name and 

"""

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", required=True)
parser.add_argument("-rp", "--root_path", required=True) #where to look for blobplots
args = parser.parse_args()

data = args.data
root_path = args.root_path

sampleLocations = {}
excludefoldernames = ["oldnames"] #folders with this name will be skipped when matching names

def find_files(filename, root_path):
    result = []
    for root, dir, files in os.walk(root_path):
       if filename in files:
           sampleLocations[filename] = os.path.join(root, filename)
           #result.append(os.path.join(root, filename))
    return sampleLocations

with open(data) as file:
    phages = [line.rstrip() for line in file]

print(phages)

#Search for files
for phage in phages:
    found = False
    for root, dir, files in os.walk(root_path):
        if dir not in excludefoldernames:
            for filename in files:
                if (phage.upper() in filename.upper()) & ("blobDB.json" in filename): #if filename is found in a blobplot .json file
                    sampleLocations[phage] = os.path.join(root, filename)
                    print("Matched " + phage + " with " + filename)
                    found = True


#data = "data/D9_EC8p3.blobDB.json"
json_file = open(data)
json = json.load(json_file)

checkpoints = {"is_virus_pass": False,
                "length_pass": False,
                "length_ratio_pass": False,
                "coverage_ratio": False}

#Checkpoint requirements
desired_family = "Uroviricota"
min_length = 10000
min_length_ratio = 5
min_cov_ratio = 10

blobs = json["dict_of_blobs"]

print("Starting Blobber (filters blobplots for best phage genome)")
print("Data: " + str(data))

#1. Take longest and second longest contig
best = blobs[list(blobs.keys())[0]]
second_best = blobs[list(blobs.keys())[1]]

#2. Check if longest contig is a virus
best_family = best["taxonomy"]["bestsum"]["phylum"]["tax"]
if best_family == desired_family:
    checkpoints["is_virus_pass"] = True
print("1. FAMILY: " + best_family + ". Passed checkpoint: " + str(checkpoints["is_virus_pass"]))

#3. Check if longest contig is over a preset minimum length (default: 10 kb)
if best["length"] >= min_length:
    checkpoints["length_pass"] = True
print("2. LENGTH (absolute): " + str(best["length"]) + " bp. Passed checkpoint: " + str(checkpoints["length_pass"]) + " (min. length: " + str(min_length) + " bp)")

#4. Check if longest contig is X times longest than second longest (default: 5x)
length_ratio = round(float(best["length"]) / float(second_best["length"]),2)
if length_ratio >= min_length_ratio:
    checkpoints["length_ratio_pass"] = True
print("3. LENGTH (ratio): " + str(length_ratio) + ". Passed checkpoint: " + str(checkpoints["length_pass"]) + " (min. length ratio: " + str(min_length_ratio) + ")")

#5. Check if longest contig has X times higher coverage than second longest (default: 10x)
cov_ratio = round(float(best["covs"]["bam0"]) / float(second_best["covs"]["bam0"]),2)
if cov_ratio > min_cov_ratio:
    checkpoints["coverage_ratio"] = True
print("4. COVERAGE (ratio): " + str(cov_ratio) + ". Passed checkpoint: " + str(checkpoints["coverage_ratio"]) + " (min. coverage ratio: " + str(min_cov_ratio) + ")")

#6. Final check
failed = False
for key, value in checkpoints.items():
    if value == False:
        print("The phage assembly failed checks. Reason: " + key)
        failed = True

if failed == True:
    print("The phage failed checkpoints. Checkpoints and their results: " + str(checkpoints))

if failed == False:
    print("The phage assembly PASSED checkpoints. Full log: " + str(checkpoints))
