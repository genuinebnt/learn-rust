use solution::*;

#[test]
fn extremes_average() {
    let mut m = MedianFinder::new();
    m.add_num(i32::MIN);
    m.add_num(i32::MAX);
    check!(r#"add i32::MIN, add i32::MAX"#, m.find_median(), Some(-0.5));
}

#[test]
fn remove_everything() {
    let mut m = MedianFinder::new();
    m.add_num(3);
    m.add_num(1);
    m.remove_num(1);
    m.remove_num(3);
    check!(r#"add 3, add 1, remove 1, remove 3"#, (m.find_median(), m.remove_num(3)), (None, false));
}

#[test]
fn refill_after_empty() {
    let mut m = MedianFinder::new();
    m.add_num(2);
    m.remove_num(2);
    m.add_num(8);
    m.add_num(6);
    check!(r#"add 2, remove 2, add 8, add 6"#, m.find_median(), Some(7.0));
}

#[test]
fn same_value_on_both_sides() {
    let mut m = MedianFinder::new();
    m.add_num(5);
    m.add_num(5);
    m.remove_num(5);
    let a = m.find_median();
    m.remove_num(5);
    let b = m.find_median();
    check!(r#"add 5, add 5, remove 5, find, remove 5, find, remove 5"#, (a, b, m.remove_num(5)), (Some(5.0), None, false));
}

#[test]
fn remove_from_the_bottom() {
    let mut m = MedianFinder::new();
    m.add_num(1);
    m.add_num(2);
    m.add_num(3);
    m.add_num(4);
    m.add_num(5);
    m.add_num(6);
    m.add_num(7);
    m.remove_num(1);
    m.remove_num(2);
    check!(r#"add 1..=7, remove 1, remove 2 → [3..=7]"#, m.find_median(), Some(5.0));
}

#[test]
fn remove_from_the_top() {
    let mut m = MedianFinder::new();
    m.add_num(1);
    m.add_num(2);
    m.add_num(3);
    m.add_num(4);
    m.add_num(5);
    m.add_num(6);
    m.add_num(7);
    m.remove_num(7);
    m.remove_num(6);
    m.remove_num(5);
    check!(r#"add 1..=7, remove 7, remove 6, remove 5 → [1..=4]"#, m.find_median(), Some(2.5));
}

#[test]
fn negatives() {
    let mut m = MedianFinder::new();
    m.add_num(-5);
    m.add_num(-1);
    m.add_num(-3);
    m.add_num(-2);
    check!(r#"add -5, add -1, add -3, add -2"#, m.find_median(), Some(-2.5));
}

#[test]
fn descending_adds() {
    let mut m = MedianFinder::new();
    m.add_num(9);
    m.add_num(8);
    m.add_num(7);
    m.add_num(6);
    m.add_num(5);
    check!(r#"add 9, 8, 7, 6, 5"#, m.find_median(), Some(7.0));
}

#[test]
fn remove_twice_one_copy() {
    let mut m = MedianFinder::new();
    m.add_num(3);
    m.add_num(3);
    let (a, b, c) = (m.remove_num(3), m.remove_num(3), m.remove_num(3));
    check!(r#"add 3, add 3, remove 3, remove 3, remove 3"#, (a, b, c), (true, true, false));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(714);
    for _ in 0..300 {
        let mut m = MedianFinder::new();
        let mut bag: Vec<i32> = Vec::new();
        let mut log = Vec::new();
        let steps = rng.below(30);
        for _ in 0..steps {
            let v = rng.int(-3, 3) as i32;
            match rng.below(5) {
                0 | 1 => {
                    m.add_num(v);
                    bag.push(v);
                    log.push(format!("add {v}"));
                }
                2 => {
                    let want = bag.iter().position(|&x| x == v).map(|i| bag.swap_remove(i)).is_some();
                    log.push(format!("remove {v}"));
                    check!(log.join(", "), m.remove_num(v), want);
                }
                _ => {
                    let mut s = bag.clone();
                    s.sort_unstable();
                    let n = s.len();
                    let want = match n {
                        0 => None,
                        _ if n % 2 == 1 => Some(s[n / 2] as f64),
                        _ => Some((s[n / 2 - 1] as f64 + s[n / 2] as f64) / 2.0),
                    };
                    log.push("find_median".to_string());
                    check!(log.join(", "), m.find_median(), want);
                }
            }
        }
    }
}

#[test]
fn scale_sliding_window() {
    // Reference: a Fenwick tree of counts over the values 0..2^18; k-th smallest by binary lifting.
    const N: usize = 1 << 18;
    fn bump(tree: &mut [i64], v: usize, d: i64) {
        let mut i = v + 1;
        while i <= N {
            tree[i] += d;
            i += i & i.wrapping_neg();
        }
    }
    fn kth(tree: &[i64], mut k: i64) -> f64 {
        let (mut pos, mut step) = (0, N);
        while step > 0 {
            if pos + step <= N && tree[pos + step] < k {
                pos += step;
                k -= tree[pos];
            }
            step >>= 1;
        }
        pos as f64
    }
    let mut tree = vec![0i64; N + 1];
    let mut rng = anneal_prelude::Rng::new(715);
    let vals: Vec<i32> = rng.vec(150_000, 0, N as i64 - 1);
    let mut m = MedianFinder::new();
    let mut first_wrong = None;
    for (i, &v) in vals.iter().enumerate() {
        m.add_num(v);
        bump(&mut tree, v as usize, 1);
        // A window of the last 50000 values: remove the one that falls out.
        if i >= 50_000 {
            let old = vals[i - 50_000];
            m.remove_num(old);
            bump(&mut tree, old as usize, -1);
        }
        let n = (i + 1).min(50_000) as i64;
        let want = if n % 2 == 1 { kth(&tree, (n + 1) / 2) } else { (kth(&tree, n / 2) + kth(&tree, n / 2 + 1)) / 2.0 };
        if m.find_median() != Some(want) && first_wrong.is_none() {
            first_wrong = Some(i);
        }
    }
    check!("150000 random values, a window of the last 50000 (add one, remove the oldest, find_median); first step with a wrong median", first_wrong, None);
}
