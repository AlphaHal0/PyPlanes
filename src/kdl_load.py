import kdl

def kdl_load():
    # Load your KDL document from a file
    with open('config/config.kdl', 'r') as file:
        doc = kdl.parse(file.read())

    # Initialize an empty dictionary to store your constants
    constants = {}

    # Iterate over the nodes in the document
    for node in doc.nodes:
        if node.name == 'data':
            for child in node.nodes:
                constants[child.name] = {}
                for grandchild in child.nodes:
                    # Store each constant in the dictionary
                    if grandchild.args:
                        constants[child.name][grandchild.name] = grandchild.args[0]
    print(constants)

def kdl_save(constants):
    # Create a new KDL document
    doc = kdl.Document()

    # Create a new node for your data
    data_node = kdl.Node('data')

    # Iterate over your constants
    for key, value in constants.items():
        # Create a new child node for each constant
        child_node = kdl.Node(key)
        for subkey, subvalue in value.items():
            # Create a new grandchild node for each sub-constant
            grandchild_node = kdl.Node(subkey)
            grandchild_node.args.append(subvalue)
            child_node.children.append(grandchild_node)
        data_node.children.append(child_node)

    # Add your data node to the document
    doc.nodes.append(data_node)

    # Save your KDL document to a file
    with open('config/config.kdl', 'w') as file:
        file.write(str(doc))

kdl_load()