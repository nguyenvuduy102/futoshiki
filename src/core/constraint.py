class InequalityConstraint:
    """
    Lớp đại diện cho một ràng buộc bất phương trình giữa 2 ô.
    Được sử dụng mạnh mẽ trong thuật toán Forward Chaining (Arc-Consistency).
    """
    def __init__(self, cell1, cell2, relation):
        """
        cell1: tuple (r1, c1) - Tọa độ ô thứ nhất
        cell2: tuple (r2, c2) - Tọa độ ô thứ hai
        relation: chuỗi '<' hoặc '>' cho biết cell1 < cell2 hay cell1 > cell2
        """
        self.cell1 = cell1
        self.cell2 = cell2
        self.relation = relation

    def is_satisfied(self, val1, val2):
        """
        Kiểm tra xem 2 giá trị được gán có thỏa mãn ràng buộc không.
        """
        if self.relation == '<':
            return val1 < val2
        elif self.relation == '>':
            return val1 > val2
        return False

    def __str__(self):
        return f"Cell{self.cell1} {self.relation} Cell{self.cell2}"


def extract_inequality_constraints(puzzle):
    """
    Hàm tiện ích: Quét qua toàn bộ dữ liệu puzzle và trích xuất tất cả 
    ràng buộc bất phương trình, gom chúng thành một danh sách các Object InequalityConstraint.
    """
    constraints = []
    N = puzzle.N

    # 1. Trích xuất ràng buộc ngang (Horizontal)
    for r in range(N):
        for c in range(N - 1):
            val = puzzle.horizontal_constraints[r][c]
            if val == 1:
                constraints.append(InequalityConstraint((r, c), (r, c+1), '<'))
            elif val == -1:
                constraints.append(InequalityConstraint((r, c), (r, c+1), '>'))

    # 2. Trích xuất ràng buộc dọc (Vertical)
    for r in range(N - 1):
        for c in range(N):
            val = puzzle.vertical_constraints[r][c]
            if val == 1:
                constraints.append(InequalityConstraint((r, c), (r+1, c), '<'))
            elif val == -1:
                constraints.append(InequalityConstraint((r, c), (r+1, c), '>'))

    return constraints

# Khối test nhanh
if __name__ == "__main__":
    import os
    try:
        from core.parser import parse_input
    except ImportError:
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from core.parser import parse_input

    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-01.txt")
    
    try:
        puzzle = parse_input(test_file)
        constraints = extract_inequality_constraints(puzzle)
        print(f"Đã trích xuất {len(constraints)} ràng buộc bất phương trình từ file.")
        for i, c in enumerate(constraints[:5]): # In thử 5 ràng buộc đầu
            print(f"  {i+1}. {c}")
    except Exception as e:
        print(f"Lỗi: {e}")