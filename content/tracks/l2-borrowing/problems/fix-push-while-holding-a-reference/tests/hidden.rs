use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], x = -2"#, { let mut v = vec![]; (add_and_max(&mut v, -2), v) }, (-2, vec![-2]));
}

#[test]
fn max_first() {
    check!(r#"v = [8, 1, 2], x = 3"#, { let mut v = vec![8, 1, 2]; add_and_max(&mut v, 3) }, 8);
}

#[test]
fn all_negative_x_larger() {
    check!(r#"v = [-9, -8], x = -1"#, { let mut v = vec![-9, -8]; add_and_max(&mut v, -1) }, -1);
}

#[test]
fn i32_extremes() {
    check!(r#"v = [i32::MIN], x = i32::MAX"#, { let mut v = vec![i32::MIN]; (add_and_max(&mut v, i32::MAX), v) }, (i32::MAX, vec![i32::MIN, i32::MAX]));
}

#[test]
fn only_min() {
    check!(r#"v = [i32::MIN], x = i32::MIN"#, { let mut v = vec![i32::MIN]; add_and_max(&mut v, i32::MIN) }, i32::MIN);
}

#[test]
fn duplicates() {
    check!(r#"v = [7, 7, 7], x = 7"#, { let mut v = vec![7, 7, 7]; (add_and_max(&mut v, 7), v) }, (7, vec![7, 7, 7, 7]));
}

#[test]
fn empty_min() {
    check!(r#"v = [], x = i32::MIN"#, { let mut v = vec![]; (add_and_max(&mut v, i32::MIN), v) }, (i32::MIN, vec![i32::MIN]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2001);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -50, 50);
        let x = rng.int(-50, 50) as i32;
        let want = v.iter().copied().chain([x]).max().unwrap();
        let mut after = v.clone();
        after.push(x);
        let mut got_v = v.clone();
        let got = add_and_max(&mut got_v, x);
        check!(format!("v = {v:?}, x = {x}"), (got, got_v), (want, after));
    }
}
