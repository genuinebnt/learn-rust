use solution::*;

#[test]
fn odd() {
    check!(r#"[1,2,3,2,1]"#, is_palindrome(list(&[1, 2, 3, 2, 1])), true);
}

#[test]
fn two_same() {
    check!(r#"[4,4]"#, is_palindrome(list(&[4, 4])), true);
}

#[test]
fn middle_differs_even() {
    check!(r#"[1,3,2,1]"#, is_palindrome(list(&[1, 3, 2, 1])), false);
}

#[test]
fn negatives() {
    check!(r#"[-1,5,-1]"#, is_palindrome(list(&[-1, 5, -1])), true);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, i32::MAX, i32::MIN]"#, is_palindrome(list(&[i32::MIN, i32::MAX, i32::MIN])), true);
}

#[test]
fn sorted_is_not() {
    check!(r#"[1,2,3]"#, is_palindrome(list(&[1, 2, 3])), false);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(509);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut v: Vec<i32> = rng.vec(n, 0, 2);
        if rng.bool() {
            for i in 0..n / 2 {
                v[n - 1 - i] = v[i];
            }
        }
        let want = v.iter().eq(v.iter().rev());
        check!(format!("{v:?}"), is_palindrome(list(&v)), want);
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..100_000).chain((0..100_000).rev()).collect();
    let mut w = v.clone();
    w[100_000] = -1;
    // is_palindrome drops the list itself, and a Box chain drops recursively: give it a big stack.
    let got = std::thread::Builder::new()
        .stack_size(512 << 20)
        .spawn(move || (is_palindrome(list(&v)), is_palindrome(list(&w))))
        .expect("spawn")
        .join()
        .expect("is_palindrome panicked");
    check!("0..100000 then back down, and the same with one value changed", got, (true, false));
}

#[test]
fn empty() {
    check!(r#"[]"#, is_palindrome(None), true);
}

#[test]
fn near_miss() {
    check!(r#"[1,2,3,1]"#, is_palindrome(list(&[1, 2, 3, 1])), false);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..5_000).chain((0..5_000).rev()).collect();
    check!(r#"10⁴ symmetric values"#, is_palindrome(list(&v)), true);
}
