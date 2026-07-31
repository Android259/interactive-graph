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
