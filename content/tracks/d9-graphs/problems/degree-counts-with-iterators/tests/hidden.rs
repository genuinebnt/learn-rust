use solution::*;

#[test]
fn cycle() {
    check!(r#"n = 2, edges = [(0, 1), (1, 0)]"#, sources(2, &[(0, 1), (1, 0)]), Vec::<usize>::new());
}

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0, 0)]"#, degrees(1, &[(0, 0)]), vec![(1, 1)]);
}
