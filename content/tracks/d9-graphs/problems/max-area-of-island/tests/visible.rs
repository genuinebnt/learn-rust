use solution::*;

#[test]
fn largest_of_several() {
    check!(r#"the 8×13 grid from the classic example"#, max_area_of_island(&[vec![0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], vec![0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0], vec![0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], vec![0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0], vec![0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0], vec![0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], vec![0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0], vec![0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]]), 6);
}

#[test]
fn no_land() {
    check!(r#"grid = [[0,0,0,0,0,0,0,0]]"#, max_area_of_island(&[vec![0, 0, 0, 0, 0, 0, 0, 0]]), 0);
}

#[test]
fn single_cell() {
    check!(r#"grid = [[1]]"#, max_area_of_island(&[vec![1]]), 1);
}

#[test]
fn diagonals_dont_join() {
    check!(r#"grid = [[1,0],[0,1]]"#, max_area_of_island(&[vec![1, 0], vec![0, 1]]), 1);
}

#[test]
fn bigger_island_later() {
    check!(r#"grid = [[1,0,1],[0,0,1],[0,1,1]]"#, max_area_of_island(&[vec![1, 0, 1], vec![0, 0, 1], vec![0, 1, 1]]), 4);
}
