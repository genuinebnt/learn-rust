use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [-1, 0, 1, 2, -1, -4]"#, three_sum(&[-1, 0, 1, 2, -1, -4]), vec![[-1, -1, 2], [-1, 0, 1]]);
}

#[test]
fn none() {
    check!(r#"nums = [0, 1, 1]"#, three_sum(&[0, 1, 1]), Vec::<[i32; 3]>::new());
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0, 0, 0]"#, three_sum(&[0, 0, 0, 0]), vec![[0, 0, 0]]);
}

#[test]
fn three_zeros() {
    check!(r#"nums = [0, 0, 0]"#, three_sum(&[0, 0, 0]), vec![[0, 0, 0]]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, three_sum(&[]), Vec::<[i32; 3]>::new());
}

#[test]
fn sorted_output() {
    check!(r#"nums = [2, -2, 0, 1, -1]"#, three_sum(&[2, -2, 0, 1, -1]), vec![[-2, 0, 2], [-1, 0, 1]]);
}
