use solution::*;

#[test]
fn all_equal() {
    check!(r#"[5, 5]"#, { let mut v = [5, 5]; bump_below_average(&mut v); v }, [5, 5]);
}

#[test]
fn floor_average() {
    check!(r#"[1, 2, 4]"#, { let mut v = [1, 2, 4]; bump_below_average(&mut v); v }, [11, 2, 4]);
}

#[test]
fn strictly_below() {
    check!(r#"[0, 10]"#, { let mut v = [0, 10]; bump_below_average(&mut v); v }, [10, 10]);
}

#[test]
fn no_overflow() {
    check!(r#"[u32::MAX, u32::MAX, 0]"#, { let mut v = [u32::MAX, u32::MAX, 0]; bump_below_average(&mut v); v }, [u32::MAX, u32::MAX, 10]);
}

#[test]
fn zeros() {
    check!(r#"[0, 0, 1]"#, { let mut v = [0, 0, 1]; bump_below_average(&mut v); v }, [0, 0, 1]);
}

#[test]
fn duplicates() {
    check!(r#"[3, 3, 9]"#, { let mut v = [3, 3, 9]; bump_below_average(&mut v); v }, [13, 13, 9]);
}

#[test]
fn bump_passes_average() {
    check!(r#"[10, 20, 30, 40]"#, { let mut v = [10, 20, 30, 40]; bump_below_average(&mut v); v }, [20, 30, 30, 40]);
}

#[test]
fn all_zero() {
    check!(r#"[0, 0]"#, { let mut v = [0, 0]; bump_below_average(&mut v); v }, [0, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2019);
    for _ in 0..300 {
        let n = rng.below(8);
        let v: Vec<u32> = rng.vec(n, 0, 50);
        let mut want = v.clone();
        if n > 0 {
            let avg = v.iter().map(|&s| s as u64).sum::<u64>() / n as u64;
            for s in want.iter_mut() {
                if (*s as u64) < avg {
                    *s += 10;
                }
            }
        }
        let mut got = v.clone();
        bump_below_average(&mut got);
        check!(format!("scores = {v:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<u32> = (0..200_000).map(|i| i % 100).collect();
    bump_below_average(&mut v);
    check!("scores = [0, 1, …, 99] × 2000 (average 49)", (v.iter().map(|&x| x as u64).sum::<u64>(), v[0], v[48], v[49]), (10_880_000, 10, 58, 49));
}
