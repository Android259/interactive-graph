#! /usr/bin/env python3
import subprocess as sub
import pandas as pd
import os


df=pd.read_csv("../../preprocessing/voronota_parameter_per_ltp.csv")

burico=list(df["buriedness_core"])
buriri=list(df["buriedness_rim"])
promin=list(df["probe_min"])
promax=list(df["probe_max"])
ltp=list(df["ltp"])

current=os.listdir()
struct=sorted([a for a in current if ".pdb1" in a])
name=[a.split("_")[0].split("-")[0] for a in struct]
for i in range(len(ltp)):
    command = f"./voronota-js-receptor-data-graph --input {struct[i]} --output-dir {name[i]} --probe-min {promin[i]} --probe-max {promax[i]} --buriedness-core {burico[i]} --buriedness-rim {buriri[i]} --subpockets 1 "
    print(command)
    sub.Popen(command.split(), stdout=sub.PIPE)

""" #bash script to move the files one level up, that or change --output_dir to ./
for parent_dir in */; do
  # move files from the only subdirectory inside this parent_dir to the parent_dir itself
  child_dir=$(find "$parent_dir" -mindepth 1 -maxdepth 1 -type d)
  if [ -n "$child_dir" ]; then
    mv "$child_dir"/* "$parent_dir"
  fi
done
"""