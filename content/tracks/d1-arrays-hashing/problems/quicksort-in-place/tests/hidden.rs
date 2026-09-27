use solution::*;

fn sorted_copy(v: &[i32]) -> Vec<i32> {
    let mut s = v.to_vec();
    s.sort_unstable();
    s
}

#[test]
fn already_sorted_20k() {
    let mut v: Vec<i32> = (0..20_000).collect();
    let want = sorted_copy(&v);
    quicksort(&mut v);
    check!("0..20000", v == want, true);
}

#[test]
fn reversed_20k() {
    let mut v: Vec<i32> = (0..20_000).rev().collect();
    let want = sorted_copy(&v);
    quicksort(&mut v);
    check!("(0..20000).rev()", v == want, true);
}

#[test]
fn all_equal_20k() {
    let mut v = vec![7; 20_000];
    quicksort(&mut v);
    check!("[7; 20000]", v == vec![7; 20_000], true);
}

#[test]
fn pseudo_random_5k() {
    let mut x: u32 = 12345;
    let mut v: Vec<i32> = (0..5_000).map(|_| { x = x.wrapping_mul(1_103_515_245).wrapping_add(12_345); (x >> 16) as i32 % 1000 - 500 }).collect();
    let want = sorted_copy(&v);
    quicksort(&mut v);
    check!("5000 values in -500..500", v == want, true);
}

#[test]
fn single() {
    let mut v = vec![42];
    quicksort(&mut v);
    check!("[42]", v, vec![42]);
}

#[test]
fn two_equal() {
    let mut v = vec![3, 3];
    quicksort(&mut v);
    check!("[3, 3]", v, vec![3, 3]);
}

#[test]
fn extremes() {
    let mut v = vec![i32::MAX, 0, i32::MIN, -1, i32::MAX];
    quicksort(&mut v);
    check!("[i32::MAX, 0, i32::MIN, -1, i32::MAX]", v, vec![i32::MIN, -1, 0, i32::MAX, i32::MAX]);
}

#[test]
fn organ_pipe_20k() {
    let mut v: Vec<i32> = (0..10_000).chain((0..10_000).rev()).collect();
    let want = sorted_copy(&v);
    quicksort(&mut v);
    check!("0..10000 then back down", v == want, true);
}

#[test]
fn random_vs_sort() {
    let mut rng = anneal_prelude::Rng::new(27);
    for _ in 0..300 {
        let n = rng.below(16);
        let v: Vec<i32> = rng.vec(n, -4, 4);
        let mut got = v.clone();
        quicksort(&mut got);
        check!(format!("{v:?}"), got, sorted_copy(&v));
    }
}

#[test]
fn scale_200k_random() {
    let mut rng = anneal_prelude::Rng::new(28);
    let mut v: Vec<i32> = rng.vec(200_000, i32::MIN as i64, i32::MAX as i64);
    let want = sorted_copy(&v);
    quicksort(&mut v);
    check!("200000 random i32 values", v == want, true);
}
