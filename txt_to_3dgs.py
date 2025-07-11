import os
import sys
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def find_font():
    """
    在系统中查找一个支持中文的无衬线字体。
    这是一个简化的实现，优先顺序可以根据需要调整。
    """
    # Windows
    if sys.platform == "win32":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # Microsoft YaHei UI
            "C:/Windows/Fonts/simhei.ttf", # SimHei
            "C:/Windows/Fonts/arial.ttf",    # Arial (for English)
        ]
    # macOS
    elif sys.platform == "darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc", # PingFang SC
            "/System/Library/Fonts/STHeiti.ttc",   # Heiti SC
            "/System/Library/Fonts/Arial.ttf",
        ]
    # Linux (common paths)
    else:
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"找到可用字体: {font_path}")
            return font_path
            
    print("警告: 未找到推荐的系统字体。将尝试使用Pillow的默认字体。")
    print("如果出现乱码或错误，请安装一个支持多语言的无衬线字体（如 'Noto Sans CJK'）并修改脚本中的`find_font`函数。")
    return None

def generate_text_cloud(text_string, output_file, thickness, color_rgb, density, font_size=128):
    """
    根据输入文本生成3D高斯溅射点云。
    
    :param density: 点云密度因子。1.0为基准，<1更稀疏，>1更密集。
    """
    # 1. 查找并加载字体
    font_path = find_font()
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"无法加载字体: {font_path}。尝试使用Pillow默认字体。")
        font = ImageFont.load_default()

    # 2. 将文本渲染到2D图像上
    dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    try:
        bbox = dummy_draw.textbbox((0, 0), text_string, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        padding = 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2
        
        img = Image.new('L', (img_width, img_height), 0)
        draw = ImageDraw.Draw(img)
        draw.text((padding - bbox[0], padding - bbox[1]), text_string, font=font, fill=255)
    except Exception as e:
         print(f"渲染文本时出错: {e}")
         print("这可能是因为字体不支持您输入的某些字符。")
         return

    # 3. 从2D图像中提取像素点
    pixels = np.array(img)
    y_coords, x_coords = np.where(pixels > 0)
    num_base_pixels = len(y_coords)

    if num_base_pixels == 0:
        print("错误: 未能从文本生成任何点。请检查您的输入文本和字体。")
        return

    # 4. **【新功能】根据密度调整点数**
    # 通过对基础像素点进行有放回的随机抽样来调整最终点数。
    # 这可以自然地处理密度小于1（稀疏）和大于1（密集）的情况。
    num_target_pixels = int(num_base_pixels * density)
    if num_target_pixels == 0:
        print(f"错误: 密度({density})过低，无法生成任何点。")
        return
        
    base_indices = np.arange(num_base_pixels)
    chosen_indices = np.random.choice(base_indices, size=num_target_pixels, replace=True)
    
    sampled_y = y_coords[chosen_indices]
    sampled_x = x_coords[chosen_indices]

    # 5. 将采样后的2D点“挤出”为3D点
    points_3d = []
    z_samples = max(1, int(thickness))

    for y, x in zip(sampled_y, sampled_x):
        for i in range(z_samples):
            z = (i / (z_samples - 1) - 0.5) * thickness if z_samples > 1 else 0.0
            
            centered_x = x - img_width / 2
            centered_y = -(y - img_height / 2)
            
            # (x, y, z) -> (-x, -y, z)
            rotated_x = -centered_x
            rotated_y = -centered_y
            
            points_3d.append((rotated_x, rotated_y, z))

    num_points = len(points_3d)
    print(f"共生成 {num_points} 个点。")

    # 6. 准备并写入PLY文件
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

    r, g, b = color_rgb
    r_norm = (r / 255.0) * 1.7
    g_norm = (g / 255.0) * 1.7
    b_norm = (b / 255.0) * 1.7
    
    opacity = 1.0
    scale = 0.2
    
    with open(output_file, 'wb') as f:
        f.write(ply_header.encode('ascii'))
        
        for point in points_3d:
            px, py, pz = point
            
            f.write(struct.pack('<fff', px, py, pz))
            f.write(struct.pack('<fff', 0.0, 0.0, 0.0))
            f.write(struct.pack('<fff', r_norm, g_norm, b_norm))
            for _ in range(45):
                f.write(struct.pack('<f', 0.0))
            f.write(struct.pack('<ffff', opacity, scale, scale, scale))
            f.write(struct.pack('<ffff', 1.0, 0.0, 0.0, 0.0))

    print(f"3D文本点云已生成: {output_file}")


if __name__ == "__main__":
    print("--- 3D文本转高斯溅射点云工具 (v2) ---")
    
    text_to_generate = input("请输入要生成的文本 (例如: Hello World 你好世界): ")
    if not text_to_generate.strip():
        print("错误: 输入文本不能为空。")
        sys.exit(1)
        
    try:
        thickness_val = float(input("请输入厚度 (默认 10.0): ") or "10.0")
    except ValueError:
        thickness_val = 10.0
        print("无效输入，使用默认厚度 10.0。")
    
    # **获取密度输入**
    while True:
        try:
            density_val = float(input("请输入点云密度 (默认 1.0, >0): ") or "1.0")
            if density_val > 0:
                break
            else:
                print("错误: 密度必须是大于0的数字。")
        except ValueError:
            density_val = 1.0
            print("无效输入，使用默认密度 1.0。")
            break

    while True:
        try:
            color_str = input("请输入RGB颜色,以逗号分隔 (默认 255,255,255 代表白色): ") or "255,255,255"
            color_parts = [int(c.strip()) for c in color_str.split(',')]
            if len(color_parts) == 3 and all(0 <= c <= 255 for c in color_parts):
                color_val = tuple(color_parts)
                break
            else:
                print("颜色格式错误。请输入三个0-255之间的数字，用逗号分隔。")
        except (ValueError, IndexError):
            print("颜色格式错误。请输入三个0-255之间的数字，用逗号分隔。")

    safe_filename = "".join([c for c in text_to_generate if c.isalnum() or c in " _-"]).rstrip()
    if not safe_filename:
        safe_filename = "text_output"
    output_filename = f"{safe_filename[:30]}_3dgs.ply"

    print("\n--- 开始生成 ---")
    print(f"文本: '{text_to_generate}'")
    print(f"厚度: {thickness_val}")
    print(f"密度: {density_val}")
    print(f"颜色: {color_val}")
    print(f"输出文件: {output_filename}")
    
    try:
        generate_text_cloud(text_to_generate, output_filename, thickness_val, color_val, density_val)
    except Exception as e:
        print(f"\n处理过程中发生严重错误: {e}")
    
    print("\n--- 处理完成 ---")
