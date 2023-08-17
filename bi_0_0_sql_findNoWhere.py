import os
import csv
import shutil
import sqlparse

folder_path = "./benchmark"
dir_list = os.listdir(folder_path)

noWhere_num = 0
andOr_num = 0
processed_num = 0
isNull_num = 0
hasCast_num = 0
alwaysTrue_num = 0

special_num = 0


# output_file = "sql_without_where.csv"
# # 打开输出 CSV 文件并写入标题行
# with open(os.path.join(folder_path, output_file), mode='w', newline='') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     csv_writer.writerow(["File", "SQL Statement"])

def create_folder_with_os(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True) #递归创建
    except Exception as e:
        print("An error occurred:", str(e))

no_where_folder = "bibench_noWhere_mutiWhere"
and_or_folder = "bibench_andOR"
processed_folder = "bibench_processed"
is_null_folder = "bibench_isNull"
has_cast_folder = "bibench_hasCast"
alwaysTrue_folder = "bibench_alwaysTrue"
# create_folder_with_os(no_where_folder)
# create_folder_with_os(and_or_folder)
create_folder_with_os(processed_folder)
# create_folder_with_os(is_null_folder)
# create_folder_with_os(has_cast_folder)
# create_folder_with_os(alwaysTrue_folder)


for dir_name in dir_list:
    if ".csv" in dir_name:
        continue
    
    # **********************************************************************************************************************
    
    # 输入文件夹和输出文件夹的路径
    input_folder = os.path.join(folder_path, dir_name, "queries_filter")
    
    # 列出输入文件夹下的所有文件
    files = os.listdir(input_folder)

    # 遍历文件列表
    for filename in files:
        
        # **********************************************************************************************************************
        # if filename != "26.sql" and filename != "29.sql":
        #     continue
        # if filename != "2.sql":
        #     continue
        
        if dir_name == "CityMaxCapita" or dir_name == "TableroSistemaPenal" or dir_name == "NYC":
            special_num += 1
            continue
        
        # 3_loki.py处理不了的
        # Hatred 和 USCensus 和 Wins 是 IndexError: list index out of range
        # IGlocations1是li_.csv为空
        # if dir_name == "Hatred" or dir_name == "IGlocations1" or dir_name == "USCensus" or dir_name == "Wins":
            # special_num += 1
            # continue
    
        # 检查文件是否为sql文件（忽略大小写）
        if filename.lower().endswith(".sql"):
            # 构造输入文件的完整路径
            input_path = os.path.join(input_folder, filename)
            # 读取输入文件内容并转为小写，然后写入输出文件
            with open(input_path, "r") as input_file:
                sql_content = input_file.read() 
                
                sql_content.replace("((", "(")    
                sql_content.replace("))", ")") 
                    
                if(sql_content.count("WHERE") == 0 or sql_content.count("WHERE") >= 2):
                    # output_filename = os.path.join(no_where_folder, dir_name, "queries")
                    # create_folder_with_os(output_filename)
                    # with open(os.path.join(no_where_folder, dir_name, "queries", filename), 'w') as output_file:
                    #         output_file.write(sql_content)
                    noWhere_num += 1
                elif(" AND " in sql_content and " OR " in sql_content):
                    # output_filename = os.path.join(and_or_folder, dir_name, "queries")
                    # create_folder_with_os(output_filename)
                    # with open(os.path.join(and_or_folder, dir_name, "queries", filename), 'w') as output_file:
                    #         output_file.write(sql_content)
                    andOr_num += 1
                elif("is null" in sql_content or "IS NULL" in sql_content):
                    # output_filename = os.path.join(is_null_folder, dir_name, "queries")
                    # create_folder_with_os(output_filename)
                    # with open(os.path.join(is_null_folder, dir_name, "queries", filename), 'w') as output_file:
                    #         output_file.write(sql_content)
                    isNull_num += 1
                elif("CAST" in sql_content.split("WHERE")[-1] or "cast" in sql_content.split("WHERE")[-1]):
                    # output_filename = os.path.join(has_cast_folder, dir_name, "queries")
                    # create_folder_with_os(output_filename)
                    # with open(os.path.join(has_cast_folder, dir_name, "queries", filename), 'w') as output_file:
                    #         output_file.write(sql_content)
                    hasCast_num += 1
                elif("'' = ''" in sql_content):
                    # output_filename = os.path.join(alwaysTrue_folder, dir_name, "queries")
                    # create_folder_with_os(output_filename)
                    # with open(os.path.join(alwaysTrue_folder, dir_name, "queries", filename), 'w') as output_file:
                    #         output_file.write(sql_content)
                    alwaysTrue_num += 1
                else:
                    output_filename = os.path.join(processed_folder, dir_name, "queries")
                    create_folder_with_os(output_filename)
                    with open(os.path.join(processed_folder, dir_name, "queries", filename), 'w') as output_file:
                            output_file.write(sql_content)    
                    processed_num += 1
                    
print("\nnoWhere_num is ", noWhere_num)
print("andOr_num is ", andOr_num)
print("isNull_num is ", isNull_num)
print("hasCast_num is ", hasCast_num)
print("processed_num is ", processed_num)
print("alwaysTrue_num is ", alwaysTrue_num)
print("special_num is ", special_num)
total_sum = alwaysTrue_num + andOr_num + processed_num + noWhere_num + isNull_num + hasCast_num + special_num
print("Total sum = ", total_sum)
