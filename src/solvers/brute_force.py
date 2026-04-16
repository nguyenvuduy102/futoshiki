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

class BruteForceSolver:
    """
    Thuật toán Vét cạn (Brute Force) theo chiến lược Generate-and-Test.
    Tạo ra TẤT CẢ các tổ hợp có thể điền vào ô trống, sau khi điền KÍN bảng
    mới tiến hành kiểm tra tính hợp lệ.
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.N = puzzle.N
        self.grid = copy.deepcopy(puzzle.grid)
        self.nodes_expanded = 0
        
        # Gom tất cả các ô trống vào một danh sách để duyệt tuyến tính (nhanh hơn tìm đệ quy)
        self.empty_cells = [(r, c) for r in range(self.N) for c in range(self.N) if self.grid[r][c] == 0]

    def is_valid_grid(self):
        """
        Kiểm tra TỔNG THỂ cả bảng xem có hợp lệ theo luật Futoshiki không.
        Chỉ được gọi khi bảng ĐÃ ĐƯỢC ĐIỀN ĐẦY.
        """
        N = self.N
        
        # 1. Kiểm tra luật Hàng và Cột (Mỗi hàng/cột không được có số trùng)
        for i in range(N):
            row_set = set()
            col_set = set()
            for j in range(N):
                # Kiểm tra hàng i
                if self.grid[i][j] in row_set: return False
                row_set.add(self.grid[i][j])
                
                # Kiểm tra cột i
                if self.grid[j][i] in col_set: return False
                col_set.add(self.grid[j][i])

        # 2. Kiểm tra luật Bất phương trình ngang
        for r in range(N):
            for c in range(N - 1):
                con = self.puzzle.horizontal_constraints[r][c]
                if con == 1 and not (self.grid[r][c] < self.grid[r][c+1]): return False
                if con == -1 and not (self.grid[r][c] > self.grid[r][c+1]): return False

        # 3. Kiểm tra luật Bất phương trình dọc
        for r in range(N - 1):
            for c in range(N):
                con = self.puzzle.vertical_constraints[r][c]
                if con == 1 and not (self.grid[r][c] < self.grid[r+1][c]): return False
                if con == -1 and not (self.grid[r][c] > self.grid[r+1][c]): return False

        return True

    def _solve_recursive(self, index):
        """
        Đệ quy sinh (Generate) các tổ hợp số cho bảng.
        - index: Vị trí của ô trống hiện tại trong danh sách self.empty_cells
        """
        # Trạng thái kết thúc (Base case): Đã điền xong tất cả ô trống
        if index == len(self.empty_cells):
            # Tiến hành bước "Test"
            return self.is_valid_grid()

        r, c = self.empty_cells[index]

        # Thử điền mù quáng từ 1 đến N mà KHÔNG KIỂM TRA (Sự khác biệt với Backtracking)
        for v in range(1, self.N + 1):
            self.grid[r][c] = v
            self.nodes_expanded += 1
            
            # Đi tiếp sang ô trống tiếp theo
            if self._solve_recursive(index + 1):
                return True
                
        # Thử hết 1->N không thành công, trả lại ô trống
        self.grid[r][c] = 0
        return False

    def solve(self):
        """Hàm kích hoạt bộ giải."""
        # Bắt đầu đệ quy từ ô trống đầu tiên (index 0)
        return self._solve_recursive(0)

# ==========================================
# Khối mã Test nhanh thuật toán
# ==========================================
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # LƯU Ý: Với Brute Force, chỉ nên test với bảng 4x4.
    test_file = os.path.join(current_dir, "..", "Inputs", "input-01.txt")
    
    try:
        puzzle = parse_input(test_file)
        solver = BruteForceSolver(puzzle)
        
        print("\nBắt đầu giải bằng Brute Force (Generate and Test)...")
        start_time = time.time()
        is_solved = solver.solve()
        end_time = time.time()
        
        if is_solved:
            print(f"\n[+] ĐÃ TÌM THẤY LỜI GIẢI!\n")
            print(format_grid(puzzle, solver.grid))
            print("-" * 40)
            print(f"Thời gian chạy:      {end_time - start_time:.6f} giây")
            print(f"Số node mở rộng:     {solver.nodes_expanded} nodes")
            print("-" * 40)
        else:
            print("[-] Bài toán không có lời giải.")
    except Exception as e:
        print(f"Lỗi: {e}")