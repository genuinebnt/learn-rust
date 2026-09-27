use solution::*;

#[test]
fn chain() {
    check!(r#"0-1, 1-2, 2-3"#, count_provinces(&[vec![1, 1, 0, 0], vec![1, 1, 1, 0], vec![0, 1, 1, 1], vec![0, 0, 1, 1]]), 1);
}

#[test]
fn pairs() {
    check!(r#"0-3 and 1-2"#, count_provinces(&[vec![1, 0, 0, 1], vec![0, 1, 1, 0], vec![0, 1, 1, 0], vec![1, 0, 0, 1]]), 2);
}

#[test]
fn last_city_alone() {
    check!(r#"0-1-2 linked, 3 alone"#, count_provinces(&[vec![1, 1, 1, 0], vec![1, 1, 1, 0], vec![1, 1, 1, 0], vec![0, 0, 0, 1]]), 2);
}

#[test]
fn hub_city() {
    check!(r#"city 0 linked to all others, which aren't linked to each other"#, count_provinces(&[vec![1, 1, 1, 1], vec![1, 1, 0, 0], vec![1, 0, 1, 0], vec![1, 0, 0, 1]]), 1);
}

#[test]
fn identity_2000() {
    let m: Vec<Vec<u8>> = (0..2000).map(|i| (0..2000).map(|j| u8::from(i == j)).collect()).collect();
    check!(r#"2000 cities, no links"#, count_provinces(&m), 2000);
}

#[test]
fn long_chain_2000() {
    let m: Vec<Vec<u8>> = (0..2000usize).map(|i| (0..2000usize).map(|j| u8::from(i.abs_diff(j) <= 1)).collect()).collect();
    check!(r#"2000 cities, i linked to i + 1"#, count_provinces(&m), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(939);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let mut m = vec![vec![0u8; n]; n];
        for i in 0..n {
            m[i][i] = 1;
            for j in i + 1..n {
                if rng.below(4) == 0 {
                    m[i][j] = 1;
                    m[j][i] = 1;
                }
            }
        }
        // Brute force: label propagation over the matrix.
        let mut label: Vec<usize> = (0..n).collect();
        let mut changed = true;
        while changed {
            changed = false;
            for i in 0..n {
                for j in 0..n {
                    if m[i][j] == 1 && label[j] < label[i] {
                        label[i] = label[j];
                        changed = true;
                    }
                }
            }
        }
        let want = (0..n).filter(|&i| label[i] == i).count();
        check!(format!("connected = {m:?}"), count_provinces(&m), want);
    }
}

#[test]
fn scale_two_interleaved_provinces() {
    // Even cities form one chain and odd cities another: i links to i + 2.
    let n = 2000;
    let m: Vec<Vec<u8>> = (0..n).map(|i: usize| (0..n).map(|j: usize| u8::from(i == j || i.abs_diff(j) == 2)).collect()).collect();
    check!("2000 cities, i linked to i + 2", count_provinces(&m), 2);
}
