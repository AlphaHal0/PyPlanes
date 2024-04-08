import kdl
from constants import *  # Import all constants from constants.py

# Define constants in a dictionary
constants = {
    'system': {
        'screen-width': SCREEN_WIDTH,
        'screen-height': SCREEN_HEIGHT
    },
    'player': {
        'aircraft-width': INITIAL_AIRCRAFT_WIDTH,
        'aircraft-height': INITIAL_AIRCRAFT_HEIGHT,
        'aircraft-x': INITIAL_AIRCRAFT_X,
        'aircraft-y': INITIAL_AIRCRAFT_Y
    },
    'bullet': {
        'bullet-x': INITIAL_BULLET_X,
        'bullet-y': INITIAL_BULLET_Y
    },
    'enemy': {},
    'background': {
        'scroll-speed': SCROLL_SPEED,
        'scroll-speed-ratio': SCROLL_SPEED_RATIO
    }
}

# Parse KDL document
doc = kdl.parse("""
data {
    system {
        screen-width
        screen-height
    }

    player {
        aircraft-width
        aircraft-height
        aircraft-x
        aircraft-y
    }

    bullet {
        bullet-x
        bullet-y
    }

    enemy {

    }

    background {
        scroll-speed
        scroll-speed-ratio
    }
}
""")

# Iterate over the nodes in the document
for node in doc.nodes:
    if node.name in constants:
        for child in node.children:
            if child.name in constants[node.name]:
                # Replace the node with a new one that includes the constant value
                node.children.remove(child)
                node.children.append(kdl.Node(child.name, args=[constants[node.name][child.name]]))