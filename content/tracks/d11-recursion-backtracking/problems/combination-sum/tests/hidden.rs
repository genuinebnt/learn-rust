use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn unsorted_candidates() {
    check!(r#"candidates = [8, 2, 3], target = 7"#, norm(combination_sum(&[8, 2, 3], 7)), vec![vec![2, 2, 3]]);
}

#[test]
fn all_too_big() {
    check!(r#"candidates = [5, 9], target = 4"#, combination_sum(&[5, 9], 4), Vec::<Vec<u32>>::new());
}

#[test]
fn no_mix_reaches() {
    check!(r#"candidates = [3, 5], target = 4"#, combination_sum(&[3, 5], 4), Vec::<Vec<u32>>::new());
}

#[test]
fn ones() {
    check!(r#"candidates = [1], target = 5"#, combination_sum(&[1], 5), vec![vec![1, 1, 1, 1, 1]]);
}

#[test]
fn exact_single() {
    check!(r#"candidates = [7], target = 7"#, combination_sum(&[7], 7), vec![vec![7]]);
}

#[test]
fn target_100() {
    check!(r#"candidates = [7, 11, 13], target = 100"#, norm(combination_sum(&[7, 11, 13], 100)), vec![vec![7, 7, 7, 7, 7, 7, 7, 7, 7, 11, 13, 13], vec![7, 7, 7, 7, 7, 7, 7, 7, 11, 11, 11, 11], vec![7, 7, 7, 7, 7, 13, 13, 13, 13, 13], vec![7, 7, 7, 7, 11, 11, 11, 13, 13, 13], vec![7, 7, 7, 11, 11, 11, 11, 11, 11, 13], vec![11, 11, 13, 13, 13, 13, 13, 13]]);
}

#[test]
fn big_candidate() {
    check!(r#"candidates = [200, 100], target = 500"#, norm(combination_sum(&[200, 100], 500)), vec![vec![100, 100, 100, 100, 100], vec![100, 100, 100, 200], vec![100, 200, 200]]);
}

#[test]
fn partitions_of_thirty() {
    check!(r#"candidates = 1..=30, target = 30"#, combination_sum(&(1..=30).collect::<Vec<u32>>(), 30).len(), 5604);
}

/// Every multiset of candidates summing to each total up to `target`, built bottom-up into sets.
fn brute(c: &[u32], target: u32) -> Vec<Vec<u32>> {
    let mut ways: Vec<std::collections::BTreeSet<Vec<u32>>> = vec![Default::default(); target as usize + 1];
    ways[0].insert(Vec::new());
    for t in 1..=target as usize {
        for &x in c {
            if x as usize <= t {
                let before: Vec<Vec<u32>> = ways[t - x as usize].iter().cloned().collect();
                for mut w in before {
                    w.push(x);
                    w.sort();
                    ways[t].insert(w);
                }
            }
        }
    }
    ways[target as usize].iter().cloned().collect()
}

#[test]
fn random_vs_bottom_up_sets() {
    let mut rng = anneal_prelude::Rng::new(1124);
    for _ in 0..300 {
        let mut pool: Vec<u32> = (1..=12).collect();
        rng.shuffle(&mut pool);
        let n = rng.int(1, 5) as usize;
        pool.truncate(n);
        let target = rng.int(1, 20) as u32;
        check!(format!("candidates = {pool:?}, target = {target}"), norm(combination_sum(&pool, target)), brute(&pool, target));
    }
}
