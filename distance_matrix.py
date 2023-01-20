import networkx as nx
import osmnx as ox
import pandas as pd
import geopandas as gpd
from ipyleaflet import * 
from time import time       

def format_address(address): #the function should change the address to a geocodable address
    ind=len(address)-1
    cnt=0
    while ind >= 0:
        if address[ind] == ',':
            cnt+=1
            if cnt==4:
                return address[ind+1 :]
        ind-=1
    return address

def geocode_delivery_orders(addresses): #returns a tuple of lists of longitudes and lattitudes
    x=[]
    y=[]
    failed_addresses=[]
    successful_addresses=[]
    for address in addresses:
        try:
            coordinate=ox.geocode(format_address(address)) 
            x.append(coordinate[1])
            y.append(coordinate[0])
            successful_addresses.append(address)
        except:
            failed_addresses.append(address)
    df=pd.DataFrame(failed_addresses, columns=['failed address'])
    df.to_csv('failed addresses')
    df=pd.DataFrame(successful_addresses, columns=['successful address'])
    df.to_csv('successful addresses')
    return x, y
            
addresses=pd.read_excel('delivery.xlsx')['address'].tolist()
x,y=geocode_delivery_orders(addresses)

#graph=gpd.read_file('bangalore.gpkg')
place_name = "Bengaluru, India"
graph = ox.graph_from_place(place_name)

delivery_nodes=ox.nearest_nodes(graph, x, y) #ids of nodes where orders are to be delivered
n=len(x)
print('Successful addresses :', n)
distance_matrix= [ [ nx.shortest_path_length(graph, delivery_nodes[i], delivery_nodes[j], weight='weight') for i in range(n)] for j in range(n) ]
print(distance_matrix)