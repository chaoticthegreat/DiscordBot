import json


def load_json():
    with open("guild.json", "r") as f:
        prefixes = json.load(f)
    return prefixes


def write_json(data):
    with open("guild.json", "w") as f:
        json.dump(data, f, indent=4)


def load_user():
    with open("users.json", "r") as f:
        prefixes = json.load(f)
    return prefixes


def write_user(data):
    with open("user.json", "w") as f:
        json.dump(data, f, indent=4)
