import logging
from datetime import datetime
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
from utils.logger import set_up_log


class RelationshipNetwork:
    def __init__(self, book_path) -> None:
        book_name = re.sub(".txt", "", book_path)
        self.book_name = re.sub("./books/", "", book_name)

        self._log = set_up_log(self.book_name)

        self._log.info(f"Initialized process for book: {self.book_name}")
        self.characters_df = load_characters()
        self.book_doc = ner(book_path)
        self._log.info("Initialized class")

    def _build_ne_list(self):
        self._log.info("Initialized named entity list private function")

        sent_entity_df = get_ne_list_per_sentence(self.book_doc)
        sent_entity_df['character_entities'] = sent_entity_df['entities'].apply(lambda x: filter_entity(x, self.characters_df))

        # Filter out sentences that don't have any character entities
        sent_entity_df_filtered = sent_entity_df[sent_entity_df['character_entities'].map(len) > 0]
        
        # Take only first name of characters
        sent_entity_df_filtered['character_entities'] = sent_entity_df_filtered['character_entities'].apply(lambda x: [item.split()[0] for item in x])
        
        self._log.info("Finished named entity list private function")
        return sent_entity_df_filtered
    
    def _build_relationships(self):
        self._log.info("Initialized build relationship private function")
        sent_entity_df_filtered = self._build_ne_list()
        relationships_df = create_relationships(sent_entity_df_filtered, window_size=5)
        self.relationships_df = relationships_df
        self._log.info("Finished build relationship private function")
    
    def create_network_graph(self, communities: bool=True):
        self._log.info("Initialized create network graph function")
        # Create a graph from a pandas dataframe
        self._build_relationships()  
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

        self._log.info(f"Built relationship network for book: {self.book_name}")

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
            self._log.info(f"Built community relationship network for book: {self.book_name}")