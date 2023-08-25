from flask import Flask, render_template, request
from flask_socketio import SocketIO
import subprocess
import csv
from profit_finder import get_promos


app = Flask(__name__)
socketio = SocketIO(app)


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

@app.route("/run_script")
def run_script_route():
    subprocess.run(['python3.10', 'main.py'])
    result = get_promos()
    return result

if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app, debug=True)
