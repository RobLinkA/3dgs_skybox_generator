import struct

def read_binary_ply_data(ply_file_path, num_vertices_to_read=5):
    """
    读取二进制PLY文件并提取前几个顶点的数据
    
    参数:
        ply_file_path: PLY文件路径
        num_vertices_to_read: 要读取的顶点数量
    """
    with open(ply_file_path, 'rb') as file:
        # 先跳过头部
        line = file.readline()
        while line and b"end_header" not in line:
            line = file.readline()
        
        # 现在我们在数据部分的开始
        # 每个顶点有60个float值 (根据你的头部信息)
        float_size = 4  # 每个浮点数占4个字节
        vertex_size = 60 * float_size  # 每个顶点的总字节数
        
        vertices = []
        for i in range(num_vertices_to_read):
            vertex_data = file.read(vertex_size)
            if not vertex_data or len(vertex_data) < vertex_size:
                break
                
            # 解析顶点数据
            values = struct.unpack('<' + 'f' * 60, vertex_data)
            vertices.append(values)
        
        return vertices

if __name__ == "__main__":
    ply_file_path = "skybox.ply"  # 替换为你的文件路径
    vertices = read_binary_ply_data(ply_file_path)
    
    if vertices:
        print(f"读取了 {len(vertices)} 个顶点的数据")
        
        # 打印顶点信息，重点关注前面的几个值
        for i, vertex in enumerate(vertices):
            print(f"\n顶点 {i+1}:")
            print(f"  位置 (x, y, z): ({vertex[0]}, {vertex[1]}, {vertex[2]})")
            print(f"  法线 (nx, ny, nz): ({vertex[3]}, {vertex[4]}, {vertex[5]})")
            print(f"  颜色 (f_dc_0, f_dc_1, f_dc_2): ({vertex[6]}, {vertex[7]}, {vertex[8]})")
            print(f"  到原点距离: {(vertex[0]**2 + vertex[1]**2 + vertex[2]**2)**0.5}")
            
            # 对于其余参数，我们只打印一些范围统计
            rest_values = vertex[9:54]  # f_rest_0 到 f_rest_44
            print(f"  f_rest_* 范围: [{min(rest_values)}, {max(rest_values)}]")
            
            print(f"  不透明度 (opacity): {vertex[54]}")
            print(f"  缩放 (scale_0, scale_1, scale_2): ({vertex[55]}, {vertex[56]}, {vertex[57]})")
            print(f"  旋转 (rot_0, rot_1, rot_2, rot_3): ({vertex[58]}, {vertex[59]}, {vertex[60] if len(vertex) > 60 else 'N/A'}, {vertex[61] if len(vertex) > 61 else 'N/A'})")
    else:
        print("无法读取顶点数据")
