import os
import csv
import shutil
import sqlparse

folder_path = "./benchmark"
# 遍历文件夹
dir_list = os.listdir(folder_path)
num = 0
output_file = "sql_without_where.csv"
# 打开输出 CSV 文件并写入标题行
with open(os.path.join(folder_path, output_file), mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["File", "SQL Statement"])

for dir_name in dir_list:
    if ".csv" in dir_name:
        continue
    
    # 输入文件夹和输出文件夹的路径
    input_folder = os.path.join(folder_path, dir_name, "queries")
    
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
                if("WHERE" not in sql_content) or (" AND " in sql_content and " OR " in sql_content):
                # if("WHERE" not in sql_content):
                    with open(os.path.join(folder_path, output_file), mode='a', newline='') as csv_file:
                        num += 1
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([input_path, sql_content])
            
print("num is ", num)
                    


