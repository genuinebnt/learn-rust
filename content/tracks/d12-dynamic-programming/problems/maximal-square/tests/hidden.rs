use solution::*;

#[test]
fn empty() {
    check!(r#"matrix = []"#, maximal_square(&[]), 0);
}

#[test]
fn single_one() {
    check!(r#"matrix = ["1"]"#, maximal_square(&["1"]), 1);
}

#[test]
fn row_of_zeros() {
    check!(r#"matrix = ["0000"]"#, maximal_square(&["0000"]), 0);
}

#[test]
fn rectangle() {
    check!(r#"matrix = ["1111", "1111"]"#, maximal_square(&["1111", "1111"]), 4);
}

#[test]
fn hole_in_the_middle() {
    check!(r#"matrix = ["111", "101", "111"]"#, maximal_square(&["111", "101", "111"]), 1);
}

#[test]
fn rounded_corners() {
    check!(r#"matrix = ["0110", "1111", "1111", "0110"]"#, maximal_square(&["0110", "1111", "1111", "0110"]), 4);
}

#[test]
fn square_at_the_edge() {
    check!(r#"matrix = ["1110", "1110", "1101"]"#, maximal_square(&["1110", "1110", "1101"]), 4);
}

#[test]
fn bottom_right() {
    check!(r#"matrix = ["11110", "11110", "11011", "11111"]"#, maximal_square(&["11110", "11110", "11011", "11111"]), 4);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1222);
    for _ in 0..300 {
        let m = rng.int(0, 6) as usize;
        let n = rng.int(1, 6) as usize;
        let rows: Vec<String> = (0..m).map(|_| rng.string(n, "1110")).collect();
        let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
        let g: Vec<&[u8]> = rows.iter().map(|r| r.as_bytes()).collect();
        let mut want = 0;
        for i in 0..m {
            for j in 0..n {
                for k in 1..=(m - i).min(n - j) {
                    if (i..i + k).all(|r| (j..j + k).all(|c| g[r][c] == b'1')) {
                        want = want.max(k * k);
                    }
                }
            }
        }
        check!(format!("matrix = {rows:?}"), maximal_square(&refs), want);
    }
}

#[test]
fn scale_all_ones() {
    let rows = vec!["1".repeat(1000); 1000];
    let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
    check!("matrix = 1000 × 1000 of '1'", maximal_square(&refs), 1_000_000);
}

#[test]
fn scale_scattered_zeros() {
    let rows: Vec<String> = (0..1000usize).map(|i| (0..1000usize).map(|j| if (i * i + j * 7) % 97 == 0 { '0' } else { '1' }).collect()).collect();
    let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
    check!("matrix = 1000 × 1000, '0' where (i² + 7j) % 97 == 0", maximal_square(&refs), 576);
}
