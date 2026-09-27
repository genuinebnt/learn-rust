use solution::*;

#[test]
fn one_island() {
    check!(r#"grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]"#, island_perimeter(&[vec![0, 1, 0, 0], vec![1, 1, 1, 0], vec![0, 1, 0, 0], vec![1, 1, 0, 0]]), 16);
}

#[test]
fn one_cell() {
    check!(r#"grid = [[1]]"#, island_perimeter(&[vec![1]]), 4);
}

#[test]
fn cell_beside_water() {
    check!(r#"grid = [[1,0]]"#, island_perimeter(&[vec![1, 0]]), 4);
}

#[test]
fn no_land() {
    check!(r#"grid = [[0,0],[0,0]]"#, island_perimeter(&[vec![0, 0], vec![0, 0]]), 0);
}

#[test]
fn square_block() {
    check!(r#"grid = [[1,1],[1,1]]"#, island_perimeter(&[vec![1, 1], vec![1, 1]]), 8);
}
