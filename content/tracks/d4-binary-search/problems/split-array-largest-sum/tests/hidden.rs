use solution::*;

#[test]
fn each_alone() {
    check!(r#"[1,4,4], k = 3"#, split_array(&[1, 4, 4], 3), 4);
}

#[test]
fn one_part() {
    check!(r#"[1,2,3], k = 1"#, split_array(&[1, 2, 3], 1), 6);
}

#[test]
fn big_values() {
    check!(r#"[4·10⁹; 4], k = 2"#, split_array(&[4_000_000_000, 4_000_000_000, 4_000_000_000, 4_000_000_000], 2), 8_000_000_000);
}

#[test]
fn long() {
    let v = vec![1u32; 100_000];
    check!(r#"10⁵ ones, k = 7"#, split_array(&v, 7), 14_286);
}
