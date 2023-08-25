import subprocess

def main():
    subprocess.run(['python3.10', 'scrap_data.py'])
    print("Data scrapped")
    subprocess.run(['python3.10', 'etl.py'])
    print("ETL finished")

if __name__ == '__main__':
    main()