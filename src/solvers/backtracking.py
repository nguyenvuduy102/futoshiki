import time
import os
import copy

try:
    from core.parser import parse_input
    from core.output_formatter import format_grid
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.parser import parse_input
    from core.output_formatter import format_grid

class BacktrackingSolver:
    """
    Thuật toán Quay lui (Backtracking) tiêu chuẩn để giải Futoshiki.
    Đóng vai trò là Baseline để so sánh hiệu năng.
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.N = puzzle.N
        # Tạo một bản sao độc lập của lưới (tránh ghi đè lên dữ liệu gốc)
        self.grid = copy.deepcopy(puzzle.grid)
        self.nodes_expanded = 0 

    def is_safe(self, r, c, v):
        """
        Kiểm tra xem việc gán giá trị v vào ô (r, c) có vi phạm luật nào không.
        Trả về True nếu an toàn, False nếu vi phạm.
        """
        # 1. Kiểm tra ràng buộc duy nhất trên Hàng và Cột
        for i in range(self.N):
            if self.grid[r][i] == v:
                return False
            if self.grid[i][c] == v:
                return False

        # 2. Kiểm tra Bất phương trình ngang (Horizontal)
        # Xét ô bên trái (r, c-1)
        if c > 0 and self.grid[r][c-1] != 0:
            constraint = self.puzzle.horizontal_constraints[r][c-1]
            left_val = self.grid[r][c-1]
            if constraint == 1 and not (left_val < v): return False   # Left < Right
            if constraint == -1 and not (left_val > v): return False  # Left > Right
            
        # Xét ô bên phải (r, c+1)
        if c < self.N - 1 and self.grid[r][c+1] != 0:
            constraint = self.puzzle.horizontal_constraints[r][c]
            right_val = self.grid[r][c+1]
            if constraint == 1 and not (v < right_val): return False  # Left < Right
            if constraint == -1 and not (v > right_val): return False # Left > Right

        # 3. Kiểm tra Bất phương trình dọc (Vertical)
        # Xét ô phía trên (r-1, c)
        if r > 0 and self.grid[r-1][c] != 0:
            constraint = self.puzzle.vertical_constraints[r-1][c]
            top_val = self.grid[r-1][c]
            if constraint == 1 and not (top_val < v): return False    # Top < Bottom
            if constraint == -1 and not (top_val > v): return False   # Top > Bottom
            
        # Xét ô phía dưới (r+1, c)
        if r < self.N - 1 and self.grid[r+1][c] != 0:
            constraint = self.puzzle.vertical_constraints[r][c]
            bottom_val = self.grid[r+1][c]
            if constraint == 1 and not (v < bottom_val): return False # Top < Bottom
            if constraint == -1 and not (v > bottom_val): return False # Top > Bottom

        return True

    def find_empty_cell(self):
        """
        Tìm ô trống (có giá trị = 0) đầu tiên theo thứ tự từ trái sang phải, từ trên xuống dưới.
        """
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] == 0:
                    return r, c
        return None

    def solve(self):
        """
        Hàm đệ quy thực thi thuật toán Backtracking.
        Trả về True nếu tìm thấy lời giải, False nếu nhánh hiện tại đi vào bế tắc.
        """
        empty_cell = self.find_empty_cell()
        
        # Nếu không còn ô trống nào, bài toán đã được giải xong
        if not empty_cell:
            return True
            
        r, c = empty_cell

        # Thử điền các số từ 1 đến N
        for v in range(1, self.N + 1):
            if self.is_safe(r, c, v):
                # Nếu an toàn, thử gán giá trị
                self.grid[r][c] = v
                self.nodes_expanded += 1

                # Đệ quy đi sâu xuống nhánh này
                if self.solve():
                    return True

                # Nếu nhánh này thất bại, QUAY LUI (Backtrack) bằng cách xóa giá trị
                self.grid[r][c] = 0

        # Thử hết 1->N mà không được, trả về False để quay lui lên node cha
        return False


# ==========================================
# Khối mã Test nhanh thuật toán
# ==========================================
if __name__ == "__main__":
    # Trỏ đường dẫn đến file test input-01.txt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-02.txt")
    
    try:
        print(f"Đang đọc file: {test_file}...")
        puzzle = parse_input(test_file)
        
        solver = BacktrackingSolver(puzzle)
        
        print("\nBắt đầu giải bằng Backtracking...")
        start_time = time.time()
        
        is_solved = solver.solve()
        
        end_time = time.time()
        exec_time = end_time - start_time
        
        if is_solved:
            print(f"\n[+] ĐÃ TÌM THẤY LỜI GIẢI!\n")
            print(format_grid(puzzle, solver.grid))
            print("-" * 40)
            print(f"Thời gian chạy:      {exec_time:.6f} giây")
            print(f"Số node mở rộng:     {solver.nodes_expanded} nodes")
            print("-" * 40)
        else:
            print("[-] Bài toán không có lời giải (hoặc input sai logic).")
            
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")