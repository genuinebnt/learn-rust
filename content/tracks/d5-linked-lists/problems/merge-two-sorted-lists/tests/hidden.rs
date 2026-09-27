use solution::*;

#[test]
fn both_empty() {
    check!(r#"[] + []"#, merge(None, None), None);
}

#[test]
fn disjoint() {
    check!(r#"[5,6] + [1,2]"#, values(&merge(list(&[5, 6]), list(&[1, 2]))), vec![1, 2, 5, 6]);
}

#[test]
fn long() {
    let odd: Vec<i32> = (0..10_000).filter(|x| x % 2 == 1).collect();
    let even: Vec<i32> = (0..10_000).filter(|x| x % 2 == 0).collect();
    check!(r#"odds + evens below 10⁴"#, values(&merge(list(&odd), list(&even))) == (0..10_000).collect::<Vec<_>>(), true);
}

#[test]
fn second_empty() {
    check!(r#"[1,2] + []"#, values(&merge(list(&[1, 2]), None)), vec![1, 2]);
}

#[test]
fn all_equal() {
    check!(r#"[3,3] + [3,3,3]"#, values(&merge(list(&[3, 3]), list(&[3, 3, 3]))), vec![3, 3, 3, 3, 3]);
}

#[test]
fn negatives() {
    check!(r#"[-5,-1] + [-3,0]"#, values(&merge(list(&[-5, -1]), list(&[-3, 0]))), vec![-5, -3, -1, 0]);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, i32::MAX] + [0]"#, values(&merge(list(&[i32::MIN, i32::MAX]), list(&[0]))), vec![i32::MIN, 0, i32::MAX]);
}

#[test]
fn rest_of_first() {
    check!(r#"[1,5,6,7] + [2]"#, values(&merge(list(&[1, 5, 6, 7]), list(&[2]))), vec![1, 2, 5, 6, 7]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(502);
    for _ in 0..300 {
        let (m, n) = (rng.below(8), rng.below(8));
        let mut a: Vec<i32> = rng.vec(m, -9, 9);
        let mut b: Vec<i32> = rng.vec(n, -9, 9);
        a.sort();
        b.sort();
        let mut want = [a.clone(), b.clone()].concat();
        want.sort();
        check!(format!("{a:?} + {b:?}"), values(&merge(list(&a), list(&b))), want);
    }
}

#[test]
fn scale_200k() {
    let even: Vec<i32> = (0..200_000).filter(|x| x % 2 == 0).collect();
    let odd: Vec<i32> = (0..200_000).filter(|x| x % 2 == 1).collect();
    let m = merge(list(&even), list(&odd));
    let got = values(&m);
    free(m);
    check!("evens + odds below 200000", got == (0..200_000).collect::<Vec<_>>(), true);
}
