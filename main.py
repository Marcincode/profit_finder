import subprocess

def main():
    subprocess.run(['python', 'scrap_data.py'])
    subprocess.run(['python', 'etl.py'])

if __name__ == '__main__':
    main()