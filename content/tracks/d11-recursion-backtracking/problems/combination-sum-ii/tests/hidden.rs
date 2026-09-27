use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn single_exact() {
    check!(r#"candidates = [7], target = 7"#, combination_sum2(&[7], 7), vec![vec![7]]);
}

#[test]
fn uses_two_copies() {
    check!(r#"candidates = [4, 1, 1, 4, 4], target = 9"#, norm(combination_sum2(&[4, 1, 1, 4, 4], 9)), vec![vec![1, 4, 4]]);
}

#[test]
fn pair_of_ones() {
    check!(r#"candidates = [1, 1], target = 2"#, combination_sum2(&[1, 1], 2), vec![vec![1, 1]]);
}

#[test]
fn all_too_big() {
    check!(r#"candidates = [40, 50], target = 30"#, combination_sum2(&[40, 50], 30), Vec::<Vec<u32>>::new());
}

#[test]
fn whole_slice() {
    check!(r#"candidates = [1, 2, 3], target = 6"#, norm(combination_sum2(&[1, 2, 3], 6)), vec![vec![1, 2, 3]]);
}

#[test]
fn two_ways() {
    check!(r#"candidates = [5, 1, 4, 2, 3], target = 5"#, norm(combination_sum2(&[5, 1, 4, 2, 3], 5)), vec![vec![1, 4], vec![2, 3], vec![5]]);
}

#[test]
fn big_values() {
    check!(r#"candidates = [50, 30, 30], target = 30"#, combination_sum2(&[50, 30, 30], 30), vec![vec![30]]);
}

#[test]
fn thirty_from_one_to_thirty() {
    check!(r#"candidates = 1..=30, target = 30"#, combination_sum2(&(1..=30).collect::<Vec<u32>>(), 30).len(), 296);
}

#[test]
fn random_vs_bitmasks_and_a_set() {
    let mut rng = anneal_prelude::Rng::new(1125);
    for _ in 0..300 {
        let n = rng.int(1, 12) as usize;
        let c: Vec<u32> = rng.vec(n, 1, 8);
        let target = rng.int(1, 20) as u32;
        let mut all = std::collections::BTreeSet::new();
        for mask in 0..1u32 << n {
            let mut s: Vec<u32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| c[i]).collect();
            if s.iter().sum::<u32>() == target {
                s.sort();
                all.insert(s);
            }
        }
        check!(format!("candidates = {c:?}, target = {target}"), norm(combination_sum2(&c, target)), all.into_iter().collect::<Vec<_>>());
    }
}

#[test]
fn scale_a_hundred_ones() {
    check!("candidates = [1; 100], target = 30", combination_sum2(&vec![1; 100], 30), vec![vec![1; 30]]);
}

#[test]
fn scale_a_hundred_mixed() {
    let c: Vec<u32> = (0..100).map(|i| i % 5 + 1).collect();
    check!("candidates = [1, 2, 3, 4, 5] × 20, target = 30", combination_sum2(&c, 30).len(), 651);
}
