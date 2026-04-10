import os

def format_grid(puzzle, solved_grid):
    """
    Trình bày lưới kết quả Futoshiki dưới dạng chuỗi (string) có chứa 
    các dấu bất phương trình ngang (<, >) và dọc (v, ^) được căn lề chuẩn xác.
    
    Quy ước từ PDF:
    - Ràng buộc dọc: 1 là Top < Bottom (dấu ^), -1 là Top > Bottom (dấu v)
    - Ràng buộc ngang: 1 là Left < Right (dấu <), -1 là Left > Right (dấu >)
    """
    N = puzzle.N
    lines = []
    
    for i in range(N):
        # 1. Xây dựng dòng chứa các con số và ràng buộc ngang
        row_str = ""
        for j in range(N):
            row_str += str(solved_grid[i][j])
            
            # Thêm ràng buộc ngang ở giữa các số (trừ cột cuối cùng)
            if j < N - 1:
                h_val = puzzle.horizontal_constraints[i][j]
                if h_val == 1:
                    row_str += " < "
                elif h_val == -1:
                    row_str += " > "
                else:
                    row_str += "   " # 3 khoảng trắng để giữ form
        lines.append(row_str)

        # 2. Xây dựng dòng chứa ràng buộc dọc (không áp dụng cho hàng cuối)
        if i < N - 1:
            v_str = ""
            for j in range(N):
                v_val = puzzle.vertical_constraints[i][j]
                if v_val == 1:
                    v_str += "^" # Trên nhỏ hơn Dưới
                elif v_val == -1:
                    v_str += "v" # Trên lớn hơn Dưới
                else:
                    v_str += " " # Không có ràng buộc
                
                # Căn lề khoảng cách tương ứng với " < " hoặc "   " ở trên
                if j < N - 1:
                    v_str += "   "
            lines.append(v_str)

    return "\n".join(lines)


def write_output(puzzle, solved_grid, input_filepath, output_dir=None):
    """
    Định dạng kết quả và ghi ra file output-XX.txt tương ứng với input-XX.txt.
    """
    # Trích xuất tên file (ví dụ: "input-01.txt")
    filename = os.path.basename(input_filepath)
    
    # Đổi "input" thành "output"
    output_filename = filename.replace("input", "output")
    
    # Xác định thư mục lưu trữ (mặc định là thư mục Outputs nằm ngang hàng với Inputs)
    if output_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "..","..", "Outputs")
        
    # Tạo thư mục Outputs nếu nó chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_filepath = os.path.join(output_dir, output_filename)
    
    formatted_result = format_grid(puzzle, solved_grid)
    
    # Ghi ra file
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_result)
        
    return output_filepath, formatted_result


# Khối code test nhanh
if __name__ == "__main__":
    # Import parser để lấy test case
    try:
        from core.parser import parse_input
    except ImportError:
        from parser import parse_input

    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-01.txt")
    
    try:
        puzzle = parse_input(test_file)
        
        # Giả lập một lưới đã giải xong (dựa trên hình solution từ PDF)
        # Lưu ý: Đây chỉ là mảng cứng (hardcode) dùng để test thuật toán in ấn.
        mock_solved_grid = [
            [2, 3, 4, 1],
            [1, 2, 3, 4],
            [4, 1, 2, 3],
            [3, 4, 1, 2]
        ]
        
        output_path, result_str = write_output(puzzle, mock_solved_grid, test_file)
        
        print("Đã định dạng và in kết quả thành công:\n")
        print(result_str)
        print(f"\nĐã lưu file tại: {output_path}")
        
    except Exception as e:
        print(f"Lỗi: {e}")