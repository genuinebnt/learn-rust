use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, { let mut v: Vec<u8> = vec![]; sort_colors(&mut v); v }, Vec::<u8>::new());
}

#[test]
fn all_twos() {
    check!(r#"nums = [2, 2, 2]"#, { let mut v = vec![2, 2, 2]; sort_colors(&mut v); v }, vec![2, 2, 2]);
}

#[test]
fn long() {
    check!(r#"nums = [2, 1, 0] × 1000"#, { let mut v: Vec<u8> = [2, 1, 0].repeat(1000); sort_colors(&mut v); (v[999], v[1000], v[2000], v[2999]) }, (0, 1, 2, 2));
}
