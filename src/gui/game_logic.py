# src/gui/game_logic.py

def is_valid_move(puzzle, current_grid, r, c, v):
    """
    Kiểm tra luật Futoshiki cho 1 ô (Giống is_safe của Backtracking).
    Trả về True nếu hợp lệ, False nếu vi phạm.
    """
    N = puzzle.N
    
    # 1. Check Hàng và Cột
    for i in range(N):
        if i != c and current_grid[r][i] == v: return False
        if i != r and current_grid[i][c] == v: return False

    # 2. Check Ngang
    if c > 0 and current_grid[r][c-1] != 0:
        constraint = puzzle.horizontal_constraints[r][c-1]
        left_val = current_grid[r][c-1]
        if constraint == 1 and not (left_val < v): return False
        if constraint == -1 and not (left_val > v): return False
        
    if c < N - 1 and current_grid[r][c+1] != 0:
        constraint = puzzle.horizontal_constraints[r][c]
        right_val = current_grid[r][c+1]
        if constraint == 1 and not (v < right_val): return False
        if constraint == -1 and not (v > right_val): return False

    # 3. Check Dọc
    if r > 0 and current_grid[r-1][c] != 0:
        constraint = puzzle.vertical_constraints[r-1][c]
        top_val = current_grid[r-1][c]
        if constraint == 1 and not (top_val < v): return False
        if constraint == -1 and not (top_val > v): return False
        
    if r < N - 1 and current_grid[r+1][c] != 0:
        constraint = puzzle.vertical_constraints[r][c]
        bottom_val = current_grid[r+1][c]
        if constraint == 1 and not (v < bottom_val): return False
        if constraint == -1 and not (v > bottom_val): return False

    return True