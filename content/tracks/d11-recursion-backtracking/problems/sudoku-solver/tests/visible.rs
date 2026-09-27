use solution::*;

/// Nine rows of nine cells separated by spaces; `.` is an empty cell.
fn grid(s: &str) -> [[u8; 9]; 9] {
    let cells: Vec<u8> = s.bytes().filter(|&b| b != b' ').map(|b| if b == b'.' { 0 } else { b - b'0' }).collect();
    assert_eq!(cells.len(), 81, "a board has 81 cells");
    let mut board = [[0; 9]; 9];
    for (i, d) in cells.into_iter().enumerate() {
        board[i / 9][i % 9] = d;
    }
    board
}

fn show(board: &[[u8; 9]; 9]) -> String {
    let rows: Vec<String> = board.iter().map(|row| row.iter().map(|&d| if d == 0 { '.' } else { (b'0' + d) as char }).collect()).collect();
    rows.join(" ")
}

/// Solves the puzzle: (the returned flag, the board afterwards).
fn run(puzzle: &str) -> (bool, String) {
    let mut board = grid(puzzle);
    let ok = solve_sudoku(&mut board);
    (ok, show(&board))
}

/// `board` is full, every row, column and box holds 1–9 once, and the givens of `puzzle` are still there.
fn completes(puzzle: &[[u8; 9]; 9], board: &[[u8; 9]; 9]) -> bool {
    let mut seen = [[0u16; 9]; 3];
    for r in 0..9 {
        for c in 0..9 {
            let d = board[r][c];
            if !(1..=9).contains(&d) || (puzzle[r][c] != 0 && puzzle[r][c] != d) {
                return false;
            }
            for (unit, i) in [(0, r), (1, c), (2, r / 3 * 3 + c / 3)] {
                if seen[unit][i] >> d & 1 == 1 {
                    return false;
                }
                seen[unit][i] |= 1 << d;
            }
        }
    }
    true
}

#[test]
fn leetcode_example() {
    check!(r#"board = 53..7.... 6..195... .98....6. 8...6...3 4..8.3..1 7...2...6 .6....28. ...419..5 ....8..79"#, run("53..7.... 6..195... .98....6. 8...6...3 4..8.3..1 7...2...6 .6....28. ...419..5 ....8..79"), (true, "534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179".to_string()));
}

#[test]
fn already_solved() {
    check!(r#"board = 534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179 (nothing to fill)"#, run("534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179"), (true, "534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179".to_string()));
}

#[test]
fn one_blank() {
    check!(r#"board = 534678912 672195348 198342567 859761423 4268.3791 713924856 961537284 287419635 345286179 (one empty cell)"#, run("534678912 672195348 198342567 859761423 4268.3791 713924856 961537284 287419635 345286179"), (true, "534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179".to_string()));
}

#[test]
fn givens_clash() {
    check!(r#"board = 5...5.... ......... ......... ......... ......... ......... ......... ......... ......... (two 5s in the first row)"#, run("5...5.... ......... ......... ......... ......... ......... ......... ......... ........."), (false, "5...5.... ......... ......... ......... ......... ......... ......... ......... .........".to_string()));
}

#[test]
fn no_digit_fits() {
    check!(r#"board = 12345678. ........9 ......... ......... ......... ......... ......... ......... ......... (the first row's last cell needs a 9, and its column has one)"#, run("12345678. ........9 ......... ......... ......... ......... ......... ......... ........."), (false, "12345678. ........9 ......... ......... ......... ......... ......... ......... .........".to_string()));
}

#[test]
fn empty_board() {
    check!(r#"board = all 0: (returned flag, board is a valid fill)"#, { let mut board = [[0; 9]; 9]; let ok = solve_sudoku(&mut board); (ok, completes(&[[0; 9]; 9], &board)) }, (true, true));
}
