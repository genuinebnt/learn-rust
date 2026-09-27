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

fn brute(n: usize) -> Vec<Vec<usize>> {
    fn go(n: usize, cols: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if cols.len() == n {
            if (0..n).all(|i| (i + 1..n).all(|j| cols[i].abs_diff(cols[j]) != j - i)) {
                out.push(cols.clone());
            }
            return;
        }
        for c in 0..n {
            if !cols.contains(&c) {
                cols.push(c);
                go(n, cols, out);
                cols.pop();
            }
        }
    }
    let mut out = Vec::new();
    go(n, &mut Vec::new(), &mut out);
    out
}

#[test]
fn one() {
    check!(r#"n = 1"#, solve_n_queens(1), vec![vec!["Q"]]);
}

#[test]
fn two() {
    check!(r#"n = 2"#, solve_n_queens(2).len(), 0);
}

#[test]
fn three() {
    check!(r#"n = 3"#, solve_n_queens(3).len(), 0);
}

#[test]
fn four_rows_are_n_long() {
    check!(r#"n = 4: every row has 4 cells"#, solve_n_queens(4).iter().flatten().all(|row| row.len() == 4), true);
}

#[test]
fn seven() {
    check!(r#"n = 7: (boards, all valid)"#, { let all = solve_n_queens(7); (all.len(), all.iter().all(|b| valid(7, b))) }, (40, true));
}

#[test]
fn eight_distinct() {
    check!(r#"n = 8: (distinct boards, all valid)"#, { let mut all = solve_n_queens(8); let ok = all.iter().all(|b| valid(8, b)); all.sort(); all.dedup(); (all.len(), ok) }, (92, true));
}

#[test]
fn nine() {
    check!(r#"n = 9"#, solve_n_queens(9).len(), 352);
}

#[test]
fn ten() {
    check!(r#"n = 10: (boards, all valid)"#, { let all = solve_n_queens(10); (all.len(), all.iter().all(|b| valid(10, b))) }, (724, true));
}

#[test]
fn eleven() {
    check!(r#"n = 11"#, solve_n_queens(11).len(), 2680);
}

#[test]
fn every_n_up_to_8_vs_permutations() {
    for n in 1..=8 {
        let want: Vec<Vec<String>> = brute(n)
            .into_iter()
            .map(|cols| cols.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect())
            .collect();
        check!(format!("n = {n}"), sorted(solve_n_queens(n)), sorted(want));
    }
}

#[test]
fn scale_twelve() {
    let mut all = solve_n_queens(12);
    let ok = all.iter().all(|b| valid(12, b));
    all.sort();
    all.dedup();
    check!("n = 12: (distinct boards, all valid)", (all.len(), ok), (14200, true));
}
