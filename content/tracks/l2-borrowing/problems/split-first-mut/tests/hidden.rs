use solution::*;

#[test]
fn two() {
    check!(r#"v = [3, 4]"#, { let mut v = [3, 4]; add_head_to_rest(&mut v); v }, [3, 7]);
}

#[test]
fn zero_head() {
    check!(r#"v = [0, 5, 6]"#, { let mut v = [0, 5, 6]; add_head_to_rest(&mut v); v }, [0, 5, 6]);
}

#[test]
fn i32_bounds() {
    check!(r#"v = [i32::MIN, i32::MAX]"#, { let mut v = [i32::MIN, i32::MAX]; add_head_to_rest(&mut v); v }, [i32::MIN, -1]);
}

#[test]
fn large_values() {
    check!(r#"v = [1000000000, 1000000000]"#, { let mut v = [1_000_000_000, 1_000_000_000]; add_head_to_rest(&mut v); v }, [1_000_000_000, 2_000_000_000]);
}

#[test]
fn same_rest() {
    check!(r#"v = [5, 1, 1]"#, { let mut v = [5, 1, 1]; add_head_to_rest(&mut v); v }, [5, 6, 6]);
}

#[test]
fn not_a_prefix_sum() {
    check!(r#"v = [1, 1, 1, 1]"#, { let mut v = vec![1, 1, 1, 1]; add_head_to_rest(&mut v); v }, vec![1, 2, 2, 2]);
}

#[test]
fn big_vec() {
    check!(r#"v = [3, 0, 0, …] (100000 values)"#, { let mut v = vec![0; 100_000]; v[0] = 3; add_head_to_rest(&mut v); (v[0], v[1], v[99_999]) }, (3, 3, 3));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2006);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -1000, 1000);
        let want: Vec<i32> = v.iter().enumerate().map(|(i, &x)| if i == 0 { x } else { x + v[0] }).collect();
        let mut got = v.clone();
        add_head_to_rest(&mut got);
        check!(format!("v = {v:?}"), got, want);
    }
}
