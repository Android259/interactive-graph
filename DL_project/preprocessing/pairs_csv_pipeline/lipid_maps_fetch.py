#! /usr/bin/env python3

import pandas as pd
import requests as rq
import pickle as pk
import json

df = pd.read_csv("ac_data_cargo.csv", sep="\t", low_memory=False)

columns = ['LTPProtein', 'ProteinDomain', 'FullIdentityOfLipid', 'Lipid', 'Screen', 'Intensity', 'Adduct', 'TotalCarbonChainLength', 'TotalCarbonChainUnsaturations', 'IonMode', 'mz', 'MeanOfRetentionTime','MinimumOfRetentionTime', 'MaximumOfRetentionTime', 'LipidAmbiguity', 'LikelySubclass']

def RemoveAdduct(df):
    copy = df
    for i in range(len(df["LTPProtein"])):
        adduct = df.at[i, "Adduct"]
        indy = len(str(adduct)) + 1
        header = df.at[i,"FullIdentityOfLipid"][indy:].strip(" ")
        copy.at[i,"FullIdentityOfLipid"] = header
    return copy
df2 = RemoveAdduct(df)


count = dict()
def SeparateChainCount(df, count):
    copy = df
    for i in range(len(df["LTPProtein"])):
        sub = copy.at[i,"FullIdentityOfLipid"]
        ltp = copy.at[i,"LTPProtein"]
        abbrev = copy.at[i,"Lipid"]
        if ("=>" in sub) or  ("L" in copy.at[i, "LikelySubclass"]):
            count[abbrev+ltp] = count.get(abbrev+ltp, 0) + 1
        else:
            count[abbrev+ltp] = count.get(abbrev+ltp, 0)
    for i in range(len(df["LTPProtein"])):
        copy.at[i, "FragmentCount"] = count[copy.at[i,"Lipid"]+copy.at[i,"LTPProtein"]]
    return copy




alone = []
result = []
def LonelyLipid(df, alone):
    copy = df
    count = 0
    for i in range(len(df["LTPProtein"])):
        if "=>" in copy.at[i, "FullIdentityOfLipid"]:
            alone.append(0)
        else:
            alone.append(1)
    for i in range(len(df["LTPProtein"])):
        copy.at[i, "Fragment"] = alone[i]
    for i in range(len(df["LTPProtein"])):
        if copy.at[i, "FragmentCount"] == 0 and copy.at[i, "Fragment"] == 1:
            copy.at[i, "IsWithoutInformation"] = 1 
            count+=1
        else:
            copy.at[i, "IsWithoutInformation"] = 0
    print(count)
    return copy    


