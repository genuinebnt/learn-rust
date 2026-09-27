use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn choose_one() {
    check!(r#"n = 4, k = 1"#, norm(combine(4, 1)), vec![vec![1], vec![2], vec![3], vec![4]]);
}

#[test]
fn one_choose_zero() {
    check!(r#"n = 1, k = 0"#, combine(1, 0), vec![Vec::<u32>::new()]);
}

#[test]
fn five_choose_three() {
    check!(r#"n = 5, k = 3"#, combine(5, 3).len(), 10);
}

#[test]
fn ten_choose_five() {
    check!(r#"n = 10, k = 5"#, combine(10, 5).len(), 252);
}

#[test]
fn values_start_at_one() {
    check!(r#"n = 2, k = 2"#, combine(2, 2), vec![vec![1, 2]]);
}

#[test]
fn n_minus_one() {
    check!(r#"n = 5, k = 4"#, norm(combine(5, 4)), vec![vec![1, 2, 3, 4], vec![1, 2, 3, 5], vec![1, 2, 4, 5], vec![1, 3, 4, 5], vec![2, 3, 4, 5]]);
}

#[test]
fn twenty_choose_ten() {
    check!(r#"n = 20, k = 10"#, combine(20, 10).len(), 184_756);
}

#[test]
fn thirty_choose_thirty() {
    check!(r#"n = 30, k = 30"#, combine(30, 30), vec![(1..=30).collect::<Vec<u32>>()]);
}

#[test]
fn random_vs_bitmasks() {
    let mut rng = anneal_prelude::Rng::new(1112);
    for _ in 0..200 {
        let n = rng.int(1, 10) as u32;
        let k = rng.int(0, n as i64) as u32;
        let want: Vec<Vec<u32>> = (0..1u32 << n)
            .filter(|m| m.count_ones() == k)
            .map(|m| (0..n).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).collect())
            .collect();
        check!(format!("n = {n}, k = {k}"), norm(combine(n, k)), norm(want));
    }
}

#[test]
fn scale_prune_when_too_few_remain() {
    let got = norm(combine(30, 28));
    check!("n = 30, k = 28", (got.len(), got[0].clone(), got[434].clone()), (435, (1..=28).collect::<Vec<u32>>(), (3..=30).collect::<Vec<u32>>()));
    check!("n = 29, k = 27", combine(29, 27).len(), 406);
}
