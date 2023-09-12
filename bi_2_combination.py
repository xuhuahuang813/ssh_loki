# -*- coding: utf-8 -*-

import pandas as pd
import psycopg2 as pg
import os
import pdb
from collections import defaultdict
import sqlparse
import time
import json
from itertools import combinations, product

WK = "ceb"
if WK in ["ceb", "job"]:
    DBNAME = "bibench"
else:
    DBNAME = WK

USER = "postgres"
DBHOST = "49.52.27.35"
PORT = 5632
PWD = ""


def get_total(sql):
    if sql == "X":
        return -1, -1

    con = pg.connect(user=USER, host=DBHOST, port=PORT,
                     password=PWD, database=DBNAME, client_encoding="UTF8")
    cursor = con.cursor()

    totalsql = sql[0:sql.find("WHERE")]
    cursor.execute(totalsql)
    output = cursor.fetchall()
    total = output[0][0]

    return total


MII2_FIXED = "mii2.info ~ '^(?:[1-9]\d*|0)?(?:\.\d+)?$' AND mii2.info::float"
MII1_FIXED = "mii1.info ~ '^(?:[1-9]\d*|0)?(?:\.\d+)?$' AND mii1.info::float"
MII_FIXED = "mii.info ~ '^(?:[1-9]\d*|0)?(?:\.\d+)?$' AND mii.info::float"


def get_rowcount(sql):
    global CARDCACHE
    if sql == "X":
        return -1, -1
    # mii2 WHERE mii2.info ~ '^(?:[1-9]\d*|0)?(?:\.\d+)?$' AND

    if "mii2.info::float" in sql:
        sql = sql.replace("mii2.info::float", MII2_FIXED)
    elif "mii1.info::float" in sql:
        sql = sql.replace("mii1.info::float", MII1_FIXED)
    elif "mii.info::float" in sql:
        sql = sql.replace("mii.info::float", MII_FIXED)

    if sql in CARDCACHE:
        return CARDCACHE[sql]

    con = pg.connect(user=USER, host=DBHOST, port=PORT,
                     password=PWD, database=DBNAME, client_encoding="UTF8")
    cursor = con.cursor()
    try:
        cursor.execute(sql)
    except Exception as e:
        print("Exception!")
        print(e)
        print(sql)
        # if "mii" not in sql:
        # pdb.set_trace()
        return -1, -1

    output = cursor.fetchall()
    rc = output[0][0]

    CARDCACHE[sql] = rc
    return rc


def parse_filter(sql):
    # print("parse_filter sql is ", sql)
    coldata = defaultdict(list)
    sql = sql[sql.find("WHERE")+5:]
    ands = sql.split("AND")

    for curexpr in ands:
        curexpr = curexpr.strip()
        if "between" in curexpr.lower():
            print("skipping between")
            continue

        if " in " in curexpr.lower():
            colname = curexpr[0:curexpr.lower().find(" ")]
            # old code
            # colvalstr = curexpr[curexpr.find("(")+1:]
            # colvalstr = colvalstr.replace(")", "", 1)
            # colvals = colvalstr.split(",")

            # for cv in colvals:
            # if "'" not in cv:
            # print(cv)
            # # pdb.set_trace()
            # coldata[colname].append(" = " + cv)

            sqp = sqlparse.parse(curexpr)
            sqp = sqp[0][0]

            par_token = None
            for idx, token in enumerate(sqp):
                if "Parenthesis" in str(type(token)):
                    par_token = token
                    break

            assert par_token is not None
            for token in par_token:
                if "Identifier" in str(type(token)):
                    # print(dir(token))
                    # # pdb.set_trace()
                    # allvals = token.value.split(",")
                    # print(allvals)
                    flats = token.flatten()
                    for val in flats:
                        val = str(val)
                        if val == "," or val == " ":
                            continue
                        # print(val)
                        coldata[colname].append(" = " + val)

            continue

        if len(curexpr.replace(" ", "")) == 0:
            continue

        sqp = sqlparse.parse(curexpr)
        sqp = sqp[0][0]

        colname, literal = None, None
        op = None

        for idx, token in enumerate(sqp):
            if "Identifier" in str(type(token)):
                colname = str(token)

            elif "Comparison" in str(token.ttype):
                op = str(token)

            elif "Literal" in str(token.ttype):
                literal = str(token)

            elif "Function" in str(type(token)) or \
                    "Operation" in str(type(token)):
                literal = str(token)

        if literal is None:
            print("literal None!")
            print(token)
            print(sql)
            # continue
            # pdb.set_trace()

        if op is None:
            print("op None")
            # pdb.set_trace()

        if colname is None:
            print("colname None")
            print(str(sqp))
            # pdb.set_trace()

        coldata[colname].append(op + " " + literal)

    return coldata


