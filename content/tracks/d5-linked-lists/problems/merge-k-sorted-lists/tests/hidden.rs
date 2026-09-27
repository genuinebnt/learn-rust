use solution::*;

#[test]
fn empty_lists() {
    check!(r#"[[],[]]"#, merge_k(vec![None, None]), None);
}

#[test]
fn duplicates_across() {
    check!(r#"[[1,1],[1],[1,1,1]]"#, values(&merge_k(vec![list(&[1, 1]), list(&[1]), list(&[1, 1, 1])])), vec![1; 6]);
}

#[test]
fn extremes() {
    check!(r#"[[MIN,MAX],[0]]"#, values(&merge_k(vec![list(&[i32::MIN, i32::MAX]), list(&[0])])), vec![i32::MIN, 0, i32::MAX]);
}

#[test]
fn uneven_lengths() {
    check!(r#"[[5],[1,2,3,4,6,7]]"#, values(&merge_k(vec![list(&[5]), list(&[1, 2, 3, 4, 6, 7])])), vec![1, 2, 3, 4, 5, 6, 7]);
}

#[test]
fn two_lists() {
    check!(r#"[[2,4],[1,3]]"#, values(&merge_k(vec![list(&[2, 4]), list(&[1, 3])])), vec![1, 2, 3, 4]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(512);
    for _ in 0..300 {
        let k = rng.below(5);
        let lists: Vec<Vec<i32>> = (0..k).map(|_| { let n = rng.below(5); let mut v: Vec<i32> = rng.vec(n, -9, 9); v.sort(); v }).collect();
        let mut want: Vec<i32> = lists.concat();
        want.sort();
        check!(format!("{lists:?}"), values(&merge_k(lists.iter().map(|v| list(v)).collect())), want);
    }
}

#[test]
fn scale_50k_lists() {
    // 50000 lists of 4 values each: list j holds j, j + 50000, j + 100000, j + 150000.
    let k = 50_000;
    let lists: Vec<_> = (0..k).map(|j| list(&[j, j + k, j + 2 * k, j + 3 * k])).collect();
    let m = merge_k(lists);
    let got = values(&m);
    free(m);
    check!("50000 lists of 4 values", got == (0..4 * k).collect::<Vec<_>>(), true);
}

#[test]
fn negatives() {
    check!(r#"[[-3,0],[-5]]"#, values(&merge_k(vec![list(&[-3, 0]), list(&[-5])])), vec![-5, -3, 0]);
}

#[test]
fn many() {
    let lists: Vec<_> = (0..100).map(|k| list(&(0..100).map(|i| i * 100 + k).collect::<Vec<i32>>())).collect();
    check!(r#"100 lists × 100 values"#, values(&merge_k(lists)) == (0..10_000).collect::<Vec<_>>(), true);
}
