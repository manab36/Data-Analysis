import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
pd.set_option('expand_frame_repr', False)
import geopandas as gpd
from include.beauti_print import *


def get_value_counts(df, col_name):
    header_print("column name: "+col_name)
    print(f"    number of 'NaN' value: {df[col_name].isna().sum()}")
    print(f"percentage of 'NaN' value: {round((df[col_name].isna().sum()/len(df[col_name]))*100,2)}%")
    print(f"   number of unique value: {df[col_name].nunique()}")
    print(f"    number of total value: {len(df[col_name])} (including none)")
    print(f"   number of total Values: {df[col_name].count()}\n\n")

def drop_nun_val_in_col(df, col_name):
    header_print(f"droping rows where {col_name} = NaN")
    len_before= len(df)
    print(f"Row counts before droping 'NaN' values: {len_before}")
    df= df.dropna(subset=[col_name])
    df.reset_index()
    len_after= len(df)
    # df[df["Customer ID"].isna()] = df[df["Customer ID"].isna()].apply(lambda v: random.randrange(1000,10000))
    print(f" Row counts after droping 'NaN' values: {len_after}")
    print("-"*40)
    warning_print(f"                     Total rows droped: {len_before-len_after}")
    warning_print(f"             Percentage of droped rows: {round(((len_before-len_after)/len_before)*100,2)}%\n\n")
    return df

def drop_canceled_items(df):
    header_print("droping rows of canceled items")
    len_before= len(df)
    print(f"Number of rows before droping canceled items: {len_before}")
    index_canceled_items= df[df["invoice"].str.startswith('|'.join(['C']))].index
    df= df.drop(index= index_canceled_items)
    len_after= len(df)
    print(f" Number of rows after droping canceled items: {len_after}")
    print("-"*40)
    warning_print(f"                          Total rows droped: {len_before-len_after}")
    warning_print(f"                  Percentage of droped rows: {round(((len_before-len_after)/len_before)*100,2)}%\n\n")
    return df

def outlier_remover(df, col,q1_threshold= 5, q3_threshold= 95):
    header_print(f"Removing outlier in col: {col}")
    hint_print(f"You have selected Q1= {q1_threshold} percentile \nand Q3= {q3_threshold} percentile\n")
    q1= df[col].quantile(q1_threshold/100)
    q3= df[col].quantile(q3_threshold/100)
    iqr= q3- q1
    upp= q3 + (1.5*iqr)
    low= q1 - (1.5*iqr)
    hint_print(f"Lowerbound: {low} \nand Upperbound: {upp}")
    
    warning_print(f"before removing outliers: \n{df[col].describe().T}\n")
    df= df[df[col] <= upp]
    df= df[df[col] >= low]
    warning_print(f" after removing outliers: \n{df[col].describe().T}")
    return df

def recheck_relationship_type(df,col1, col2):
    header_print(f"rechecking relationship for \t{col1} -to- {col2}")
    many_cust= []
    for id in tqdm(df[col1].unique()):
        if df[df[col1]== id][col2].nunique() >1:
            many_cust.append(id)
            # return False
    if len(many_cust)== 0:
        hint_print(f"'{col1}' and '{col2}' have either 'one-to-many' or 'one-to-one' relationhsip")
        return many_cust
    hint_print(f"{len(many_cust)} '{col1}' are related to more than one '{col2}'\n{many_cust}")
    return many_cust
    
def check_relationship_type(df, col1, col2):
    header_print(f"Checking relationship for \t{col1} -to- {col2}")
    if len(df[df[col1].isna()]) or  len(df[df[col2].isna()]):
        print(f"There are few missing values, relationships may not be accurate !")
    
    first_max = df.groupby(col1)[col2].count().max()
    second_max = df.groupby(col2)[col1].count().max()
    if first_max==1:
        if second_max==1:
            hint_print('one-to-one')
        else:
            hint_print('one-to-many')
    else:
        if second_max==1:
            hint_print('many-to-one')
        else:
            hint_print('many-to-many')
            
def get_descriptive_stats(df,cols):
    numeric_cols= []
    desc_cols= []

    for col in cols:
        if df[col].dtypes in [np.int64, np.int32, np.float64, np.float32]:
            numeric_cols.append(col)
        else:
            desc_cols.append(col)
    
    if len(numeric_cols)>0:
        header_print(f"Descriptive Stats for {numeric_cols} :")
        desc_table= df[numeric_cols].describe().T
        desc_table["IQR"]= desc_table["75%"]- desc_table["25%"]
        desc_table["lower bound"]= desc_table["25%"]- (1.5* desc_table["IQR"])
        desc_table["upper bound"]= desc_table["75%"]+ (1.5* desc_table["IQR"])
        print(desc_table,"\n\n")
        
        
        #plot
        i=1
        fig= plt.figure(figsize=(15,len(numeric_cols)*5))
        for col in numeric_cols:
            plt.subplot(len(numeric_cols),1,i)
            sns.boxplot(data=df,x= col,color="red")
            i+=1
        fig.tight_layout(pad=5.0)
        plt.show()

    if len(desc_cols)>0:
        header_print(f"Descriptive Stats for {desc_cols} :")
        print(f"{df[desc_cols].describe().T}","\n\n")

        #plot
        i=1
        fig= plt.figure(figsize=(15,len(desc_cols)*5))
        for col in desc_cols:
            new_data= pd.DataFrame(data=df[col].value_counts().reset_index())[:5]

            plt.subplot(len(desc_cols),1,i)
            sns.barplot(data=new_data,x= col, y= "count",color="black")
            i+=1

            fig.tight_layout(pad=5.0)
            plt.xticks(rotation=45,fontsize=8)
        fig.suptitle("Box Plot for top 5 frequent")
        plt.show()

    print("\n\n")

