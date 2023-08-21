from flask import Flask, render_template, request
import csv
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
    csv_data = []
    with open('data/output/iphone_profit.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            csv_data.append(row)
    return render_template('index.html', csv_data=csv_data[1:])  # Ignorujemy nagłówki kolumn

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request
import csv
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        updated_data = request.form.getlist('updated_data[]')
        update_csv(updated_data)
    csv_data = read_csv()
    return render_template('index.html', csv_data=csv_data)

def read_csv():
    csv_data = []
    with open('data/output/iphone_profit.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            csv_data.append(row)
    return csv_data


def update_csv(updated_data):
    with open('data/output/iphone_profit.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)

    for i, row in enumerate(rows[1:]):
        row[-1] = updated_data[i]

    with open('data/output/iphone_profit.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(rows)


if __name__ == '__main__':
    app.run(debug=True)
