use solution::*;

#[test]
fn deltas_basic() {
    check!(r#"v = [1, 4, 9]"#, deltas(&[1, 4, 9]), vec![3, 5]);
}

#[test]
fn deltas_empty() {
    check!(r#"v = []"#, deltas(&[]), Vec::<i64>::new());
}

#[test]
fn peaks_basic() {
    check!(r#"v = [1, 3, 2, 5, 4]"#, peaks(&[1, 3, 2, 5, 4]), vec![1, 3]);
}

#[test]
fn sum16_odd_length() {
    check!(r#"bytes = [0x12, 0x34, 0x56]"#, sum16(&[0x12, 0x34, 0x56]), 0x6834);
}

#[test]
fn commas_seven_digits() {
    check!(r#""1234567""#, with_commas("1234567"), "1,234,567".to_string());
}
