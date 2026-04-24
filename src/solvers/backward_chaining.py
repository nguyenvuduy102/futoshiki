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


class BackwardChainingSolver:
    """
    Thuật toán Suy diễn lùi (Backward Chaining) ứng dụng SLD Resolution kiểu Prolog.
    Mô phỏng quá trình: Đặt câu hỏi (Query) -> Chứng minh qua các Mệnh đề Horn -> Gán giá trị (Binding).
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.N = puzzle.N
        self.grid = copy.deepcopy(puzzle.grid)
        self.nodes_expanded = 0
        self.inferences_made = 0  
        # Tập hợp các mục tiêu (Goals) cầns chứng minh: là danh sách các ô trống.
        self.goals = self._extract_goals()

    def _extract_goals(self):
        """Trích xuất tất cả các ô cần tìm giá trị thành danh sách Goal."""
        goals = []
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] == 0:
                    goals.append((r, c))
        return goals

    # =====================================================================
    # KHỐI LOGIC: MÔ PHỎNG MỆNH ĐỀ HORN (HORN CLAUSES) TRONG PROLOG
    # Val(r, c, v) :- InRange(v), RowSafe(r, c, v), ColSafe(r, c, v), IneqSafe(r, c, v).
    # =====================================================================

    def prove_Val(self, r, c, v):
        """
        Chứng minh mệnh đề Val(r, c, v) là TRUE.
        Nó sẽ kiểm tra các điều kiện (Body của Horn clause).
        """
        if not self.prove_RowSafe(r, c, v): return False
        if not self.prove_ColSafe(r, c, v): return False
        if not self.prove_IneqSafe(r, c, v): return False
        return True

    def prove_RowSafe(self, r, c, v):
        """Chứng minh v không trùng lặp trên hàng r."""
        for i in range(self.N):
            if i != c and self.grid[r][i] == v:
                return False
        return True

    def prove_ColSafe(self, r, c, v):
        """Chứng minh v không trùng lặp trên cột c."""
        for i in range(self.N):
            if i != r and self.grid[i][c] == v:
                return False
        return True

    def prove_IneqSafe(self, r, c, v):
        """Chứng minh v thỏa mãn tất cả các ràng buộc bất phương trình xung quanh."""

        # 1. Ràng buộc bên trái (Left)
        if c > 0 and self.grid[r][c-1] != 0:
            con = self.puzzle.horizontal_constraints[r][c-1]
            v_left = self.grid[r][c-1]
            if con == 1 and not (v_left < v): return False
            if con == -1 and not (v_left > v): return False

        # 2. Ràng buộc bên phải (Right)
        if c < self.N - 1 and self.grid[r][c+1] != 0:
            con = self.puzzle.horizontal_constraints[r][c]
            v_right = self.grid[r][c+1]
            if con == 1 and not (v < v_right): return False
            if con == -1 and not (v > v_right): return False

        # 3. Ràng buộc phía trên (Top)
        if r > 0 and self.grid[r-1][c] != 0:
            con = self.puzzle.vertical_constraints[r-1][c]
            v_top = self.grid[r-1][c]
            if con == 1 and not (v_top < v): return False
            if con == -1 and not (v_top > v): return False

        # 4. Ràng buộc phía dưới (Bottom)
        if r < self.N - 1 and self.grid[r+1][c] != 0:
            con = self.puzzle.vertical_constraints[r][c]
            v_bottom = self.grid[r+1][c]
            if con == 1 and not (v < v_bottom): return False
            if con == -1 and not (v > v_bottom): return False

        return True

    # =====================================================================
    # SLD RESOLUTION (SUY DIỄN LÙI ĐỆ QUY TRÊN CÁC GOALS)
    # =====================================================================

    def ask_goal(self, goal_index):
        
        """
        Quá trình hỏi (Querying): Cố gắng giải quyết (resolve) Goal hiện tại.
        Nếu thành công, nó sẽ tiếp tục SLD Resolution với các Goal tiếp theo.
        """
        # Nếu đã duyệt qua hết tất cả các goals, nghĩa là chứng minh thành công
        if goal_index == len(self.goals):
            return True

        r, c = self.goals[goal_index]

        # Đặt câu hỏi truy vấn: Val(r, c, ?v) - v có thể là các giá trị từ 1 đến N
        for v in range(1, self.N + 1):

            self.inferences_made += 1
            # Áp dụng suy diễn lùi để chứng minh Val(r, c, v)
            if self.prove_Val(r, c, v):
                
                # Nếu chứng minh thành công phần đầu, thực hiện phép gán (Binding / Unification)
                self.grid[r][c] = v
                self.nodes_expanded += 1

                # Đệ quy hỏi Goal tiếp theo trong Goal Stack
                if self.ask_goal(goal_index + 1):
                    return True

                # Nếu nhánh này dẫn đến bế tắc, tháo gỡ (Undo Binding) và quay lui
                self.grid[r][c] = 0

        # Toàn bộ phép thử thất bại => Quay lui (Backtracking in SLD resolution)
        return False

    def solve(self):
        """Hàm kích hoạt bộ giải."""
        # Bắt đầu SLD resolution từ goal đầu tiên
        return self.ask_goal(0)


# ==========================================
# Khối mã Test nhanh thuật toán
# ==========================================
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-03.txt")
    
    try:
        puzzle = parse_input(test_file)
        solver = BackwardChainingSolver(puzzle)
        
        print("\nBắt đầu giải bằng Backward Chaining (SLD Resolution)...")
        start_time = time.time()
        is_solved = solver.solve()
        end_time = time.time()
        
        if is_solved:
            print(f"\n[+] ĐÃ CHỨNG MINH THÀNH CÔNG VÀ TÌM THẤY LỜI GIẢI!\n")
            print(format_grid(puzzle, solver.grid))
            print("-" * 40)
            print(f"Thời gian chạy:      {end_time - start_time:.6f} giây")
            print(f"Số node mở rộng:     {solver.nodes_expanded} nodes")
            print("-" * 40)
        else:
            print("[-] Không thể chứng minh được giải pháp (Vô nghiệm).")
    except Exception as e:
        print(f"Lỗi: {e}")