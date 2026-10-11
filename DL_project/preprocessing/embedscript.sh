# Legacy driver for the UniProt-to-PDB alignment step at the bottom of EmbedProtein.py
# (section 3 of its header docstring): for every per-protein directory under the current
# working directory, picks that protein's UniProt FASTA, its PDB-derived FASTA, and its
# ESM2 embedding pickle, then calls EmbedProtein.py <uniprot.fasta> <pdb.fasta>
# <embedding.pkl> to remap the embedding onto the PDB numbering.
#
# Usage: cd <directory containing one subfolder per protein>; bash ../embedscript.sh
for i in [0-9A-Z]*/
do
a=$(ls ${i}*.fasta | awk 'NR==1')
b=$(ls ${i}*.pdb*.fasta)
c=$(ls ${i}*_ESM2.fasta)
if [[ "$a" == "$b" ]]
then
a=$(ls ${i}*.fasta | awk 'NR==2')
fi
echo $a
echo $b
echo $c
python3 EmbedProtein.py $a $b $c
done
