#! /usr/bin/env python3

import pandas as pd
from itertools import product 
import sys

df = pd.read_csv(sys.argv[1], sep=";")

#can reference specific line as such
#print(df[df.LTPProtein=="BPI"][df.FullIdentityOfLipid=="Phosphatidylcholine (O-32:1)"])



# Step 1: Get unique values from each column
unique_proteins = df["LTPProtein"].unique()
unique_lipids = df["FullIdentityOfLipid"].unique()

# Step 2: Cartesian product of all possible pairs
all_pairs = pd.DataFrame(list(product(unique_proteins, unique_lipids)), columns=["LTPProtein", "FullIdentityOfLipid"])

# Step 3: Find pairs NOT in original df (negative interactions)
negative_pairs = all_pairs.merge(df, on=["LTPProtein", "FullIdentityOfLipid"], how='left', indicator=True)
negative_pairs = negative_pairs[negative_pairs['_merge'] == 'left_only'].drop(columns=['_merge'])

# Add a label column to distinguish positive and negative if needed
df['Interaction'] = 1
negative_pairs['Interaction'] = 0

# Combine them if you want a single dataset
full_dataset = pd.concat([df, negative_pairs], ignore_index=True)

print(full_dataset)

# list all combinations of gene and lipid
#add column with 1 for positive interaction
df2 = df
df2["Interaction"]=1




#for each combination not present in dataset, append line with 0 for interaction

positiv_int = df2[["LTPProtein", "FullIdentityOfLipid"]]

ltp = df2["LTPProtein"].unique()

lipid = df2["FullIdentityOfLipid"].unique()

comblist = list(product(ltp, lipid))
combdf = pd.DataFrame(data=comblist, columns=["LTPProtein", "Lipid"])
print(combdf)

buffer = []
int_copy = pd.DataFrame()
for line in range(len(df2["Lipid"])) :
	if df2.iloc[line]["FullIdentityOfLipid"] not in buffer :
		int_copy = pd.concat([int_copy, pd.DataFrame([df2.iloc[line]])], ignore_index=True)
		buffer.append(df2.iloc[line]["FullIdentityOfLipid"])
df3 = df2

count=0
flag=False
for i in range(len(combdf["Lipid"])):
	int_line=combdf.iloc[i]
	for j in range(len(positiv_int["LTPProtein"])):
		if int_line["LTPProtein"] == positiv_int.iloc[j]["LTPProtein"] and int_line["Lipid"] == positiv_int.iloc[j]["FullIdentityOfLipid"]:
			flag=False
			break
		else:
			flag=True

	if flag == True:
		append_line = int_copy[int_copy["FullIdentityOfLipid"]==int_line["Lipid"]]
		ap = append_line.copy().reset_index()
		ap.at[0,'Interaction'] = 0
		ap.at[0,'LTPProtein'] = int_line["LTPProtein"]
		df3 = df3._append(ap, ignore_index=True)
	
df3.to_csv("Processed_Negative_int.csv")

"""
import pandas
csv=pandas.read_csv("Total_interaction_Cargo_v2.csv")
tp = csv[csv['Interaction'] == 1]
csv2 = csv.drop(tp.index)
csv3 = csv2.sample(frac=0.1)
print(csv2['index'])
print(csv3['index'])
csv4 = pandas.concat([tp,csv3], ignore_index=True).drop(['Unnamed: 0.1', 'Unnamed: 0','index'],axis = 1)
print(csv4)
csv4.to_csv("Total_interaction_Cargo_v3.csv")
"""