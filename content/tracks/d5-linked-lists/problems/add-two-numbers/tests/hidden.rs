use solution::*;

#[test]
fn carry_out() {
    check!(r#"9999999 + 9999"#, values(&add_two_numbers(list(&[9, 9, 9, 9, 9, 9, 9]), list(&[9, 9, 9, 9]))), vec![8, 9, 9, 9, 0, 0, 0, 1]);
}

#[test]
fn final_carry() {
    check!(r#"5 + 5"#, values(&add_two_numbers(list(&[5]), list(&[5]))), vec![0, 1]);
}

#[test]
fn second_longer() {
    check!(r#"12 + 99921"#, values(&add_two_numbers(list(&[2, 1]), list(&[1, 2, 9, 9, 9]))), vec![3, 3, 9, 9, 9]);
}

#[test]
fn carry_chain_into_longer() {
    check!(r#"1 + 999"#, values(&add_two_numbers(list(&[1]), list(&[9, 9, 9]))), vec![0, 0, 0, 1]);
}

#[test]
fn zero_plus_number() {
    check!(r#"0 + 507"#, values(&add_two_numbers(list(&[0]), list(&[7, 0, 5]))), vec![7, 0, 5]);
}

#[test]
fn past_u64() {
    check!(r#"20 nines + 1"#, values(&add_two_numbers(list(&[9; 20]), list(&[1]))), { let mut v = vec![0; 20]; v.push(1); v });
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(508);
    for _ in 0..300 {
        let (m, n) = (1 + rng.below(9), 1 + rng.below(9));
        let mut a: Vec<i32> = rng.vec(m, 0, 9);
        let mut b: Vec<i32> = rng.vec(n, 0, 9);
        // No leading zeros, except for the number 0 itself.
        if m > 1 {
            a[m - 1] = rng.int(1, 9) as i32;
        }
        if n > 1 {
            b[n - 1] = rng.int(1, 9) as i32;
        }
        let num = |d: &[i32]| d.iter().rev().fold(0u64, |acc, &x| acc * 10 + x as u64);
        let mut sum = num(&a) + num(&b);
        let mut want = vec![(sum % 10) as i32];
        sum /= 10;
        while sum > 0 {
            want.push((sum % 10) as i32);
            sum /= 10;
        }
        check!(format!("{a:?} + {b:?}"), values(&add_two_numbers(list(&a), list(&b))), want);
    }
}

#[test]
fn scale_100k_digits() {
    let a = list(&vec![9; 100_000]);
    let b = list(&vec![9; 100_000]);
    let s = add_two_numbers(a, b);
    let got = values(&s);
    free(s);
    check!("10⁵ nines + 10⁵ nines", (got.len(), got[0], got[1], got[99_999], got[100_000]), (100_001, 8, 9, 9, 1));
}

#[test]
fn one_empty() {
    check!(r#"[] + 12"#, values(&add_two_numbers(None, list(&[2, 1]))), vec![2, 1]);
}

#[test]
fn huge() {
    let nines = vec![9; 10_000];
    check!(r#"10⁴ nines + 1"#, { let s = values(&add_two_numbers(list(&nines), list(&[1]))); (s.len(), s[0], s[9_999], s[10_000]) }, (10_001, 0, 0, 1));
}
