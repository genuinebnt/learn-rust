use solution::*;

#[test]
fn fills_the_region() {
    check!(r#"image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1, color = 2"#, flood_fill(vec![vec![1, 1, 1], vec![1, 1, 0], vec![1, 0, 1]], 1, 1, 2), vec![vec![2, 2, 2], vec![2, 2, 0], vec![2, 0, 1]]);
}

#[test]
fn already_that_colour() {
    check!(r#"image = [[0,0,0],[0,0,0]], sr = 0, sc = 0, color = 0"#, flood_fill(vec![vec![0, 0, 0], vec![0, 0, 0]], 0, 0, 0), vec![vec![0, 0, 0], vec![0, 0, 0]]);
}

#[test]
fn single_pixel() {
    check!(r#"image = [[5]], sr = 0, sc = 0, color = 9"#, flood_fill(vec![vec![5]], 0, 0, 9), vec![vec![9]]);
}

#[test]
fn diagonals_are_not_neighbours() {
    check!(r#"image = [[1,0],[0,1]], sr = 0, sc = 0, color = 3"#, flood_fill(vec![vec![1, 0], vec![0, 1]], 0, 0, 3), vec![vec![3, 0], vec![0, 1]]);
}

#[test]
fn only_the_starting_colour_spreads() {
    check!(r#"image = [[1,2,1],[1,2,1]], sr = 0, sc = 0, color = 2"#, flood_fill(vec![vec![1, 2, 1], vec![1, 2, 1]], 0, 0, 2), vec![vec![2, 2, 1], vec![2, 2, 1]]);
}
