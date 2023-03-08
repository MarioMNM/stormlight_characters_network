from os import walk, getcwd

from full_model.build_network import RelationshipNetwork

if __name__ == "__main__": 
    f = []
    for (dirpath, dirnames, filenames) in walk('./data/books'):
        f.extend(filenames)
        break

    for book_path in f:
        rn = RelationshipNetwork(book_path=f"./data/books/{book_path}")
        rn.create_network_graph(communities=True)
    
