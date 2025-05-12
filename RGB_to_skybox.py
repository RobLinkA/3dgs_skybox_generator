import numpy as np
from plyfile import PlyData, PlyElement
import os

def create_solid_color_skybox(skybox_template_path, output_path, rgb_color):
    """
    创建一个纯色的天空球PLY文件
    
    参数:
    - skybox_template_path: 模板天空球PLY文件路径
    - output_path: 输出PLY文件路径
    - rgb_color: (R, G, B) 元组，值范围为0-255
    """
    print(f"创建颜色为 RGB{rgb_color} 的天空球...")
    
    # 读取模板PLY文件
    plydata = PlyData.read(skybox_template_path)
    
    # 复制原始顶点数据
    vertex_data = plydata['vertex'].data.copy()
    
    # 将RGB值归一化到[0,1]范围
    r, g, b = [c / 255.0 for c in rgb_color]
    
    # 更新所有点的f_dc_0, f_dc_1, f_dc_2字段（对应RGB）
    if 'f_dc_0' in vertex_data.dtype.names and 'f_dc_1' in vertex_data.dtype.names and 'f_dc_2' in vertex_data.dtype.names:
        vertex_data['f_dc_0'] = r  # R
        vertex_data['f_dc_1'] = g  # G
        vertex_data['f_dc_2'] = b  # B
        print(f"已更新 f_dc_0, f_dc_1, f_dc_2 字段")
    else:
        print(f"警告: 找不到 f_dc_0, f_dc_1, f_dc_2 字段")
        return False
    
    # 创建新的PLY元素
    vertex_element = PlyElement.describe(vertex_data, 'vertex')
    
    # 创建并保存新的PLY文件
    new_plydata = PlyData([vertex_element], text=plydata.text)
    new_plydata.write(output_path)
    
    print(f"已创建颜色为 RGB{rgb_color} 的天空球: {output_path}")
    return True

def parse_rgb_input(rgb_input):
    """解析用户输入的RGB值"""
    try:
        # 尝试解析不同格式的RGB输入
        rgb_input = rgb_input.strip()
        
        # 格式1: "r,g,b" 或 "r, g, b"
        if ',' in rgb_input:
            values = [int(x.strip()) for x in rgb_input.split(',')]
            if len(values) == 3:
                return tuple(np.clip(values, 0, 255))
        
        # 格式2: "r g b"
        elif ' ' in rgb_input:
            values = [int(x.strip()) for x in rgb_input.split()]
            if len(values) == 3:
                return tuple(np.clip(values, 0, 255))
        
        # 格式3: "#rrggbb" 或 "rrggbb" (十六进制)
        elif rgb_input.startswith('#') or all(c in '0123456789abcdefABCDEF' for c in rgb_input.replace('#', '')):
            hex_color = rgb_input.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
    except:
        pass
    
    return None

def main():
    skybox_template_path = "skybox.ply"
    
    # 检查模板文件是否存在
    if not os.path.exists(skybox_template_path):
        print(f"错误: 找不到天空球模板文件 {skybox_template_path}")
        return
    
    # 获取用户输入的RGB值
    print("\n=== 创建纯色天空球 ===")
    print("请输入RGB颜色值，格式可以是以下几种:")
    print("- 逗号分隔: 例如 '255,0,0' (红色)")
    print("- 空格分隔: 例如 '255 0 0' (红色)")
    print("- 十六进制: 例如 '#FF0000' 或 'FF0000' (红色)")
    
    while True:
        rgb_input = input("\n请输入RGB颜色 (或输入'q'退出): ")
        
        if rgb_input.lower() == 'q':
            print("程序已退出")
            break
        
        rgb_color = parse_rgb_input(rgb_input)
        
        if rgb_color is None:
            print("错误: 无法识别的RGB格式，请重新输入")
            continue
        
        # 创建输出目录
        output_dir = "solid_skyboxes"
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建输出文件名
        color_str = f"rgb_{rgb_color[0]}_{rgb_color[1]}_{rgb_color[2]}"
        output_path = os.path.join(output_dir, f"skybox_{color_str}.ply")
        
        # 创建纯色天空球
        success = create_solid_color_skybox(skybox_template_path, output_path, rgb_color)
        
        if success:
            # 询问是否继续
            choice = input("\n是否继续创建其他颜色的天空球? (y/n): ")
            if choice.lower() != 'y':
                print("程序已退出")
                break
        else:
            print("创建天空球失败，请检查错误信息")

if __name__ == "__main__":
    main()
