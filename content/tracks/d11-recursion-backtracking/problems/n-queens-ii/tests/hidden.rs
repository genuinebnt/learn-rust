use solution::*;

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
    check!(r#"n = 1"#, total_n_queens(1), 1);
}

#[test]
fn six() {
    check!(r#"n = 6"#, total_n_queens(6), 4);
}

#[test]
fn seven() {
    check!(r#"n = 7"#, total_n_queens(7), 40);
}

#[test]
fn nine() {
    check!(r#"n = 9"#, total_n_queens(9), 352);
}

#[test]
fn ten() {
    check!(r#"n = 10"#, total_n_queens(10), 724);
}

#[test]
fn eleven() {
    check!(r#"n = 11"#, total_n_queens(11), 2680);
}

#[test]
fn twelve() {
    check!(r#"n = 12"#, total_n_queens(12), 14200);
}

#[test]
fn thirteen() {
    check!(r#"n = 13"#, total_n_queens(13), 73712);
}

#[test]
fn every_n_up_to_8_vs_permutations() {
    for n in 1..=8 {
        check!(format!("n = {n}"), total_n_queens(n), brute(n).len());
    }
}

#[test]
fn scale_fourteen() {
    check!("n = 14", total_n_queens(14), 365_596);
}
