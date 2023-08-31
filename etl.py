"""
ETL and data cleaning for data collected with scrap_data.py

Clean data, merge with current file and save for further use.
"""
import pandas as pd
import numpy as np
from os import listdir as ld, path, replace as osreplace
import re
from datetime import datetime as dt
import locale

# Set locale to PL to correctly parse date
locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")

# Set directories and paths
stage_dir = "data/stage/"
stage_files = [stage_dir + d for d in ld(stage_dir) if ".csv" in d]
output_file_path = "data/output/iphone_olx_data.csv"


def read_transform_clean(file):
    """
    Read stage files, transform, clean data and assign correct types

    Parameters
    ----------
    file: string
        File to process

    Returns
    -------
    DataFrame
        Cleaned dataframe with desired columns

    """
    stage_columns = [
        "Tytuł",
        "Model telefonu",
        "Wbudowana pamięć",
        "Stan",
        "Cena",
        "Typ",
        "Kolor",
        "Data opublikowania ogłoszenia",
        "URL",
    ]
    output_columns = [
        "Tytuł",
        "Model telefonu",
        "Wbudowana pamięć (GB)",
        "Stan",
        "Cena (zł)",
        "Typ",
        "Kolor",
        "Data ekstraktu",
        "Data opublikowania",
        "URL",
    ]

    # Read date from gile name and format
    date_from_file = "".join(re.findall(r"\d", file))
    extract_datetime = dt.strptime(date_from_file, "%Y%m%d%H%M").strftime(
        "%Y-%m-%d %H:%M"
    )
    extract_date = dt.strptime(date_from_file, "%Y%m%d%H%M").strftime("%Y-%m-%d")

    df_source = pd.read_csv(file)
    df = df_source[stage_columns]

    # Use regexp to extract price from raw column
    df["Cena (zł)"] = df_source["Cena"].str.extract(r"(\d+[\d ]+)\s+zł")
    df["Cena (zł)"] = df["Cena (zł)"].str.replace(" ", "").astype("Int64")

    # Format extract date
    df["Data ekstraktu"] = extract_datetime
    df["Data opublikowania"] = df["Data opublikowania ogłoszenia"].map(
        lambda x: extract_date + x.replace("Dzisiaj o", "")
        if "Dzisiaj o" in x
        else dt.strptime(x, "%d %B %Y").strftime("%Y-%m-%d 00:00")
    )

    # Replace not needed characters to have int value
    df["Wbudowana pamięć (GB)"] = df["Wbudowana pamięć"].str.replace("GB", "")
    df["Wbudowana pamięć (GB)"] = df["Wbudowana pamięć (GB)"].str.replace(".0", "")

    df_output = df[output_columns]

    return df_output


def merge_and_save(df):
    """
    Merges old df with the one processed and save to target directory

    Parameters
    ----------
    df: DataFrame
        Dataframe with processed data from stage
    """
    if path.isfile(output_file_path):
        input_df = pd.read_csv(output_file_path)
        df_diff = pd.concat([input_df, df], ignore_index=True).drop_duplicates(
            subset="URL", keep="first"
        )
        df_diff.to_csv(output_file_path, index=False)
        new_rows = len(df_diff) - len(input_df)
        if new_rows > 0:
            print(f"Added {new_rows} new rows")
        else:
            print("No new rows added")

    else:
        df.to_csv(output_file_path, index=False)


def archive(file):
    """
    Move stage file to archive directory

    Parameters
    ----------
    file: string
        File to archive
    """
    osreplace(file, file.replace("stage", "archive"))


def main():
    """Orchiestrate functions and handle errors in files."""
    if len(stage_files) > 0:
        for file in stage_files:
            try:
                df = read_transform_clean(file)
                merge_and_save(df)
                archive(file)
            except Exception as e:
                print("Error with file: " + file)
                print(e)
    else:
        print("No files in stage found")


if __name__ == "__main__":
    main()