def get_rowcounts_consts(sqls, exprhashes, inputs, jobids):
    # 创建空字典列表
    countdata = defaultdict(list)

    for si, sql in enumerate(sqls):
        # print("si is ", si)
        coldata = parse_filter(sql)
        ehash = exprhashes[si]
        expr_inp = inputs[si]
        expr_jid = jobids[si]

        '''
        使用排列组合支持多列
        '''
        all_combinations = []

        for group_size in range(1, len(coldata) + 1):
            for combination_keys in combinations(coldata.keys(), group_size):
                values_combinations = []
                for key in combination_keys:
                    values_combinations.append(coldata[key])
                for combo in product(*values_combinations):
                    combined_dict = {key: value.lstrip() for key, value in zip(combination_keys, combo)}
                    all_combinations.append(combined_dict)

        # print(all_combinations)

        for c_i in all_combinations:
            newsql_start = sql[0:sql.find("WHERE")-1]
            col_total_sql = newsql_start
            totalc = get_rowcount(col_total_sql)

            newsql = newsql_start + " WHERE " + " AND ".join([f"{key} {value}" for key, value in c_i.items()])

            # print(newsql)

            rc = get_rowcount(newsql)

            countdata["exprhash"].append(ehash)
            countdata["RowCount"].append(rc)
            countdata["InputCardinality"].append(totalc)
            countdata["RowSql"].append(newsql)
            countdata["Column"].append("|".join([key for key, value in c_i.items()]))
            countdata["input"].append(expr_inp)
            countdata["jobid"].append(expr_jid)
            countdata["Op"].append("|".join([value[0:value.find(" ")] for key, value in c_i.items()]))
            countdata["Value"].append("|".join([value[value.find(" ")+1:] for key, value in c_i.items()]))
        '''
        原代码只支持两列
        '''
        # # per column-literal pair
        # # per column,column - literal,literal pairs
        # for curcol, colvals in coldata.items():
        #     newsql_start = sql[0:sql.find("WHERE")-1]
        #     col_total_sql = newsql_start
        #     totalc = get_rowcount(col_total_sql)

        #     newsql_start += " WHERE " + curcol + " "

        #     for cv in colvals:
        #         newsql = newsql_start + cv
        #         rc = get_rowcount(newsql)
        #         countdata["exprhash"].append(ehash)
        #         countdata["RowCount"].append(rc)
        #         countdata["InputCardinality"].append(totalc)
        #         countdata["RowSql"].append(newsql)
        #         countdata["Column"].append(curcol)
        #         countdata["input"].append(expr_inp)
        #         countdata["jobid"].append(expr_jid)

        #         cv = cv.strip()
        #         op = cv[0:cv.find(" ")]
        #         colval = cv[cv.find(" ")+1:]
        #         countdata["Op"].append(op)
        #         countdata["Value"].append(colval)

        # # combining colvals from two columns
        # seencols = set()
        # print("coldata.items is:", coldata.items())
        # for curcol, colvals in coldata.items():
        #     for curcol2, colvals2 in coldata.items():
        #         if curcol == curcol2:
        #             continue
        #         allcols = [curcol,curcol2]
        #         #尝试
        #         allcols = str(sorted(allcols))

        #         # 代码有误？allcols.sort()返回值是None
        #         # allcols = str(allcols.sort())

        #         if allcols in seencols:
        #             continue
        #         seencols.add(allcols)

        #         col_total_sql = sql[0:sql.find("WHERE")-1]
        #         totalc = get_rowcount(col_total_sql)

        #         for cv in colvals:
        #             newsql_start = sql[0:sql.find("WHERE")-1]

        #             newsql_start += " WHERE " + curcol + " " + cv

        #             for cv2 in colvals2:
        #                 newsql = newsql_start + " AND " + curcol2 + " " + cv2
        #                 rc = get_rowcount(newsql)

        #                 countdata["exprhash"].append(ehash)
        #                 countdata["RowCount"].append(rc)
        #                 countdata["InputCardinality"].append(totalc)
        #                 countdata["RowSql"].append(newsql)
        #                 countdata["Column"].append(curcol + "|" + curcol2)
        #                 countdata["input"].append(expr_inp)
        #                 countdata["jobid"].append(expr_jid)

        #                 cv = cv.strip()
        #                 op = cv[0:cv.find(" ")]
        #                 colval = cv[cv.find(" ")+1:]

        #                 cv2 = cv2.strip()
        #                 op2 = cv2[0:cv2.find(" ")]
        #                 colval2 = cv2[cv2.find(" ")+1:]

        #                 countdata["Op"].append(op + "|" + op2)
        #                 countdata["Value"].append(colval + "|" + colval2)

    countdf = pd.DataFrame(countdata)
    return countdf


print("========================================bi_2_get_const_rowcounts.py========================================")

# folder_path = "./bibench_processed"
folder_path = "./NewSqlsSmall"

# 遍历文件夹
dir_list = os.listdir(folder_path)

for dir_name in dir_list:
    if ".csv" in dir_name:
        continue

    EXPRFN = os.path.join(folder_path, dir_name, "dfs", "expr_df.csv")
    OPFN = os.path.join(folder_path, dir_name, "dfs", "op_df.csv")

    exprdf = pd.read_csv(EXPRFN)
    opdf = pd.read_csv(OPFN)

    LITERAL_DATA_FN = os.path.join(folder_path, dir_name, "dfs", "literal_df.csv")

    CARDCACHE = {}

    # 尝试：目前只有一个sql，如果还使用下采样，会导致dataFrame为空。尝试注释掉下一句
    # exprdf = exprdf.sample(frac=0.001)

    sqls = exprdf["filtersql"].values
    jobids = exprdf["jobid"].values
    inputs = exprdf["input"].values
    aliases = exprdf["alias"].values
    exprhashes = exprdf["exprhash"].values

    # for each sql expression, divide into each AND operator, and each IN (...)
    # print("sqls len is ", len(sqls))

    start = time.time()
    rdata = get_rowcounts_consts(sqls, exprhashes, inputs, jobids)

    # print("took: ", time.time()-start)

    # 尝试注释Selectivity
    # rdata["Selectivity"] = rdata.apply(lambda x: float(x["RowCount"]) / x["InputCardinality"] ,axis=1)
    # 尝试注释tmp2
    # tmp2 = rdata[rdata["RowCount"] != -1]
    # print(opdf.keys())

    # print(LITERAL_DATA_FN)
    rdata.to_csv(LITERAL_DATA_FN, index=False)
    # print(OPFN)
    opdf.to_csv(OPFN, index=False)

    # pdb.set_trace()

    print("finish ", dir_name, "\n")
