#! /usr/bin/env python3

#ESM

#HF_API_TOKEN=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
import os
from huggingface_hub import login, HfApi
from esm.models.esm3 import ESM3
from esm.sdk.api import ESM3InferenceClient, ESMProtein, SamplingConfig
import torch
import pickle as pkl

import sys

def read_fasta(fasta_path):
    sequences = dict()
    with open( fasta_path, 'r' ) as fasta_f:
        for line in fasta_f:
            # get uniprot ID from header and create new entry
            if line.startswith('>'):
                if ":" in line:
                    split_char=":"
                    id_field=0
                if "|" in line :
                    split_char="|"
                    id_field=1
                uniprot_id = line.replace('>', '').strip().split(split_char)[id_field]
                # replace tokens that are mis-interpreted when loading h5
                uniprot_id = uniprot_id.replace("/","_").replace(".","_")
                sequences[ uniprot_id ] = ''
            else:
                # repl. all white-space chars and join seqs spanning multiple lines
                sequences[ uniprot_id ] += ''.join( line.split() ).replace("-","")
                    
    return sequences,uniprot_id

seq=list(read_fasta(sys.argv[1])[0].values())[0]
id=list(read_fasta(sys.argv[1])[0].keys())[0]

print(seq)
print(id)
print(len(seq))
# Check if the Hugging Face API token is available in the environment
token = os.getenv("HF_API_TOKEN")

if token:
    # Use the existing token
    api = HfApi(token=token)
    print("Using existing Hugging Face token.")
else:
    # Prompt the user to log in if no token is found
    login()

# Check that MPS is available
if not torch.backends.mps.is_available():
    if not torch.backends.mps.is_built():
        print("MPS not available because the current PyTorch install was not "
              "built with MPS enabled.")
    else:
        print("MPS not available because the current MacOS version is not 12.3+ "
              "and/or you do not have an MPS-enabled device on this machine.")

device = torch.device("cpu")
# device = "cpu"
print(f"device: {device}")

# Load the ESM 3.0.4 model
model: ESM3InferenceClient = ESM3.from_pretrained("esm3-sm-open-v1").to(device)

# Check if the model is on MPS
model_device = next(model.parameters()).device
print(f"Model is running on device: {model_device}")

protein = ESMProtein(
    sequence=seq
)
protein_tensor = model.encode(protein)

output = model.forward_and_sample(
    protein_tensor, SamplingConfig(return_per_residue_embeddings=True)
)
print(output.per_residue_embedding)
print(output.per_residue_embedding.shape)
#with open(id+"_ESM3.pkl","wb")as f:
#    pkl.dump(output.per_residue_embedding,f)

    













