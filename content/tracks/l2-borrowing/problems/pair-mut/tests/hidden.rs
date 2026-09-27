use solution::*;

#[test]
fn pair_adjacent() {
    check!(r#"v = [1, 2], pair (1, 0), a += 10"#, { let mut v = [1, 2]; let (a, _) = pair_mut(&mut v, 1, 0).unwrap(); *a += 10; v }, [1, 12]);
}

#[test]
fn pair_at_end() {
    check!(r#"pair (0, len - 1) of 5"#, { let mut v = [0, 1, 2, 3, 4]; let (a, b) = pair_mut(&mut v, 0, 4).unwrap(); (*a, *b) }, (0, 4));
}

#[test]
fn pair_empty() {
    check!(r#"pair (0, 1) of []"#, pair_mut(&mut [0u8; 0], 0, 1).is_none(), true);
}

#[test]
fn pair_i_out() {
    check!(r#"pair (3, 0) of 3"#, pair_mut(&mut [1, 2, 3], 3, 0).is_none(), true);
}

#[test]
fn pair_strings() {
    check!(r#"pair (1, 0) of ["a", "b"], push b onto a"#, { let mut v = ["a", "b"].map(String::from); let (b, a) = pair_mut(&mut v, 1, 0).unwrap(); a.push_str(b); v }, ["ab", "b"].map(String::from));
}

#[test]
fn prefix_sums() {
    check!(r#"[1, 2, 3, 4], b += a"#, { let mut v = [1, 2, 3, 4]; for_each_adjacent_mut(&mut v, |a, b| *b += *a); v }, [1, 3, 6, 10]);
}

#[test]
fn visits_in_order() {
    check!(r#"record pairs of [1, 2, 3]"#, { let mut seen = vec![]; for_each_adjacent_mut(&mut [1, 2, 3], |a, b| seen.push((*a, *b))); seen }, vec![(1, 2), (2, 3)]);
}

#[test]
fn carry_through_nines() {
    check!(r#"digits [10, 9, 9, 0]"#, { let mut v = [10u32, 9, 9, 0]; for_each_adjacent_mut(&mut v, |a: &mut u32, b: &mut u32| { *b += *a / 10; *a %= 10; }); v }, [0, 0, 0, 1]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6225);
    for _ in 0..300 {
        let n = rng.below(7);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let (i, j) = (rng.below(n + 2), rng.below(n + 2));
        let mut got = v.clone();
        let pair = pair_mut(&mut got, i, j).map(|(a, b)| {
            let seen = (*a, *b);
            *a += 100;
            *b -= 100;
            seen
        });
        let mut want = v.clone();
        let want_pair = if i != j && i < n && j < n {
            let seen = (v[i], v[j]);
            want[i] += 100;
            want[j] -= 100;
            Some(seen)
        } else {
            None
        };
        check!(format!("pair_mut({v:?}, {i}, {j})"), (pair, got), (want_pair, want));

        let mut got = v.clone();
        for_each_adjacent_mut(&mut got, |a, b| {
            *b = *b * 2 - *a;
            *a += 1;
        });
        let mut want = v.clone();
        for k in 1..n {
            want[k] = want[k] * 2 - want[k - 1];
            want[k - 1] += 1;
        }
        check!(format!("for_each_adjacent_mut({v:?}, b = 2b - a, a += 1)"), got, want);
    }
}

#[test]
fn long_slice() {
    let mut v = vec![1u64; 200_000];
    for_each_adjacent_mut(&mut v, |a, b| *b += *a);
    check!("prefix sums of 200000 ones", (v[0], v[199_999]), (1, 200_000));
}
