"""
Finds proffitable offers from csv database file 

Extracts data from site to stage files in csv format
"""

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

from bs4 import BeautifulSoup
import urllib.request
from scrap_data import get_ad_title
from os import path
from time import sleep

# Set paths to all data file, profit data file and reviewed file
data_file_path = "data/output/iphone_olx_data.csv"
profit_file_path = "data/output/iphone_profit.csv"
reviewed_file_path = "data/output/to_delete.csv"


def delete_not_available_offers(df):
    """
    Loop through URL column from df, check if offer is still available and delete if not available

    Parameters
    ----------
    df: DataFrame
        DF with promo offers

    Returns
    -------
    DataFrame
        Cleaned dataframe

    """
    for URL in df["URL"]:
        try:
            source = urllib.request.urlopen(URL).read()
            soup = BeautifulSoup(source, "html.parser")
            get_ad_title(soup)
        except Exception as e:
            print(e)
            if (
                str(e) == "local variable 'ad_title' referenced before assignment"
            ) or str(e) == "HTTP Error 404: Not Found":
                df = df.loc[df["URL"] != URL]
                print(URL + " deleted")
                continue
        sleep(2)

    return df


def merge_clean_save(df):
    """
    Read current profit data file, delete reviewed offers, set Revieved? (Y/N) flag to N for new offers
    Save merged and cleaned df to csv file

    Parameters
    ----------
    df: DataFrame
        DF with promo offers

    Returns
    -------
    DataFrame
        Cleaned dataframe

    """
    if path.isfile(profit_file_path):
        input_df = pd.read_csv(profit_file_path)
        if "Revieved? (Y/N)" in input_df.columns:
            to_delete = input_df.loc[input_df["Revieved? (Y/N)"] == "Y"]
            if path.isfile(reviewed_file_path):
                to_delete_src = pd.read_csv(reviewed_file_path)
                to_delete = pd.concat(
                    [to_delete_src, to_delete], ignore_index=True
                ).drop_duplicates(subset="URL", keep="first")
            to_delete.to_csv(reviewed_file_path, index=False)
            to_delete = to_delete["URL"].values.tolist()
        else:
            to_delete = []

    df = df.query("URL not in @to_delete")
    df["Revieved? (Y/N)"] = "N"
    df = delete_not_available_offers(df)
    df.to_csv(profit_file_path, index=False)
    print(f"{len(df)} promos available for review")
    return df


def get_promos():
    """
    Logic to find new promo offers
    Calculate median of price for model, memory and condition
    Proffitable price is calulated by x - (x * 0.15) where x is median price
    Potential profit calculated: Proffitable price - offer price

    Returns
    -------
    String
        String with number of offers for review

    """
    promos = 0
    df = pd.read_csv(data_file_path)
    df["Cena (Mediana - Model, pamięć, stan)"] = df.groupby(
        ["Model telefonu", "Wbudowana pamięć (GB)", "Stan"]
    )["Cena (zł)"].transform("median")
    df["Okazyjna cena dla parametrów"] = df["Cena (Mediana - Model, pamięć, stan)"].map(
        lambda x: x - (x * 0.15)
    )
    df["Potencjalny zysk?"] = df["Okazyjna cena dla parametrów"] - df["Cena (zł)"]
    df_promo = df.loc[df["Potencjalny zysk?"] > 0].sort_values(
        "Potencjalny zysk?", ascending=False
    )
    promos = merge_clean_save(df_promo)
    return f"{len(promos)} offers available for review."


def main():
    """Run get_promos function"""
    get_promos()


if __name__ == "__main__":
    main()
