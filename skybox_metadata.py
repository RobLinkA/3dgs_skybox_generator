def extract_ply_header(ply_file_path):
    """
    读取PLY文件并提取头部信息，尝试多种编码
    
    参数:
        ply_file_path: PLY文件路径
        
    返回:
        头部信息的字符串
    """
    encodings = ['utf-8', 'latin1', 'ascii']
    
    for encoding in encodings:
        try:
            header_lines = []
            with open(ply_file_path, 'r', encoding=encoding) as file:
                line = file.readline()
                header_lines.append(line.strip())
                
                # 继续读取直到找到end_header行
                while line and "end_header" not in line:
                    line = file.readline()
                    header_lines.append(line.strip())
            
            print(f"成功使用 {encoding} 编码读取文件")
            return "\n".join(header_lines)
        
        except Exception as e:
            print(f"使用 {encoding} 编码读取文件时出错: {e}")
    
    # 如果所有编码都失败了，尝试二进制模式
    try:
        with open(ply_file_path, 'rb') as file:
            header_bytes = b''
            line = file.readline()
            header_bytes += line
            
            # 继续读取直到找到end_header行
            while line and b"end_header" not in line:
                line = file.readline()
                header_bytes += line
            
            # 尝试多种解码方式
            for encoding in encodings:
                try:
                    header_text = header_bytes.decode(encoding)
                    print(f"成功使用二进制模式和 {encoding} 解码")
                    return header_text
                except:
                    continue
            
            # 如果解码都失败，返回前100个字节的十六进制表示
            print("无法解码二进制数据，返回十六进制表示")
            hex_representation = ' '.join(f'{b:02x}' for b in header_bytes[:100])
            return f"Binary PLY header (first 100 bytes in hex):\n{hex_representation}"
    
    except Exception as e:
        print(f"以二进制模式读取文件时出错: {e}")
        return None

# 使用方法
if __name__ == "__main__":
    # 替换为你的skybox.ply文件路径
    ply_file_path = "skybox.ply"
    
    header = extract_ply_header(ply_file_path)
    if header:
        print("\nPLY文件头部结构:")
        print(header)
        
        # 将头部结构保存到文件中
        with open("ply_header.txt", "w", encoding="utf-8") as f:
            f.write(header)
        print("\n头部结构已保存到 ply_header.txt")
    else:
        print("无法提取PLY文件头部结构")
