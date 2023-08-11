import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from scrap_data import get_add_title
from os import path
from time import sleep

input_dir = 'data/output/iphone_olx_data.csv'
output_dir = 'data/output/iphone_profit.csv'

def delete_not_available_offers(df):

    for URL in df['URL']:
        source = urllib.request.urlopen(URL).read()
        soup = BeautifulSoup(source,'html.parser')
        try:
            get_add_title(soup)
        except Exception as e:
            if e == "local variable 'add_title' referenced before assignment":
                df = df.loc[df['URL'] != URL]
        sleep(2)
    
    return df

def merge_clean_save(df):

 ### TO DO: Create code to save(append) revieved URL's to file and then delete URL from dataframe   
    if path.isfile(output_dir):
        input_df = pd.read_csv(output_dir)
        if 'Revieved? (Y/N)' in input_df.columns:
            to_delete = input_df.loc[input_df['Revieved? (Y/N)'] == 'Y']
            to_delete = to_delete['URL'].values.tolist()
        else:
            to_delete = [] 

    df = df.query('URL not in @to_delete')
    df['Revieved? (Y/N)'] = 'N'
    df = delete_not_available_offers(df)
    df.to_csv(output_dir, index=False)


def main():

    df = pd.read_csv(input_dir)
    df['Cena (Mediana - Model, pamięć, stan)'] = df.groupby(['Model telefonu', 'Wbudowana pamięć (GB)', 'Stan'])['Cena (zł)'].transform('median')
    df['Okazyjna cena dla parametrów'] = df['Cena (Mediana - Model, pamięć, stan)'].map(lambda x: x - (x * 0.15))
    df['Potencjalny zysk?'] =  df['Okazyjna cena dla parametrów'] - df['Cena (zł)']
    df_promo = df.loc[df['Potencjalny zysk?']>0].sort_values('Potencjalny zysk?', ascending=False)
    merge_clean_save(df_promo)


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()