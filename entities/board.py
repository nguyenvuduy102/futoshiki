import heapq
import time

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import (
    QPointF,
    QPoint,
    QSequentialAnimationGroup,
    QPropertyAnimation,
    QRect,
    QEasingCurve,
    Qt,
    QTimer
)
import random
from entities.block import Block
from entities.operator import Operator


class Board(QLabel):
    def __init__(self, parent, grid_size: QPoint, position: QPoint, size, offset):
        super().__init__(parent)
        self.isWin = False
        self.grid_size = grid_size
        self.gridItems = []
        self.operator = []
        self._size = size
        self._offset = offset
        self.rows = grid_size.x()
        self.cols = grid_size.y() 
        self.total_cells = self.rows * self.cols
        self.constraits = {}
        self.padding = 40
        self._parent = parent
        self.grid_value = []
        width = (self.cols * size) + ((self.cols - 1) * offset) + (2 * self.padding)
        height = (self.rows * size) + ((self.rows - 1) * offset) + (2 * self.padding)
        self.setFixedSize(width, height)
        self.move(position.x() - self.padding, position.y() - self.padding)
        self.final_result_domains = None

        self.setStyleSheet(
            f"""
            
            """
        )

    def SetupGame(self):

        for item in self.gridItems:
            item.deleteLater()

        for op in self.operator:
            op.deleteLater()

        self.gridItems = []
        self.operator = []
        self.constraits = {}
        self.grid_value = []
        self.GridConstruct()
        self.CreateTableValue()
        self.OperatorConstruct()

        self.isWin = False

    def GridConstruct(self):
        size = self._size
        offset = self._offset
        self.gridItems = []
        for j in range(self.rows): 
            for i in range(self.cols):
                posX = self.padding + (i * (size + offset))
                posY = self.padding + (j * (size + offset))
                
                newPos = QPoint(posX, posY)
                color = "#EDF2EF"
                if (i + j) % 2 == 1: color = "#56876D" 

                item = Block(self, newPos, QPoint(size, size), color)
                item.show()
                self.gridItems.append(item)

    def get_valid_neighbor(self, index):
        while True:
            direction = random.randint(0, 3)
            is_invalid = (
                (direction == 0 and index < self.cols)
                or (direction == 2 and index >= self.total_cells - self.cols) 
                or (direction == 3 and index % self.cols == 0)
                or (direction == 1 and index % self.cols == self.cols - 1) 
            )
            if not is_invalid:
                return direction

    def OperatorConstruct(self):
        count = self.total_cells // 3
        self.operator = []
        self.constraits = {i: [] for i in range(self.total_cells)}
        existing_pairs = set()

        while len(self.operator) < count:
            index = random.randint(0, len(self.gridItems) - 1)
            neighborIndex = self.get_valid_neighbor(index)
            secondIndex = 0

            if neighborIndex == 0:
                secondIndex = index - self.cols
            elif neighborIndex == 1:
                secondIndex = index + 1
            elif neighborIndex == 2:
                secondIndex = index + self.cols
            elif neighborIndex == 3:
                secondIndex = index - 1

            pair = tuple(sorted((index, secondIndex)))
            if pair in existing_pairs:
                continue
            existing_pairs.add(pair)

            if index >= len(self.grid_value) or secondIndex >= len(self.grid_value):
                continue

            is_greater = self.grid_value[index] > self.grid_value[secondIndex]
            realtype = ">" if is_greater else "<"
            display_type = ""

            if neighborIndex == 1:
                display_type = ">" if is_greater else "<"
            elif neighborIndex == 3:
                display_type = "<" if is_greater else ">"
            elif neighborIndex == 0:
                display_type = "^" if is_greater else "v"
            elif neighborIndex == 2:
                display_type = "v" if is_greater else "^"

            self.constraits[index].append({"neighbor": secondIndex, "type": realtype})
            reverse_type = "<" if realtype == ">" else ">"
            self.constraits[secondIndex].append(
                {"neighbor": index, "type": reverse_type}
            )

            newOperator = Operator(
                self,
                self.gridItems[index],
                self.gridItems[secondIndex],
                display_type,
            )
            newOperator.show()
            self.operator.append(newOperator)

    def ShuffleArray(self, arr):
        limit = len(arr) - 1
        for j in range(len(arr) * 2):
            index1 = random.randint(0, limit)
            index2 = random.randint(0, limit)
            arr[index1], arr[index2] = arr[index2], arr[index1]
        return arr

    def CreateTableValue(self):
        nums = list(range(1, self.cols + 1))
        

        possibleValues = [self.ShuffleArray(nums.copy()) for _ in range(self.total_cells)]

        index = 0
        self.grid_value = []

        while index < self.total_cells:
            value = 0
            if len(possibleValues[index]) > 0:
                value = possibleValues[index].pop()
            else:

                possibleValues[index] = self.ShuffleArray(nums.copy())
                index -= 1
                if len(self.grid_value) > 0:
                    self.grid_value.pop()
                continue
                
            isValid = True
 
            for i in range(len(self.grid_value)):

                if i // self.cols == index // self.cols or i % self.cols == index % self.cols:
                    if value == self.grid_value[i]:
                        isValid = False
                        break
            
            if isValid:
                self.grid_value.append(value)

                self.gridItems[index].setText(str(value))
                index += 1


        deleteCount = int(self.total_cells * 0.7) 
        
        while deleteCount > 0:
            idx = random.randint(0, self.total_cells - 1)
            
            if self.gridItems[idx].text() == "":
                continue
                
        
            self.gridItems[idx].isConstance = False
            self.gridItems[idx].SetConstance() 

            self.gridItems[idx].setText("")
            deleteCount -= 1

    def IsLegal(self, index, val, board):
        row_idx = index // self.cols
        col_idx = index % self.cols

        for i in range(self.cols):
            if board[row_idx * self.cols + i] == val: return False
        
        for i in range(self.rows):
            if board[i * self.cols + col_idx] == val: return False


        for check in self.constraits[index]:
            neighbor_val = board[check["neighbor"]]
            if neighbor_val != 0:
                if check["type"] == ">" and not (val > neighbor_val): return False
                if check["type"] == "<" and not (val < neighbor_val): return False

        return True

    def BrutalForceSolver(self):
        starttime = time.perf_counter()
        data = []
        empty = []

        for i in range(self.total_cells):
            txt = self.gridItems[i].text()
            if txt != "" and self.gridItems[i].isConstance:
                data.append(int(txt))
            else:
                data.append(0)
                empty.append(i)

        def solve(step):
            if step == len(empty): return True

            idx = empty[step]
            for num in range(1, self.cols + 1):
                if self.IsLegal(idx, num, data):
                    data[idx] = num
                    if solve(step + 1): return True
                    data[idx] = 0
            return False

        if solve(0):
            endtime = time.perf_counter()
            print(f"Giải xong trong {(endtime - starttime):.4f} giây!")
            self.DisplayResultSlowly(data, empty)
        else:
            print("Không có lời giải!")



    def get_best_empty_cell(self, current_domains, emptyList):
        bestIdx = None
        minOptions = 99

        for idx in emptyList:

            num_options = len(current_domains[idx])
            if num_options > 1:
                if num_options < minOptions:
                    minOptions = num_options
                    bestIdx = idx

            if minOptions == 2:
                break

        return bestIdx

    def reduce_domains(self, idx, val, domains):
        newDomains = [list(d) for d in domains]
        newDomains[idx] = [val]

        row, col = idx // self.cols, idx % self.cols

        for i in range(self.cols):
            r_idx = row * self.cols + i
            if r_idx != idx and val in newDomains[r_idx]:
                newDomains[r_idx].remove(val)
                if not newDomains[r_idx]:
                    return None

            c_idx = i * self.cols + col
            if c_idx != idx and val in newDomains[c_idx]:
                newDomains[c_idx].remove(val)
                if not newDomains[c_idx]:
                    return None

        for check in self.constraits[idx]:
            nIdx = check["neighbor"]
            nDom = newDomains[nIdx]

            if check["type"] == "<":
                newDomains[nIdx] = [v for v in nDom if v > val]
            elif check["type"] == ">":
                newDomains[nIdx] = [v for v in nDom if v < val]

            if not newDomains[nIdx]:
                return None

        return newDomains

    def ForwardCheckingSolver(self):
        starttime = time.perf_counter()
        initialDomains = []
        empty = []

        for i in range(self.total_cells):
            txt = self.gridItems[i].text()
            if txt != "" and self.gridItems[i].isConstance:
                initialDomains.append([int(txt)])
            else:
                initialDomains.append(list(range(1, self.cols + 1))) # Dynamic domain
                empty.append(i)

        def solve(currentDomains):
            idx = self.get_best_empty_cell(currentDomains, empty)

            if idx is None:
                return currentDomains

            for val in list(currentDomains[idx]):

                new_domains = self.reduce_domains(idx, val, currentDomains)

                if new_domains is not None:
                    result = solve(new_domains)
                    if result is not None:
                        return result
            return None

        final_result = solve(initialDomains)

        if final_result:
            endtime = time.perf_counter()
            executiontime = endtime - starttime

            solved_data = [d[0] for d in final_result]
            self.DisplayResultSlowly(solved_data, empty)

            print(f"Đã giải xong bằng Forward Checking trong {executiontime:.4f} s!")




    def AStarSolver(self):
        starttime = time.perf_counter()
        
        initialData = []
        emptyIndices = []
        for i in range(self.total_cells):
            txt = self.gridItems[i].text()
            if txt != "" and self.gridItems[i].isConstance:
                initialData.append(int(txt))
            else:
                initialData.append(0)
                emptyIndices.append(i)

        queue = []
        
        heapq.heappush(queue, (len(emptyIndices), initialData))

        final_data = None
        while queue:
            rem_count, current_data = heapq.heappop(queue)

            if rem_count == 0:
                final_data = current_data
                break

            best_idx = -1
            minOptions = 7
            best_options = []

            for i in emptyIndices:
                if current_data[i] == 0:
                    options = []
                    for v in range(1, self.cols + 1): # Thử từ 1 đến N
                        if self.IsLegal(i, v, current_data):
                            options.append(v)
                    
                    if len(options) < minOptions:
                        minOptions = len(options)
                        best_idx = i
                        best_options = options
                    
                    if minOptions == 0: break
            
            if minOptions == 0 or best_idx == -1:
                continue

            for val in best_options:
                new_data = list(current_data)
                new_data[best_idx] = val
                heapq.heappush(queue, (rem_count - 1, new_data))

        if final_data:
            endtime = time.perf_counter()
            executiontime = (endtime - starttime)
            self.DisplayResultSlowly(final_data, emptyIndices)
            print(f"Da giai xong bang A* trong {executiontime:.4f} s!")
        else:
            print("Khong co loi giai")


    def BackwardSolver(self):
        starttime = time.perf_counter()
        data = [0] * self.total_cells
        empty = []
        
        for i in range(self.total_cells):
            txt = self.gridItems[i].text()
            if txt != "" and self.gridItems[i].isConstance:
                data[i] = int(txt)
            else:
                empty.append(i)

        def solve(step):
            if step == len(empty):
                return True
            
            idx = empty[step]
            
            valid_numbers = []
            for num in range(1, self.cols + 1): # Thử từ 1 đến N
                if self.IsLegal(idx, num, data):
                    valid_numbers.append(num)
            
            for num in valid_numbers:
                data[idx] = num
                if solve(step + 1):
                    return True
                data[idx] = 0
                
            return False

        if solve(0):
            endtime = time.perf_counter()
            executiontime = (endtime - starttime)
            self.DisplayResultSlowly(data, empty)
            print(f"Da giai xong bang Backward trong {executiontime:.4f} s!")
        else:
            print("Khong co loi giai")


    def CheckWin(self):
        if self.isWin: return
        data = []
        for i in range(self.total_cells):
            txt = self.gridItems[i].text()
            if txt == "":
                self.Animation("Fill All Node!", "Continue Or Play New Game!", "#D90368")
                return
            data.append(int(txt))

        for i in range(self.rows):
            rowValues = set()
            colValues = set()
            for j in range(self.cols):
                val_row = data[i * self.cols + j]
                if val_row in rowValues: return False
                rowValues.add(val_row)

                
                val_col = data[j * self.cols + i]
                if val_col in colValues: return False
                colValues.add(val_col)


        for idx in range(self.total_cells):
            value = data[idx]
            for check in self.constraits[idx]:
                neighborIdx = check["neighbor"]
                neighborValue = data[neighborIdx]

                if check["type"] == ">" and not (value > neighborValue):
                    self.Animation("Logic Error!", "Constraint violated!", "#D90368")
                    return
                if check["type"] == "<" and not (value < neighborValue):
                    self.Animation("Logic Error!", "Constraint violated!", "#D90368")
                    return

        self.isWin = True   
        self.Animation("You Win!", "Congratulations!", "#08B2E3")

    def Animation(self, label_text, label1_text, bgcolor):

        label = QLabel(self._parent)
        label.setText(label_text)
        label.setFixedSize(600, 100)
        label.move(-1000, 100)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"color: white; background-color: {bgcolor}; font-size: 36px; border-radius: 4px; border: 1px solid black"
        )

        label1 = QLabel(self._parent)
        label1.setText(label1_text)
        label1.move(-1000, 100)
        label1.setFixedSize(600, 80)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label1.setStyleSheet(
            f"color: white; background-color: {bgcolor}; font-size: 36px; border-radius: 4px; border: 1px solid black"
        )

        label.hide()
        label1.hide()

        self.groupanim = QSequentialAnimationGroup()

        anim1_in = QPropertyAnimation(label, b"geometry")
        anim1_in.setDuration(600)

        anim1_in.setStartValue(QRect(-600, 400, 600, 100))
        anim1_in.setEndValue(QRect(600, 400, 600, 100))
        anim1_in.setEasingCurve(QEasingCurve.Type.OutBack)

        label.show()
        self.groupanim.addAnimation(anim1_in)

        self.groupanim.addPause(2000)

        anim1_out = QPropertyAnimation(label, b"geometry")
        anim1_out.setDuration(400)
        anim1_out.setStartValue(QRect(600, 400, 600, 100))
        anim1_out.setEndValue(QRect(2000, 400, 600, 100))
        anim1_out.setEasingCurve(QEasingCurve.Type.InQuart)
        self.groupanim.addAnimation(anim1_out)

        anim2_in = QPropertyAnimation(label1, b"geometry")
        anim2_in.setDuration(500)
        anim2_in.setStartValue(QRect(600, 1200, 600, 80))
        anim2_in.setEndValue(QRect(600, 400, 600, 80))
        anim2_in.setEasingCurve(QEasingCurve.Type.OutBack)

        label1.show()
        self.groupanim.addAnimation(anim2_in)

        self.groupanim.addPause(1000)

        anim2_out = QPropertyAnimation(label1, b"geometry")
        anim2_out.setDuration(400)
        anim2_out.setStartValue(QRect(600, 400, 600, 100))
        anim2_out.setEndValue(QRect(600, -500, 600, 100))
        anim2_out.setEasingCurve(QEasingCurve.Type.InQuart)
        self.groupanim.addAnimation(anim2_out)

        self.groupanim.finished.connect(label.deleteLater)
        self.groupanim.finished.connect(label1.deleteLater)

        self.groupanim.start()



    def fill_next_box(self):
        if not self.temp_empty:
            self.display_timer.stop()
            return

        idx = self.temp_empty.pop(0)
        block = self.gridItems[idx]

        val = self.temp_data[idx]
        block.setText(str(val))

        block.setStyleSheet(
            block.styleSheet().replace(f"color: {block.text_color};", "color: #0056b3;")
        )

        anim = QPropertyAnimation(block, b"geometry")
        anim.setDuration(300)
        current = block.geometry()
        
        center = current.center()
        anim.setStartValue(QRect(center.x(), center.y(), 0, 0))
        anim.setEndValue(current)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        if not hasattr(self, 'anim_list'): self.anim_list = []
        self.anim_list.append(anim)
        anim.start()


    def DisplayResultSlowly(self, final_data, empty_indices):
        self.temp_empty = empty_indices.copy()
        self.temp_data = final_data
        

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.fill_next_box)
        self.display_timer.start(100)
