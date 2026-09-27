use solution::*;

#[test]
fn all_water() {
    check!(r#"grid = ["000"]"#, num_islands(&["000"]), 0);
}

#[test]
fn diagonal_not_connected() {
    check!(r#"grid = ["10", "01"]"#, num_islands(&["10", "01"]), 2);
}

#[test]
fn big_spiral() {
    let row = "1".repeat(300);
    let grid: Vec<&str> = (0..300).map(|_| row.as_str()).collect();
    check!(r#"300×300 all land"#, num_islands(&grid), 1);
}
