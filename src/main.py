import os
import time
import glob

# Import các module core
from core.parser import parse_input
from core.output_formatter import write_output

# Import các solver (Hiện tại mới có Backtracking, ta sẽ mở khóa các module khác sau)
from solvers.backtracking import BacktrackingSolver
from solvers.brute_force import BruteForceSolver
from solvers.forward_chaining import ForwardChainingSolver
from solvers.backward_chaining import BackwardChainingSolver
from solvers.astar import AStarSolver

def run_solver(puzzle, algorithm_choice):
    """
    Khởi tạo và chạy thuật toán tương ứng dựa trên lựa chọn của người dùng.
    """
    solver = None
    if algorithm_choice == '1':
        solver = BacktrackingSolver(puzzle)
        algo_name = "Backtracking"
    elif algorithm_choice == '2':
        solver = BruteForceSolver(puzzle)
        algo_name = "Brute Force"
    elif algorithm_choice == '3':
        solver = ForwardChainingSolver(puzzle)
        algo_name = "Forward Chaining"
    elif algorithm_choice == '4':
        solver = BackwardChainingSolver(puzzle)
        algo_name = "Backward Chaining (SLD)"
    elif algorithm_choice == '5':
        solver = AStarSolver(puzzle)
        algo_name = "A* Search"
    else:
        print("[-] Lựa chọn không hợp lệ hoặc thuật toán chưa được cài đặt!")
        return None, 0, 0, ""

    print(f"\n[*] Đang giải bằng thuật toán: {algo_name}...")
    
    start_time = time.time()
    is_solved = solver.solve()
    end_time = time.time()
    
    exec_time = end_time - start_time
    nodes = getattr(solver, 'nodes_expanded', 0) # Lấy số node mở rộng nếu solver có hỗ trợ
    
    if is_solved:
        return solver.grid, exec_time, nodes, algo_name
    else:
        return None, exec_time, nodes, algo_name

def process_file(filepath, algorithm_choice):
    """
    Xử lý một file input cụ thể: Đọc, Giải, và In kết quả.
    """
    filename = os.path.basename(filepath)
    print(f"\n{'='*50}")
    print(f" ĐANG XỬ LÝ: {filename}")
    print(f"{'='*50}")

    try:
        puzzle = parse_input(filepath)
        print(f"Kích thước lưới: {puzzle.N}x{puzzle.N}")
        
        solved_grid, exec_time, nodes, algo_name = run_solver(puzzle, algorithm_choice)
        
        if solved_grid:
            print(f"\n[+] TÌM THẤY LỜI GIẢI ({filename}):")
            # Ghi ra file và lấy chuỗi định dạng
            output_path, formatted_result = write_output(puzzle, solved_grid, filepath)
            print(formatted_result)
            
            print(f"\n[Thống kê - {algo_name}]")
            print(f"Thời gian chạy : {exec_time:.6f} giây")
            print(f"Số node mở rộng: {nodes} nodes")
            print(f"Đã lưu kết quả : {output_path}")
        else:
            if algo_name:
                print("\n[-] Bài toán KHÔNG có lời giải (hoặc input sai logic).")
    except Exception as e:
        print(f"\n[-] LỖI khi xử lý file {filename}: {e}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    inputs_dir = os.path.join(current_dir,"..", "Inputs")
    
    if not os.path.exists(inputs_dir):
        print(f"[-] Không tìm thấy thư mục Inputs tại: {inputs_dir}")
        return

    while True:
        print("\n" + "#"*40)
        print(" ĐỒ ÁN 2: FUTOSHIKI SOLVER (LOGIC)")
        print("#"*40)
        print("1. Chọn thuật toán để giải một file (Test case)")
        print("2. Chạy TẤT CẢ các file (Batch mode - Phục vụ báo cáo)")
        print("0. Thoát")
        
        choice = input("\nNhập lựa chọn của bạn: ").strip()
        
        if choice == '0':
            print(" see you later!")
            break
            
        elif choice in ['1', '2']:
            print("\n--- DANH SÁCH THUẬT TOÁN ---")
            print("1. Backtracking (Baseline)")
            print("2. Brute Force ")
            print("3. Forward Chaining ")
            print("4. Backward Chaining ")
            print("5. A* Search")
            algo_choice = input("Chọn thuật toán (1-5): ").strip()
            
            # Lấy danh sách file input và sắp xếp theo tên
            input_files = sorted(glob.glob(os.path.join(inputs_dir, "input-*.txt")))
            
            if not input_files:
                print("[-] Thư mục Inputs trống!")
                continue

            if choice == '1':
                print("\n--- DANH SÁCH TEST CASE ---")
                for i, filepath in enumerate(input_files):
                    print(f"{i+1}. {os.path.basename(filepath)}")
                
                try:
                    file_idx = int(input(f"Chọn file (1-{len(input_files)}): ").strip()) - 1
                    if 0 <= file_idx < len(input_files):
                        process_file(input_files[file_idx], algo_choice)
                    else:
                        print("[-] Lựa chọn file không hợp lệ!")
                except ValueError:
                    print("[-] Vui lòng nhập số!")
                    
            elif choice == '2':
                print(f"\n[*] Đang chạy tự động {len(input_files)} test cases...")
                for filepath in input_files:
                    process_file(filepath, algo_choice)
        else:
            print("[-] Lựa chọn không hợp lệ. Vui lòng thử lại!")

if __name__ == "__main__":
    main()