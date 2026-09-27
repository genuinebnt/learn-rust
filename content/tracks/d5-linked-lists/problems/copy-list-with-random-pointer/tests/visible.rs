use solution::*;

#[test]
fn example() {
    let spec = [(7, None), (13, Some(0)), (11, Some(4)), (10, Some(2)), (1, Some(0))];
    check!(r#"[(7,-),(13,0),(11,4),(10,2),(1,0)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn empty() {
    check!(r#"[]"#, to_arena(&None), vec![]);
}
