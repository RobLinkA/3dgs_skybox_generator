import numpy as np
from PIL import Image
import struct
import os
import math
import glob

def generate_ground_plane(image_path, output_file, num_points, size):
    """
    将图像转换为XZ平面上的点云，使用内切圆
    size: 平面的直径
    """
    # 加载地面图像
    ground_img = Image.open(image_path)
    img_width, img_height = ground_img.size
    
    # 确定圆的中心和半径
    center_x = img_width / 2
    center_y = img_height / 2
    img_radius = min(center_x, center_y)
    
    # 计算点数开方，用于均匀分布
    sqrt_points = int(math.sqrt(num_points))
    actual_points = 0  # 用于统计实际生成的点数
    
    # 预先生成点位置
    points = []
    colors = []
    
    # 使用极坐标方式生成点（从内到外生成圆）
    for radius_idx in range(sqrt_points):
        # 生成从0到1的半径比例
        radius_ratio = radius_idx / (sqrt_points - 1)
        
        # 确定当前半径上的点数，外圈更多
        points_in_ring = max(1, int(radius_ratio * sqrt_points * 3.14))
        
        for theta_idx in range(points_in_ring):
            # 计算极坐标
            theta = 2 * math.pi * theta_idx / points_in_ring
            radius = radius_ratio * size / 2
            
            # 转换为笛卡尔坐标
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            
            # 归一化半径从圆心到边缘
            norm_radius = radius_ratio
            
            # 从极坐标映射到图像坐标
            img_x = int(center_x + norm_radius * img_radius * math.cos(theta))
            img_y = int(center_y + norm_radius * img_radius * math.sin(theta))
            
            # 确保坐标在图像范围内
            if 0 <= img_x < img_width and 0 <= img_y < img_height:
                # 获取图像像素颜色
                pixel = ground_img.getpixel((img_x, img_y))
                
                # 如果图像是RGB格式
                if len(pixel) == 3:
                    r, g, b = pixel
                # 如果图像是RGBA格式
                elif len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r = g = b = pixel
                
                # 将RGB值归一化后乘以常数（基于示例数据）
                r_norm = (r / 255.0) * 1.7
                g_norm = (g / 255.0) * 1.7
                b_norm = (b / 255.0) * 1.7
                
                points.append((x, 0, z))
                colors.append((r_norm, g_norm, b_norm))
                actual_points += 1
    
    # 准备PLY文件头部
    ply_header = f"""ply
format binary_little_endian 1.0
element vertex {actual_points}
property float x
property float y
property float z
property float nxx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float f_rest_0
property float f_rest_1
property float f_rest_2
property float f_rest_3
property float f_rest_4
property float f_rest_5
property float f_rest_6
property float f_rest_7
property float f_rest_8
property float f_rest_9
property float f_rest_10
property float f_rest_11
property float f_rest_12
property float f_rest_13
property float f_rest_14
property float f_rest_15
property float f_rest_16
property float f_rest_17
property float f_rest_18
property float f_rest_19
property float f_rest_20
property float f_rest_21
property float f_rest_22
property float f_rest_23
property float f_rest_24
property float f_rest_25
property float f_rest_26
property float f_rest_27
property float f_rest_28
property float f_rest_29
property float f_rest_30
property float f_rest_31
property float f_rest_32
property float f_rest_33
property float f_rest_34
property float f_rest_35
property float f_rest_36
property float f_rest_37
property float f_rest_38
property float f_rest_39
property float f_rest_40
property float f_rest_41
property float f_rest_42
property float f_rest_43
property float f_rest_44
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
"""

    with open(output_file, 'wb') as f:
        f.write(ply_header.encode('ascii'))
        
        for i in range(len(points)):
            x, y, z = points[i]
            r_norm, g_norm, b_norm = colors[i]
            
            # 写入顶点数据
            # 位置 (x, y, z)
            f.write(struct.pack('<fff', x, y, z))
            
            # 法线 (nx, ny, nz) - 向上的法线
            f.write(struct.pack('<fff', 0.0, 1.0, 0.0))
            
            # 颜色 (f_dc_0, f_dc_1, f_dc_2)
            f.write(struct.pack('<fff', r_norm, g_norm, b_norm))
            
            # f_rest_0到f_rest_44 - 设为小随机值
            for _ in range(45):
                f.write(struct.pack('<f', np.random.uniform(-0.03, 0.02)))
            
            # opacity, scale_0, scale_1, scale_2
            # 这里将y轴方向的缩放比例缩小为原来的1/10，使其更扁平
            f.write(struct.pack('<ffff', 4.6, 0.636, 0.0636, 0.636))
            
            # rot_0, rot_1, rot_2, rot_3
            f.write(struct.pack('<ffff', 1.0, 0.0, 0.0, 0.0))

    print(f"地面平面已生成: {output_file}")
    print(f"实际使用了 {actual_points} 个点，平面直径为 {size}")

if __name__ == "__main__":
    try:
        num_points = int(input("请输入点的数量 (默认 40000): ") or "40000")
    except ValueError:
        num_points = 40000
        print("无效输入，使用默认值40000。")
    
    try:
        size = float(input("请输入平面直径 (默认 200.0): ") or "200.0")
    except ValueError:
        size = 200.0
        print("无效输入，使用默认直径200.0。")
    
    # 获取当前目录下所有支持的图像文件
    supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.bmp']
    image_files = []
    
    for ext in supported_extensions:
        image_files.extend(glob.glob(ext))
    
    if not image_files:
        print("当前目录下没有找到图像文件。")
    else:
        print(f"找到 {len(image_files)} 个图像文件，开始处理...")
        
        for img_file in image_files:
            output_file = os.path.splitext(img_file)[0] + "_ground.ply"
            try:
                generate_ground_plane(img_file, output_file, num_points, size)
                print(f"已处理: {img_file} -> {output_file}")
            except Exception as e:
                print(f"处理 {img_file} 时出错: {str(e)}")
        
        print("所有图像处理完成。")
