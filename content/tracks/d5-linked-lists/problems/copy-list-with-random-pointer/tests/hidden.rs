use solution::*;

#[test]
fn self_random() {
    let spec = [(1, Some(0)), (2, Some(1))];
    check!(r#"[(1,0),(2,1)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn equal_values() {
    let spec = [(5, Some(2)), (5, None), (5, Some(0))];
    check!(r#"three nodes with value 5"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn long() {
    let spec: Vec<(i32, Option<usize>)> = (0..2_000).map(|i| (i as i32, Some(1_999 - i))).collect();
    check!(r#"2000 nodes, random = reversed index"#, to_arena(&build(&spec)) == spec, true);
}
