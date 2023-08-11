from query_representation.query import *
from query_representation.utils import *
from networkx.readwrite import json_graph
import os
import pdb

import sys
sys.path.append("./")

# 加载参数配置文件
settings = {}
with open("./settings.json", 'r') as f:
    settings = json.load(f)

# sql文件生成pkl文件
INPUT_SQLS_PATH_LIST = os.listdir(settings["sqlPath"])
OUTPUT_DIR = settings["workloadPath"]
make_dir(OUTPUT_DIR)


for i, sql_path in enumerate(INPUT_SQLS_PATH_LIST): #读INPUT_SQLS_PATH_LIST文件夹下所有的sql文件，并返回初步pkl文件，存于
    print(i, end="\r")
    with open(settings["sqlPath"] + "/" + sql_path, "r", encoding='utf-8') as f:
        sql = f.read()

    output_fn = OUTPUT_DIR + "/" + sql_path.replace(".sql", "") + ".pkl"

    if "SELECT" not in sql:
        print("SELECT not in sql")
        continue

    qrep = parse_sql(sql, None, None, None, None, None,
                     compute_ground_truth=False)

    qrep["subset_graph"] = \
        nx.OrderedDiGraph(json_graph.adjacency_graph(qrep["subset_graph"]))
    qrep["join_graph"] = json_graph.adjacency_graph(qrep["join_graph"])

    save_qrep(output_fn, qrep)
