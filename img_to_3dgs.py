import os
import numpy as np
from PIL import Image

# ---------------- 配置参数 (可根据需要修改) ----------------
MAX_RES = 1024          # 限制最大分辨率，防止点云过密导致运行缓慢
GRID_SIZE = 1.0        # 转换后在 3D 空间中的初始物理尺寸 (宽度)
OVERLAP_FACTOR = 1.2   # 控制高斯点之间的重叠度。值越大边缘越平滑，越小越清晰
ALPHA_THRESHOLD = 0.05 # 透明度阈值。若使用 PNG 格式抠出了圆形瓶底，透明度低于此值的像素会被过滤，从而生成圆形补丁
# --------------------------------------------------------

def image_to_3dgs_ply(img_path, output_path):
    print(f"正在处理: {img_path} ...")
    try:
        img = Image.open(img_path)
    except Exception as e:
        print(f"读取图片失败 {img_path}: {e}")
        return

    # 1. 限制分辨率，避免点数过多导致渲染和编辑卡顿
    w, h = img.size
    if max(w, h) > MAX_RES:
        scale = MAX_RES / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        w, h = new_w, new_h

    # 2. 统一转为 RGBA 格式
    img = img.convert('RGBA')
    img_data = np.array(img)

    # 归一化颜色和透明度
    rgb = img_data[..., :3] / 255.0
    alpha = img_data[..., 3] / 255.0

    # 3. 过滤透明像素（如果使用带有透明通道的 PNG 抠图，这会非常有用）
    mask = alpha >= ALPHA_THRESHOLD
    if not np.any(mask):
        print(f"跳过 {img_path}: 没有满足透明度阈值的像素。")
        return

    rows, cols = np.where(mask)
    num_points = len(rows)

    # 计算 3D 空间中的像素步长
    scale_factor = GRID_SIZE / max(w, h)

    # 计算 3D 位置 (以 0,0,0 为中心平铺在 XY 平面上)
    x = (cols - w / 2.0 + 0.5) * scale_factor
    y = -(rows - h / 2.0 + 0.5) * scale_factor  # 图像 Y 轴向下，3D Y 轴向上，故取反
    z = np.zeros_like(x)

    positions = np.stack([x, y, z], axis=-1)

    # 法线默认设为朝向 +Z
    normals = np.zeros((num_points, 3))
    normals[:, 2] = 1.0

    # 4. 颜色转换为 3DGS 0阶球谐系数 (f_dc)
    # 转换公式：f_dc = (RGB - 0.5) / C0，其中 C0 ≈ 0.28209479177387814
    sh_c0 = 0.28209479177387814
    pixel_rgbs = rgb[mask]
    f_dc = (pixel_rgbs - 0.5) / sh_c0

    # 高阶球谐系数初始化为 0 (f_rest_0 到 f_rest_44)
    f_rest = np.zeros((num_points, 45))

    # 5. 不透明度转换为 logit 空间 (inverse_sigmoid)
    pixel_alphas = np.clip(alpha[mask], 1e-4, 1.0 - 1e-4)
    opacity = np.log(pixel_alphas / (1.0 - pixel_alphas))
    opacity = opacity[:, np.newaxis]

    # 6. 计算缩放尺度 (log 空间)
    # xy 轴根据步长和重叠系数计算，z 轴设得非常薄，使其呈扁平状
    s_x = scale_factor * OVERLAP_FACTOR
    s_y = scale_factor * OVERLAP_FACTOR
    s_z = s_x * 0.01  # 极薄

    scale_0 = np.log(s_x)
    scale_1 = np.log(s_y)
    scale_2 = np.log(s_z)

    scales = np.tile([scale_0, scale_1, scale_2], (num_points, 1))

    # 7. 旋转四元数设为无旋转 [1, 0, 0, 0]
    rotations = np.tile([1.0, 0.0, 0.0, 0.0], (num_points, 1))

    # 8. 构造标准的 3DGS ply 结构
    dtype = [
        ('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
        ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
        ('f_dc_0', 'f4'), ('f_dc_1', 'f4'), ('f_dc_2', 'f4')
    ]
    for i in range(45):
        dtype.append((f'f_rest_{i}', 'f4'))
    dtype.append(('opacity', 'f4'))
    for i in range(3):
        dtype.append((f'scale_{i}', 'f4'))
    for i in range(4):
        dtype.append((f'rot_{i}', 'f4'))

    data = np.empty(num_points, dtype=dtype)
    data['x'] = positions[:, 0]
    data['y'] = positions[:, 1]
    data['z'] = positions[:, 2]
    data['nx'] = normals[:, 0]
    data['ny'] = normals[:, 1]
    data['nz'] = normals[:, 2]
    data['f_dc_0'] = f_dc[:, 0]
    data['f_dc_1'] = f_dc[:, 1]
    data['f_dc_2'] = f_dc[:, 2]
    for i in range(45):
        data[f'f_rest_{i}'] = f_rest[:, i]
    data['opacity'] = opacity[:, 0]
    data['scale_0'] = scales[:, 0]
    data['scale_1'] = scales[:, 1]
    data['scale_2'] = scales[:, 2]
    data['rot_0'] = rotations[:, 0]
    data['rot_1'] = rotations[:, 1]
    data['rot_2'] = rotations[:, 2]
    data['rot_3'] = rotations[:, 3]

    # 9. 写入二进制 PLY 文件 (3DGS 常用标准)
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
"""
    for i in range(45):
        header += f"property float f_rest_{i}\n"
    header += """property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
"""

    with open(output_path, 'wb') as f:
        f.write(header.encode('utf-8'))
        f.write(data.tobytes())

    print(f"成功导出: {output_path} (包含 {num_points} 个高斯点)\n")

def main():
    # 获取当前目录下所有的常见图片文件
    supported_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
    current_dir = os.getcwd()
    
    files = os.listdir(current_dir)
    image_files = [f for f in files if f.lower().endswith(supported_extensions)]
    
    if not image_files:
        print("当前目录下没有找到常见的图片文件 (.png, .jpg, .jpeg, .webp, .bmp)")
        return
        
    print(f"共找到 {len(image_files)} 张图片，开始转换...\n")
    
    for img_file in image_files:
        name, _ = os.path.splitext(img_file)
        output_ply = f"./{name}_patch.ply"
        image_to_3dgs_ply(img_file, output_ply)
        
    print("所有转换已完成。")

if __name__ == "__main__":
    main()
