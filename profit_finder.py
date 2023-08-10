import pandas as pd

input_dir = 'data/output/iphone_olx_data.csv'
output_dir = 'data/output/iphone_profit.csv'

def main():

    df = pd.read_csv(input_dir)
    df['Cena (Mediana - Model, pamięć, stan)'] = df.groupby(['Model telefonu', 'Wbudowana pamięć (GB)', 'Stan'])['Cena (zł)'].transform('median')
    df['Okazyjna cena dla parametrów'] = df['Cena (Mediana - Model, pamięć, stan)'].map(lambda x: x - (x * 0.15))
    df['Potencjalny zysk?'] =  df['Okazyjna cena dla parametrów'] - df['Cena (zł)']
    df_promo = df.loc[df['Potencjalny zysk?']>0].sort_values('Potencjalny zysk?', ascending=False)
    df_promo.to_csv(output_dir, index=False)


main()