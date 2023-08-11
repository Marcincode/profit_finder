import pandas as pd
import numpy as np
from os import listdir as ld, path, replace as osreplace
import re
from datetime import datetime as dt
import locale

# Set locale to PL to correctly parse date
locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')

stage_dir = 'data/stage/'
stage_files = [stage_dir + d for d in ld(stage_dir) if '.csv' in d]
output_dir = 'data/output/iphone_olx_data.csv'

def transform_file_to_df(file):
    stage_columns = ['Tytuł', 'Model telefonu', 'Wbudowana pamięć', 'Stan', 'Cena', 'Typ', 'Kolor',
        'Data opublikowania ogłoszenia', 'URL']
    output_columns = ['Tytuł', 'Model telefonu', 'Wbudowana pamięć (GB)', 'Stan', 'Cena (zł)', 'Typ', 'Kolor',
        'Data ekstraktu', 'Data opublikowania', 'URL']

    date_from_file = ''.join(re.findall(r'\d', file))
    extract_datetime = dt.strptime(date_from_file, "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M")
    extract_date = dt.strptime(date_from_file, "%Y%m%d%H%M").strftime("%Y-%m-%d")

    df_source = pd.read_csv(file)
    df = df_source[stage_columns]

    df['Cena (zł)'] = df_source['Cena'].str.extract(r'(\d+[\d ]+)\s+zł')
    df['Cena (zł)'] = df['Cena (zł)'].str.replace(" ", "").astype('int32')

    df['Data ekstraktu'] = extract_datetime
    df['Data opublikowania'] = df['Data opublikowania ogłoszenia'].map(lambda x: extract_date + x.replace('Dzisiaj o', '') if 'Dzisiaj o' in x else dt.strptime(x, '%d %B %Y').strftime("%Y-%m-%d 00:00"))
    
    df['Wbudowana pamięć (GB)'] = df['Wbudowana pamięć'].str.replace('GB','')
    df['Wbudowana pamięć (GB)'] = df['Wbudowana pamięć (GB)'].str.replace(".0","")
    
    df_output = df[output_columns]

    return df_output

def merge_and_save(df):
    if path.isfile(output_dir):
        input_df = pd.read_csv(output_dir)
        # Make sure to keep those up-to-date in case of offer changes
        df_diff = pd.concat([input_df, df],ignore_index=True).drop_duplicates(subset='URL', keep="first")
        df_diff.to_csv(output_dir, index=False)
        new_rows = len(df_diff) - len(input_df)
        if new_rows>0:
            print(f'Added {new_rows} new rows')
        else:
            print("No new rows added")

    else:
        df.to_csv(output_dir, index=False)

def archive(file):
    osreplace(file, file.replace('stage', 'archive'))
    
def main():
    if len(stage_files)>0:
        for file in stage_files:
            df = transform_file_to_df(file)
            merge_and_save(df)
            archive(file)
    else:
        print("No files in stage found")

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()

