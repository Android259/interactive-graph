#! /usr/bin/env python3

for i in raw/*
do
j=$(echo $i | tr -d "/")
python3 ../../preprocessing/pdb2fasta.py $i > fasta/$j.fasta
done

