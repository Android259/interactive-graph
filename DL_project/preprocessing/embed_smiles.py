#! /usr/bin/env python3
"""Legacy SMILES collector, superseded by embed_smiles_isomeric_and_nonisomeric.py.

Read ../data/Processed_dataset.csv. Select SmileGlobal/SmileFragment, split candidate
lists and remove duplicates. Write primary_embedding.pkl for an embedding script.
Paths are relative to the working directory.

    cd preprocessing
    python3 embed_smiles.py
"""

import pandas as pd
import pickle as pkl

final_list = []

df = pd.read_csv("../data/Processed_dataset.csv")
for i in range(len(df["SmileFragment"])):
	current_list = ""
	if df["SmileFragment"][i] != "0" and df["SmileGlobal"][i] == "0" :
		if ";" in df["SmileFragment"][i] :
			for j in df["SmileFragment"][i].split(";"):
				final_list.append(j)
		else :
			current_list = df["SmileFragment"][i].split(";")[0]
		final_list.append(current_list)
	else:
		if df["SmileGlobal"][i] != "0" and df["SmileFragment"][i] == "0" :
			if ";" in df["SmileGlobal"][i] :
				for j in df["SmileGlobal"][i].split(";"):
					final_list.append(j)
			else :
				current_list = df["SmileGlobal"][i].split(";")[0]
			final_list.append(current_list)


print(len(set(final_list)))
final = list(set(final_list))

dfi=pd.DataFrame(final, columns=['smile'])
print(dfi)
with open("primary_embedding.pkl", 'wb') as f:
	pkl.dump(final,f)
