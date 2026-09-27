use solution::*;

#[test]
fn example() {
    check!(r#"342 + 465"#, values(&add_two_numbers(list(&[2, 4, 3]), list(&[5, 6, 4]))), vec![7, 0, 8]);
}

#[test]
fn zeros() {
    check!(r#"0 + 0"#, values(&add_two_numbers(list(&[0]), list(&[0]))), vec![0]);
}

#[test]
fn carry_out() {
    check!(r#"9999999 + 9999"#, values(&add_two_numbers(list(&[9, 9, 9, 9, 9, 9, 9]), list(&[9, 9, 9, 9]))), vec![8, 9, 9, 9, 0, 0, 0, 1]);
}

#[test]
fn final_carry() {
    check!(r#"5 + 5"#, values(&add_two_numbers(list(&[5]), list(&[5]))), vec![0, 1]);
}

#[test]
fn both_empty() {
    check!(r#"[] + []"#, add_two_numbers(None, None), None);
}
