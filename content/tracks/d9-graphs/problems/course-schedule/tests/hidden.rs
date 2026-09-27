use solution::*;

#[test]
fn self_loop() {
    check!(r#"n = 1, prereqs = [(0, 0)]"#, can_finish(1, &[(0, 0)]), false);
}

#[test]
fn cycle_off_to_the_side() {
    check!(r#"n = 4, prereqs = [(0, 1), (2, 3), (3, 2)]"#, can_finish(4, &[(0, 1), (2, 3), (3, 2)]), false);
}

#[test]
fn long_chain() {
    let chain: Vec<(usize, usize)> = (0..99_999).map(|i| (i, i + 1)).collect();
    check!(r#"n = 10⁵, chain 0 → 1 → … → 99999"#, can_finish(100_000, &chain), true);
}
