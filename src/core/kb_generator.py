import os

# Import hàm parse_input từ file parser.py cùng thư mục
try:
    from core.parser import parse_input
except ImportError:
    from parser import parse_input

class KBGenerator:
    """
    Lớp chịu trách nhiệm sinh Ground Knowledge Base dạng CNF 
    từ các tiên đề First-Order Logic (FOL).
    """
    def __init__(self, puzzle):
        self.N = puzzle.N
        self.puzzle = puzzle
        self.clauses = [] # Lưu trữ danh sách các mệnh đề CNF

    def to_var(self, i, j, v):
        """
        Mã hóa tọa độ (i, j) và giá trị v thành một biến nguyên duy nhất.
        i, j, v đều được tính từ 1 đến N.
        Dấu âm (-) ở bên ngoài sẽ biểu thị phép phủ định (NOT).
        """
        return (i - 1) * (self.N ** 2) + (j - 1) * self.N + v

    def from_var(self, var):
        """
        Giải mã từ số nguyên về lại (i, j, v) để phục vụ cho việc in kết quả
        hay debug trong quá trình suy diễn.
        Trat về tuple: (is_positive, i, j, v)
        """
        is_positive = var > 0
        abs_var = abs(var) - 1
        i = (abs_var // (self.N ** 2)) + 1
        j = ((abs_var % (self.N ** 2)) // self.N) + 1
        v = (abs_var % self.N) + 1
        return is_positive, i, j, v

    def generate_kb(self):
        """
        Sinh toàn bộ các mệnh đề CNF dựa trên 5 bộ tiên đề.
        Mỗi mệnh đề (clause) là một list các số nguyên đại diện cho phép OR.
        Toàn bộ KB là một list các mệnh đề đại diện cho phép AND.
        """
        self.clauses = []
        N = self.N

        # ---------------------------------------------------------
        # A1: Mỗi ô có ít nhất 1 giá trị
        # Val(i,j,1) v Val(i,j,2) v ... v Val(i,j,N)
        # ---------------------------------------------------------
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                clause = [self.to_var(i, j, v) for v in range(1, N + 1)]
                self.clauses.append(clause)

        # ---------------------------------------------------------
        # A2: Mỗi ô có nhiều nhất 1 giá trị
        # ~Val(i,j,v1) v ~Val(i,j,v2) với mọi v1 != v2
        # ---------------------------------------------------------
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                for v1 in range(1, N + 1):
                    for v2 in range(v1 + 1, N + 1): # v2 > v1 để tránh trùng lặp tổ hợp
                        self.clauses.append([-self.to_var(i, j, v1), -self.to_var(i, j, v2)])

        # ---------------------------------------------------------
        # A3a: Ràng buộc duy nhất trên Hàng (Row uniqueness)
        # ---------------------------------------------------------
        for i in range(1, N + 1):
            for v in range(1, N + 1):
                for j1 in range(1, N + 1):
                    for j2 in range(j1 + 1, N + 1):
                        self.clauses.append([-self.to_var(i, j1, v), -self.to_var(i, j2, v)])

        # ---------------------------------------------------------
        # A3b: Ràng buộc duy nhất trên Cột (Column uniqueness)
        # ---------------------------------------------------------
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                for i1 in range(1, N + 1):
                    for i2 in range(i1 + 1, N + 1):
                        self.clauses.append([-self.to_var(i1, j, v), -self.to_var(i2, j, v)])

        # ---------------------------------------------------------
        # A4: Bất phương trình ngang (Horizontal Constraints)
        # Nếu ô(i, j) < ô(i, j+1), thì không thể có v1 >= v2.
        # Phủ định điều kiện vi phạm: ~Val(i, j, v1) v ~Val(i, j+1, v2)
        # ---------------------------------------------------------
        for i in range(1, N + 1):
            for j in range(1, N): # Chỉ chạy đến N-1
                constraint = self.puzzle.horizontal_constraints[i-1][j-1]
                if constraint == 1: # Left < Right
                    for v1 in range(1, N + 1):
                        for v2 in range(1, N + 1):
                            if v1 >= v2:
                                self.clauses.append([-self.to_var(i, j, v1), -self.to_var(i, j+1, v2)])
                elif constraint == -1: # Left > Right
                    for v1 in range(1, N + 1):
                        for v2 in range(1, N + 1):
                            if v1 <= v2:
                                self.clauses.append([-self.to_var(i, j, v1), -self.to_var(i, j+1, v2)])

        # ---------------------------------------------------------
        # A4: Bất phương trình dọc (Vertical Constraints)
        # ---------------------------------------------------------
        for i in range(1, N): # Chỉ chạy đến N-1
            for j in range(1, N + 1):
                constraint = self.puzzle.vertical_constraints[i-1][j-1]
                if constraint == 1: # Top < Bottom
                    for v1 in range(1, N + 1):
                        for v2 in range(1, N + 1):
                            if v1 >= v2:
                                self.clauses.append([-self.to_var(i, j, v1), -self.to_var(i+1, j, v2)])
                elif constraint == -1: # Top > Bottom
                    for v1 in range(1, N + 1):
                        for v2 in range(1, N + 1):
                            if v1 <= v2:
                                self.clauses.append([-self.to_var(i, j, v1), -self.to_var(i+1, j, v2)])

        # ---------------------------------------------------------
        # A5: Dữ kiện ban đầu (Given Clues)
        # Đây là các Unit Clauses (mệnh đề chỉ có 1 phần tử)
        # ---------------------------------------------------------
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                val = self.puzzle.grid[i-1][j-1]
                if val != 0:
                    self.clauses.append([self.to_var(i, j, val)])

        return self.clauses


# Khối code test nhanh
if __name__ == "__main__":
    # Đảm bảo đường dẫn tuyệt đối động giống như đã chốt ở parser.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-01.txt")
    
    try:
        puzzle = parse_input(test_file)
        kb_gen = KBGenerator(puzzle)
        cnf_clauses = kb_gen.generate_kb()
        
        print(f"Đã sinh thành công {len(cnf_clauses)} mệnh đề (clauses) dạng CNF cho lưới {puzzle.N}x{puzzle.N}!")
        
        # In thử 5 mệnh đề đầu tiên và 5 mệnh đề cuối cùng để kiểm tra
        print("\n5 mệnh đề đầu tiên (A1 - Mỗi ô có ít nhất 1 giá trị):")
        for c in cnf_clauses[:5]:
            print(c)
            
        print("\n5 mệnh đề cuối cùng (A5 - Dữ kiện có sẵn từ input):")
        for c in cnf_clauses[-5:]:
            print(c)
            
    except Exception as e:
        print(f"Lỗi: {e}")