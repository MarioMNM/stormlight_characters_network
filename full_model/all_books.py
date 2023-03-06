from os import walk

from full_model.build_network import RelationshipNetwork

if __name__ == "__main__":
    f = []
    for (dirpath, dirnames, filenames) in walk('./books'):
        f.extend(filenames)
        break
    
    for book_path in f:
        rn = RelationshipNetwork(book_path=book_path)
        rn.create_network_graph(communities=True)
