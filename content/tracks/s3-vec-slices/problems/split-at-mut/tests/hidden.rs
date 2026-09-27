use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: [i32; 0] = []; add_halves(&mut v); v }, []);
}

#[test]
fn one() {
    check!(r#"v = [4]"#, { let mut v = [4]; add_halves(&mut v); v }, [4]);
}

#[test]
fn three() {
    check!(r#"v = [1, 2, 3]"#, { let mut v = [1, 2, 3]; add_halves(&mut v); v }, [1, 3, 3]);
}

#[test]
fn zeros() {
    check!(r#"v = [0, 0, 0, 0]"#, { let mut v = [0; 4]; add_halves(&mut v); v }, [0; 4]);
}

#[test]
fn big_values() {
    check!(r#"v = [1000000000, 1000000000]"#, { let mut v = [1_000_000_000, 1_000_000_000]; add_halves(&mut v); v }, [1_000_000_000, 2_000_000_000]);
}

#[test]
fn first_half_unchanged() {
    check!(r#"v = [7, 8, 9, 1, 2, 3]"#, { let mut v = [7, 8, 9, 1, 2, 3]; add_halves(&mut v); v }, [7, 8, 9, 8, 10, 12]);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, 0, i32::MAX, 0]"#, { let mut v = [i32::MIN, 0, i32::MAX, 0]; add_halves(&mut v); v }, [i32::MIN, 0, -1, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2311);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -100, 100);
        let mid = n / 2;
        let mut want = v.clone();
        for i in 0..mid {
            want[mid + i] += v[i];
        }
        let mut got = v.clone();
        add_halves(&mut got);
        check!(format!("v = {v:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut v = vec![1; 200_001];
    add_halves(&mut v);
    check!("v = [1; 200001]", (v[99_999], v[100_000], v[199_999], v[200_000]), (1, 2, 2, 1));
}