'''

#######################    

#Prost5



import argparse
import time
from pathlib import Path
import torch
#import h5py
from transformers import T5EncoderModel, T5Tokenizer
import pickle as pkl

if torch.cuda.is_available():
    device = torch.device('cuda:0')
elif torch.backends.mps.is_available():
    device = torch.device('mps')
else:
    device = torch.device('cpu')
print("Using device: {}".format(device))


def get_T5_model(model_dir):
    print("Loading T5 from: {}".format(model_dir))
    model = T5EncoderModel.from_pretrained(model_dir).to(device)
    model = model.eval()
    vocab = T5Tokenizer.from_pretrained(model_dir, do_lower_case=False )
    return model, vocab


def read_fasta( fasta_path, split_char, id_field, is_3Di ):
    
    sequences = dict()
    with open( fasta_path, 'r' ) as fasta_f:
        for line in fasta_f:
            # get uniprot ID from header and create new entry
            if line.startswith('>'):
                if ":" in line:
                    split_char=":"
                    id_field=0
                uniprot_id = line.replace('>', '').strip().split(split_char)[id_field]
                # replace tokens that are mis-interpreted when loading h5
                uniprot_id = uniprot_id.replace("/","_").replace(".","_")
                sequences[ uniprot_id ] = ''
            else:
                # repl. all white-space chars and join seqs spanning multiple lines
                if is_3Di:
                    sequences[ uniprot_id ] += ''.join( line.split() ).replace("-","").lower() # drop gaps and cast to upper-case
                else:
                    sequences[ uniprot_id ] += ''.join( line.split() ).replace("-","")
                    
    return sequences,uniprot_id


def get_embeddings( seq_path, emb_path, model_dir, split_char, id_field, 
                       per_protein, half_precision, is_3Di,
                       max_residues=4000, max_seq_len=1000, max_batch=100 ):
    
    seq_dict = dict()
    emb_dict = dict()

    # Read in fasta
    seq_dict,id = read_fasta( seq_path, split_char, id_field, is_3Di )
    prefix = "<fold2AA>" if is_3Di else "<AA2fold>"
    
    model, vocab = get_T5_model(model_dir)
    if half_precision:
        model = model.half()
        print("Using model in half-precision!")

    print('########################################')
    print(f"Input is 3Di: {is_3Di}")
    print('Example sequence: {}\n{}'.format( next(iter(
            seq_dict.keys())), next(iter(seq_dict.values()))) )
    print('########################################')
    print('Total number of sequences: {}'.format(len(seq_dict)))

    avg_length = sum([ len(seq) for _, seq in seq_dict.items()]) / len(seq_dict)
    n_long     = sum([ 1 for _, seq in seq_dict.items() if len(seq)>max_seq_len])
    # sort sequences by length to trigger OOM at the beginning
    seq_dict   = sorted( seq_dict.items(), key=lambda kv: len( seq_dict[kv[0]] ), reverse=True )
    
    print("Average sequence length: {}".format(avg_length))
    print("Number of sequences >{}: {}".format(max_seq_len, n_long))
    
    start = time.time()
    batch = list()
    for seq_idx, (pdb_id, seq) in enumerate(seq_dict,1):
        # replace non-standard AAs
        seq = seq.replace('U','X').replace('Z','X').replace('O','X')
        seq_len = len(seq)
        seq = prefix + ' ' + ' '.join(list(seq))
        batch.append((pdb_id,seq,seq_len))

        # count residues in current batch and add the last sequence length to
        # avoid that batches with (n_res_batch > max_residues) get processed 
        n_res_batch = sum([ s_len for  _, _, s_len in batch ]) + seq_len 
        if len(batch) >= max_batch or n_res_batch>=max_residues or seq_idx==len(seq_dict) or seq_len>max_seq_len:
            pdb_ids, seqs, seq_lens = zip(*batch)
            batch = list()

            token_encoding = vocab.batch_encode_plus(seqs, 
                                                     add_special_tokens=True, 
                                                     padding="longest", 
                                                     return_tensors='pt' 
                                                     ).to(device)
            try:
                with torch.no_grad():
                    embedding_repr = model(token_encoding.input_ids, 
                                           attention_mask=token_encoding.attention_mask
                                           )
            except RuntimeError:
                print("RuntimeError during embedding for {} (L={})".format(
                    pdb_id, seq_len)
                    )
                continue
            
            # batch-size x seq_len x embedding_dim
            # extra token is added at the end of the seq
            for batch_idx, identifier in enumerate(pdb_ids):
                s_len = seq_lens[batch_idx]
                # account for prefix in offset
                emb = embedding_repr.last_hidden_state[batch_idx,1:s_len+1]
                
                if per_protein:
                    emb = emb.mean(dim=0)
                emb_dict[ identifier ] = emb.detach().cpu().numpy().squeeze()
                if len(emb_dict) == 1:
                    print("Example: embedded protein {} with length {} to emb. of shape: {}".format(
                                identifier, s_len, emb.shape))

    end = time.time()
    
    #with h5py.File(str(emb_path), "w") as hf:
    #    for sequence_id, embedding in emb_dict.items():
    #        # noinspection PyUnboundLocalVariable
    #        hf.create_dataset(sequence_id, data=embedding)

    print('\n############# STATS #############')
    print('Total number of embeddings: {}'.format(len(emb_dict)))
    print('Total time: {:.2f}[s]; time/prot: {:.4f}[s]; avg. len= {:.2f}'.format( 
            end-start, (end-start)/len(emb_dict), avg_length))
    print(emb_dict)
    with open(id+"_PT5.pkl","wb")as f:
        pkl.dump(emb_dict,f)
    return True


def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""

    # Instantiate the parser
    parser = argparse.ArgumentParser(description=( 
            'embed.py creates ProstT5-Encoder embeddings for a given text '+
            ' file containing sequence(s) in FASTA-format.' +
            'Example: python embed.py --input /path/to/some_sequences.fasta --output /path/to/some_embeddings.h5 --half 1 --is_3Di 0 --per_protein 1' ) )
    
    # Required positional argument
    parser.add_argument( '-i', '--input', required=True, type=str,
                    help='A path to a fasta-formatted text file containing protein sequence(s).')

    # Optional positional argument
    parser.add_argument( '-o', '--output', required=False, type=str, 
                    help='A path for saving the created embeddings as NumPy npz file.')

    
    # Required positional argument
    parser.add_argument('--model', required=False, type=str,
                    default="Rostlab/ProstT5",
                    help='Either a path to a directory holding the checkpoint for a pre-trained model or a huggingface repository link.' )

    # Optional argument
    parser.add_argument('--split_char', type=str, 
                    default='|',
                    help='The character for splitting the FASTA header in order to retrieve ' +
                        "the protein identifier. Should be used in conjunction with --id." +
                        "Default: '!' ")
    
    # Optional argument
    parser.add_argument('--id', type=int, 
                    default=1,
                    help='The index for the uniprot identifier field after splitting the ' +
                        "FASTA header after each symbole in ['|', '#', ':', ' ']." +
                        'Default: 0')
    # Optional argument
    parser.add_argument('--per_protein', type=int, 
                    default=0,
                    help="Whether to return per-residue embeddings (0: default) or the mean-pooled per-protein representation (1).")
        
    parser.add_argument('--half', type=int, 
                    default=0,
                    help="Whether to use half_precision or not. Default: 0 (full-precision)")
    
    parser.add_argument('--is_3Di', type=int, 
                    default=0,
                    help="Whether to create embeddings for 3Di or AA file. Default: 0 (generate AA-embeddings)")
    
    return parser

def main():
    parser     = create_arg_parser()
    args       = parser.parse_args()
    
    seq_path   = Path( args.input ) # path to input FASTAS
    emb_path   = 0#Path( args.output) # path where embeddings should be stored
    model_dir  = args.model # path/repo_link to checkpoint
    
    split_char = args.split_char
    id_field   = args.id

    per_protein    = False if int(args.per_protein) == 0 else True
    half_precision = False if int(args.half)        == 0 else True
    is_3Di         = False if int(args.is_3Di)      == 0 else True


    get_embeddings( 
        seq_path, 
        emb_path, 
        model_dir, 
        split_char, 
        id_field, 
        per_protein=per_protein,
        half_precision=half_precision, 
        is_3Di=is_3Di 
        )


if __name__ == '__main__':
    main()

    









####################################

import sys

#map embeddings from uniprot sequence to pdb sequence

import biotite.sequence.align as ali
import biotite.sequence as seq
import biotite.sequence.io as io
import torch
import pickle


#with open(sys.argv[3].split("/")[0]+"/"+sys.argv[3].split("/")[1][:6]+'_ESM3pdb.pkl','rb')as f:
#    a=pickle.load(f)
#print(a.shape)

    



uni = sys.argv[1]
pdb = sys.argv[2]


uni= seq.ProteinSequence(io.load_sequence(uni))
pdb= seq.ProteinSequence(io.load_sequence(pdb))

matrix = ali.SubstitutionMatrix.std_protein_matrix()


alignment, order, tree, distances = ali.align_multiple([uni,pdb],matrix)

print(len(pdb))
print(len(uni))
print(alignment)

uno=range(len(alignment.get_gapped_sequences()[0]))
dos=range(len(alignment.get_gapped_sequences()[1]))

dicuni = {uno[i]:alignment.get_gapped_sequences()[0][i] for i in uno}
dicpdb = {dos[i]:alignment.get_gapped_sequences()[1][i] for i in uno}




with open(sys.argv[3],'rb') as f:
    tens = pickle.load(f)

j=0
for i in range(len(dicuni)):
    if dicuni[i]=='-':
        continue
    dicuni[i] = tens[j]
    j+=1

for k,v in dicuni.items():
    if dicpdb[k] != '-':
        try:
            dicpdb[k] = v
        except:
            pass

newnew=dicpdb.copy()
for k,v in dicpdb.items():
    if v == '-':
        del newnew[k]
lis=[]
for k,v in newnew.items():
    lis.append(v)

print(torch.stack(lis).shape)
if not (torch.stack(lis).shape[0] == len(pdb)):
    print("******************************************************************************************************")
with open(sys.argv[3].split("/")[0]+"/"+sys.argv[3].split("/")[1][:6]+'_ESM2pdb.pkl','wb')as f:
    pickle.dump(torch.stack(lis),f)

'''
