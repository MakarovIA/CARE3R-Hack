import json


def read_json(file_path):
    with open(file_path) as f:
        return json.load(f)


def read_txt(file_path):
    with open(file_path) as f:
        return f.read()
