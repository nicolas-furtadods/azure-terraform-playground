import json


def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def overwrite_json_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(json.dumps(data, indent=4))
