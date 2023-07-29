import csv

FILENAME = "special.csv"

coordinates = [
    ["530", "930", "1045", "1150", "1260"],
    ["1740", "2130", "2245", "2350", "2460"],
    ["460", "575", "685", "790", "900", "1010", "1120", "1230", "1340"]
]


def all_conf():
    with open(FILENAME, "r", newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)

def get_config():
    pass
