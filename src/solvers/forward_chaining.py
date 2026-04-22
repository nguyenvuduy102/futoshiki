import time
import os
import copy

try:
    from core.parser import parse_input
    from core.output_formatter import format_grid
    from core.constraint import extract_inequality_constraints
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.parser import parse_input
    from core.output_formatter import format_grid
    from core.constraint import extract_inequality_constraints

'''
Số node mở rộng (nodes_expanded) là số lần solver phải gán một giá trị thử và quay lui (backtracking) khi Forward Chaining không thể tự động tìm ra lời giải hoàn toàn.

'''
class ForwardChainingSolver:

    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.N = puzzle.N
        self.grid = copy.deepcopy(puzzle.grid)

        # Thống kê
        self.nodes_expanded = 0       # Số lần gán giá trị (khi FC đơn thuần không đủ)
        self.inferences_made = 0      # Số lần suy diễn (loại giá trị khỏi domain)
        self.fc_propagations = 0      # Số vòng lặp forward chaining

        # Khởi tạo domains: domain[r][c] = set các giá trị có thể của ô (r,c)
        self.domains = self._initialize_domains()

        # Trích xuất danh sách ràng buộc bất phương trình
        self.inequality_constraints = extract_inequality_constraints(puzzle)

        # Tổ chức arc list: arcs[cell] = list các (neighbor_cell, relation)
        # cell < neighbor => relation = '<'
        # cell > neighbor => relation = '>'
        self.arcs = self._build_arc_map()

    # =========================================================================
    # KHỞI TẠO
    # =========================================================================

    def _initialize_domains(self):
        """
        Khởi tạo domain cho từng ô:
        - Ô đã có giá trị (given clue): domain = {v}
        - Ô trống: domain = {1, 2, ..., N}
        """
        N = self.N
        domains = [[None] * N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                if self.grid[r][c] != 0:
                    domains[r][c] = {self.grid[r][c]}
                else:
                    domains[r][c] = set(range(1, N + 1))
        return domains

    def _build_arc_map(self):
        """
        Xây dựng bản đồ các arc từ danh sách ràng buộc.
        arcs[(r,c)] = list[(neighbor, relation)]
        - relation '<': cell < neighbor
        - relation '>': cell > neighbor
        """
        arcs = {}
        N = self.N
        for r in range(N):
            for c in range(N):
                arcs[(r, c)] = []

        for con in self.inequality_constraints:
            (r1, c1), (r2, c2), rel = con.cell1, con.cell2, con.relation
            if rel == '<':
                arcs[(r1, c1)].append(((r2, c2), '<'))
                arcs[(r2, c2)].append(((r1, c1), '>'))
            elif rel == '>':
                arcs[(r1, c1)].append(((r2, c2), '>'))
                arcs[(r2, c2)].append(((r1, c1), '<'))
        return arcs

    # =========================================================================
    # FORWARD CHAINING - PROPAGATION CORE
    # =========================================================================

    def _forward_chain(self, domains):
        """
        Vòng lặp Forward Chaining chính.

        Lặp liên tục đến khi không còn suy diễn nào được thực hiện:
          1. Với mỗi ô đã được xác định (domain size = 1):
             - Lan truyền ràng buộc hàng/cột: loại giá trị đó khỏi các ô
               cùng hàng/cột (áp dụng A3a, A3b).
             - Lan truyền ràng buộc bất phương trình: thu hẹp domain
               của các ô liên kết qua arc.
          2. Với mỗi ô chưa xác định: kiểm tra nếu chỉ còn 1 giá trị thỏa
             ràng buộc => xác định ô đó.

        Trả về:
          - True: propagation thành công, domains đã cập nhật.
          - False: phát hiện contradiction (domain rỗng).
        """
        N = self.N
        changed = True

        while changed:
            changed = False
            self.fc_propagations += 1

            # -----------------------------------------------------------------
            # BƯỚC 1: Suy diễn từ các ô đã xác định
            # Tương ứng tiên đề A3a (row uniqueness), A3b (col uniqueness)
            # -----------------------------------------------------------------
            for r in range(N):
                for c in range(N):
                    if len(domains[r][c]) == 1:
                        assigned_val = next(iter(domains[r][c]))

                        # Loại assigned_val khỏi tất cả ô cùng hàng
                        for c2 in range(N):
                            if c2 != c and assigned_val in domains[r][c2]:
                                domains[r][c2].discard(assigned_val)
                                self.inferences_made += 1
                                changed = True
                                if len(domains[r][c2]) == 0:
                                    return False  # Contradiction

                        # Loại assigned_val khỏi tất cả ô cùng cột
                        for r2 in range(N):
                            if r2 != r and assigned_val in domains[r2][c]:
                                domains[r2][c].discard(assigned_val)
                                self.inferences_made += 1
                                changed = True
                                if len(domains[r2][c]) == 0:
                                    return False  # Contradiction

            # -----------------------------------------------------------------
            # BƯỚC 2: AC-3 - Arc Consistency cho ràng buộc bất phương trình
            # Tương ứng tiên đề A4 (horizontal & vertical inequality)
            # -----------------------------------------------------------------
            ac3_changed, ok = self._ac3_propagate(domains)
            if not ok:
                return False
            # Nếu AC-3 thu hẹp được domain, tiếp tục vòng lặp để
            # Bước 1 có thể lan truyền thêm từ các ô vừa được xác định.
            if ac3_changed:
                changed = True

        return True

    def _ac3_propagate(self, domains):
        """
        Chạy một bước AC-3 trên tất cả các arc bất phương trình.

        Với arc (cell1 rel cell2):
        - Nếu rel == '<': loại tất cả v1 khỏi domain[cell1] mà không tồn tại
          v2 trong domain[cell2] thỏa v1 < v2.
        - Nếu rel == '>': loại tất cả v1 khỏi domain[cell1] mà không tồn tại
          v2 trong domain[cell2] thỏa v1 > v2.

        Trả về tuple (changed, ok):
          - changed: True nếu có ít nhất 1 giá trị bị loại khỏi domain nào đó.
          - ok: False nếu phát hiện domain rỗng (contradiction).
        """
        from collections import deque

        any_changed = False

        # Khởi tạo queue với tất cả arc
        queue = deque()
        for cell, neighbors in self.arcs.items():
            for (nbr, rel) in neighbors:
                queue.append((cell, nbr, rel))

        while queue:
            (r1, c1), (r2, c2), rel = queue.popleft()

            # Tính tập giá trị cần loại khỏi domain[r1][c1]
            to_remove = set()
            for v1 in domains[r1][c1]:
                # Kiểm tra xem có giá trị v2 nào trong domain[r2][c2] thỏa mãn không
                satisfied = False
                for v2 in domains[r2][c2]:
                    if rel == '<' and v1 < v2:
                        satisfied = True
                        break
                    elif rel == '>' and v1 > v2:
                        satisfied = True
                        break
                if not satisfied:
                    to_remove.add(v1)

            if to_remove:
                domains[r1][c1] -= to_remove
                self.inferences_made += len(to_remove)
                self.fc_propagations += 1
                any_changed = True

                if len(domains[r1][c1]) == 0:
                    return True, False  # changed=True, contradiction

                # Thêm lại tất cả arc liên quan đến (r1,c1) vào queue
                for (nbr2, rel2) in self.arcs[(r1, c1)]:
                    queue.append(((r1, c1), nbr2, rel2))

        return any_changed, True

    # =========================================================================
    # KIỂM TRA HỢP LỆ (dùng khi backtrack)
    # =========================================================================

    def _is_consistent(self, domains, r, c, v):
        """
        Kiểm tra nhanh xem việc gán v vào (r, c) có vi phạm ràng buộc ngay lập tức không.
        Dùng để lọc ứng viên trước khi gán trong phase backtracking.
        """
        # Hàng và cột
        for c2 in range(self.N):
            if c2 != c and domains[r][c2] == {v}:
                return False
        for r2 in range(self.N):
            if r2 != r and domains[r2][c] == {v}:
                return False

        # Bất phương trình
        for (nbr, rel) in self.arcs[(r, c)]:
            nr, nc = nbr
            nbr_domain = domains[nr][nc]
            if rel == '<':
                # v phải < một số nào đó trong nbr_domain
                if not any(v < v2 for v2 in nbr_domain):
                    return False
            elif rel == '>':
                # v phải > một số nào đó trong nbr_domain
                if not any(v > v2 for v2 in nbr_domain):
                    return False
        return True

    # =========================================================================
    # CHỌN Ô TIẾP THEO (MRV Heuristic)
    # =========================================================================

    def _select_unassigned_cell(self, domains):
        """
        Chọn ô chưa xác định có domain nhỏ nhất (MRV - Minimum Remaining Values).
        Đây là heuristic giúp phát hiện contradiction sớm và giảm không gian tìm kiếm.
        """
        min_size = float('inf')
        chosen = None
        for r in range(self.N):
            for c in range(self.N):
                d_size = len(domains[r][c])
                if d_size > 1 and d_size < min_size:
                    min_size = d_size
                    chosen = (r, c)
        return chosen

    def _all_assigned(self, domains):
        """Kiểm tra tất cả ô đều đã được xác định (domain size = 1)."""
        return all(len(domains[r][c]) == 1
                   for r in range(self.N)
                   for c in range(self.N))

    # =========================================================================
    # GIẢI CHÍNH: FORWARD CHAINING + BACKTRACKING
    # =========================================================================

    def _solve_recursive(self, domains):
        """
        Kết hợp Forward Chaining và Backtracking:

        1. Chạy Forward Chaining để propagate hết có thể.
        2. Nếu đã xác định hết tất cả ô => thành công.
        3. Nếu còn ô chưa xác định => chọn ô có domain nhỏ nhất (MRV),
           thử từng giá trị, clone domains, gán giá trị, chạy lại FC.
        4. Nếu tất cả giá trị thất bại => backtrack.

        Điều này khác với Backtracking thuần túy ở chỗ: mỗi lần gán một giá trị,
        Forward Chaining được kích hoạt ngay lập tức để thu hẹp không gian tìm kiếm
        (lookahead), tránh đi vào nhiều nhánh sai.
        """
        # Bước 1: Forward Chaining propagation
        if not self._forward_chain(domains):
            return False  # Contradiction

        # Bước 2: Kiểm tra xong chưa
        if self._all_assigned(domains):
            return True

        # Bước 3: Chọn ô tiếp theo để gán (MRV)
        cell = self._select_unassigned_cell(domains)
        if cell is None:
            return True  # Không còn ô nào cần gán

        r, c = cell

        # Thử từng giá trị trong domain theo thứ tự tăng dần
        for v in sorted(domains[r][c]):
            if self._is_consistent(domains, r, c, v):
                # Clone domains để tránh ảnh hưởng khi backtrack
                new_domains = [row[:] for row in domains]
                new_domains = [[set(domains[r2][c2]) for c2 in range(self.N)]
                               for r2 in range(self.N)]

                # Gán giá trị v vào ô (r, c)
                new_domains[r][c] = {v}
                self.nodes_expanded += 1

                # Đệ quy với domains mới
                if self._solve_recursive(new_domains):
                    # Cập nhật domains của instance (dùng cho extract kết quả)
                    for r2 in range(self.N):
                        for c2 in range(self.N):
                            domains[r2][c2] = new_domains[r2][c2]
                    return True

        return False  # Tất cả giá trị đều thất bại => backtrack

    def solve(self):
        """
        Hàm giải chính. Trả về True nếu tìm được lời giải.
        Kết quả được lưu vào self.grid.
        """
        domains = [[set(self.domains[r][c]) for c in range(self.N)]
                   for r in range(self.N)]

        success = self._solve_recursive(domains)

        if success:
            # Chuyển kết quả từ domains về grid
            for r in range(self.N):
                for c in range(self.N):
                    if len(domains[r][c]) == 1:
                        self.grid[r][c] = next(iter(domains[r][c]))
                    else:
                        # Lưới chưa giải hoàn toàn (không nên xảy ra nếu success=True)
                        return False
            return True

        return False


# ==========================================
# Khối mã Test nhanh
# ==========================================
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        os.path.join(current_dir, "..", "Inputs", "input-01.txt"),
        os.path.join(current_dir, "..", "Inputs", "input-02.txt"),
    ]

    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"File không tồn tại: {test_file}")
            continue

        print(f"\nĐang đọc file: {test_file}...")
        puzzle = parse_input(test_file)

        solver = ForwardChainingSolver(puzzle)

        print(f"Bắt đầu giải bằng Forward Chaining (lưới {puzzle.N}x{puzzle.N})...")
        start_time = time.time()
        is_solved = solver.solve()
        end_time = time.time()

        if is_solved:
            print(f"\n[+] ĐÃ TÌM THẤY LỜI GIẢI!\n")
            print(format_grid(puzzle, solver.grid))
            print("-" * 40)
            print(f"Thời gian chạy      : {end_time - start_time:.6f} giây")
            print(f"Số node mở rộng     : {solver.nodes_expanded} nodes")
            print(f"Số suy diễn (FC)    : {solver.inferences_made} lần")
            print(f"Số vòng propagation : {solver.fc_propagations} lần")
            print("-" * 40)
        else:
            print("[-] Bài toán không có lời giải.")