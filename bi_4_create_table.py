import argparse
import pandas as pd
import numpy as np
import string

import psycopg2 as pg
import os
import pdb
from collections import defaultdict
import sqlparse
import time
import random
import copy
import uuid
import logging
from sqlalchemy import create_engine

ALIAS_TO_TABS = {}

CREATE_TEMPLATE = "CREATE TABLE {TABLE_NAME} AS {SEL_SQL}"

NEW_NAME_FMT = "{INP}_{DATA_KIND}"
DROP_TEMPLATE = "DROP TABLE IF EXISTS {TABLE_NAME}"
ENGINE_CMD_FMT = """postgresql://{USER}:{PWD}@{HOST}:{PORT}/{DB}"""

NULL_VAL = "#NULL1234"
WK = "ceb"
if WK in ["ceb", "job"]:
    DBNAME="bibench"
else:
    DBNAME = WK

USER="postgres"
DBHOST="49.52.27.35"
PWD=""

def read_flags():
    parser = argparse.ArgumentParser()

    # parser.add_argument("--inp_fn", type=str, required=False,
    #         default="./bibench_processed/CMSprovider/results/cmsprovider_2.csv")

    parser.add_argument("--data_kind", type=str, required=False,
            default="gen_shuffle", help="suffix for the table")
    parser.add_argument("--port", type=int, required=False,
            default=5632, help="")

    return parser.parse_args()

def main():
    print("========================================bi_4_create_table.py========================================")

    # folder_path = "./bibench_processed"
    folder_path = "./NewSqlsSmall"
    
    # 遍历文件夹
    dir_list = os.listdir(folder_path)
    for dir_name in dir_list:
        
        if ".csv" in dir_name:
            continue
        dir_path = os.path.join(folder_path, dir_name, "results")
        file_list = os.listdir(dir_path)

        # 遍历sql文件
        for file_name in file_list:
            result_file_path = os.path.join(dir_path, file_name)  
            
            if os.path.exists(result_file_path):
                df = pd.read_csv(result_file_path)
                # df = df.drop(columns="Unnamed: 0")

            # basetable = os.path.basename(args.inp_fn).replace(".csv", "")
            basetable = result_file_path.split("/")[-1].replace(".csv", "")

            if basetable not in ALIAS_TO_TABS:
                pg_orig_table = basetable
            else:
                pg_orig_table = ALIAS_TO_TABS[basetable]

            new_table_name = NEW_NAME_FMT.format(INP = basetable,
                                            DATA_KIND = args.data_kind)
            drop_sql = DROP_TEMPLATE.format(TABLE_NAME = new_table_name)
            con = pg.connect(user=USER, host=DBHOST, port=args.port,
                    password=PWD, database=DBNAME)

            cursor = con.cursor()
            cursor.execute(drop_sql)
            con.commit()

            cursor.close()
            con.close()


            if "shuffle2" in args.data_kind:
                df = df.sample(frac=1.0)

                for k in df.keys():
                    df[k] = df[k].apply(lambda x: x if pd.notnull(x) else
                            ''.join(random.choice(string.ascii_uppercase
                                + string.digits) for _ in range(random.randint(1,50))))

                print("done updating NULL values w/ random strings")

            elif "shuffle" in args.data_kind:
                df = df.sample(frac=1.0)

            fixedkeys = {}
            for dk in df.keys():
                fixedkeys[dk] = dk.replace('"','')
            df = df.rename(columns=fixedkeys)
            print(df.keys())

            if args.data_kind == "true_cols":
                if basetable not in ALIAS_TO_TABS:
                    inp_table = basetable
                else:
                    inp_table = ALIAS_TO_TABS[basetable]

                cols = ",".join(list(df.keys()))

                if DBNAME == "bibench":
                    cols = "id," + cols
                elif DBNAME == "financial":
                    cols = "index," + cols

                sel_sql = "SELECT {} FROM {}".format(cols, inp_table)
                print(sel_sql)
                create_sql = CREATE_TEMPLATE.format(TABLE_NAME = new_table_name,
                                                    SEL_SQL = sel_sql)
                print(create_sql)
                con = pg.connect(user=USER, host=DBHOST, port=args.port,
                        password=PWD, database=DBNAME)

                cursor = con.cursor()
                cursor.execute(create_sql)
                con.commit()

                cursor.close()
                con.close()

            elif args.data_kind == "random_domain":
                # update each column to be from same domain but randomly chosen
                newdf = copy.deepcopy(df)
                for key in df.keys():
                    domain = list(set(df[key].dropna()))
                    newdf[key] = np.array([random.choice(domain) for _ in range(len(df))])
                    # newdf[key.replace('"','')] = np.array([random.choice(domain) for _ in range(len(df))])

                df = newdf
                engine_cmd = ENGINE_CMD_FMT.format(USER = USER,
                                                PWD = PWD,
                                                HOST = DBHOST,
                                                PORT = args.port,
                                                DB = DBNAME)

                engine = create_engine(engine_cmd)
                df.to_sql(new_table_name, engine)

            elif args.data_kind == "random_domain2":
                # update each column to be from same domain but randomly chosen
                # newdf = copy.deepcopy(df)

                for key in df.keys():
                    domain = list(set(df[key].dropna()))
                    print(domain)
                    print(len(domain))
                    domain.append(None)
                    df[key] = np.array([random.choice(domain) for _ in range(len(df))])

                # df = newdf
                print(df.head(30))
                engine_cmd = ENGINE_CMD_FMT.format(USER = USER,
                                                PWD = PWD,
                                                HOST = DBHOST,
                                                PORT = args.port,
                                                DB = DBNAME)

                engine = create_engine(engine_cmd)
                df.to_sql(new_table_name, engine)

            elif args.data_kind == "random_domain3":
                engine_cmd = ENGINE_CMD_FMT.format(USER = USER,
                                                PWD = PWD,
                                                HOST = DBHOST,
                                                PORT = args.port,
                                                DB = DBNAME)

                engine = create_engine(engine_cmd)
                df = pd.read_sql_query('select * from {}'.format(pg_orig_table),con=engine)
                print(df.keys())

                for key in df.keys():
                    domain = list(set(df[key].dropna()))
                    domain.append(None)
                    df[key] = np.array([random.choice(domain) for _ in range(len(df))])

                print(df.head(30))
                # engine_cmd = ENGINE_CMD_FMT.format(USER = USER,
                                                # PWD = PWD,
                                                # HOST = DBHOST,
                                                # args.port = args.port,
                                                # DB = DBNAME)

                # engine = create_engine(engine_cmd)
                df.to_sql(new_table_name, engine)

            else:
                engine_cmd = ENGINE_CMD_FMT.format(USER = USER,
                                                PWD = PWD,
                                                HOST = DBHOST,
                                                PORT = args.port,
                                                DB = DBNAME)
                engine = create_engine(engine_cmd, client_encoding='utf8')
                print("new_table_name is ", new_table_name)
                df.to_sql(new_table_name, engine)
                print("finish create table")

args = read_flags()
main()
