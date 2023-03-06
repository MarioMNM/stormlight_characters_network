import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

import scipy as sp
import spacy
from spacy import displacy
import networkx as nx
from pyvis.network import Network
import community.community_louvain as community_louvain

import os
import re

from utils.helpers import *

class RelationshipNetwork:
    def __init__(self, book_path) -> None:
        self.book_name = re.sub(".txt", "", book_path)
        self.characters_df = load_characters()
        self.book_doc = ner(book_path)

    def _build_ne_list(self):
        sent_entity_df = get_ne_list_per_sentence(self.book_doc)
        sent_entity_df['character_entities'] = sent_entity_df['entities'].apply(lambda x: filter_entity(x, self.characters_df))

        # Filter out sentences that don't have any character entities
        sent_entity_df_filtered = sent_entity_df[sent_entity_df['character_entities'].map(len) > 0]
        
        # Take only first name of characters
        sent_entity_df_filtered['character_entities'] = sent_entity_df_filtered['character_entities'].apply(lambda x: [item.split()[0] for item in x])

        return sent_entity_df_filtered
    
    def _build_relationships(self):
        sent_entity_df_filtered = self._build_ne_list()
        relationship_df = create_relationships(sent_entity_df_filtered, window_size=5)
        self.relationship_df = relationship_df
    
    def create_network_graph(self, communities: bool=True):
        # Create a graph from a pandas dataframe
        G = nx.from_pandas_edgelist(self.relationships_df, 
                                    source = "source", 
                                    target = "target", 
                                    edge_attr = "value", 
                                    create_using = nx.Graph())
        
        net = Network(notebook = False, width="1000px", height="700px", bgcolor='#222222', font_color='white')

        node_degree = dict(G.degree)

        #Setting up node size attribute
        nx.set_node_attributes(G, node_degree, 'size')

        net.from_nx(G)
        net.save_graph(f"../networks/{self.book_name}.html")

        if communities == True:
            # Degree centrality
            degree_dict = nx.degree_centrality(G)
            degree_df = pd.DataFrame.from_dict(degree_dict, orient='index', columns=['centrality'])
            
            # Betweenness centrality
            betweenness_dict = nx.betweenness_centrality(G)
            betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['centrality'])

            # Closeness centrality
            closeness_dict = nx.closeness_centrality(G)
            closeness_df = pd.DataFrame.from_dict(closeness_dict, orient='index', columns=['centrality'])

            # Save centrality measures
            nx.set_node_attributes(G, degree_dict, 'degree_centrality')
            nx.set_node_attributes(G, betweenness_dict, 'betweenness_centrality')
            nx.set_node_attributes(G, closeness_dict, 'closeness_centrality')

            communities = community_louvain.best_partition(G)

            nx.set_node_attributes(G, communities, 'group')

            com_net = Network(notebook = False, width="1000px", height="700px", bgcolor='#222222', font_color='white')
            com_net.from_nx(G)
            com_net.save_graph(f"../networks/{self.book_name}_communities.html")