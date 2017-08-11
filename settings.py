import json

settings = {}

def load(filename):
    with open(filename) as file:
        global settings
        settings = json.load(file)
