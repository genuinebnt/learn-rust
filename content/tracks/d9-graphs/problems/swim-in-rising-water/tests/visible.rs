use solution::*;

#[test]
fn wait_for_the_corner() {
    check!(r#"grid = [[0,2],[1,3]]"#, swim_in_water(&[vec![0, 2], vec![1, 3]]), 3);
}

#[test]
fn spiral() {
    check!(r#"grid = [[0,1,2,3,4],[24,23,22,21,5],[12,13,14,15,16],[11,17,18,19,20],[10,9,8,7,6]]"#, swim_in_water(&[vec![0, 1, 2, 3, 4], vec![24, 23, 22, 21, 5], vec![12, 13, 14, 15, 16], vec![11, 17, 18, 19, 20], vec![10, 9, 8, 7, 6]]), 16);
}

#[test]
fn one_cell() {
    check!(r#"grid = [[0]]"#, swim_in_water(&[vec![0]]), 0);
}

#[test]
fn start_is_the_highest() {
    check!(r#"grid = [[3,2],[0,1]]"#, swim_in_water(&[vec![3, 2], vec![0, 1]]), 3);
}

#[test]
fn low_road_around() {
    check!(r#"grid = [[0,9,9],[1,9,9],[2,3,4]]"#, swim_in_water(&[vec![0, 9, 9], vec![1, 9, 9], vec![2, 3, 4]]), 4);
}