def PositiveRequest(df):
    count=0
    copy = df
    resultlistglobal = []
    resultlistfragments = []
    for i in range(len(df["LTPProtein"])):
        ishex = False
        if df.at[i, "IsWithoutInformation"] == 0:
            fetchdetails = True
        else:
            fetchdetails = False
        if str(df.at[i, "Lipid"][0:3]) == "Hex":
            ishex = True
            header = df.at[i,"Lipid"].split("(")[0]
            if header == "BMP":
                    header = "LBPA"
            if header == "FA" :
                header = ""
            if "/" in header:
                header = header.split("/")[0]
            carbon_count = df.at[i, "Lipid"].split(":")[0][-2:]
            unsaturations = df.at[i, "Lipid"].split(":")[1][0]
            req1_abbrev = str(header+"%20"+carbon_count+"%3A"+unsaturations+"%3B"+"O2").replace("*","")
            req2_abbrev = str(header+"%20"+carbon_count+"%3A"+unsaturations+"%3B"+"O3").replace("*","")
            req1 = rq.get("https://www.lipidmaps.org/rest/compound/abbrev/"+req1_abbrev+"/all")
            req1.raise_for_status()
            req2 = rq.get("https://www.lipidmaps.org/rest/compound/abbrev/"+req2_abbrev+"/all")
            req2.raise_for_status()
            if (req1.status_code == 200) and (req2.status_code == 200) :
                subset = []
                try:
                    if len(str(req1.json())) > 5:
                        count+=1
                        subset.append(req1.json())
                        if len(str(req2.json())) > 5:
                            subset.append(req2.json())
                        resultlistglobal.append(subset)
                        resultlistfragments.append(0)
                    else:
                        if len(str(req2.json())) > 5:
                            count+=1
                            resultlistglobal.append(req2.json())
                            resultlistfragments.append(0)
                        else:
                            resultlistglobal.append("Empty")
                            resultlistfragments.append(0)
                except:
                    resultlistglobal.append("Empty")
                    resultlistfragments.append("Empty")
            else:
                resultlistglobal.append("Empty")
                resultlistfragments.append("Empty")
        else:
            if fetchdetails and ("=>" in df.at[i,"FullIdentityOfLipid"]):
                print("frag")
                header = df.at[i,"Lipid"].split("(")[0]
                if header == "BMP":
                    header = "LBPA"
                if header == "FA" :
                    header = ""
                if "/" in header:
                    header = header.split("/")[0]
                print(df.at[i,"FullIdentityOfLipid"])
                #wrong one because abbrev seems to react in a different way s described, and only 532 on 1022 working
                #goes to 679 when considering "abbrev_chains" API, and now 1022 still, have to take FA into account
                
                #pas sur du replace *
                chain_detail=df.at[i,"FullIdentityOfLipid"].split("=>")[1].strip().replace("*","")
                print(chain_detail)
                req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev_chains/"+header+chain_detail.replace("/","_")+"/all")
                req.raise_for_status()
                if req.status_code == 200:
                    try:
                        if len(str(req.json())) > 5:
                            print("***************")
                            count+=1
                            resultlistfragments.append(req.json())
                            resultlistglobal.append(0)
                        #relaunch general request when result isnt positive here AND fetchdetails = True 
                        else:
                            #remain to do : switch back to other version with inverse chain order
                            print("alternative")
                            chain_detail=df.at[i,"FullIdentityOfLipid"].split("=>")[1].strip().replace("*","").replace("(","").replace(")","").split("/")
                            print(chain_detail)
                            first=chain_detail[0]
                            second=chain_detail[1]
                            req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev_chains/"+header+"("+second+"_"+first+")"+"/all")
                            header+"("+second+"_"+first+")"
                            req.raise_for_status()
                            if req.status_code == 200:
                                try:
                                    if len(str(req.json())) > 5:
                                        print("***************")
                                        count+=1
                                        resultlistfragments.append(req.json())
                                        resultlistglobal.append(0)
                                    #relaunch general request when result isnt positive here AND fetchdetails = True 
                                    else:
                                        #this is global
                                        req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev/"+(df.at[i, "Lipid"].replace("*",""))+"/all")
                                        req.raise_for_status()
                                        if req.status_code == 200:
                                            try:
                                                if len(str(req.json())) > 5:
                                                    count+=1
                                                    resultlistglobal.append(req.json())
                                                    resultlistfragments.append(0)

                                                else:
                                                    resultlistglobal.append("Empty")
                                                    resultlistfragments.append("Empty")

                                            except:
                                                resultlistglobal.append("Empty")
                                                resultlistfragments.append("Empty")
                                        else:
                                            resultlistglobal.append("Empty")
                                            resultlistfragments.append("Empty")
                                except:
                                    resultlistglobal.append("Empty")
                                    resultlistfragments.append("Empty")
                    except:
                        resultlistglobal.append("Empty")
                        resultlistfragments.append("Empty")
                else:
                    resultlistglobal.append("Empty")
                    resultlistfragments.append("Empty")
            else:
                print(df.at[i,"Lipid"])
                header = df.at[i,"Lipid"].split("(")[0]
                if header == "BMP":
                    header = "LBPA"
                if header == "FA" :
                    header = ""
                if "/" in header:
                    header = header.split("/")[0]
                try :
                    chain = df.at[i,"Lipid"].split("(")[1].replace("*","")
                except:
                    resultlistglobal.append(0)
                    resultlistfragments.append(0)
                    continue
                req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev/"+header+"("+chain+"/all")
                req.raise_for_status()
                if req.status_code == 200:
                    print(header+chain)
                    try:
                        if len(str(req.json())) > 5:
                            print("yes")
                            count+=1
                            resultlistglobal.append(req.json())
                            resultlistfragments.append(0)
                        else:
                            resultlistglobal.append("Empty")
                            resultlistfragments.append("Empty")
                            print("no")
                    except:
                        resultlistglobal.append("Empty")
                        resultlistfragments.append("Empty")
                else:
                    resultlistglobal.append("Empty")
                    resultlistfragments.append("Empty")
    #bug here?
    #for i in range(len(df["LTPProtein"])):
    #    copy.at[i,"IsRequestPositive"] = result[i]
    print(count)
    return copy, resultlistglobal, resultlistfragments

def GetSmiles(df, resultlistglobal, resultlistfragments):
    copy = df
    countfrag = 0
    countglob = 0
    for i in range(len(df["LTPProtein"])):
        oneline = ""
        resultlist = resultlistglobal
        if resultlist[i] == 0 :
            oneline = "0"
        else:
            if type(resultlistglobal[i]) == list:
                for j in range(len(resultlist[i])):
                    if resultlist[i][j] == "Empty":
                        oneline = "Empty"
                    else:
                        if list(resultlist[i][j].keys())[0] == "input":
                            oneline = resultlist[i][j]["smiles"]
                            countglob += 1
                        elif list(resultlist[i][j].keys())[0][0] == "R":
                            countglob += 1
                            for k in resultlist[i][j].keys():
                                oneline+=(resultlist[i][j][k]["smiles"]+"; ")
                                #break
                        else:
                            oneline="NonConclusive"
            else:
                if resultlist[i] == "Empty":
                    oneline = "Empty"
                else:
                    if list(dict(resultlist[i]).keys())[0] == "input":
                        countglob += 1
                        oneline = resultlist[i]["smiles"]
                    elif list(resultlist[i].keys())[0][0] == "R":
                        countglob += 1
                        for k in resultlist[i].keys():
                            oneline+=(resultlist[i][k]["smiles"]+"; ")
                            #break
                    else:
                        oneline="NonConclusive"
        copy.at[i,"SmileGlobal"] = oneline
    print("global : "+str(countglob))
    for i in range(len(df["LTPProtein"])):
        oneline = ""
        resultlist = resultlistfragments
        if resultlist[i] == 0 :
            oneline = "0"
        else:
            if type(resultlistfragments[i]) == list:
                for j in range(len(resultlist[i])):
                    if resultlist[i][j] == "Empty":
                        oneline = "Empty"
                    else:
                        if list(resultlist[i][j].keys())[0] == "input":
                            countfrag += 1
                            oneline = resultlist[i][j]["smiles"]
                        elif list(resultlist[i][j].keys())[0][0] == "R":
                            countfrag += 1
                            for k in resultlist[i][j].keys():
                                oneline+=(resultlist[i][j][k]["smiles"]+"; ")
                                #break
                        else:
                            oneline="NonConclusive"
            else:
                if resultlist[i] == "Empty":
                    oneline = "Empty"
                else:
                    if list(resultlist[i].keys())[0] == "input":
                        countfrag += 1
                        oneline = resultlist[i]["smiles"]
                    elif list(resultlist[i].keys())[0][0] == "R":
                        countfrag += 1
                        for k in resultlist[i].keys():
                            oneline+=(resultlist[i][k]["smiles"]+"; ")
                            #break
                    else:
                        oneline="NonConclusive"
        copy.at[i,"SmileFragment"] = oneline
    print("fragments : :"+str(countfrag))
    return copy



#count inaccurate, dismiss all Lyso- and FA
#fragcount = SeparateChainCount(df2, count)
#fragcount.to_csv("Full_Cargo_Fragment_countv2.csv", columns=fragcount.columns)

#alony = LonelyLipid(fragcount, alone)
#alony = alony[ ['IsWithoutInformation', 'IsRequestPositive'] + [ col for col in alony.columns if ((col != 'IsWithoutInformation'))   ] ]
#alony.to_csv("Full_Cargo_Fragment_count_with_state.csv", columns=alony.columns)

#reqcount, smileslistglobal, smileslistfragments = PositiveRequest(alony)
#with open("dataframe4.pkl", "wb") as f:
#    pk.dump(reqcount,f)
#with open("smiles_listglobal4.pkl", "wb") as f:
#    pk.dump(smileslistglobal,f)
#with open("smiles_listfragments4.pkl", "wb") as f:
#    pk.dump(smileslistfragments,f)
with open("dataframe4.pkl", "rb") as f:
    reqcount = pk.load(f)
with open("smiles_listglobal4.pkl", "rb") as f:
    smileslistglobal = pk.load(f)
with open("smiles_listfragments4.pkl", "rb") as f:
    smileslistfragments = pk.load(f)
final_global = GetSmiles(reqcount, smileslistglobal, smileslistfragments)
final_global = final_global[ ['SmileGlobal', 'SmileFragment'] + [ col for col in final_global.columns if ((col != 'SmileGlobal') and (col != 'SmileFragment'))]]
#df4 = alony[["LTPProtein","FullIdentityOfLipid","IsWithoutInformation"]]
#final_global.to_csv("Full_Cargo_Fragment_count_with_states_v13.csv", columns=final_global.columns)

print(len(final_global['SmileFragment'].unique()))






















#look what type of description it is :

def AddSmiles(df):
    copy = df
    smile = []
    for i in range(len(df["LTPProtein"])):
        tipe = df.at[i, "FullIdentityOfLipid"]

        #are the chain described separately? 
        #request XX from "Lipid" (before "(" ) and format (XX:X_XX:X)
        #do the headgroup here, not only the first two letters, split on parenthesis and check for t* and d*

        #can make choice on IsWithoutInformation too
        #will have to either delete redundant lines or keep them and import only known information or all
        #because can we *really* know that a lipid is revealed twice? and not a different one?
        if "=>" in str(tipe):
            full_lipid = tipe.split("=>")[1].strip(" ").replace("/","_")
            headgrp = df.at[i,"Lipid"].split("(")[1]
            req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev_chains/"+headgrp+full_lipid+"/all")
            #now we should choose which row correspond to what we want
            if req.json() == []:
                smile.append("NotFound")
            else:
                #print(req.json().keys())
                if list(req.json().keys())[0] == "Row1":
                    smile.append(str(req.json()["Row1"]["smiles"])) #have to test this
                else:
                    smile.append(str(req.json()["smiles"])) #have to test this

#is it only total carbon? (no "=>" sign in "FullIdentityOfLipid")
#request XX(XX:X) from "Lipid"

        else :
            headgrp = df.at[i,"Lipid"][0:2]
            total_lipid = "(" + str(int(df.at[i,"TotalCarbonChainLength"])) + ":" + str(int(df.at[i,"TotalCarbonChainUnsaturations"])) + ")"
            req = rq.get("https://www.lipidmaps.org/rest/compound/abbrev/"+headgrp+total_lipid+"/all")
            
            #now we should choose which row correspond to what we want
            if req.json() == []:
                smile.append("NotFound")
            else:
                if list(req.json().keys())[0] == "Row1":
                    smile.append(str(req.json()["Row1"]["smiles"])) #have to test this
                else:
                    smile.append(str(req.json()["smiles"])) #have to test this


    copy.assign(smiles=smile)

    return copy
#df5 = AddSmiles(df4)























#df["FullIdentityOfLipid"] = df["FullIdentityOfLipid"].apply(lambda x(RemoveAdduct(x,df["Adduct"])))
#df = pd.read_csv("ac_data_memb.csv", low_memory=False)
#prots = df["protein"].unique()
#print(len(prots))
#memblip = (df["membrane"].astype("string")+df["sig_lip"].astype("string")).unique()
#print(len(memblip))

#print(len(prots)*len(memblip))
#memblip = (df["membrane"].astype("string")+df["sig_lip"].astype("string")+df["conc_sig_lip"].astype("string")).unique()
#print(len(prots)*len(memblip))
