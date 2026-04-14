# algorithm forward_chaining

Giải thích thuật toán Forward Chaining đã implement
Kiến trúc tổng thể
File gồm class ForwardChainingSolver với 3 tầng hoạt động:

## Tầng 1 — Khởi tạo

\_initialize_domains(): mỗi ô có domain {1..N}, ô đã cho sẵn thì domain = {v} (tương ứng A5).
\_build_arc_map(): từ các inequality constraint, xây dựng map arc 2 chiều giữa các ô có bất phương trình.

## Tầng 2 — Forward Chaining + AC-3 (phần cốt lõi)

\_forward_chain(domains): vòng lặp lặp đi lặp lại cho đến khi không còn gì thay đổi:

Row/Col propagation (A3a, A3b): nếu ô (r,c) đã xác định = v, loại v khỏi tất cả ô cùng hàng và cột.
\_ac3_propagate() (A4): với mỗi arc (cell1 < cell2), loại khỏi domain[cell1] mọi giá trị v1 mà không tồn tại v2 > v1 trong domain[cell2] — đây chính là Modus Ponens từ FOL.
Nếu domain của bất kỳ ô nào rỗng → trả về False (contradiction).

## Tầng 3 — Backtracking khi FC không đủ

\_solve_recursive(): khi FC không đủ để xác định hết tất cả ô, chọn ô có domain nhỏ nhất (MRV heuristic), thử từng giá trị, clone domains, gán, rồi chạy lại FC — nếu thất bại thì backtrack. Điều này khác Backtracking thuần túy ở chỗ mỗi lần gán đều có FC lookahead ngay lập tức.

Kết quả test
File Thời gian Nodes backtrack Inferences (FC)
input-01.txt (4×4) 0.0035s 0 (FC đủ!) 18
input-02.txt (4×4) 0.0003s 6 99
