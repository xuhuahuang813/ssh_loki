import os
import shutil

def transform_quotes_to_lowercase(line):
    result = []
    in_quotes = False
    current_word = ""
    
    for char in line:
        if char == '"':
            if in_quotes:
                result.append(current_word.lower())
                current_word = ""
            in_quotes = not in_quotes
        else:
            if in_quotes:
                current_word += char
            else:
                result.append(char)
    
    return ''.join(result)

# 输入文件夹和输出文件夹的路径
input_folder = "./benchmark_small/CMSprovider/queries"
output_folder = input_folder.replace("queries", "queries_processed")

# 确保输出文件夹存在，如果不存在则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
else:
    # os.rmdir(output_folder)  # 删除文件夹
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
        
        # 构造输出文件的完整路径，保持原文件名但转为小写
        output_filename = filename.lower()
        output_path = os.path.join(output_folder, output_filename)
        
        # 读取输入文件内容并转为小写，然后写入输出文件
        with open(input_path, "r") as input_file:
            sql_content = input_file.read()
            # print(sql_content)
            sql_content = transform_quotes_to_lowercase(sql_content)
            sql_content = sql_content.replace("double", "double precision")
            # print(sql_content)
            with open(output_path, "w") as output_file:
                output_file.write(sql_content)

print("已完成文件内容转换和存储。")
