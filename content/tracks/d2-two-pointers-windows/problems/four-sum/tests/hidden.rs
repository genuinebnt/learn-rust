use solution::*;

#[test]
fn overflow() {
    check!(r#"nums = [1e9 × 4], target = 4e9"#, four_sum(&[1_000_000_000; 4], 4_000_000_000), vec![[1_000_000_000; 4]]);
}

#[test]
fn too_short() {
    check!(r#"nums = [1, 2, 3], target = 6"#, four_sum(&[1, 2, 3], 6), Vec::<[i32; 4]>::new());
}
