use solution::*;

#[test]
fn negatives() {
    check!(r#"nums = [3, -1, -2]"#, running_sum(&[3, -1, -2]), vec![3, 2, 0]);
}

#[test]
fn ten_thousand_ones() {
    check!(r#"nums = [1; 10000]"#, *running_sum(&[1; 10000]).last().unwrap(), 10000);
}
