import copy
import numpy as np
import pandas as pd


def get_constraints_df(c_df, table, max_cols=1):
    constraints_df = c_df.where(c_df['input'] == table).dropna()
    
    max_cols_ids = constraints_df['Column'].str.split('|').apply(len).idxmax()
    max_cols = len(constraints_df.loc[max_cols_ids]['Column'].split("|"))
    print(constraints_df.loc[max_cols_ids]['Column'])
    print("max_cols", max_cols)
    
    constraints_df['Value'] = constraints_df['Value'].astype(str)
    constraints_df['opstring'] = constraints_df['Column'] + constraints_df['Op'] + constraints_df['Value']
    constraints_df = constraints_df.join(constraints_df['Column'].str.split('|', expand=True).add_prefix('Column'))
    constraints_df = constraints_df.join(constraints_df['Op'].str.split('|', expand=True).add_prefix('Op'))
    constraints_df = constraints_df.join(constraints_df['Value'].str.split('|', expand=True).add_prefix('Value'))
    for col in [f'Column{i}' for i in range(max_cols)]:
        constraints_df[col] = constraints_df[col].str.extract(r'\S+\.(\S+)')
    return constraints_df


def get_table_cardinality(constraints_df):
    return int(constraints_df['InputCardinality'].max())


def get_co_optimized_columns(constraints_df, columns, max_cols=1):
    max_cols_ids = constraints_df['Column'].str.split('|').apply(len).idxmax()
    max_cols = len(constraints_df.loc[max_cols_ids]['Column'].split("|"))
    print(constraints_df.loc[max_cols_ids]['Column'])
    print("max_cols", max_cols)
    
    co_optimized_cols = {column: set() for column in columns}
    for row in constraints_df[constraints_df.columns & [f'Column{i}' for i in range(max_cols)]].iterrows():
        combo = [x for x in list(row[1].dropna()) if x is not None]
        if len(combo) > 1:
            for col in combo:
                cols = set(combo)
                cols.remove(col)
                co_optimized_cols[col] |= cols
    return co_optimized_cols


def get_programs(co_optimized_cols):
    programs = []
    for col, co in co_optimized_cols.items():
        closure = set([col]) | co
        prev_len = 0
        while len(closure) > prev_len:
            prev_len = len(closure)
            new_closure = copy.deepcopy(closure)
            for col2 in closure:
                new_closure |= co_optimized_cols[col2]
            closure = new_closure
        if closure not in programs:
            programs.append(closure)
    return programs


def parse_constraints(program, constraints_df):
    constraints = {}
    max_cols_ids = constraints_df['Column'].str.split('|').apply(len).idxmax()
    max_cols = len(constraints_df.loc[max_cols_ids]['Column'].split("|"))
    print(constraints_df.loc[max_cols_ids]['Column'])
    print("max_cols", max_cols)
    

    
    # # 选择列名包含 "Column" 字符串的列
    # selected_columns = [col for col in constraints_df.columns if "Column" in col]

    # # 对选定的列名进行排序
    # selected_columns.sort()
    
    for row in constraints_df.itertuples():  # Deal with input format mess
        if max_cols == 3:
            columns = [row.Column0, row.Column1, row.Column2] if not pd.isnull(row.Column0) and not pd.isnull(row.Column1) else [row.Column0]
            ops = [row.Op0, row.Op1, row.Op2] if not pd.isnull(row.Op0) and not pd.isnull(row.Op1) else [row.Op0]
            values = [row.Value0, row.Value1, row.Value2] if not pd.isnull(row.Value0) and not pd.isnull(row.Value1) else [row.Value0]
        elif max_cols == 2:
            columns = [row.Column0, row.Column1] if not pd.isnull(row.Column0) and not pd.isnull(row.Column1) else [row.Column0]
            ops = [row.Op0, row.Op1] if not pd.isnull(row.Op0) and not pd.isnull(row.Op1) else [row.Op0]
            values = [row.Value0, row.Value1] if not pd.isnull(row.Value0) and not pd.isnull(row.Value1) else [row.Value0]
        else:
            columns = [row.Column0]
            ops = [row.Op0]
            values = [row.Value0]
        if len(set(columns).intersection(set(program))) == 0:  # Kick out constraints that are not for this program
            continue

        values = [value.replace('\'', '') for value in values]
        # Sorting by col ensures proper uniqueness above
        row_constraints = tuple(sorted([(col, op, val) for col, op, val in zip(columns, ops, values)]))
        cardinality = int(row.RowCount)
        if row_constraints not in constraints or constraints[row_constraints] < cardinality:
            constraints[row_constraints] = cardinality
    return constraints
