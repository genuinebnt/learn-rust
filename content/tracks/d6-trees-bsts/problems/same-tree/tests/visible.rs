use solution::*;

#[test]
fn leetcode_same() {
    check!(r#"p = [1,2,3], q = [1,2,3]"#, is_same_tree(tree(&[Some(1), Some(2), Some(3)]), tree(&[Some(1), Some(2), Some(3)])), true);
}

#[test]
fn leetcode_shape_differs() {
    check!(r#"p = [1,2], q = [1,null,2]"#, is_same_tree(tree(&[Some(1), Some(2)]), tree(&[Some(1), None, Some(2)])), false);
}

#[test]
fn leetcode_values_differ() {
    check!(r#"p = [1,2,1], q = [1,1,2]"#, is_same_tree(tree(&[Some(1), Some(2), Some(1)]), tree(&[Some(1), Some(1), Some(2)])), false);
}

#[test]
fn both_empty() {
    check!(r#"p = [], q = []"#, is_same_tree(None, None), true);
}

#[test]
fn one_empty() {
    check!(r#"p = [], q = [1]"#, is_same_tree(None, tree(&[Some(1)])), false);
}
