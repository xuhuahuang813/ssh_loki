import networkx as nx
from networkx.readwrite import json_graph
import pickle
# import numpy as np

# settings = {}
# with open("./settings.json", 'r') as f:
#     settings = json.load(f)
    
fn = "./imdb-new-workload/multi_column_3/8a506.pkl"

with open(fn, "rb") as f:
    query = pickle.load(f)
    
# 选择要保存的文件名
file_name = 'query.txt'

# 保存字典到文本文件
with open(file_name, 'w') as f:
    for key, value in query.items():
        f.write(f"{key}: {value}\n")