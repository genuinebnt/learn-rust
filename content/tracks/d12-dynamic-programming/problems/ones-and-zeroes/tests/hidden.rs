use solution::*;

#[test]
fn not_enough_zeros() {
    check!(r#"strs = ["00"], m = 1, n = 5"#, find_max_form(&["00"], 1, 5), 0);
}

#[test]
fn all_fit() {
    check!(r#"strs = ["0", "0", "1", "1"], m = 2, n = 2"#, find_max_form(&["0", "0", "1", "1"], 2, 2), 4);
}

#[test]
fn ones_budget_zero() {
    check!(r#"strs = ["11", "0", "0"], m = 2, n = 0"#, find_max_form(&["11", "0", "0"], 2, 0), 2);
}

#[test]
fn shortest_first_fails() {
    check!(r#"strs = ["111", "001", "110", "0001"], m = 4, n = 3"#, find_max_form(&["111", "001", "110", "0001"], 4, 3), 2);
}

#[test]
fn shortest_first_fails_again() {
    check!(r#"strs = ["001", "110", "0000", "0000"], m = 9, n = 2"#, find_max_form(&["001", "110", "0000", "0000"], 9, 2), 3);
}

#[test]
fn duplicates() {
    check!(r#"strs = ["01"; 10], m = 4, n = 100"#, find_max_form(&["01"; 10], 4, 100), 4);
}

#[test]
fn big_budget() {
    check!(r#"strs = ["01"; 600], m = 100, n = 100"#, find_max_form(&["01"; 600], 100, 100), 100);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1234);
    for _ in 0..300 {
        let k = rng.below(10);
        let mut strs: Vec<String> = Vec::new();
        for _ in 0..k {
            let len = rng.int(1, 4) as usize;
            strs.push(rng.string(len, "01"));
        }
        let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
        let (m, n) = (rng.int(0, 6) as usize, rng.int(0, 6) as usize);
        let mut want = 0;
        for mask in 0u32..(1 << k) {
            let picked: Vec<&String> = (0..k).filter(|&i| mask >> i & 1 == 1).map(|i| &strs[i]).collect();
            let zeros: usize = picked.iter().map(|s| s.bytes().filter(|&b| b == b'0').count()).sum();
            let total: usize = picked.iter().map(|s| s.len()).sum();
            if zeros <= m && total - zeros <= n {
                want = want.max(picked.len());
            }
        }
        check!(format!("strs = {strs:?}, m = {m}, n = {n}"), find_max_form(&refs, m, n), want);
    }
}

#[test]
fn scale_600() {
    let strs: Vec<String> = (0..600usize)
        .map(|i| (0..(i * 13) % 9 + 1).map(|k| if (i * 7 + k * 3) % 5 < 2 { '0' } else { '1' }).collect())
        .collect();
    let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
    check!("600 strings of length 1–9, m = 100, n = 100", find_max_form(&refs, 100, 100), 127);
}
