import argparse
import json
import logging
import sys

import copy
import numpy as np
import pandas as pd
import os

import loki

from loki.util import constraints, postprocessing
from loki.solver import sat

if __name__ == '__main__':
    print("========================================bi_3_loki.py========================================")
    
    parser = argparse.ArgumentParser(description='Run Loki.')
    parser.add_argument('--vars_per_col', '-n', default=1000)
    parser.add_argument('--verbose', '-v', default=True, action='store_true')

    args = parser.parse_args()
    
    folder_path = "./benchmark_small"
    # 遍历文件夹
    dir_list = os.listdir(folder_path)

    for dir_name in dir_list:
        if dir_name == "results.csv":
            continue
        
        log_file_path = os.path.join(folder_path, dir_name, "logs")
        
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)
            # print(f"文件夹 '{log_file_path}' 已创建")
        # else:
            # print(f"文件夹 '{log_file_path}' 已存在")

        logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format="%(asctime)s %(levelname)-8s [%(name)s]  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(log_file_path + "/loki.log"), logging.StreamHandler()])

        logger = logging.getLogger('MAIN')

        df = pd.read_csv(os.path.join(folder_path, dir_name, "dfs", "op_df.csv")) #"df": "sample-data/op_df.csv"
        
        tables = set(df['input']) 
        table_columns = {table: set(df['column'].where(df['input'] == table).dropna()) for table in tables}
        # print("table_columns is", table_columns)
        
        c_df = pd.read_csv(os.path.join(folder_path, dir_name, "dfs", "literal_df.csv")) #literal_df.csv
        
        # 创建输出文件夹
        result_folder = os.path.join(folder_path, dir_name, "results")
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)
            # print(f"文件夹 '{result_folder}' 已创建")
        # else:
            # print(f"文件夹 '{result_folder}' 已存在")
            
        # table不能直接取第一个，因为同一个文件夹下的sql会针对多个数据表，只是单个sql本身不会join多个表
        tableList = list(tables)
        
        for table in tableList:
            columns = table_columns[table]
            
            constraints_df = constraints.get_constraints_df(c_df, table)
            table_cardinality = constraints.get_table_cardinality(constraints_df)
            co_optimized_columns = constraints.get_co_optimized_columns(constraints_df, columns)
            programs = constraints.get_programs(co_optimized_columns)

            leftover_constraints = []

            vars_per_col = args.vars_per_col

            solutions = []
            for program in programs:
                logger.info(f'Solving: {program}')
                constraints_ = constraints.parse_constraints(program, constraints_df)
                model, vars, cols, col_values_ids_map = sat.build_model(program, constraints_, leftover_constraints, table_cardinality, vars_per_col)
                solution = sat.solve(model, vars, cols, col_values_ids_map, vars_per_col)
                solutions.append(solution)
                logger.info(f'Solved: {program}')


            # Combine all programs' solutions into a single dictionary solution
            full_solution = {k: v for s in solutions for k, v in s.items()}

            postprocessing.apply_leftover_constraints(full_solution, leftover_constraints)
            solution_df = postprocessing.solution_to_df(full_solution)
            final_solution_df = postprocessing.scale_solution_df(solution_df, table_cardinality, vars_per_col)
            
            final_solution_df.to_csv(os.path.join(folder_path, dir_name, "results") + f"/{table}.csv")
            
            logger.info(f"table {table} solved!")

            logger.info('Exiting Loki!')
    sys.exit(0)