use solution::*;

#[test]
fn carry_out() {
    check!(r#"9999999 + 9999"#, values(&add_two_numbers(list(&[9, 9, 9, 9, 9, 9, 9]), list(&[9, 9, 9, 9]))), vec![8, 9, 9, 9, 0, 0, 0, 1]);
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
