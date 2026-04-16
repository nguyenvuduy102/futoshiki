import os

class FutoshikiInstance:
    """
    Lớp lưu trữ toàn bộ dữ kiện của một câu đố Futoshiki sau khi parse.
    """
    def __init__(self, n, grid, horizontal_constraints, vertical_constraints):
        self.N = n
        self.grid = grid
        self.horizontal_constraints = horizontal_constraints
        self.vertical_constraints = vertical_constraints

    def __str__(self):
        result = f"--- KÍCH THƯỚC: {self.N}x{self.N} ---\n"
        result += "Grid (Bảng chứa số):\n"
        for row in self.grid:
            result += f"  {row}\n"
        
        result += "\nHorizontal Constraints (Ràng buộc ngang):\n"
        for row in self.horizontal_constraints:
            result += f"  {row}\n"
            
        result += "\nVertical Constraints (Ràng buộc dọc):\n"
        for row in self.vertical_constraints:
            result += f"  {row}\n"
            
        return result

def parse_input(file_path):
    """
    Hàm đọc file input.txt và trả về đối tượng FutoshikiInstance.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Bước 1: Làm sạch dữ liệu (Bỏ qua comment và dòng trống)
    cleaned_lines = []
    for line in lines:
        # Bỏ qua phần chú thích sau dấu '#'
        line_content = line.split('#')[0].strip()
        if line_content:
            cleaned_lines.append(line_content)

    if not cleaned_lines:
        raise ValueError("File rỗng hoặc chỉ chứa comment.")

    # Bước 2: Xác định kích thước N
    first_line = cleaned_lines[0]
    try:
        # Nếu dòng đầu là số (VD: '4', '5')
        N = int(first_line)
        data_start_idx = 1
    except ValueError:
        # Nếu dòng đầu là chữ 'N' (như trong mẫu input), tự nội suy N từ độ dài của hàng đầu tiên
        N = len(cleaned_lines[1].split(','))
        data_start_idx = 1

    # Bước 3: Đọc Grid (Bảng số)
    grid = []
    for i in range(N):
        row_str = cleaned_lines[data_start_idx + i]
        row_values = [int(x.strip()) for x in row_str.split(',')]
        grid.append(row_values)
    
    data_start_idx += N

    # Bước 4: Đọc Horizontal constraints (Ràng buộc ngang)
    # Ràng buộc ngang có N hàng, mỗi hàng có N-1 giá trị
    horizontal_constraints = []
    for i in range(N):
        row_str = cleaned_lines[data_start_idx + i]
        row_values = [int(x.strip()) for x in row_str.split(',')]
        horizontal_constraints.append(row_values)
        
    data_start_idx += N

    # Bước 5: Đọc Vertical constraints (Ràng buộc dọc)
    # Ràng buộc dọc có N-1 hàng, mỗi hàng có N giá trị
    vertical_constraints = []
    for i in range(N - 1):
        row_str = cleaned_lines[data_start_idx + i]
        row_values = [int(x.strip()) for x in row_str.split(',')]
        vertical_constraints.append(row_values)

    return FutoshikiInstance(N, grid, horizontal_constraints, vertical_constraints)


# Khối code test nhanh: Chỉ chạy khi execute trực tiếp file này
# if __name__ == "__main__":
#     #  có thể tạo nhanh file input-01.txt cùng thư mục để test
#     test_file = "Inputs/input-01.txt"
#     try:
#         puzzle = parse_input(test_file)
#         print("Đọc file thành công!\n")
#         print(puzzle)
#     except Exception as e:
#         print(f"Lỗi khi đọc file: {e}")