def get_rmf_data_set(df):
    header_print("RMF dataset prepartion")
    max_date= df["invoicedate"].max()
    min_date= df["invoicedate"].min()

    hint_print(f"Date starts from: {min_date} to {max_date}")

    df_2 = df.groupby('customerid').agg({
                'invoicedate': lambda x: (max_date - x.max()).days, 
                'invoice': lambda x: x.nunique(), 
                "totalprice": lambda x: x.sum()
        }).reset_index()
    df_2.rename(columns= {
        "invoicedate": "recency",
        "invoice": "frequency",
        "totalprice": "monetary"
    }, inplace= True)

    Shopping_Cycle = df.groupby('customerid').agg({'invoicedate': lambda x: ((x.max() - x.min()).days)}).reset_index()
    Shopping_Cycle.rename(columns= {
        "invoicedate": "shopping_cycle",
    }, inplace= True)
    df_2= df_2.merge(Shopping_Cycle, on='customerid', how='right', indicator=True)

    warning_print("We are only conside the customers who made more than one purchase")
    df_2= df_2[(df_2["_merge"]== "both") & (df_2["frequency"]>1)]
    df_2["interpurchase_time"] = df_2["shopping_cycle"] // df_2["frequency"]
    df_2.drop(columns=['shopping_cycle', '_merge'], inplace= True)
    
    print("Sample data:\n",df_2.sample(3))


    cols= ["recency",  "frequency",  "monetary"]
    i=1
    fig= plt.figure(figsize=(8,15))
    for col in cols:
        plt.subplot(3,1,i)
        sns.histplot(data = df_2[col], kde = True)
        plt.ylabel('No of customer' )
        plt.xlabel(col.capitalize())
        i+=1
        fig.tight_layout(pad=5.0)
    plt.xticks(rotation=45,fontsize=8)
    plt.show()

    return df_2

def rfm_score_calculate(df):
    header_print("dfT score :                ")
    quartiles= df[["recency",  "frequency",  "monetary", "interpurchase_time"]].quantile(q=[0.25, 0.5, 0.75]).T.reset_index()
    quartiles.rename(columns={"index":"type"}, inplace=True)
    
    get_score= lambda x,y: 1 if x< quartiles[quartiles["type"]== y][0.25].tolist()[0] else 2 if x< quartiles[quartiles["type"]== y][0.5].tolist()[0] else 3 if x< quartiles[quartiles["type"]== y][0.75].tolist()[0] else 4

    df['R'] = df['recency'].apply(get_score, args=("recency",))
    df['F'] = df['frequency'].apply(get_score, args=("frequency",))
    df['M'] = df['monetary'].apply(get_score, args=("monetary",))
    df['T'] = df['interpurchase_time'].apply(get_score, args=("interpurchase_time",))

    df["rfm_score"]= df['R']+ df['F']+ df['M']
    hint_print(f"max rmf_score: {df["rfm_score"].max()}\nmin rmf_score: {df["rfm_score"].min()}")
    df['label'] = 'Bronze' 
    df.loc[df['rfm_score'] > 1, 'label'] = 'Silver' 
    df.loc[df['rfm_score'] > 3, 'label'] = 'Gold'
    df.loc[df['rfm_score'] > 5, 'label'] = 'Platinum'
    df.loc[df['rfm_score'] > 9, 'label'] = 'Diamond'

    print(f"sample:\n{df.sample(4)}")
    return df

def choropleth_map_plot(df, map_source_url):
    header_print("Calculating information for Choropleth Map")
    
    country_data = gpd.read_file(map_source_url)

    choropleth_df= df.groupby('country').agg({
        'totalprice': lambda x: x.sum(),
        'price': lambda x: x.sum(),
        'quantity': lambda x: x.sum(),
    }).reset_index()
    
    country_df= country_data[["ADMIN", "geometry"]]
    country_df= country_df.rename(columns= {
        "ADMIN": "country", 
    })
    
    #checking missing country
    missing_list= []
    for i in choropleth_df["country"].str.lower().unique().tolist():
        if i not in country_df["country"].str.lower().unique().tolist():
            missing_list.append(i)
    warning_print(f"Cound not find geometry for {len(missing_list)} countries\n{missing_list}")

    #merge datasets
    merged_df = choropleth_df.merge(country_df, on='country', how='left', indicator=True)
    merged_df= merged_df[merged_df["_merge"]== "both"]
    merged_df.drop(columns=['_merge'], inplace= True)
    merged_df= gpd.GeoDataFrame(merged_df)

    #ploting graph
    merged_df.plot(
        column='totalprice', 
        legend=True, 
        cmap='OrRd',
        legend_kwds={"label": "Total Sales", "orientation": "horizontal"},
        figsize=(15, 10),
        missing_kwds={
                "color": "lightgrey",
                "edgecolor": "red",
                "hatch": "///",
                "label": "Missing values",
        }
    )
    return merged_df