use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [1, 0, -1, 0, -2, 2], target = 0"#, four_sum(&[1, 0, -1, 0, -2, 2], 0), vec![[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]);
}

#[test]
fn all_twos() {
    check!(r#"nums = [2, 2, 2, 2, 2], target = 8"#, four_sum(&[2, 2, 2, 2, 2], 8), vec![[2, 2, 2, 2]]);
}

#[test]
fn too_short() {
    check!(r#"nums = [1, 2, 3], target = 6"#, four_sum(&[1, 2, 3], 6), Vec::<[i32; 4]>::new());
}

#[test]
fn empty() {
    check!(r#"nums = [], target = 0"#, four_sum(&[], 0), Vec::<[i32; 4]>::new());
}

#[test]
fn sorted_output() {
    check!(r#"nums = [4, -1, 3, 0], target = 6"#, four_sum(&[4, -1, 3, 0], 6), vec![[-1, 0, 3, 4]]);
}
