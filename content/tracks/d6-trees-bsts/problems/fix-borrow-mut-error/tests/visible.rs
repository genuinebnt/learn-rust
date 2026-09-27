use solution::*;

#[test]
fn three() {
    let root = tree(&[Some(1), Some(2), Some(3)]);
    add_path_sums(&root);
    check!(r#"root = [1,2,3]"#, level_order_values(&root), vec![Some(1), Some(3), Some(4)]);
}

#[test]
fn empty() {
    let root = tree(&[]);
    add_path_sums(&root);
    check!(r#"root = []"#, level_order_values(&root), Vec::<Option<i32>>::new());
}

#[test]
fn single() {
    let root = tree(&[Some(5)]);
    add_path_sums(&root);
    check!(r#"root = [5]"#, level_order_values(&root), vec![Some(5)]);
}

#[test]
fn sums_go_all_the_way_down() {
    let root = tree(&[Some(1), Some(2), None, Some(3)]);
    add_path_sums(&root);
    check!(r#"root = [1,2,null,3]"#, level_order_values(&root), vec![Some(1), Some(3), None, Some(6)]);
}

#[test]
fn negatives() {
    let root = tree(&[Some(1), Some(-1), Some(-2), None, Some(4)]);
    add_path_sums(&root);
    check!(r#"root = [1,-1,-2,null,4]"#, level_order_values(&root), vec![Some(1), Some(0), Some(-1), None, Some(4)]);
}
