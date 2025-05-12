import numpy as np
from plyfile import PlyData
import os

def analyze_ply(ply_path):
    """分析 PLY 文件并提取关键信息，保存到文本文件"""
    print(f"正在分析 {ply_path}...")
    plydata = PlyData.read(ply_path)
    
    # 获取点的总数
    vertex_count = len(plydata['vertex'])
    
    # 获取数据规范 (字段和格式)
    vertex_properties = [prop.name for prop in plydata['vertex'].properties]
    vertex_formats = [prop.val_dtype for prop in plydata['vertex'].properties]
    
    # 提取 XYZ 坐标
    x = plydata['vertex']['x']
    y = plydata['vertex']['y']
    z = plydata['vertex']['z']
    
    xyz = np.column_stack((x, y, z))
    
    # 创建结果文本文件
    base_name = os.path.splitext(ply_path)[0]
    info_file = f"{base_name}_info.txt"
    xyz_file = f"{base_name}_xyz.txt"
    
    # 保存基本信息
    with open(info_file, 'w') as f:
        f.write(f"PLY 文件: {ply_path}\n")
        f.write(f"点数量: {vertex_count}\n")
        f.write(f"字段列表: {', '.join(vertex_properties)}\n")
        f.write(f"字段格式: {', '.join(str(fmt) for fmt in vertex_formats)}\n")
    
    # 保存 XYZ 坐标
    with open(xyz_file, 'w') as f:
        f.write("# 点云中每个点的 X Y Z 坐标\n")
        f.write("# 格式: X Y Z\n")
        for i in range(xyz.shape[0]):
            f.write(f"{xyz[i, 0]} {xyz[i, 1]} {xyz[i, 2]}\n")
    
    print(f"基本信息已保存到 {info_file}")
    print(f"XYZ 坐标已保存到 {xyz_file}")

if __name__ == "__main__":
    # 查找当前目录下的 skybox.ply 文件
    ply_path = "skybox.ply"
    if not os.path.exists(ply_path):
        print(f"错误: 在当前目录下找不到 {ply_path}")
    else:
        analyze_ply(ply_path)
