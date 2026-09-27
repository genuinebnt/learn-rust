use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

fn valid(n: usize, board: &[String]) -> bool {
    if board.len() != n {
        return false;
    }
    let mut queens = Vec::new(); // (row, column)
    for (r, row) in board.iter().enumerate() {
        if row.len() != n || row.bytes().any(|b| b != b'.' && b != b'Q') || row.matches('Q').count() != 1 {
            return false;
        }
        queens.push((r, row.find('Q').unwrap()));
    }
    queens.iter().enumerate().all(|(i, &(r1, c1))| queens[i + 1..].iter().all(|&(r2, c2)| c1 != c2 && r2 - r1 != c1.abs_diff(c2)))
}

#[test]
fn leetcode_four() {
    check!(r#"n = 4"#, sorted(solve_n_queens(4)), vec![vec!["..Q.", "Q...", "...Q", ".Q.."], vec![".Q..", "...Q", "Q...", "..Q."]]);
}

#[test]
fn leetcode_one() {
    check!(r#"n = 1"#, solve_n_queens(1), vec![vec!["Q"]]);
}

#[test]
fn two_has_none() {
    check!(r#"n = 2"#, solve_n_queens(2), Vec::<Vec<String>>::new());
}

#[test]
fn three_has_none() {
    check!(r#"n = 3"#, solve_n_queens(3), Vec::<Vec<String>>::new());
}

#[test]
fn five_has_ten() {
    check!(r#"n = 5: (boards, all valid)"#, { let all = solve_n_queens(5); (all.len(), all.iter().all(|b| valid(5, b))) }, (10, true));
}

#[test]
fn six_exactly() {
    check!(r#"n = 6"#, sorted(solve_n_queens(6)), vec![vec!["....Q.", "..Q...", "Q.....", ".....Q", "...Q..", ".Q...."], vec!["...Q..", "Q.....", "....Q.", ".Q....", ".....Q", "..Q..."], vec!["..Q...", ".....Q", ".Q....", "....Q.", "Q.....", "...Q.."], vec![".Q....", "...Q..", ".....Q", "Q.....", "..Q...", "....Q."]]);
}
