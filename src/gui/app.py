import sys
import os
import copy
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QFrame, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator

# Đảm bảo import được các module từ thư mục root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.parser import parse_input


from threads import SolverThread
from game_logic import is_valid_move

class FutoshikiGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Futoshiki AI Solver - Edition")
        self.setMinimumSize(950, 750)
        self.puzzle = None
        self.current_grid = []
        self.cell_widgets = {}
        
        self.init_ui()
        self.load_selected_level()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- PANEL ĐIỀU KHIỂN ---
        control_panel = QFrame()
        control_panel.setFixedWidth(280)
        control_panel.setStyleSheet("background-color: #2c3e50; border-right: 2px solid #34495e;")
        control_layout = QVBoxLayout(control_panel)

        title = QLabel("FUTOSHIKI")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; margin-bottom: 20px; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title)

        # Chọn Ván
        control_layout.addWidget(self._create_label("🏆 Chọn Ván Chơi:"))
        self.combo_level = QComboBox()
        self.combo_level.addItems([f"Ván {i}" for i in range(1, 15)])
        self.combo_level.setFixedHeight(40)
        self.combo_level.setStyleSheet(self._combo_stylesheet("#3498db"))
        self.combo_level.currentIndexChanged.connect(self.load_selected_level)
        control_layout.addWidget(self.combo_level)

        control_layout.addSpacing(20)

        # Chọn AI
        control_layout.addWidget(self._create_label("🧠 Thuật toán AI:"))
        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["Backtracking (Baseline)", "Brute Force", "Forward Chaining", "Backward Chaining", "A* Search"])
        self.combo_algo.setFixedHeight(40)
        self.combo_algo.setStyleSheet(self._combo_stylesheet("#9b59b6"))
        control_layout.addWidget(self.combo_algo)

        control_layout.addSpacing(30)

        # Buttons
        self.btn_solve = self._create_button("AI GIẢI NGAY", "#27ae60", "#2ecc71", 60)
        self.btn_solve.clicked.connect(self.start_solving)
        control_layout.addWidget(self.btn_solve)

        self.btn_stop = self._create_button("DỪNG LẠI", "#e74c3c", "#c0392b", 60)
        self.btn_stop.clicked.connect(self.stop_solving)
        self.btn_stop.hide() # Ẩn lúc mới mở app
        control_layout.addWidget(self.btn_stop)

        self.btn_reset = self._create_button("Chơi Lại / Reset", "#e67e22", "#f39c12", 40)
        self.btn_reset.clicked.connect(self.load_selected_level)
        control_layout.addWidget(self.btn_reset)
        
        self.btn_exit = self._create_button("Thoát Game", "#c0392b", "#e74c3c", 40)
        self.btn_exit.clicked.connect(self.close)
        control_layout.addWidget(self.btn_exit)

        control_layout.addStretch()

        # Status
        self.status_label = QLabel("Sẵn sàng phục vụ...")
        self.status_label.setStyleSheet("color: #ecf0f1; background: #34495e; padding: 10px; border-radius: 5px;")
        self.status_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)

        main_layout.addWidget(control_panel)

        # --- VÙNG HIỂN THỊ LƯỚI ---
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.grid_container, 1)

    # --- CÁC HÀM TIỆN ÍCH DÀNH CHO UI ---


    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #bdc3c7; font-weight: bold; border: none;")
        return lbl

    def _create_button(self, text, bg_color, hover_color, height):
        btn = QPushButton(text)
        btn.setFixedHeight(height)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {bg_color}; color: white; border-radius: 5px; font-weight: bold; font-size: 14px;}}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        return btn

    def _combo_stylesheet(self, hover_color):
        return f"""
            QComboBox {{ background-color: #ffffff; color: #2c3e50; border: 2px solid #bdc3c7; border-radius: 5px; padding-left: 10px; font-weight: bold; }}
            QComboBox:hover {{ border: 2px solid {hover_color}; }}
            QComboBox QAbstractItemView {{ background-color: #ffffff; selection-background-color: {hover_color}; color: black;}}
        """

    # --- LOGIC GIAO DIỆN CHÍNH ---

    def stop_solving(self):
        """Dừng AI ngay lập tức"""
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.terminate() # Ngắt luồng AI ngay lập tức
            self.thread.wait()      # Đợi luồng dọn dẹp xong
            self.status_label.setText("ĐÃ HỦY: đã dừng AI.")
            self._reset_ui_after_solve()

    def load_selected_level(self):
        index = self.combo_level.currentIndex() + 1
        level_file = f"input-{str(index).zfill(2)}.txt"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "..", "Inputs", level_file)
        
        try:
            self.puzzle = parse_input(file_path)
            self.current_grid = copy.deepcopy(self.puzzle.grid)
            self.draw_puzzle()
            self.status_label.setText(f"Đã tải {level_file}!\nCó thể tự điền số hoặc nhờ AI giải.")
            self.btn_solve.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"Lỗi: Không tìm thấy {level_file}")

    def draw_puzzle(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        self.cell_widgets = {}
        N = self.puzzle.N
        cell_size = 55 if N < 7 else 45 
        sign_size = 30 
        validator = QIntValidator(1, N, self)

        for r in range(N):
            for c in range(N):
                val = self.puzzle.grid[r][c]
                cell = QLineEdit()
                cell.setFixedSize(cell_size, cell_size)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(QFont("Arial", 18, QFont.Weight.Bold))
                cell.setMaxLength(len(str(N)))
                cell.setValidator(validator)
                
                if val != 0:
                    cell.setText(str(val))
                    cell.setReadOnly(True)
                    cell.setStyleSheet("background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 5px; color: #2c3e50;")
                else:
                    cell.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 5px; color: #2980b9;")
                    cell.textChanged.connect(lambda text, row=r, col=c: self.on_user_input(row, col, text))
                
                self.grid_layout.addWidget(cell, r * 2, c * 2)
                self.cell_widgets[(r, c)] = cell

                # Vẽ dấu ngang
                if c < N - 1:
                    h_val = self.puzzle.horizontal_constraints[r][c]
                    sign = "<" if h_val == 1 else ">" if h_val == -1 else ""
                    lbl = QLabel(sign)
                    lbl.setFixedSize(sign_size, cell_size)
                    lbl.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.grid_layout.addWidget(lbl, r * 2, c * 2 + 1)

            # Vẽ dấu dọc
            if r < N - 1:
                for c in range(N):
                    v_val = self.puzzle.vertical_constraints[r][c]
                    sign = "∧" if v_val == 1 else "∨" if v_val == -1 else ""
                    lbl = QLabel(sign)
                    lbl.setFixedSize(cell_size, sign_size)
                    lbl.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold;")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.grid_layout.addWidget(lbl, r * 2 + 1, c * 2)

    def on_user_input(self, r, c, text):
        cell_widget = self.cell_widgets[(r, c)]
        if text == "":
            self.current_grid[r][c] = 0
        else:
            try:
                val = int(text)
                if val < 1 or val > self.puzzle.N:
                    cell_widget.blockSignals(True) 
                    cell_widget.setText("")
                    cell_widget.blockSignals(False)
                    self.current_grid[r][c] = 0
                else:
                    self.current_grid[r][c] = val
            except ValueError:
                cell_widget.blockSignals(True) 
                cell_widget.setText("")
                cell_widget.blockSignals(False)
                self.current_grid[r][c] = 0

        self.update_grid_colors()
        self.check_win_condition()

    def update_grid_colors(self):
        for r in range(self.puzzle.N):
            for c in range(self.puzzle.N):
                if self.puzzle.grid[r][c] == 0:
                    cell_widget = self.cell_widgets[(r, c)]
                    val = self.current_grid[r][c]
                    
                    if val == 0:
                        cell_widget.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 5px; color: #2980b9;")
                    # Lấy is_valid_move từ module game_logic
                    elif is_valid_move(self.puzzle, self.current_grid, r, c, val):
                        cell_widget.setStyleSheet("background-color: #e8f8f5; border: 2px solid #2ecc71; border-radius: 5px; color: #27ae60;")
                    else:
                        cell_widget.setStyleSheet("background-color: #fadedb; border: 2px solid #e74c3c; border-radius: 5px; color: #c0392b;")

    def check_win_condition(self):
        for r in range(self.puzzle.N):
            for c in range(self.puzzle.N):
                val = self.current_grid[r][c]
                if val == 0 or not is_valid_move(self.puzzle, self.current_grid, r, c, val):
                    return 
        self.status_label.setText("🏆 BINGO! Giải mã thành công!")
        QMessageBox.information(self, "Chiến thắng!", "Quá xuất sắc! Bạn đã tự mình giải mã thành công câu đố này!")

    def start_solving(self):
        # 1. Ẩn nút Giải, Hiện nút Dừng
        self.btn_solve.hide()
        self.btn_stop.show()
        
        # 2. KHÓA các chức năng khác để tránh bấm tào lao
        self.combo_level.setEnabled(False)
        self.combo_algo.setEnabled(False)
        self.btn_reset.setEnabled(False)
        
        self.status_label.setText("AI đang tính toán, vui lòng đợi...")

  
        QApplication.processEvents()

        # 3. Chuẩn bị lưới
        self.current_grid = copy.deepcopy(self.puzzle.grid)
        self.draw_puzzle() 

        # 4. Kích hoạt AI ngầm
        algo_name = self.combo_algo.currentText().split(" (")[0]
        self.thread = SolverThread(self.puzzle, algo_name)
        self.thread.finished.connect(self.on_solve_finished)
        self.thread.start()

    def _reset_ui_after_solve(self):
        """Hàm phụ để khôi phục trạng thái các nút bấm"""
        self.btn_stop.hide()
        self.btn_solve.show()
        self.btn_solve.setEnabled(True)
        self.combo_level.setEnabled(True)
        self.combo_algo.setEnabled(True)
        self.btn_reset.setEnabled(True)

    def on_solve_finished(self, result_grid, exec_time, nodes):
        """Xử lý khi AI chạy xong hoặc bị lỗi"""
        if result_grid:
            self.current_grid = result_grid
            for r in range(self.puzzle.N):
                for c in range(self.puzzle.N):
                    self.cell_widgets[(r, c)].blockSignals(True)
                    self.cell_widgets[(r, c)].setText(str(result_grid[r][c]))
                    self.cell_widgets[(r, c)].setStyleSheet("background-color: #e8f8f5; border: 2px solid #2ecc71; border-radius: 5px; color: #27ae60;")
                    self.cell_widgets[(r, c)].blockSignals(False)
            self.status_label.setText(f"XONG!\n⏱ {exec_time:.4f}s\n🧩 {nodes} nodes")
        else:
            if "ĐÃ HỦY" not in self.status_label.text():
                self.status_label.setText("Bế tắc! Không tìm thấy lời giải.")
        
        self._reset_ui_after_solve()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FutoshikiGUI()
    window.show()
    sys.exit(app.exec())