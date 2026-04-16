# src/gui/threads.py
import time
from PyQt6.QtCore import QThread, pyqtSignal

# Import các thuật toán
from solvers.backtracking import BacktrackingSolver
from solvers.brute_force import BruteForceSolver
from solvers.forward_chaining import ForwardChainingSolver
from solvers.backward_chaining import BackwardChainingSolver
from solvers.astar import AStarSolver

class SolverThread(QThread):
    """Luồng xử lý để không treo GUI khi AI giải"""
    finished = pyqtSignal(object, float, int)

    def __init__(self, puzzle, algo_name):
        super().__init__()
        self.puzzle = puzzle
        self.algo_name = algo_name

    def run(self):
        start_time = time.time()
        
        # Lựa chọn solver dựa trên tên thuật toán
        if self.algo_name == "Brute Force":
            solver = BruteForceSolver(self.puzzle)
        elif self.algo_name == "Forward Chaining":
            solver = ForwardChainingSolver(self.puzzle)
        elif self.algo_name == "Backward Chaining":
            solver = BackwardChainingSolver(self.puzzle)
        elif self.algo_name == "A* Search":
            solver = AStarSolver(self.puzzle)
        else:
            solver = BacktrackingSolver(self.puzzle) # Mặc định
            
        success = solver.solve()
        exec_time = time.time() - start_time
        
        # Emit kết quả về cho giao diện chính
        nodes = getattr(solver, 'nodes_expanded', 0)
        self.finished.emit(solver.grid if success else None, exec_time, nodes)