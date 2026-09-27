use solution::*;

#[test]
fn empty() {
    check!(r#"envelopes = []"#, max_envelopes(&[]), 0);
}

#[test]
fn chain() {
    check!(r#"envelopes = [(1, 2), (2, 3), (3, 4)]"#, max_envelopes(&[(1, 2), (2, 3), (3, 4)]), 3);
}

#[test]
fn shuffled_chain() {
    check!(r#"envelopes = [(3, 4), (1, 2), (2, 3)]"#, max_envelopes(&[(3, 4), (1, 2), (2, 3)]), 3);
}

#[test]
fn tie_on_width() {
    check!(r#"envelopes = [(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)]"#, max_envelopes(&[(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)]), 4);
}

#[test]
fn mixed() {
    check!(r#"envelopes = [(1, 3), (3, 5), (6, 7), (6, 8), (8, 4), (9, 5)]"#, max_envelopes(&[(1, 3), (3, 5), (6, 7), (6, 8), (8, 4), (9, 5)]), 3);
}

#[test]
fn many_ties() {
    check!(r#"envelopes = [(2, 100), (3, 200), (4, 300), (5, 500), (5, 400), (5, 250), (6, 370), (6, 360), (7, 380)]"#, max_envelopes(&[(2, 100), (3, 200), (4, 300), (5, 500), (5, 400), (5, 250), (6, 370), (6, 360), (7, 380)]), 5);
}

#[test]
fn equal_heights() {
    check!(r#"envelopes = [(1, 5), (2, 5), (3, 5)]"#, max_envelopes(&[(1, 5), (2, 5), (3, 5)]), 1);
}

#[test]
fn largest_values() {
    check!(r#"envelopes = [(100000, 100000), (1, 1)]"#, max_envelopes(&[(100_000, 100_000), (1, 1)]), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1217);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut env: Vec<(u32, u32)> = Vec::new();
        for _ in 0..n {
            let w = rng.int(1, 5) as u32;
            let h = rng.int(1, 5) as u32;
            env.push((w, h));
        }
        // Chain DP after a plain sort: fits[j] < fits[i] needs both sides smaller.
        let mut sorted = env.clone();
        sorted.sort_unstable();
        let mut best = vec![1usize; n];
        for i in 0..n {
            for j in 0..i {
                if sorted[j].0 < sorted[i].0 && sorted[j].1 < sorted[i].1 {
                    best[i] = best[i].max(best[j] + 1);
                }
            }
        }
        let want = best.into_iter().max().unwrap_or(0);
        check!(format!("envelopes = {env:?}"), max_envelopes(&env), want);
    }
}

#[test]
fn scale_100k() {
    let env: Vec<(u32, u32)> = (0..100_000u64).map(|i| ((i * 7919 % 100_003 + 1) as u32, (i * 104_729 % 99_991 + 1) as u32)).collect();
    check!("envelopes[i] = ((7919·i) % 100003 + 1, (104729·i) % 99991 + 1), 100000 envelopes", max_envelopes(&env), 544);
}

#[test]
fn scale_width_pairs() {
    let env: Vec<(u32, u32)> = (0..100_000u32).map(|i| (1 + i / 2, 1 + i / 2)).collect();
    check!("envelopes = [(1, 1), (1, 1), (2, 2), (2, 2), …] (100000 envelopes)", max_envelopes(&env), 50_000);
}
