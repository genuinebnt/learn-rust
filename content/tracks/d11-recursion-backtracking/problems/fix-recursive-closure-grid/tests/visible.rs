use solution::*;

#[test]
fn two_islands() {
    check!(r#"grid = [[1, 1, 0], [0, 1, 0], [0, 0, 1]]"#, island_sizes(vec![vec![1, 1, 0], vec![0, 1, 0], vec![0, 0, 1]]), vec![3, 1]);
}

#[test]
fn no_land() {
    check!(r#"grid = [[0, 0], [0, 0]]"#, island_sizes(vec![vec![0, 0], vec![0, 0]]), Vec::<usize>::new());
}

#[test]
fn empty_grid() {
    check!(r#"grid = []"#, island_sizes(Vec::new()), Vec::<usize>::new());
}

#[test]
fn diagonals_do_not_join() {
    check!(r#"grid = [[1, 0], [0, 1]]"#, island_sizes(vec![vec![1, 0], vec![0, 1]]), vec![1, 1]);
}

#[test]
fn order_of_first_cells() {
    check!(r#"grid = [[0, 0, 1], [1, 0, 0], [1, 0, 0]]"#, island_sizes(vec![vec![0, 0, 1], vec![1, 0, 0], vec![1, 0, 0]]), vec![1, 2]);
}
