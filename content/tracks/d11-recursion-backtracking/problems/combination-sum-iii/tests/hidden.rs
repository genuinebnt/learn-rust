use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn all_nine() {
    check!(r#"k = 9, n = 45"#, combination_sum3(9, 45), vec![vec![1, 2, 3, 4, 5, 6, 7, 8, 9]]);
}

#[test]
fn all_nine_wrong_sum() {
    check!(r#"k = 9, n = 44"#, combination_sum3(9, 44), Vec::<Vec<u32>>::new());
}

#[test]
fn two_largest() {
    check!(r#"k = 2, n = 17"#, combination_sum3(2, 17), vec![vec![8, 9]]);
}

#[test]
fn too_big() {
    check!(r#"k = 2, n = 18"#, combination_sum3(2, 18), Vec::<Vec<u32>>::new());
}

#[test]
fn no_repeats() {
    check!(r#"k = 2, n = 2"#, combination_sum3(2, 2), Vec::<Vec<u32>>::new());
}

#[test]
fn four_twenty() {
    check!(r#"k = 4, n = 20"#, combination_sum3(4, 20).len(), 12);
}

#[test]
fn sixty() {
    check!(r#"k = 9, n = 60"#, combination_sum3(9, 60), Vec::<Vec<u32>>::new());
}

#[test]
fn zero_not_a_digit() {
    check!(r#"k = 2, n = 9"#, norm(combination_sum3(2, 9)), vec![vec![1, 8], vec![2, 7], vec![3, 6], vec![4, 5]]);
}

#[test]
fn every_k_and_n_vs_bitmasks() {
    let mut rng = anneal_prelude::Rng::new(1126);
    let mut cases: Vec<(usize, u32)> = (1..=9).flat_map(|k| (1..=60).map(move |n| (k, n))).collect();
    rng.shuffle(&mut cases);
    for (k, n) in cases {
        let want: Vec<Vec<u32>> = (0..512u32)
            .filter(|m| m.count_ones() as usize == k && (0..9).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).sum::<u32>() == n)
            .map(|m| (0..9).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).collect())
            .collect();
        check!(format!("k = {k}, n = {n}"), norm(combination_sum3(k, n)), norm(want));
    }
}
