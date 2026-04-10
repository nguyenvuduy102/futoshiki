import sys
import os
import time
import copy
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QFrame, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator

# Đảm bảo import được các module từ thư mục core và solvers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.parser import parse_input
from solvers.backtracking import BacktrackingSolver

class SolverThread(QThread):
    """Luồng xử lý để không treo GUI khi AI giải"""
    finished = pyqtSignal(object, float, int)

    def __init__(self, puzzle):
        super().__init__()
        self.puzzle = puzzle

    def run(self):
        start_time = time.time()
        solver = BacktrackingSolver(self.puzzle)
        success = solver.solve()
        exec_time = time.time() - start_time
        self.finished.emit(solver.grid if success else None, exec_time, solver.nodes_expanded)


class FutoshikiGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Futoshiki AI Solver - Đại Vương Edition")
        self.setMinimumSize(950, 750)
        self.puzzle = None
        self.current_grid = [] # Lưới lưu trạng thái hiện tại (bao gồm người chơi tự nhập)
        self.cell_widgets = {}
        self.init_ui()
        self.load_selected_level()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- PANEL ĐIỀU KHIỂN (BÊN TRÁI) ---
        control_panel = QFrame()
        control_panel.setFixedWidth(280)
        control_panel.setStyleSheet("background-color: #2c3e50; border-right: 2px solid #34495e;")
        control_layout = QVBoxLayout(control_panel)

        # Tiêu đề
        title = QLabel("FUTOSHIKI")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; margin-bottom: 20px; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title)

        # Chọn Ván chơi
        label_level = QLabel("🏆 Chọn Ván Chơi:")
        label_level.setStyleSheet("color: #bdc3c7; font-weight: bold; border: none;")
        control_layout.addWidget(label_level)

        self.combo_level = QComboBox()
        self.combo_level.addItems([f"Ván {i}" for i in range(1, 11)])
        self.combo_level.setFixedHeight(40)
        self.combo_level.setStyleSheet("padding-left: 10px; font-size: 14px;")
        self.combo_level.currentIndexChanged.connect(self.load_selected_level)
        control_layout.addWidget(self.combo_level)

        control_layout.addSpacing(20)

        # Chọn Thuật toán
        label_algo = QLabel("🧠 Thuật toán AI:")
        label_algo.setStyleSheet("color: #bdc3c7; font-weight: bold; border: none;")
        control_layout.addWidget(label_algo)

        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["Backtracking (Baseline)", "A* (Đang khóa)", "Forward Chaining (Đang khóa)"])
        self.combo_algo.setFixedHeight(40)
        control_layout.addWidget(self.combo_algo)

        control_layout.addSpacing(30)

        # Nút giải bằng AI
        self.btn_solve = QPushButton("⚡ AI GIẢI NGAY")
        self.btn_solve.setFixedHeight(60)
        self.btn_solve.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; border-radius: 8px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_solve.clicked.connect(self.start_solving)
        control_layout.addWidget(self.btn_solve)

        # Nút Reset Ván
        self.btn_reset = QPushButton("🔄 Chơi Lại / Reset")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.setStyleSheet("""
            QPushButton { background-color: #e67e22; color: white; border-radius: 5px; font-weight: bold;}
            QPushButton:hover { background-color: #f39c12; }
        """)
        self.btn_reset.clicked.connect(self.load_selected_level)
        control_layout.addWidget(self.btn_reset)
        
        # Nút Thoát
        self.btn_exit = QPushButton("❌ Thoát Game")
        self.btn_exit.setFixedHeight(40)
        self.btn_exit.setStyleSheet("""
            QPushButton { background-color: #c0392b; color: white; border-radius: 5px; font-weight: bold;}
            QPushButton:hover { background-color: #e74c3c; }
        """)
        self.btn_exit.clicked.connect(self.close)
        control_layout.addWidget(self.btn_exit)

        control_layout.addStretch()

        # Trạng thái
        self.status_label = QLabel("Sẵn sàng phục vụ...")
        self.status_label.setStyleSheet("color: #ecf0f1; background: #34495e; padding: 10px; border-radius: 5px; border: none;")
        self.status_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)

        main_layout.addWidget(control_panel)

        # --- VÙNG HIỂN THỊ LƯỚI (BÊN PHẢI) ---
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(0) # Đưa spacing về 0 để kiểm soát chính xác bằng kích thước label
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.grid_container, 1)

    def load_selected_level(self):
        """Tải file input và reset lại lưới"""
        index = self.combo_level.currentIndex() + 1
        level_file = f"input-{str(index).zfill(2)}.txt"
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "..", "Inputs", level_file)
        
        try:
            self.puzzle = parse_input(file_path)
            self.current_grid = copy.deepcopy(self.puzzle.grid) # Copy để người dùng nhập không ảnh hưởng đề gốc
            self.draw_puzzle()
            self.status_label.setText(f"Đã tải {level_file}!\nĐại Vương có thể tự điền số hoặc nhờ AI giải.")
            self.btn_solve.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"Lỗi: Không tìm thấy {level_file}")
            print(f"Path error: {e}")

    def draw_puzzle(self):
        """Vẽ lưới, hỗ trợ khoảng cách đều và QLineEdit cho phép nhập tay"""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.cell_widgets = {}
        N = self.puzzle.N
        
        cell_size = 55 if N < 7 else 45 
        sign_size = 30 # Kích thước cho các ô chứa dấu (hoặc khoảng trắng)

        # Validator chỉ cho phép nhập số từ 1 đến N
        validator = QIntValidator(1, N, self)

        for r in range(N):
            for c in range(N):
                val = self.puzzle.grid[r][c]
                
                # Thay QLabel bằng QLineEdit để cho phép nhập
                cell = QLineEdit()
                cell.setFixedSize(cell_size, cell_size)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(QFont("Arial", 18, QFont.Weight.Bold))
                cell.setValidator(validator)
                
                if val != 0:
                    # Ô đề bài: Khóa không cho sửa
                    cell.setText(str(val))
                    cell.setReadOnly(True)
                    cell.setStyleSheet("background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 5px; color: #2c3e50;")
                else:
                    # Ô trống: Cho phép nhập
                    cell.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 5px; color: #2980b9;")
                    # Bắt sự kiện người dùng gõ số
                    cell.textChanged.connect(lambda text, row=r, col=c: self.on_user_input(row, col, text))
                
                self.grid_layout.addWidget(cell, r * 2, c * 2)
                self.cell_widgets[(r, c)] = cell

                # Vẽ khoảng cách / dấu ngang
                if c < N - 1:
                    h_val = self.puzzle.horizontal_constraints[r][c]
                    sign = ""
                    if h_val == 1: sign = "<"
                    elif h_val == -1: sign = ">"
                    
                    lbl = QLabel(sign)
                    lbl.setFixedSize(sign_size, cell_size) # Cố định chiều rộng để căn lề đều
                    lbl.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold; border: none;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.grid_layout.addWidget(lbl, r * 2, c * 2 + 1)

            # Vẽ khoảng cách / dấu dọc
            if r < N - 1:
                for c in range(N):
                    v_val = self.puzzle.vertical_constraints[r][c]
                    sign = ""
                    if v_val == 1: sign = "∧"
                    elif v_val == -1: sign = "∨"
                    
                    lbl = QLabel(sign)
                    lbl.setFixedSize(cell_size, sign_size) # Cố định chiều cao
                    lbl.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold; border: none;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.grid_layout.addWidget(lbl, r * 2 + 1, c * 2)

    def on_user_input(self, r, c, text):
        """Xử lý khi người dùng nhập số vào lưới"""
        cell_widget = self.cell_widgets[(r, c)]
        
        if text == "":
            self.current_grid[r][c] = 0
            cell_widget.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 5px; color: #2980b9;")
            return

        val = int(text)
        self.current_grid[r][c] = val

        # Kiểm tra tính hợp lệ của số vừa nhập
        if self.is_valid_move(r, c, val):
            # Đúng logic
            cell_widget.setStyleSheet("background-color: #e8f8f5; border: 2px solid #2ecc71; border-radius: 5px; color: #27ae60;")
            self.check_win_condition()
        else:
            # Sai logic
            cell_widget.setStyleSheet("background-color: #fadedb; border: 2px solid #e74c3c; border-radius: 5px; color: #c0392b;")

    def is_valid_move(self, r, c, v):
        """Kiểm tra luật Futoshiki cho 1 ô (Giống is_safe của Backtracking)"""
        N = self.puzzle.N
        
        # 1. Check Hàng và Cột
        for i in range(N):
            if i != c and self.current_grid[r][i] == v: return False
            if i != r and self.current_grid[i][c] == v: return False

        # 2. Check Ngang
        if c > 0 and self.current_grid[r][c-1] != 0:
            constraint = self.puzzle.horizontal_constraints[r][c-1]
            left_val = self.current_grid[r][c-1]
            if constraint == 1 and not (left_val < v): return False
            if constraint == -1 and not (left_val > v): return False
            
        if c < N - 1 and self.current_grid[r][c+1] != 0:
            constraint = self.puzzle.horizontal_constraints[r][c]
            right_val = self.current_grid[r][c+1]
            if constraint == 1 and not (v < right_val): return False
            if constraint == -1 and not (v > right_val): return False

        # 3. Check Dọc
        if r > 0 and self.current_grid[r-1][c] != 0:
            constraint = self.puzzle.vertical_constraints[r-1][c]
            top_val = self.current_grid[r-1][c]
            if constraint == 1 and not (top_val < v): return False
            if constraint == -1 and not (top_val > v): return False
            
        if r < N - 1 and self.current_grid[r+1][c] != 0:
            constraint = self.puzzle.vertical_constraints[r][c]
            bottom_val = self.current_grid[r+1][c]
            if constraint == 1 and not (v < bottom_val): return False
            if constraint == -1 and not (v > bottom_val): return False

        return True

    def check_win_condition(self):
        """Kiểm tra xem người dùng đã chiến thắng chưa"""
        N = self.puzzle.N
        for r in range(N):
            for c in range(N):
                val = self.current_grid[r][c]
                if val == 0 or not self.is_valid_move(r, c, val):
                    return # Chưa điền xong hoặc có lỗi
        
        # Nếu chạy qua hết mà không return, nghĩa là đã thắng
        QMessageBox.information(self, "Chiến thắng!", "Quá xuất sắc! Đại Vương đã tự mình giải mã thành công câu đố này!")

    def start_solving(self):
        """Chạy AI giải thuật"""
        self.btn_solve.setEnabled(False)
        self.status_label.setText("🚀 Đại Vương đợi chút, AI đang tính toán...")
        
        # Reset lưới về mặc định của puzzle trước khi AI giải (xóa các số user nhập sai)
        self.current_grid = copy.deepcopy(self.puzzle.grid)
        self.draw_puzzle() 

        self.thread = SolverThread(self.puzzle)
        self.thread.finished.connect(self.on_solve_finished)
        self.thread.start()

    def on_solve_finished(self, result_grid, exec_time, nodes):
        if result_grid:
            self.current_grid = result_grid # Cập nhật lưới hiện tại
            for r in range(self.puzzle.N):
                for c in range(self.puzzle.N):
                    # Bỏ block tín hiệu textChanged để không kích hoạt hàm on_user_input khi AI điền số
                    self.cell_widgets[(r, c)].blockSignals(True)
                    self.cell_widgets[(r, c)].setText(str(result_grid[r][c]))
                    self.cell_widgets[(r, c)].setStyleSheet("background-color: #e8f8f5; border: 2px solid #2ecc71; border-radius: 5px; color: #27ae60;")
                    self.cell_widgets[(r, c)].blockSignals(False)

            self.status_label.setText(f"✅ AI Đã Giải Xong!\n⏱ {exec_time:.4f}s\n🧩 {nodes} nodes")
        else:
            self.status_label.setText("❌ Bế tắc! AI không tìm thấy lời giải!")
        self.btn_solve.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FutoshikiGUI()
    window.show()
    sys.exit(app.exec())