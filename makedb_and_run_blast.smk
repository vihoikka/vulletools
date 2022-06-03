'''
Created on Dec 9, 2021

Blasts your fasta files against a given genome in NCBI.

1. Input a desired NCBI ID for a genome (db_id) -> generates blast database
2. Configure path to your fasta files (uses wildcards)
3. The program runs megablast against the desired genome and outputs .out files
    for each query fasta given.

@author: Ville Hoikkala
'''

db_id = "NC_001417" #provide the NCBI id of the genome you wish to use as database
outpath = "" #where the results will be stored
query_folder_path = "" #where your fastq query files are

#path to folder with queries
queries = glob_wildcards(query_folder_path + "{id}.fq.gz") #use \w+ wldcard constraint ({id,\w+}) to prevent subfolders being searched. Remember, a wildcard is a ny string, including a folder path
print(queries)
rule all:
    input: expand(outpath + db_id + "/{sample}.out", sample=queries.id)


rule get_db_sequence_by_id:
    output:
        outpath + db_id + "/" + db_id + ".fasta"
    params:
        format = "fasta",
        db = "nucleotide"
    conda:
        "envs/blast_tools.yaml"
    message:
        "Fetching fasta file to be used as database"
    shell:
        """
        esearch -db {params.db} -query {db_id} | efetch -format {params.format} > {output}
        """

#blast the assembled contigs remotely
rule make_blast_db:
    input:
        fasta = rules.get_db_sequence_by_id.output
    output:
        outpath + db_id + "/" + db_id + ".ndb"
    params:
        out = outpath + db_id + "/" + db_id
    conda:
        "envs/blast_tools.yaml"
    message:
        "Creating blast database from " + db_id
    shell:
        """
        makeblastdb -in {input} -out {params.out} -parse_seqids -dbtype nucl
        """

#if your queries are fastq (i.e. reads) use rules unzip and fq_to_fa to prepare them for blasting
rule unzip:
    input: query_folder_path + "{sample}.fq.gz"
    output: query_folder_path + "{sample}.fq"
    shell: "gzip -dk {input}"

#if your queries are fastq (i.e. reads) use this convert them to plain fasta
rule fq_to_fa:
    input: query_folder_path + "{sample}.fq"
    output: query_folder_path + "{sample}.fasta"
    conda: "envs/blast_tools.yaml"
    shell:
        """
        fastq_to_fasta -i {input} -o {output}
        """

#blast the assembled contigs remotely
rule blast:
    input:
        #contig = query_folder_path + "{sample}/scaffolds.fasta",
        #contig = query_folder_path + "{sample}.fq.gz",
        contig = rules.fq_to_fa.output,
        db_done = rules.make_blast_db.output
    output:
        outpath + db_id + "/{sample}.out"
    params:
        format = "6 qseqid staxids bitscore std",
        db_path = outpath + db_id + "/" + db_id
    conda:
        "envs/blast_tools.yaml"
    message:
        "Blasting contigs"
    threads: 3
    shell:
        """
        blastn -task megablast -query {input.contig} -db {params.db_path} -outfmt "{params.format}" -out {output} -num_threads {threads}
        """
