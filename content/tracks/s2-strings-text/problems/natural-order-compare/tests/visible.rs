use solution::*;
use std::cmp::Ordering;

#[test]
fn numbers_by_value() {
    check!(r#""file9" vs "file10""#, (natural_cmp("file9", "file10"), natural_cmp("file10", "file9")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn text_then_number() {
    check!(r#""a2b" vs "a10a""#, (natural_cmp("a2b", "a10a"), natural_cmp("a10a", "a2b")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn leading_zeros_tie_break() {
    check!(r#""x01" vs "x1""#, (natural_cmp("x01", "x1"), natural_cmp("x1", "x01")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn sorts_a_listing() {
    let mut v = vec!["img12.png", "img10.png", "img2.png", "img1.png"];
    v.sort_by(|a, b| natural_cmp(a, b));
    check!(r#"["img12.png", "img10.png", "img2.png", "img1.png"]"#, v, vec!["img1.png", "img2.png", "img10.png", "img12.png"]);
}

#[test]
fn luhn_valid_card() {
    check!(r#""4539 3195 0343 6467""#, luhn_valid("4539 3195 0343 6467"), true);
}
