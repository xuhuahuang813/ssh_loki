input_file = "./benchmark_small/CMSprovider/queries/1.sql"
output_file = "benchmark_small/CMSprovider/queries/1_lower.sql"

# 读取 SQL 文件并将内容转为小写
with open(input_file, "r") as f:
    sql_content = f.read().lower().replace('"', '')

# 将转换后的内容写入输出文件
with open(output_file, "w") as f:
    f.write(sql_content)
