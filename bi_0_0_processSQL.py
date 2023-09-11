import os

# 遍历当前目录下的文件
for filename in os.listdir("./sqlqueries"):
    # 使用下划线分割文件名
    parts = filename.split('_')
    if len(parts) >= 2:
        folder_name = parts[0]
        new_filename = parts[1]

        # 创建文件夹（如果不存在）
        folder_path = os.path.join("./NewSqls", folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 移动文件到文件夹并重命名
        new_file_path = os.path.join(folder_path, new_filename)
        os.rename("./sqlqueries/"+filename, new_file_path)
