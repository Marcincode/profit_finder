"""
Crate and run flask app

Create flask app to review and update proffit offers
"""
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import subprocess
from time import sleep
import csv
from profit_finder import get_promos


app = Flask(__name__)
socketio = SocketIO(app)

profit_file_path = "data/output/iphone_profit.csv"


@app.route("/", methods=["GET", "POST"])
def index():
    """Index function to read csv data and render template on data update"""
    if request.method == "POST":
        updated_data = request.form.getlist("updated_data[]")
        update_csv(updated_data)
    csv_data = read_csv()
    return render_template("index.html", csv_data=csv_data)


def read_csv():
    """Read data from csv profit file"""
    csv_data = []
    with open(profit_file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            csv_data.append(row)
    return csv_data


def update_csv(updated_data):
    """Update profit file with reviewed offers flag"""
    with open(profit_file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)

    for i, row in enumerate(rows[1:]):
        row[-1] = updated_data[i]

    with open(profit_file_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(rows)


@app.route("/run_script")
def run_script_route():
    """Run main.py to trigger data scrap and etl and assign output of get_promos function to result to show text on page"""
    subprocess.run(["python3.10", "main.py"])
    result = get_promos()
    return result


if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app, debug=True)
