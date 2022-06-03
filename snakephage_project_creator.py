"""

Automated creation of Snakephage projects.

Often we want to run snakemake analysis on a number of files that are scattered
among sequencing batches on the 1 Tb storage disk. To get the desired fastas,
you need a file with filenames separated by newlines, a path to search from and
a new project name. The script will not overwrite existing projects.

Arguments:
-- root_path (top level folder from which to search from, e.g. /media/volume/genomes/assemblies)
-- samplelist (newline separated file of samples with extensions)
-- project (name the analysis project)

Given that naming schemes differ, we will first search strictly (the filename
must match exactly). Then, we do a fuzzier search

The script will attempt to find the files in the samplelist and will create a
new queue folder in snakemake (snakemake/input/queue/projectname). The files are
then copied to that folder.

Ville Hoikkala 2022

"""

import os
import argparse
import re
import shutil

default_extension = ".fasta" #what extension should be used when searching for samples whose extension is not defined
queueFolder_path = "/home/ubuntu/snakephage_suite/snakephage/input/queue"

parser = argparse.ArgumentParser()
parser.add_argument("-rp", "--root_path", required=True)
parser.add_argument("-sl", "--samplelist", required=True)
parser.add_argument("-p", "--project", required=True)
args = parser.parse_args()

root_path = args.root_path
samplelist = args.samplelist
project = args.project

#samplelist = ["fTalEC20p1.fasta","fNenEC3p6.fasta","morjestaminavaan"]
sampleLocations = {}

fuzzysearchList = [] #this will be populated with samples for which no match was found during strict search
excludefoldernames = ["oldnames"] #folders with this name will be skipped when matching names

def find_files(filename, root_path):
    result = []
    for root, dir, files in os.walk(root_path):
       if filename in files:
           sampleLocations[filename] = os.path.join(root, filename)
           #result.append(os.path.join(root, filename))
    return sampleLocations

# Read samples to list
with open(samplelist) as file:
    samples = [line.rstrip() for line in file]

#Remove duplicate entries by converting to dictionary and then back to list
deduplicated_samples = list(dict.fromkeys(samples))
removed = len(samples)-len(deduplicated_samples)
print("Removed " + str(removed) + " duplicates from list")
samples = deduplicated_samples

#Often the sample list does not contain extensions. Check this and add
#extensions if necessary
renamed_samples = []
for sample in samples:
    if ((re.match(".fasta", sample)) == None) and ((re.match(".fa", sample)) == None):
        renamed_samples.append(sample + default_extension)
    else:
        renamed_samples.append(sample)

# STRICT SEARCH
for sample in renamed_samples:
    found = False
    for root, dir, files in os.walk(root_path):
        if dir not in excludefoldernames:
            for filename in files:
                if sample.upper() == filename.upper(): #upper() avoids case issues
                    sampleLocations[sample] = os.path.join(root, filename)
                    print("Matched " + sample + " with " + filename)
                    found = True
    if found == False: #if no match was found, add the sample to a follow-up search list
        fuzzysearchList.append(sample)


# Create new project folder
projectfolder = os.path.join(queueFolder_path,project)
os.mkdir(projectfolder)

#Copy all samples that were found in the filesystem
for sample,path in sampleLocations.items():
    print(path)
    shutil.copy2(path,projectfolder)

print("Finished")
