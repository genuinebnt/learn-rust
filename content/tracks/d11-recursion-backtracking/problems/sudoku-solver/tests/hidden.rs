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
fn box_clash() {
    check!(r#"board = 5........ .5....... ......... ......... ......... ......... ......... ......... ......... (two 5s in the top-left box, different rows and columns)"#, run("5........ .5....... ......... ......... ......... ......... ......... ......... ........."), (false, "5........ .5....... ......... ......... ......... ......... ......... ......... .........".to_string()));
}

#[test]
fn column_clash() {
    check!(r#"board = ...7..... ......... ......... ......... ......... ...7..... ......... ......... ......... (two 7s in the fourth column)"#, run("...7..... ......... ......... ......... ......... ...7..... ......... ......... ........."), (false, "...7..... ......... ......... ......... ......... ...7..... ......... ......... .........".to_string()));
}

#[test]
fn clash_among_many_givens() {
    check!(r#"board = 534678912 672195348 198342567 859761423 4268.3791 713924856 961537284 2874196.5 345286178 (the last given repeats a digit of its row and column)"#, run("534678912 672195348 198342567 859761423 4268.3791 713924856 961537284 2874196.5 345286178"), (false, "534678912 672195348 198342567 859761423 4268.3791 713924856 961537284 2874196.5 345286178".to_string()));
}

#[test]
fn ai_escargot() {
    check!(r#"board = 1....7.9. .3..2...8 ..96..5.. ..53..9.. .1..8...2 6....4... 3......1. .4......7 ..7...3.."#, run("1....7.9. .3..2...8 ..96..5.. ..53..9.. .1..8...2 6....4... 3......1. .4......7 ..7...3.."), (true, "162857493 534129678 789643521 475312986 913586742 628794135 356478219 241935867 897261354".to_string()));
}

#[test]
fn easter_monster() {
    check!(r#"board = 1.......2 .9.4...5. ..6...7.. .5.9.3... ....7.... ...85..4. 7.....6.. .3...9.8. ..2.....1"#, run("1.......2 .9.4...5. ..6...7.. .5.9.3... ....7.... ...85..4. 7.....6.. .3...9.8. ..2.....1"), (true, "174385962 293467158 586192734 451923876 928674315 367851249 719548623 635219487 842736591".to_string()));
}

#[test]
fn last_cell_blank() {
    check!(r#"board = 534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 34528617. (only the bottom-right cell is empty)"#, run("534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 34528617."), (true, "534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179".to_string()));
}

#[test]
fn first_cell_blank() {
    check!(r#"board = .34678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179 (only the top-left cell is empty)"#, run(".34678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179"), (true, "534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179".to_string()));
}

#[test]
fn one_given_row() {
    check!(r#"board = 123456789 then eight empty rows: (returned flag, board is a valid fill)"#, { let puzzle = grid("123456789 ......... ......... ......... ......... ......... ......... ......... ........."); let mut board = puzzle; let ok = solve_sudoku(&mut board); (ok, completes(&puzzle, &board)) }, (true, true));
}

#[test]
fn empty_board() {
    check!(r#"board = all 0: (returned flag, board is a valid fill)"#, { let mut board = [[0; 9]; 9]; let ok = solve_sudoku(&mut board); (ok, completes(&[[0; 9]; 9], &board)) }, (true, true));
}

/// Reading-order backtracking that checks a digit by scanning its row, column and box.
fn brute(board: &mut [[u8; 9]; 9]) -> bool {
    fn fits(b: &[[u8; 9]; 9], r: usize, c: usize, d: u8) -> bool {
        (0..9).all(|i| b[r][i] != d && b[i][c] != d && b[r / 3 * 3 + i / 3][c / 3 * 3 + i % 3] != d)
    }
    fn go(b: &mut [[u8; 9]; 9], i: usize) -> bool {
        if i == 81 {
            return true;
        }
        let (r, c) = (i / 9, i % 9);
        if b[r][c] != 0 {
            return go(b, i + 1);
        }
        for d in 1..=9 {
            if fits(b, r, c, d) {
                b[r][c] = d;
                if go(b, i + 1) {
                    return true;
                }
            }
        }
        b[r][c] = 0;
        false
    }
    for r in 0..9 {
        for c in 0..9 {
            let d = board[r][c];
            if d != 0 {
                board[r][c] = 0;
                let alone = fits(board, r, c, d);
                board[r][c] = d;
                if !alone {
                    return false;
                }
            }
        }
    }
    go(board, 0)
}

/// A random full grid: the pattern (3·(r % 3) + r / 3 + c) % 9 with bands, rows, stacks, columns and digits shuffled.
fn random_grid(rng: &mut anneal_prelude::Rng) -> [[u8; 9]; 9] {
    fn order(rng: &mut anneal_prelude::Rng) -> Vec<usize> {
        let mut bands = vec![0, 1, 2];
        rng.shuffle(&mut bands);
        let mut out = Vec::new();
        for band in bands {
            let mut inner = vec![0, 1, 2];
            rng.shuffle(&mut inner);
            out.extend(inner.into_iter().map(|i| band * 3 + i));
        }
        out
    }
    let rows = order(rng);
    let cols = order(rng);
    let mut digits: Vec<u8> = (1..=9).collect();
    rng.shuffle(&mut digits);
    let mut board = [[0; 9]; 9];
    for r in 0..9 {
        for c in 0..9 {
            let (a, b) = (rows[r], cols[c]);
            board[r][c] = digits[(3 * (a % 3) + a / 3 + b) % 9];
        }
    }
    board
}

#[test]
fn random_vs_reading_order() {
    let mut rng = anneal_prelude::Rng::new(1133);
    for _ in 0..150 {
        let mut puzzle = random_grid(&mut rng);
        let blanks = rng.int(0, 50) as usize;
        let mut cells: Vec<usize> = (0..81).collect();
        rng.shuffle(&mut cells);
        for &i in &cells[..blanks] {
            puzzle[i / 9][i % 9] = 0;
        }
        if rng.below(3) == 0 {
            // Overwrite a given: usually a clash, sometimes a puzzle with no solution or a different one.
            let at = rng.int(blanks as i64, 80) as usize;
            let i = cells[at];
            puzzle[i / 9][i % 9] = rng.int(1, 9) as u8;
        }
        let mut reference = puzzle;
        let solvable = brute(&mut reference);
        let mut board = puzzle;
        let ok = solve_sudoku(&mut board);
        let kept = if ok { completes(&puzzle, &board) } else { board == puzzle };
        check!(format!("board = {}", show(&puzzle)), (ok, kept), (solvable, true));
    }
}

#[test]
fn scale_against_reading_order() {
    check!("board = ......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1.... ....4...9", run("......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1.... ....4...9"), (true, "987654321 246173985 351928746 128537694 634892157 795461832 519286473 472319568 863745219".to_string()));
    check!("board = ......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1.... ....4.5.9", run("......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1.... ....4.5.9"), (false, "......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1.... ....4.5.9".to_string()));
    check!("board = ......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1...4 ....4...9", run("......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1...4 ....4...9"), (false, "......... .....3.85 ..1.2.... ...5.7... ..4...1.. .9....... 5......73 ..2.1...4 ....4...9".to_string()));
}
