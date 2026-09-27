use solution::*;

#[test]
fn row_three_middle() {
    check!(r#"n = 3, k = 3"#, kth_grammar(3, 3), 1);
}

#[test]
fn last_of_row_four() {
    check!(r#"n = 4, k = 8"#, kth_grammar(4, 8), 1);
}

#[test]
fn last_of_row_five() {
    check!(r#"n = 5, k = 16"#, kth_grammar(5, 16), 0);
}

#[test]
fn row_ten() {
    check!(r#"n = 10, k = 500"#, kth_grammar(10, 500), 1);
}

#[test]
fn row_thirty_first() {
    check!(r#"n = 30, k = 1"#, kth_grammar(30, 1), 0);
}

#[test]
fn row_thirty_last() {
    check!(r#"n = 30, k = 2^29"#, kth_grammar(30, 1 << 29), 1);
}

#[test]
fn row_64_first() {
    check!(r#"n = 64, k = 1"#, kth_grammar(64, 1), 0);
}

#[test]
fn row_64_last() {
    check!(r#"n = 64, k = 2^63"#, kth_grammar(64, 1 << 63), 1);
}

#[test]
fn row_64_middle() {
    check!(r#"n = 64, k = 2^62"#, kth_grammar(64, 1 << 62), 0);
}

#[test]
fn row_64_just_past_middle() {
    check!(r#"n = 64, k = 2^62 + 1"#, kth_grammar(64, (1 << 62) + 1), 1);
}

#[test]
fn row_64_large_k() {
    check!(r#"n = 64, k = 12345678901234567"#, kth_grammar(64, 12_345_678_901_234_567), 1);
}

#[test]
fn random_vs_built_rows() {
    let mut rows: Vec<Vec<u8>> = vec![vec![0]];
    for _ in 1..12 {
        let next = rows.last().unwrap().iter().flat_map(|&s| if s == 0 { [0, 1] } else { [1, 0] }).collect();
        rows.push(next);
    }
    let mut rng = anneal_prelude::Rng::new(1102);
    for _ in 0..400 {
        let n = rng.int(1, 12) as u32;
        let k = rng.int(1, 1 << (n - 1)) as u64;
        check!(format!("n = {n}, k = {k}"), kth_grammar(n, k), rows[n as usize - 1][k as usize - 1]);
    }
}

#[test]
fn scale_100k_queries_on_row_64() {
    let mut rng = anneal_prelude::Rng::new(1103);
    for _ in 0..100_000 {
        let k = rng.next_u64() % (1 << 63) + 1;
        let want = ((k - 1).count_ones() % 2) as u8;
        let got = kth_grammar(64, k);
        if got != want {
            check!(format!("n = 64, k = {k}"), got, want);
        }
    }
}
