pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
    matrix.iter().any(|row| row.first().is_some_and(|&x| x <= target) && row.last().is_some_and(|&x| x >= target) && row.binary_search(&target).is_ok())
}
