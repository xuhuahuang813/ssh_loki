import os
import sys
import pandas as pd
import time
import psycopg2 as pg
import numpy as np
import csv
import argparse
import pdb
import uuid
import logging
import json

class CSVHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.csv_file = open(file_path, mode='a', newline='')
        self.csv_writer = csv.writer(self.csv_file)

    def append_row(self, data_row):
        self.csv_writer.writerow(data_row)

    def close(self):
        self.csv_file.close()
        
NEW_NAME_FMT = "{INP}_{DATA_KIND}"

ALIAS_TO_TABS = {}
ZDBS = ["financial"]

def read_flags():
    parser = argparse.ArgumentParser()

    # parser.add_argument("--result_dir", type=str, required=False,
    #         default="./bibench_processed/CMSprovider/results")
    # parser.add_argument("--inp_to_eval", type=str, required=False,
    #         default="cmsprovider_2")

    parser.add_argument("--data_kind", type=str, required=False,
            default="gen_shuffle", help="suffix for the table")

    parser.add_argument("--reps", type=int, required=False,
            default=1)

    parser.add_argument("--skip_likes", type=int, required=False,
            default=0)

    parser.add_argument("--num_queries", type=int, required=False,
            default=100)

    parser.add_argument("--workload", type=str, required=False,
            default="ceb")

    parser.add_argument("--db_name", type=str, required=False,
            default="bibench")
    parser.add_argument("--db_host", type=str, required=False,
            default="49.52.27.35")
    parser.add_argument("--user", type=str, required=False,
            default="postgres")
    parser.add_argument("--pwd", type=str, required=False,
            default="")
    parser.add_argument("--port", type=int, required=False,
            default=5632)

    return parser.parse_args()


LOG_FMT = "{EHASH} - {INP} - {REP} - QErr:{QERR} [real:{REAL} - estimate:{ESTIMATE}] --> TIME:{TIME}"

def run_filters(sqls, ehashes, inputs, trueys, logger, csv_handler):
    exec_times = []
    con = pg.connect(user=args.user, host=args.db_host, port=args.port,
            password=args.pwd, database=args.db_name)
    cursor = con.cursor()

    rcs = []

    for ri in range(args.reps):
        for si, sql in enumerate(sqls):
            true_est = float(trueys[si])
            if true_est <= 0:
                true_est += 1

            eh = ehashes[si]
            inp = inputs[si]

            if args.data_kind != "":
                if inp not in ALIAS_TO_TABS:
                    table_name = inp
                    new_tab = NEW_NAME_FMT.format(INP = inp.replace('"',''),
                                                  DATA_KIND = args.data_kind)
                    new_tab = '"{}"'.format(new_tab)
                else:
                    table_name = ALIAS_TO_TABS[inp]

                    new_tab = NEW_NAME_FMT.format(INP = inp,
                                                  DATA_KIND = args.data_kind)
                sql = sql.replace(table_name, new_tab, 1)
                # print(sql)
                # pdb.set_trace()

            start = time.time()
            try:
                cursor.execute(sql)
            except Exception as e:
                # logging.error(str(e))
                # logging.error(sql)
                print(sql)
                print(str(e))
                pdb.set_trace()

            output = cursor.fetchall()
            rc = output[0][0] #rc就是模拟的sql在模拟的表中的获取的行数
            if rc <= 0:
                rc += 1

            qerr = max((rc / true_est), (true_est / rc)) #qerr是误差，越靠近1越好

            # if qerr > 10000:
                # print(qerr)
                # pdb.set_trace()

            exec_time = time.time() - start
            exec_times.append(exec_time)
            logline = LOG_FMT.format(EHASH=eh, INP = inp, REP = ri,
                    QERR = qerr,
                    REAL=true_est,
                    ESTIMATE=rc,
                    TIME = exec_time)

            logger.info(logline)
            
            csv_handler.append_row([inp, sql, true_est, rc, qerr])

            if len(rcs) != len(sqls):
                rcs.append(rc)

    logger.info("Total execution time: {}".format(np.sum(exec_times)))
    # print("Total execution time: {}".format(np.sum(exec_times)))

    return rcs

