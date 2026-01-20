import os
import struct
import numpy as np

def make_pedestal():
    print("--- 3DGS 底座生成器 ---")
    
    # 1. 交互获取参数
    try:
        l = float(input("请输入长度 (X轴) [默认 1.0]: ") or "1.0")
        w = float(input("请输入宽度 (Z轴) [默认 1.0]: ") or "1.0")
        h = float(input("请输入高度 (Y轴) [默认 0.2]: ") or "0.2")
        c_str = input("请输入颜色 RGB [默认 255,255,255]: ") or "255,255,255"
        color_rgb = tuple(map(int, c_str.split(',')))
    except ValueError:
        l, w, h, color_rgb = 1.0, 1.0, 0.2, (255, 255, 255)

    density = 100
    points_data = []
    
    # SH 基础色计算
    r_norm = (color_rgb[0] / 255.0 - 0.5) / 0.28209
    g_norm = (color_rgb[1] / 255.0 - 0.5) / 0.28209
    b_norm = (color_rgb[2] / 255.0 - 0.5) / 0.28209

    nx, ny, nz = max(2, int(l*density)), max(2, int(h*density)), max(2, int(w*density))
    step_x = l / (nx - 1)
    step_y = h / (ny - 1)
    step_z = w / (nz - 1)

    scale_flat = -5.0  # 保证侧看可见
    s_x = np.log(step_x * 0.8)
    s_y = np.log(step_y * 0.8)
    s_z = np.log(step_z * 0.8)

    def add_face(axis_vals_1, axis_vals_2, fixed_val, axis_idx, s_mode):
        for v1 in axis_vals_1:
            for v2 in axis_vals_2:
                pos = [0, 0, 0]
                if axis_idx == 0: pos = [fixed_val, v2, v1] # X面
                elif axis_idx == 1: pos = [v1, fixed_val, v2] # Y面
                else: pos = [v1, v2, fixed_val]             # Z面
                
                # 沿用 v3 各向异性缩放逻辑
                if s_mode == 1:   s = [s_x, scale_flat, s_z]
                elif s_mode == 0: s = [scale_flat, s_y, s_z]
                else:             s = [s_x, s_y, scale_flat]
                
                points_data.append((pos, s))

    # --- 2. 生成六个面 (底面对齐 Y=0, 向上翻转) ---
    # 顶面：Y=h
    add_face(np.linspace(-l/2, l/2, nx), np.linspace(-w/2, w/2, nz), h, 1, 1)
    # 底面：Y=0 (红线)
    add_face(np.linspace(-l/2, l/2, nx), np.linspace(-w/2, w/2, nz), 0, 1, 1)
    # 四个侧面：Y 从 0 到 h
    add_face(np.linspace(-l/2, l/2, nx), np.linspace(0, h, ny), w/2, 2, 2)  # 前
    add_face(np.linspace(-l/2, l/2, nx), np.linspace(0, h, ny), -w/2, 2, 2) # 后
    add_face(np.linspace(-w/2, w/2, nz), np.linspace(0, h, ny), l/2, 0, 0)  # 右
    add_face(np.linspace(-w/2, w/2, nz), np.linspace(0, h, ny), -l/2, 0, 0) # 左

    # --- 3. 写入文件 ---
    num_points = len(points_data)
    header = f"""ply
format binary_little_endian 1.0
element vertex {num_points}
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
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

    with open("pedestal_cube.ply", 'wb') as f:
        f.write(header.encode('ascii'))
        for pos, s in points_data:
            f.write(struct.pack('<fff', *pos))
            f.write(struct.pack('<fff', 0, 0, 0))
            f.write(struct.pack('<fff', r_norm, g_norm, b_norm))
            f.write(struct.pack('<f', 15.0))
            f.write(struct.pack('<fff', *s))
            f.write(struct.pack('<ffff', 1, 0, 0, 0))

    print(f"\n生成成功！")

if __name__ == "__main__":
    make_pedestal()