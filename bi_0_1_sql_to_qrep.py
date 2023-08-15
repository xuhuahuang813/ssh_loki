from query_representation.query import *
from query_representation.utils import *
from networkx.readwrite import json_graph
import os
import pdb

import sys
sys.path.append("./")

'''
设置输入路径（文件夹为单位）
设置输出路径（文件夹为单位），并创建文件夹

外层遍历所有文件夹，内层遍历每个文件夹的queries列表，获取图数据并存在workload文件夹中
'''
print("========================================runnning bi_0_1_sql_to_qrep.py========================================")

folder_path = "./benchmark_small"
# 遍历文件夹
dir_list = os.listdir(folder_path)

for dir_name in dir_list:
    if dir_name == "results.csv":
        continue
    
    dir_path = os.path.join(folder_path, dir_name, "queries_processed")
    file_list = os.listdir(dir_path)

    # 创建输出workload文件夹
    workload_dir = os.path.join(folder_path, dir_name, "workload")
    make_dir(workload_dir)

    # 遍历sql文件
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)  # ./benchmark/Arade/queries/2.sql

        with open(file_path, encoding="utf-8") as f:
            sql = f.read()

            if "SELECT" not in sql and "select" not in sql:
                print("SELECT not in sql ", file_path)
                continue

            # pkl文件路径
            workload_path = file_path.replace("queries_processed", "workload").replace(".sql", ".pkl")  # ./benchmark/Arade/workload/2.pkl

            print("file_name is: ", file_name)
            qrep = parse_sql(sql, None, None, None, None, None, compute_ground_truth=False)

            qrep["subset_graph"] = nx.OrderedDiGraph(json_graph.adjacency_graph(qrep["subset_graph"]))
            qrep["join_graph"] = json_graph.adjacency_graph(qrep["join_graph"])

            save_qrep(workload_path, qrep)
