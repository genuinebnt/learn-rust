use solution::*;

#[test]
fn single_five() {
    check!(r#"bills = [5]"#, lemonade_change(&[5]), true);
}

#[test]
fn first_pays_twenty() {
    check!(r#"bills = [20]"#, lemonade_change(&[20]), false);
}

#[test]
fn ten_but_no_five() {
    check!(r#"bills = [5, 10, 20]"#, lemonade_change(&[5, 10, 20]), false);
}

#[test]
fn ten_and_five() {
    check!(r#"bills = [5, 5, 10, 20]"#, lemonade_change(&[5, 5, 10, 20]), true);
}

#[test]
fn fives_run_out() {
    check!(r#"bills = [5, 5, 5, 20, 20]"#, lemonade_change(&[5, 5, 5, 20, 20]), false);
}

#[test]
fn later_five_too_late() {
    check!(r#"bills = [10, 5]"#, lemonade_change(&[10, 5]), false);
}

#[test]
fn twenties_are_not_change() {
    check!(r#"bills = [5, 5, 5, 20, 10]"#, lemonade_change(&[5, 5, 5, 20, 10]), false);
}

#[test]
fn many_fives() {
    check!(r#"bills = [5; 1000]"#, lemonade_change(&vec![5; 1000]), true);
}

#[test]
fn random_vs_brute_force() {
    // Tries both ways of changing every 20.
    fn ok(bills: &[u32], fives: i32, tens: i32) -> bool {
        let Some((&b, rest)) = bills.split_first() else { return true };
        match b {
            5 => ok(rest, fives + 1, tens),
            10 => fives > 0 && ok(rest, fives - 1, tens + 1),
            _ => (tens > 0 && fives > 0 && ok(rest, fives - 1, tens - 1)) || (fives >= 3 && ok(rest, fives - 3, tens)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(802);
    for _ in 0..400 {
        let n = rng.below(13);
        let bills: Vec<u32> = (0..n).map(|_| *rng.pick(&[5, 5, 5, 10, 10, 20])).collect();
        check!(format!("bills = {bills:?}"), lemonade_change(&bills), ok(&bills, 0, 0));
    }
}

#[test]
fn scale_200k() {
    let bills: Vec<u32> = [5, 5, 5, 10, 20].repeat(40_000);
    let mut late_ten = bills.clone();
    late_ten.insert(0, 10);
    check!("bills = [5, 5, 5, 10, 20] × 40000, then with a 10 in front", (lemonade_change(&bills), lemonade_change(&late_ten)), (true, false));
}
