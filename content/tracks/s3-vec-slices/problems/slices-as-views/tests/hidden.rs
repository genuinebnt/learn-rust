use solution::*;

#[test]
fn middle_of_empty() {
    check!(r#"v = []"#, middle(&[]), &[][..]);
}

#[test]
fn trim_all_zero() {
    check!(r#"v = [0, 0]"#, trim_zeros(&[0, 0]), &[][..]);
}

#[test]
fn middle_of_two() {
    check!(r#"v = [1, 2]"#, middle(&[1, 2]), &[][..]);
}

#[test]
fn trim_empty() {
    check!(r#"v = []"#, trim_zeros(&[]), &[][..]);
}

#[test]
fn trim_single_zero() {
    check!(r#"v = [0]"#, trim_zeros(&[0]), &[][..]);
}

#[test]
fn trim_single_value() {
    check!(r#"v = [7]"#, trim_zeros(&[7]), &[7][..]);
}

#[test]
fn trim_negatives() {
    check!(r#"v = [0, -1, 0, -2, 0]"#, trim_zeros(&[0, -1, 0, -2, 0]), &[-1, 0, -2][..]);
}

#[test]
fn trim_trailing_only() {
    check!(r#"v = [4, 0, 0]"#, trim_zeros(&[4, 0, 0]), &[4][..]);
}

#[test]
fn views_not_copies() {
    let v = vec![0, 3, 4, 0];
    check!(r#"results point into v"#, (middle(&v).as_ptr() == v[1..].as_ptr(), trim_zeros(&v).as_ptr() == v[1..].as_ptr()), (true, true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2304);
    for _ in 0..300 {
        let n = rng.below(8);
        let v: Vec<i32> = rng.vec(n, -1, 1);
        let want_middle: Vec<i32> = if n < 2 { vec![] } else { v[1..n - 1].to_vec() };
        let mut t = v.clone();
        while t.first() == Some(&0) {
            t.remove(0);
        }
        while t.last() == Some(&0) {
            t.pop();
        }
        check!(format!("v = {v:?}"), (middle(&v).to_vec(), trim_zeros(&v).to_vec()), (want_middle, t));
    }
}

#[test]
fn scale_200k() {
    let mut v = vec![0; 200_000];
    v[100_000] = 5;
    check!("v = 200000 zeros with a 5 at index 100000", (trim_zeros(&v), middle(&v).len()), (&[5][..], 199_998));
}
