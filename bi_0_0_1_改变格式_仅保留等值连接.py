import os
import shutil

total_num = 0
save_num = 0

# 遍历当前目录下的文件
for filename in os.listdir("./sqlqueriesReDup"):
    total_num += 1
    # 使用下划线分割文件名
    parts = filename.split('_')
    if len(parts) >= 2:
        folder_name = parts[0]
        new_filename = parts[1]

        # 创建文件夹（如果不存在）
        folder_path = os.path.join("./NewSqlsSmall", folder_name, "queries")

        # 构建文件的源路径和目标路径
        source_file_path = os.path.join("./sqlqueriesReDup", filename)
        new_file_path = os.path.join(folder_path, new_filename)

        # 打开文件并检查内容
        with open(source_file_path, 'r') as file:
            file_content = file.read()

        # 检查文件内容是否包含 ">"
        if ">" in file_content or "<" in file_content:
            print(f"文件 {filename} 包含 '>'，将不会拷贝。")
        else:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 使用shutil.copy复制文件
            shutil.copy(source_file_path, new_file_path)
            save_num += 1
print(total_num, " ", save_num)
