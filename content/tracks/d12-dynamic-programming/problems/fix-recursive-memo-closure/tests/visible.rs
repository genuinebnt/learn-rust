use solution::*;

#[test]
fn four_stairs() {
    check!(r#"n = 4"#, climb_ways(4), 7);
}

#[test]
fn no_stairs() {
    check!(r#"n = 0 (one way: stay put)"#, climb_ways(0), 1);
}

#[test]
fn one_stair() {
    check!(r#"n = 1"#, climb_ways(1), 1);
}

#[test]
fn three_stairs() {
    check!(r#"n = 3"#, climb_ways(3), 4);
}

#[test]
fn fifty() {
    check!(r#"n = 50"#, climb_ways(50), 10_562_230_626_642);
}
