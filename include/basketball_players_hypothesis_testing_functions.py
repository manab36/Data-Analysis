import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from include.beauti_print import *

def clean_non_active_players(df):
    header_print("Cleaning Non active players, Not male players and Non basketball players")
    if df[df["sport"] != "Basketball"]["player_name"].count()!= 0:
        df =df[df["sport"] == "Basketball"]

    if df[df["active_status"] != True]["player_name"].count()!= 0:
        df= df[df["active_status"] == True]

    if df[df["gender"] != "M"]["player_name"].count()!= 0:
        df= df[df["gender"] == "M"]

    df.drop(columns=["sport", "active_status", "gender"], inplace= True)
    return df

def outlier_remover(df, cols,q1_threshold= 5, q3_threshold= 95):
    # header_print(f"Removing outlier in col: {cols}")
    for col in cols:
        num_1= len(df)

        # hint_print(f"You have selected Q1= {q1_threshold} percentile \nand Q3= {q3_threshold} percentile\n")
        q1= df[col].quantile(q1_threshold/100)
        q3= df[col].quantile(q3_threshold/100)
        iqr= q3- q1
        upp= q3 + (1.5*iqr)
        low= q1 - (1.5*iqr)
        # hint_print(f"Lowerbound: {low} \nand Upperbound: {upp}")
        
        df= df[df[col] <= upp]
        df= df[df[col] >= low]

        num_2= len(df)
        # print(f'Before cleaning number of rows: {num_1}')
        # print(f' After cleaning number of rows: {num_2}')
        if num_1> num_2:
            warning_print(f"{num_1- num_2} rows removed")

        # print('\n\n')
    

    if False:
        fig= plt.figure(figsize=(7*len(cols),5))

        i=1
        for col in cols:
            plt.subplot(1,len(cols),i)
            sns.boxplot(data=df,x= col, color="blue")
            plt.xticks(rotation=45,fontsize=8)
            i+=1
        fig.suptitle("Barplot")
        plt.show()
    return df


