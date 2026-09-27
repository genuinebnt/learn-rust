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
