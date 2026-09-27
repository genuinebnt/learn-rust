use solution::*;

#[test]
fn whole_i32() {
    check!(r#"intervals = [(-2147483648, 2147483647)], queries = [0]"#, min_interval(&[(i32::MIN, i32::MAX)], &[0]), vec![Some(4_294_967_296)]);
}

#[test]
fn query_at_i32_edges() {
    check!(r#"intervals = [(-2147483648, -2147483648), (2147483647, 2147483647)], queries = [2147483647, -2147483648, 0]"#, min_interval(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)], &[i32::MAX, i32::MIN, 0]), vec![Some(1), Some(1), None]);
}

#[test]
fn negatives() {
    check!(r#"intervals = [(-5, -1), (-3, 3), (0, 0)], queries = [-4, -3, 0, 1, 4]"#, min_interval(&[(-5, -1), (-3, 3), (0, 0)], &[-4, -3, 0, 1, 4]), vec![Some(5), Some(5), Some(1), Some(7), None]);
}

#[test]
fn nested() {
    check!(r#"intervals = [(1, 10), (2, 9), (3, 8), (4, 7)], queries = [5, 1, 9, 11]"#, min_interval(&[(1, 10), (2, 9), (3, 8), (4, 7)], &[5, 1, 9, 11]), vec![Some(4), Some(10), Some(8), None]);
}

#[test]
fn repeated_queries() {
    check!(r#"intervals = [(1, 3)], queries = [2, 2, 2]"#, min_interval(&[(1, 3)], &[2, 2, 2]), vec![Some(3); 3]);
}

#[test]
fn small_one_ends_first() {
    check!(r#"intervals = [(1, 2), (1, 100)], queries = [3, 2]"#, min_interval(&[(1, 2), (1, 100)], &[3, 2]), vec![Some(100), Some(2)]);
}

#[test]
fn same_interval_twice() {
    check!(r#"intervals = [(4, 6), (4, 6)], queries = [5, 7]"#, min_interval(&[(4, 6), (4, 6)], &[5, 7]), vec![Some(3), None]);
}

#[test]
fn before_everything() {
    check!(r#"intervals = [(10, 20)], queries = [9, 10, 20, 21]"#, min_interval(&[(10, 20)], &[9, 10, 20, 21]), vec![None, Some(11), Some(11), None]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(826);
    for _ in 0..400 {
        let n = rng.below(7);
        let intervals: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let left = rng.int(-5, 10) as i32;
                let len = rng.int(0, 5) as i32;
                (left, left + len)
            })
            .collect();
        let m = rng.below(7);
        let queries: Vec<i32> = rng.vec(m, -6, 16);
        let want: Vec<Option<u64>> = queries
            .iter()
            .map(|&q| intervals.iter().filter(|&&(l, r)| l <= q && q <= r).map(|&(l, r)| (r - l + 1) as u64).min())
            .collect();
        check!(format!("intervals = {intervals:?}, queries = {queries:?}"), min_interval(&intervals, &queries), want);
    }
}

#[test]
fn scale_100k() {
    let mut intervals: Vec<(i32, i32)> = (0..99_999).rev().map(|i| (2 * i, 2 * i + 1)).collect();
    intervals.push((0, 200_005));
    let queries: Vec<i32> = (0..100_000).rev().map(|j| 3 * j).collect();
    let out = min_interval(&intervals, &queries);
    let count = |v: Option<u64>| out.iter().filter(|&&x| x == v).count();
    check!(
        "(2i, 2i + 1) for i in 0..99999 plus (0, 200005); queries 3j for j from 99999 down to 0",
        (count(Some(2)), count(Some(200_006)), count(None), out[0], out[99_999]),
        (66_666, 3, 33_331, None, Some(2))
    );
}