def qerr_func(ytrue, yhat):
    errors = np.maximum((ytrue / yhat), (yhat / ytrue))
    return errors

def main():
    print("========================================bi_5_eval_data.py========================================")
        
    folder_path = "./bibench_processed"
    
    result_all_path = os.path.join(folder_path, "results.csv")
    with open(result_all_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["input", "sql", "real", "estimate", "qerr"])  # 写入标题行

    csv_handler = CSVHandler(result_all_path)
    
    # 遍历文件夹
    dir_list = os.listdir(folder_path)
    for dir_name in dir_list:
        if ".csv" in dir_name:
            continue
        
        dir_path = os.path.join(folder_path, dir_name, "results")
        file_list = os.listdir(dir_path)
        
        # 遍历sql文件
        for file_name in file_list:
                  
            # filename = uuid.uuid4().hex + ".log"
            filename = os.path.join(dir_path, file_name.replace(".csv", ".log"))
            
             # 创建局部的logger对象
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

            # 创建文件处理程序和标准输出处理程序
            file_handler = logging.FileHandler(filename=filename)
            stdout_handler = logging.StreamHandler(sys.stdout)
            file_handler.setLevel(logging.INFO)
            stdout_handler.setLevel(logging.INFO)

            # 设置处理程序的格式
            formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            stdout_handler.setFormatter(formatter)

            # 清空之前的处理程序
            logger.handlers = []

            # 将处理程序添加到局部logger对象
            logger.addHandler(file_handler)
            logger.addHandler(stdout_handler)

            # EXPRFN = "./bibench_processed/CMSprovider/dfs/expr_df.csv"
            EXPRFN = os.path.join(folder_path, dir_name, "dfs", "expr_df.csv")
            # print(EXPRFN)
            exprdf = pd.read_csv(EXPRFN)

            # inps = args.inp_to_eval.split(",")
            inps = [file_name.replace(".csv", "")]

            if args.workload in ["financial"]:
                inps = ['"{}"'.format(iname) for iname in inps]

            exprdf = exprdf[exprdf.input.isin(inps)]

            if args.skip_likes:
                exprdf = exprdf[~exprdf["filtersql"].str.contains("like")]
                exprdf = exprdf[~exprdf["filtersql"].str.contains("LIKE")]

            if args.db_name in ZDBS:
                exprdf = exprdf[~exprdf["filtersql"].str.contains("<")]
                exprdf = exprdf[~exprdf["filtersql"].str.contains(">")]
                exprdf = exprdf[~exprdf["filtersql"].str.contains("!=")]
                exprdf = exprdf[~exprdf["filtersql"].str.contains("NOT")]
                print("num queries left after filtering: ", len(exprdf))

            exprdf = exprdf.drop_duplicates("filtersql")

            if args.num_queries != -1 and args.num_queries < len(exprdf):
                exprdf = exprdf.head(args.num_queries)

            logger.info(str(args))
            logger.info("Number of sqls to evaluate: {}".format(len(exprdf)))

            # print("Number of sqls to evaluate: {}".format(len(exprdf)))

            sqls = exprdf["filtersql"].values

            ehashes = exprdf["exprhash"].values
            inputs = exprdf["input"].values
            truey = exprdf["RowCount"].values
            truey = np.maximum(truey, 1.0)

            rcs = run_filters(sqls, ehashes, inputs, truey, logger, csv_handler)
            rcs = np.array(rcs)
            rcs = np.maximum(1, rcs)

            qerrs = qerr_func(truey, rcs)
            # logging.info("QError, mean: {}, median: {}, 90p: {}".format(
                # np.mean(qerrs), np.median(qerrs), np.percentile(qerrs, 90)))
            # print("QError, mean: {}, median: {}, 90p: {}".format(
                # np.mean(qerrs), np.median(qerrs), np.percentile(qerrs, 90)))

            # TODO: evaluate cardinality accuracy
            # for qi, rc in enumerate(rcs):
                # if rc == 1:
                    # print(sqls[qi])

    csv_handler.close()
    print("数据已添加到 CSV 文件:", result_all_path)
args = read_flags()
main()
