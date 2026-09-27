use solution::*;

#[test]
fn leetcode_symmetric() {
    check!(r#"root = [1,2,2,3,4,4,3]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(3), Some(4), Some(4), Some(3)])), true);
}

#[test]
fn leetcode_not_symmetric() {
    check!(r#"root = [1,2,2,null,3,null,3]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), None, Some(3), None, Some(3)])), false);
}

#[test]
fn empty() {
    check!(r#"root = []"#, is_symmetric(None), true);
}

#[test]
fn single() {
    check!(r#"root = [1]"#, is_symmetric(tree(&[Some(1)])), true);
}

#[test]
fn values_differ() {
    check!(r#"root = [1,2,3]"#, is_symmetric(tree(&[Some(1), Some(2), Some(3)])), false);
}
