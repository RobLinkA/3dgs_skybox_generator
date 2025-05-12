import numpy as np
from PIL import Image
import struct
import os
import math
import glob

def fibonacci_sphere(samples=1000, radius=100):
    """
    使用黄金螺旋算法生成均匀分布的球面点
    """
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  # 黄金角度

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y从1到-1
        radius_at_y = math.sqrt(1 - y * y)  # 在当前y值的圆半径
        
        theta = phi * i  # 黄金角度递增
        
        x = math.cos(theta) * radius_at_y
        z = math.sin(theta) * radius_at_y
        
        # 缩放到指定半径
        points.append((x * radius, y * radius, z * radius))
    
    return points

def generate_sky_sphere(hdri_path, output_file, num_points, radius):
    # 加载HDRI图像
    hdri = Image.open(hdri_path)
    hdri_width, hdri_height = hdri.size
    
    # 生成均匀分布的球面点
    points = fibonacci_sphere(samples=num_points, radius=radius)
    
    # 准备PLY文件头部
    ply_header = f"""ply
format binary_little_endian 1.0
element vertex {num_points}
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
        
        for point in points:
            x, y, z = point
            
            # 将笛卡尔坐标转换为球坐标（用于HDRI映射）
            r = np.sqrt(x*x + y*y + z*z)
            theta = np.arccos(y / r)  # 0到π
            phi = np.arctan2(z, x)    # -π到π
            
            # 调整phi为0到2π范围
            if phi < 0:
                phi += 2 * np.pi
            
            # 计算HDRI上的UV坐标
            u = phi / (2 * np.pi) * hdri_width
            v = (1 - theta / np.pi) * hdri_height
            
            # 对u和v进行插值，确保在图像范围内
            u = int(u) % hdri_width
            v = min(max(int(v), 0), hdri_height - 1)
            
            # 获取HDRI颜色值
            pixel = hdri.getpixel((u, v))
            
            # 如果HDRI是RGB格式
            if len(pixel) == 3:
                r, g, b = pixel
            # 如果HDRI是RGBA格式
            elif len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r = g = b = pixel
            
            # 将RGB值归一化后乘以常数（基于示例数据）
            r_norm = (r / 255.0) * 1.7
            g_norm = (g / 255.0) * 1.7
            b_norm = (b / 255.0) * 1.7
            
            # 写入顶点数据
            # 位置 (x, y, z)
            f.write(struct.pack('<fff', x, y, z))
            
            # 法线 (nx, ny, nz) - 设为0
            f.write(struct.pack('<fff', 0.0, 0.0, 0.0))
            
            # 颜色 (f_dc_0, f_dc_1, f_dc_2)
            f.write(struct.pack('<fff', r_norm, g_norm, b_norm))
            
            # f_rest_0到f_rest_44 - 设为小随机值
            for _ in range(45):
                f.write(struct.pack('<f', np.random.uniform(-0.03, 0.02)))
            
            # opacity, scale_0, scale_1, scale_2
            f.write(struct.pack('<ffff', 4.6, 0.636, 0.636, 0.636))
            
            # rot_0, rot_1, rot_2, rot_3
            f.write(struct.pack('<ffff', 1.0, 0.0, 0.0, 0.0))

    print(f"天空球已生成: {output_file}")

if __name__ == "__main__":
    try:
        num_points = int(input("请输入点的数量 (默认 100000): ") or "100000")
    except ValueError:
        num_points = 100000
        print("无效输入，使用默认值100000。")
    
    try:
        radius = float(input("请输入球体半径 (默认 100.0): ") or "100.0")
    except ValueError:
        radius = 100.0
        print("无效输入，使用默认半径100.0。")
    
    # 获取当前目录下所有支持的图像文件
    supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.bmp', '*.hdr', '*.exr']
    image_files = []
    
    for ext in supported_extensions:
        image_files.extend(glob.glob(ext))
    
    if not image_files:
        print("当前目录下没有找到图像文件。")
    else:
        print(f"找到 {len(image_files)} 个图像文件，开始处理...")
        
        for img_file in image_files:
            output_file = os.path.splitext(img_file)[0] + "_skysphere.ply"
            try:
                generate_sky_sphere(img_file, output_file, num_points, radius)
                print(f"已处理: {img_file} -> {output_file}")
            except Exception as e:
                print(f"处理 {img_file} 时出错: {str(e)}")
        
        print("所有图像处理完成。")
