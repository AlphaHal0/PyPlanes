import kdl

with open('config/config.kdl', 'r') as file:
    config = kdl.parse(file.read())
