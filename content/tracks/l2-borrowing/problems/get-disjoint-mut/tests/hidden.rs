use solution::*;

#[test]
fn settle_nothing() {
    check!(r#"settle with N = 0"#, { let mut b = [4]; (settle(&mut b, [], []), b) }, (Ok(()), [4]));
}

#[test]
fn settle_one_zero() {
    check!(r#"settle [0] by [0]"#, { let mut b = [4]; (settle(&mut b, [0], [0]), b) }, (Ok(()), [4]));
}

#[test]
fn settle_one_nonzero() {
    check!(r#"settle [0] by [3]"#, { let mut b = [4]; settle(&mut b, [0], [3]) }, Err(SettleError::Unbalanced));
}

#[test]
fn drain_to_zero() {
    check!(r#"[7, 0], 0 -> 1, 7"#, { let mut b = [7, 0]; (transfer(&mut b, 0, 1, 7), b) }, (Ok(()), [0, 7]));
}

#[test]
fn unordered_indices() {
    check!(r#"[1, 2, 3, 4], idx [3, 0, 2], deltas [-4, 1, 3]"#, { let mut b = [1, 2, 3, 4]; (settle(&mut b, [3, 0, 2], [-4, 1, 3]), b) }, (Ok(()), [2, 2, 6, 0]));
}

#[test]
fn index_error_before_balance() {
    check!(r#"idx [0, 9] and unbalanced deltas"#, { let mut b = [1, 1]; settle(&mut b, [0, 9], [1, 1]) }, Err(SettleError::NoSuchAccount));
}

#[test]
fn overlap_before_balance() {
    check!(r#"idx [1, 1] and unbalanced deltas"#, { let mut b = [1, 1]; settle(&mut b, [1, 1], [1, 1]) }, Err(SettleError::SameAccount));
}

#[test]
fn empty_slice() {
    check!(r#"no accounts; transfer 0 -> 1"#, transfer(&mut [], 0, 1, 0), Err(SettleError::NoSuchAccount));
}

#[test]
fn balance_before_funds() {
    check!(r#"[0, 0], settle by [-1, 2]"#, { let mut b = [0, 0]; settle(&mut b, [0, 1], [-1, 2]) }, Err(SettleError::Unbalanced));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6232);
    for _ in 0..400 {
        let n = rng.below(5);
        let start: Vec<i64> = rng.vec(n, 0, 6);
        let idx = [rng.below(n + 1), rng.below(n + 1), rng.below(n + 1)];
        let mut deltas = [rng.int(-4, 4), rng.int(-4, 4), 0];
        deltas[2] = if rng.below(4) == 0 { rng.int(-3, 3) } else { -deltas[0] - deltas[1] };
        let mut b = start.clone();
        let got = settle(&mut b, idx, deltas);
        let mut want_b = start.clone();
        let mut idx_err = None;
        for k in 0..3 {
            if idx[k] >= n {
                idx_err = Some(SettleError::NoSuchAccount);
                break;
            }
            if idx[..k].contains(&idx[k]) {
                idx_err = Some(SettleError::SameAccount);
                break;
            }
        }
        let want = if let Some(e) = idx_err {
            Err(e)
        } else if deltas.iter().sum::<i64>() != 0 {
            Err(SettleError::Unbalanced)
        } else if (0..3).any(|k| start[idx[k]] + deltas[k] < 0) {
            Err(SettleError::Insufficient)
        } else {
            for k in 0..3 {
                want_b[idx[k]] += deltas[k];
            }
            Ok(())
        };
        check!(format!("balances {start:?}, idx {idx:?}, deltas {deltas:?}"), (got, b), (want, want_b));
    }
}

#[test]
fn many_transfers() {
    let mut b = vec![1i64; 100_000];
    let mut ok = 0;
    for i in 0..99_999 {
        let amount = b[i];
        if transfer(&mut b, i, i + 1, amount).is_ok() {
            ok += 1;
        }
    }
    check!("100000 accounts of 1, each passing everything to the next", (ok, b[99_999], b[0]), (99_999, 100_000, 0));
}
