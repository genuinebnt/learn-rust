pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
    let rows = matrix.partition_point(|row| row.first().is_some_and(|&x| x < target));
    rows > 0 && matrix[rows - 1].binary_search(&target).is_ok()
}
