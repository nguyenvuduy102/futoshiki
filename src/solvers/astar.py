import time
import os
import copy
import heapq
from collections import deque

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

class State:
    """
    Đại diện cho một trạng thái trong không gian tìm kiếm A*.
    Bao gồm: lưới hiện tại, domains hiện tại, chi phí g(n) và heuristic h(n).
    """
    def __init__(self, grid, domains, g, h, tie_breaker):
        self.grid = grid
        self.domains = domains
        self.g = g                  # Chi phí từ node gốc (số ô đã điền)
        self.h = h                  # Heuristic: số ô còn trống
        self.f = self.g + self.h    # Hàm đánh giá f(n) = g(n) + h(n)
        
        # Tie-breaker (tổng kích thước các domains). 
        # Dùng để ưu tiên các trạng thái có ít lựa chọn hơn (tương tự MRV) khi f(n) bằng nhau.
        self.tie_breaker = tie_breaker 

    def __lt__(self, other):
        # Ưu tiên f(n) nhỏ nhất. Nếu f(n) bằng nhau (thường xuyên xảy ra trong CSP),
        # ưu tiên trạng thái có tie_breaker (tổng số lượng domain còn lại) nhỏ hơn.
        if self.f == other.f:
            return self.tie_breaker < other.tie_breaker
        return self.f < other.f


class AStarSolver:
    """
    Thuật toán A* Search kết hợp Arc-Consistency (AC-3).
    Sử dụng Min-Heap (Priority Queue) để duyệt các trạng thái tiềm năng nhất.
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.N = puzzle.N
        self.grid = copy.deepcopy(puzzle.grid)
        self.nodes_expanded = 0
        
        self.domains = self._initialize_domains()
        self.inequality_constraints = extract_inequality_constraints(puzzle)
        self.arcs = self._build_arc_map()

    def _initialize_domains(self):
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
        arcs = {(r, c): [] for r in range(self.N) for c in range(self.N)}
        for con in self.inequality_constraints:
            (r1, c1), (r2, c2), rel = con.cell1, con.cell2, con.relation
            if rel == '<':
                arcs[(r1, c1)].append(((r2, c2), '<'))
                arcs[(r2, c2)].append(((r1, c1), '>'))
            elif rel == '>':
                arcs[(r1, c1)].append(((r2, c2), '>'))
                arcs[(r2, c2)].append(((r1, c1), '<'))
        return arcs

    def _ac3_propagate(self, domains, initial_queue=None):
        """
        Thuật toán AC-3 để cắt tỉa domain. Trả về False nếu có domain rỗng (Vô nghiệm).
        """
        queue = initial_queue if initial_queue else deque()
        if not initial_queue:
            for cell, neighbors in self.arcs.items():
                for (nbr, rel) in neighbors:
                    queue.append((cell, nbr, rel))

        while queue:
            (r1, c1), (r2, c2), rel = queue.popleft()
            to_remove = set()
            
            for v1 in domains[r1][c1]:
                satisfied = False
                for v2 in domains[r2][c2]:
                    if rel == '<' and v1 < v2: satisfied = True; break
                    elif rel == '>' and v1 > v2: satisfied = True; break
                if not satisfied:
                    to_remove.add(v1)

            if to_remove:
                domains[r1][c1] -= to_remove
                if len(domains[r1][c1]) == 0:
                    return False # Mâu thuẫn
                for (nbr2, rel2) in self.arcs[(r1, c1)]:
                    if nbr2 != (r2, c2):
                        queue.append(((r1, c1), nbr2, rel2))
        return True

    def _calculate_heuristic(self, domains):
        """
        Hàm Heuristic: Đếm số ô chưa được gán giá trị (len(domain) > 1).
        Hàm này là Admissible (Chấp nhận được) vì mỗi ô cần đúng 1 bước để điền.
        Đồng thời tính tổng kích thước domain để làm tie-breaker.
        """
        unassigned = 0
        total_domain_size = 0
        for r in range(self.N):
            for c in range(self.N):
                d_size = len(domains[r][c])
                if d_size > 1:
                    unassigned += 1
                total_domain_size += d_size
        return unassigned, total_domain_size

    def _select_best_cell(self, domains):
        """Chọn ô trống để phát triển (Sử dụng MRV để giảm nhánh)."""
        min_size = float('inf')
        chosen = None
        for r in range(self.N):
            for c in range(self.N):
                d_size = len(domains[r][c])
                if d_size > 1 and d_size < min_size:
                    min_size = d_size
                    chosen = (r, c)
        return chosen

    def solve(self):
        """Vòng lặp chính của thuật toán A* Search"""
        # Bước 1: Lan truyền ràng buộc ban đầu
        if not self._ac3_propagate(self.domains):
            return False

        # Khởi tạo PQ và nạp trạng thái gốc
        h_val, tie_breaker = self._calculate_heuristic(self.domains)
        initial_state = State(self.grid, self.domains, g=0, h=h_val, tie_breaker=tie_breaker)
        
        pq = []
        heapq.heappush(pq, initial_state)

        while pq:
            # Lấy trạng thái có f(n) nhỏ nhất
            current_state = heapq.heappop(pq)
            
            # Kiểm tra trạng thái đích
            if current_state.h == 0:
                # Đã điền xong toàn bộ bảng
                for r in range(self.N):
                    for c in range(self.N):
                        self.grid[r][c] = next(iter(current_state.domains[r][c]))
                return True

            # Chọn 1 ô trống để sinh trạng thái con (MRV)
            cell = self._select_best_cell(current_state.domains)
            if not cell:
                continue
                
            r, c = cell

            # Sinh các trạng thái con cho mỗi giá trị khả dĩ
            for v in current_state.domains[r][c]:
                # Deep copy grid và domains
                new_grid = [row[:] for row in current_state.grid]
                new_grid[r][c] = v
                
                new_domains = [[set(current_state.domains[i][j]) for j in range(self.N)] for i in range(self.N)]
                new_domains[r][c] = {v}
                
                # Cập nhật ràng buộc hàng và cột (A3a, A3b)
                is_valid = True
                for i in range(self.N):
                    if i != c and v in new_domains[r][i]:
                        new_domains[r][i].discard(v)
                        if not new_domains[r][i]: is_valid = False; break
                    if i != r and v in new_domains[i][c]:
                        new_domains[i][c].discard(v)
                        if not new_domains[i][c]: is_valid = False; break
                
                if not is_valid: continue

                # Chạy AC-3 để cắt tỉa (Pruning). Nếu vô nghiệm -> h = infinity (bỏ qua)
                queue = deque()
                for (nbr, rel) in self.arcs[(r, c)]:
                    queue.append(((r, c), nbr, rel))
                
                if self._ac3_propagate(new_domains, initial_queue=queue):
                    self.nodes_expanded += 1
                    g_new = current_state.g + 1
                    h_new, tie_new = self._calculate_heuristic(new_domains)
                    
                    child_state = State(new_grid, new_domains, g_new, h_new, tie_new)
                    heapq.heappush(pq, child_state)

        return False


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "..", "Inputs", "input-03.txt")
    
    try:
        puzzle = parse_input(test_file)
        solver = AStarSolver(puzzle)
        
        print("\nBắt đầu giải bằng A* Search (với AC-3 Heuristic)...")
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
            print("[-] Không có lời giải.")
    except Exception as e:
        print(f"Lỗi: {e}")