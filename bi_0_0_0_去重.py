import os
import shutil

# 指定原始文件夹路径
source_folder_path = "./sqlqueries"

# 指定目标文件夹路径
target_folder_path = "./sqlqueriesReDup"

# 用于存储文件内容的字典，键是文件内容的散列值，值是具有相同内容的文件列表
file_contents = {}

# 用于跟踪处理前文件数量和去重后文件数量的计数器
original_file_count = 0
unique_file_count = 0

# 遍历原始文件夹下的文件
for filename in os.listdir(source_folder_path):
    file_path = os.path.join(source_folder_path, filename)

    # 忽略文件夹
    if os.path.isdir(file_path):
        continue

    # 增加处理前文件数量计数器
    original_file_count += 1

    # 读取文件内容并计算内容的哈希值
    with open(file_path, 'rb') as file:
        file_content = file.read()
        content_hash = hash(file_content)

    # 如果哈希值已存在于字典中，说明内容相同
    if content_hash in file_contents:
        file_contents[content_hash].append(filename)
    else:
        file_contents[content_hash] = [filename]
        # 增加去重后文件数量计数器
        unique_file_count += 1

# 创建目标文件夹（如果不存在）
if not os.path.exists(target_folder_path):
    os.makedirs(target_folder_path)

# 找到内容相同的文件，并保留字典序最小的文件
for hash_value, filenames in file_contents.items():
    if len(filenames) >= 1:
        filenames.sort()  # 对文件名进行字典序排序
        smallest_filename = filenames[0]  # 获取字典序最小的文件名

        # 打印内容相同的文件名
        print(f"内容相同的文件：{', '.join(filenames)}")

        # 复制字典序最小的文件到目标文件夹
        source_file_path = os.path.join(source_folder_path, smallest_filename)
        target_file_path = os.path.join(target_folder_path, smallest_filename)
        shutil.copy(source_file_path, target_file_path)

print("处理前文件数量:", original_file_count)
print("去重后文件数量:", unique_file_count)
print("处理完成。")
