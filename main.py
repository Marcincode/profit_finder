import subprocess

def main():
    subprocess.run(['python3.10', 'scrap_data.py'])
    subprocess.run(['python3.10', 'etl.py'])

if __name__ == '__main__':
    main()