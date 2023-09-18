import os
import shutil
import re

def transform_quotes_to_lowercase(line):
    result = []
    in_quotes = False
    current_word = ""
    
    for char in line:
        if char == '"':
            if in_quotes:
                result.append(current_word.lower().replace(" ", ""))
                current_word = ""
            in_quotes = not in_quotes
        else:
            if in_quotes:
                current_word += char
            else:
                result.append(char)
    
    return ''.join(result)

print("========================================runnning bi_0_0_sql_process.py========================================")
# folder_path = "./bibench_processed"
folder_path = "./NewSqlsSmall"

# 遍历文件夹
dir_list = os.listdir(folder_path)

# notEqual = 0 #sql中包含<或>的sql数量

for dir_name in dir_list:
    if ".csv" in dir_name:
        continue
    
    # 输入文件夹和输出文件夹的路径
    input_folder = os.path.join(folder_path, dir_name, "queries")
    output_folder = input_folder.replace("queries", "queries_processed")

    # 确保输出文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        shutil.rmtree(output_folder) # 删除文件夹
        os.makedirs(output_folder)  # 重新创建文件夹

    # 列出输入文件夹下的所有文件
    files = os.listdir(input_folder)

    # 遍历文件列表
    for filename in files:
        
        # 检查文件是否为sql文件（忽略大小写）
        if filename.lower().endswith(".sql"):
            # 构造输入文件的完整路径
            input_path = os.path.join(input_folder, filename)
                       
            # 读取输入文件内容并转为小写，然后写入输出文件
            with open(input_path, "r") as input_file:
                sql_content = input_file.read()
                
                # 滤去(没有where)或(and和or都有的)
                if("WHERE" not in sql_content) or (" AND " in sql_content and " OR " in sql_content):
                    # print(input_path)
                    # print(sql_content)
                    continue
                
                # print(sql_content)
                sql_content = transform_quotes_to_lowercase(sql_content)
                sql_content = sql_content.replace("double", "double precision")
                
                # if "((" in sql_content:
                #     sql_content = sql_content.replace("((", "(")
                #     sql_content = sql_content.replace("))", ")")
                # print(sql_content)
                
                # if ">" in sql_content or "<" in sql_content:
                #     notEqual += 1
                #     print(input_path,"*******", sql_content)
                #     continue
                
                # 查找所有 "IN" 出现的位置
                in_positions = [match.end() for match in re.finditer(r'\bIN\b', sql_content)]

                # 获取每个 "IN" 后面的第一个 "(" 和 ")" 字符的位置
                parentheses_positions = []
                for pos in in_positions:
                    open_paren_pos = sql_content.find('(', pos)
                    close_paren_pos = sql_content.find(')', pos)
                    
                    if open_paren_pos != -1 and close_paren_pos != -1:
                        parentheses_positions.extend([open_paren_pos, close_paren_pos])
                    
                # 查找所有 "(" 和 ")" 的位置
                all_positions = [i for i, c in enumerate(sql_content) if c == '(' or c == ')']

                delete_positions = list(set(all_positions) - set(parentheses_positions))

                # 过滤字符串中所有不在上述找出的位置中的 "(" 和 ")"
                filtered_str = ''.join([c if i not in delete_positions else '' for i, c in enumerate(sql_content)])
                
                print("filtered_str is ", filtered_str)
                # 构造输出文件的完整路径，保持原文件名但转为小写
                output_filename = filename.lower()
                output_path = os.path.join(output_folder, output_filename)
                with open(output_path, "w") as output_file:
                    output_file.write(filtered_str)

    # print(f"notEqual is {notEqual}")