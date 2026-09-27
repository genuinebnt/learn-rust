use solution::*;

#[test]
fn out_of_bounds() {
    check!(r#"0 → 7"#, { let mut b = [10, 0]; transfer(&mut b, 0, 7, 1) }, Err("no such account"));
}

#[test]
fn insufficient() {
    check!(r#"[1, 0], 0 → 1, 5"#, { let mut b = [1, 0]; (transfer(&mut b, 0, 1, 5), b) }, (Err("insufficient funds"), [1, 0]));
}

#[test]
fn from_out_of_bounds() {
    check!(r#"[1, 2], 9 → 0"#, { let mut b = [1, 2]; transfer(&mut b, 9, 0, 1) }, Err("no such account"));
}

#[test]
fn unchanged_on_error() {
    check!(r#"[10, 0], 0 → 7"#, { let mut b = [10, 0]; (transfer(&mut b, 0, 7, 1), b) }, (Err("no such account"), [10, 0]));
}

#[test]
fn negative_source() {
    check!(r#"[-5, 0], 0 → 1, 1"#, { let mut b = [-5, 0]; (transfer(&mut b, 0, 1, 1), b) }, (Err("insufficient funds"), [-5, 0]));
}

#[test]
fn zero_amount() {
    check!(r#"[0, 0], 0 → 1, 0"#, { let mut b = [0, 0]; (transfer(&mut b, 0, 1, 0), b) }, (Ok(()), [0, 0]));
}

#[test]
fn large_values() {
    check!(r#"[i64::MAX, 0], move all"#, { let mut b = [i64::MAX, 0]; (transfer(&mut b, 0, 1, i64::MAX), b) }, (Ok(()), [0, i64::MAX]));
}

#[test]
fn empty_slice() {
    check!(r#"[], 0 → 1"#, { let mut b: [i64; 0] = []; transfer(&mut b, 0, 1, 1) }, Err("no such account"));
}

#[test]
fn middle_untouched() {
    check!(r#"[5, 5, 5], 0 → 2, 5"#, { let mut b = [5, 5, 5]; (transfer(&mut b, 0, 2, 5), b) }, (Ok(()), [0, 5, 10]));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2029);
    for _ in 0..300 {
        let len = rng.below(4);
        let b0: Vec<i64> = rng.vec(len, -5, 20);
        let from = rng.below(len + 2);
        let to = rng.below(len + 2);
        let amount = rng.int(0, 25);
        if from == to && from >= len {
            continue;
        }
        let mut want_b = b0.clone();
        let want = if from >= len || to >= len {
            Err("no such account")
        } else if from == to {
            Err("same account")
        } else if b0[from] < amount {
            Err("insufficient funds")
        } else {
            want_b[from] -= amount;
            want_b[to] += amount;
            Ok(())
        };
        let mut b = b0.clone();
        let got = transfer(&mut b, from, to, amount);
        check!(format!("balances {b0:?}, {from} → {to}, {amount}"), (got, b), (want, want_b));
    }
}
