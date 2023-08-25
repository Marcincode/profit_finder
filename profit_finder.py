import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from bs4 import BeautifulSoup
import urllib.request
from scrap_data import get_add_title
from os import path
from time import sleep

input_dir = 'data/output/iphone_olx_data.csv'
output_dir = 'data/output/iphone_profit.csv'
to_delete_csv = 'data/output/to_delete.csv'

def delete_not_available_offers(df):

    for URL in df['URL']:
        try:
            source = urllib.request.urlopen(URL).read()
            soup = BeautifulSoup(source,'html.parser')
            get_add_title(soup)
        except Exception as e:
            print(e)
            if (str(e) == "local variable 'add_title' referenced before assignment") or str(e) == 'HTTP Error 404: Not Found':
                df = df.loc[df['URL'] != URL]
                print(URL + ' deleted')
                continue
        sleep(2)
    
    return df

def merge_clean_save(df):

    if path.isfile(output_dir):
        input_df = pd.read_csv(output_dir)
        if 'Revieved? (Y/N)' in input_df.columns:
            to_delete = input_df.loc[input_df['Revieved? (Y/N)'] == 'Y']
            if path.isfile(to_delete_csv):
                to_delete_src = pd.read_csv(to_delete_csv)
                to_delete = pd.concat([to_delete_src, to_delete],ignore_index=True).drop_duplicates(subset='URL', keep="first")
            to_delete.to_csv(to_delete_csv, index=False)
            to_delete = to_delete['URL'].values.tolist()
        else:
            to_delete = [] 

    df = df.query('URL not in @to_delete')
    df['Revieved? (Y/N)'] = 'N'
    df = delete_not_available_offers(df)
    df.to_csv(output_dir, index=False)
    print(f'{len(df)} promos available for review')
    return df


def get_promos():
    promos = 0
    df = pd.read_csv(input_dir)
    df['Cena (Mediana - Model, pamięć, stan)'] = df.groupby(['Model telefonu', 'Wbudowana pamięć (GB)', 'Stan'])['Cena (zł)'].transform('median')
    df['Okazyjna cena dla parametrów'] = df['Cena (Mediana - Model, pamięć, stan)'].map(lambda x: x - (x * 0.15))
    df['Potencjalny zysk?'] =  df['Okazyjna cena dla parametrów'] - df['Cena (zł)']
    df_promo = df.loc[df['Potencjalny zysk?']>0].sort_values('Potencjalny zysk?', ascending=False)
    promos = merge_clean_save(df_promo)
    return f'{len(promos)} offers available for review.'

def main():
    get_promos()


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()