use solution::*;

#[test]
fn join_two_islands() {
    check!(r#"grid = [[1,0],[0,1]]"#, largest_island(&[vec![1, 0], vec![0, 1]]), 3);
}

#[test]
fn fill_the_gap() {
    check!(r#"grid = [[1,1],[1,0]]"#, largest_island(&[vec![1, 1], vec![1, 0]]), 4);
}

#[test]
fn no_water_to_flip() {
    check!(r#"grid = [[1,1],[1,1]]"#, largest_island(&[vec![1, 1], vec![1, 1]]), 4);
}

#[test]
fn only_water() {
    check!(r#"grid = [[0]]"#, largest_island(&[vec![0]]), 1);
}

#[test]
fn same_island_on_every_side() {
    check!(r#"grid = [[1,1,1],[1,0,1],[1,1,1]]"#, largest_island(&[vec![1, 1, 1], vec![1, 0, 1], vec![1, 1, 1]]), 9);
}
