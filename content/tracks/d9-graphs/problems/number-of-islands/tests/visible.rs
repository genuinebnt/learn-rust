use solution::*;

#[test]
fn three() {
    check!(r#"grid = ["11000", "11000", "00100", "00011"]"#, num_islands(&["11000", "11000", "00100", "00011"]), 3);
}

#[test]
fn one_big() {
    check!(r#"grid = ["11110", "11010", "11000", "00000"]"#, num_islands(&["11110", "11010", "11000", "00000"]), 1);
}

#[test]
fn single_land() {
    check!(r#"grid = ["1"]"#, num_islands(&["1"]), 1);
}

#[test]
fn diagonals_dont_join() {
    check!(r#"grid = ["101", "010", "101"]"#, num_islands(&["101", "010", "101"]), 5);
}

#[test]
fn ring_around_a_lake() {
    check!(r#"grid = ["111", "101", "111"]"#, num_islands(&["111", "101", "111"]), 1);
}
