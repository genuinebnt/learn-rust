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

#[test]
fn both_point_to_second() {
    let spec = [(1, Some(1)), (2, Some(1))];
    check!(r#"[(1,1),(2,1)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn equal_values() {
    let spec = [(3, None), (3, Some(0)), (3, None)];
    check!(r#"[(3,-),(3,0),(3,-)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn single_no_random() {
    let spec = [(9, None)];
    check!(r#"[(9,-)]"#, to_arena(&build(&spec)), spec.to_vec());
}
