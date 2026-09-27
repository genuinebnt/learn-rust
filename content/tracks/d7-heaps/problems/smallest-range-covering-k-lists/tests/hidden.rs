use solution::*;

#[test]
fn full_i32_width() {
    check!(r#"lists = [[i32::MIN], [i32::MAX]]"#, smallest_range(&[vec![i32::MIN], vec![i32::MAX]]), Some((i32::MIN, i32::MAX)));
}

#[test]
fn wide_then_narrow() {
    check!(r#"lists = [[i32::MIN, 0], [1, i32::MAX]]"#, smallest_range(&[vec![i32::MIN, 0], vec![1, i32::MAX]]), Some((0, 1)));
}

#[test]
fn negatives() {
    check!(r#"lists = [[-10, -5], [-7, 3], [-6]]"#, smallest_range(&[vec![-10, -5], vec![-7, 3], vec![-6]]), Some((-7, -5)));
}

#[test]
fn duplicates_inside_a_list() {
    check!(r#"lists = [[1, 1, 1, 9], [9, 9]]"#, smallest_range(&[vec![1, 1, 1, 9], vec![9, 9]]), Some((9, 9)));
}

#[test]
fn one_long_list() {
    check!(r#"lists = [0..1000, [500]]"#, smallest_range(&[(0..1000).collect(), vec![500]]), Some((500, 500)));
}

#[test]
fn disjoint_blocks() {
    check!(r#"lists = [[1, 2, 3], [10, 11], [20]]"#, smallest_range(&[vec![1, 2, 3], vec![10, 11], vec![20]]), Some((3, 20)));
}

#[test]
fn answer_at_the_end() {
    check!(r#"lists = [[1, 100], [50, 101], [80, 102]]"#, smallest_range(&[vec![1, 100], vec![50, 101], vec![80, 102]]), Some((100, 102)));
}

#[test]
fn empty_list_last() {
    check!(r#"lists = [[1], [2], []]"#, smallest_range(&[vec![1], vec![2], vec![]]), None);
}

#[test]
fn many_equal_widths() {
    check!(r#"lists = [[0, 5, 10], [2, 7, 12]]"#, smallest_range(&[vec![0, 5, 10], vec![2, 7, 12]]), Some((0, 2)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(718);
    for _ in 0..300 {
        let k = rng.below(4);
        let mut lists: Vec<Vec<i32>> = Vec::new();
        for _ in 0..k {
            let len = rng.below(5);
            let mut v: Vec<i32> = rng.vec(len, -8, 8);
            v.sort_unstable();
            lists.push(v);
        }
        let values: Vec<i32> = lists.concat();
        let mut want: Option<(i32, i32)> = None;
        if k > 0 && lists.iter().all(|l| !l.is_empty()) {
            for &a in &values {
                for &b in &values {
                    let covers = a <= b && lists.iter().all(|l| l.iter().any(|&x| a <= x && x <= b));
                    if covers && want.is_none_or(|(c, d)| (b - a, a) < (d - c, c)) {
                        want = Some((a, b));
                    }
                }
            }
        }
        check!(format!("lists = {lists:?}"), smallest_range(&lists), want);
    }
}

#[test]
fn scale_10k_lists() {
    let mut rng = anneal_prelude::Rng::new(719);
    let lists: Vec<Vec<i32>> = (0..10_000)
        .map(|_| {
            let mut v: Vec<i32> = rng.vec(20, -1_000_000_000, 1_000_000_000);
            v.sort_unstable();
            v
        })
        .collect();
    // Reference: a sliding window over all values sorted, counting how many lists it covers.
    let mut all: Vec<(i32, usize)> = lists.iter().enumerate().flat_map(|(l, v)| v.iter().map(move |&x| (x, l))).collect();
    all.sort_unstable();
    let (mut count, mut covered, mut left) = (vec![0usize; lists.len()], 0, 0);
    let mut want: Option<(i32, i32)> = None;
    for right in 0..all.len() {
        if count[all[right].1] == 0 {
            covered += 1;
        }
        count[all[right].1] += 1;
        while covered == lists.len() {
            let (a, b) = (all[left].0, all[right].0);
            if want.is_none_or(|(c, d)| (b as i64 - a as i64) < (d as i64 - c as i64)) {
                want = Some((a, b));
            }
            count[all[left].1] -= 1;
            if count[all[left].1] == 0 {
                covered -= 1;
            }
            left += 1;
        }
    }
    check!("10000 sorted lists of 20 random values in ±10⁹", smallest_range(&lists), want);
}
