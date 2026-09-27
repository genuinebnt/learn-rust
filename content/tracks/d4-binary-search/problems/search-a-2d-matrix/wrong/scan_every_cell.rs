pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
    matrix.iter().flatten().any(|&x| x == target)
}
