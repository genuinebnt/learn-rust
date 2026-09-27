use solution::*;

fn m(rows: &[&[i64]]) -> Matrix<i64> {
    Matrix::from_rows(rows.iter().map(|r| r.to_vec()).collect())
}

fn panics<R>(f: impl FnOnce() -> R) -> bool {
    std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).is_err()
}

#[test]
fn add() {
    check!(r#"[[1,2],[3,4]] + [[5,6],[7,8]]"#, m(&[&[1, 2], &[3, 4]]) + m(&[&[5, 6], &[7, 8]]), m(&[&[6, 8], &[10, 12]]));
}

#[test]
fn product() {
    check!(r#"&[[1,2],[3,4]] * &[[5,6],[7,8]]"#, &m(&[&[1, 2], &[3, 4]]) * &m(&[&[5, 6], &[7, 8]]), m(&[&[19, 22], &[43, 50]]));
}

#[test]
fn transpose_non_square() {
    check!(r#"transpose [[1,2,3],[4,5,6]]"#, m(&[&[1, 2, 3], &[4, 5, 6]]).transpose(), m(&[&[1, 4], &[2, 5], &[3, 6]]));
}

#[test]
fn index_mut_then_row() {
    let mut a = m(&[&[1, 2], &[3, 4]]);
    a[(1, 0)] = 9;
    check!(r#"a[(1, 0)] = 9; a.row(1)"#, (a.row(1).to_vec(), a[(0, 1)]), (vec![9, 4], 2));
}

#[test]
fn rows_iter_sums() {
    check!(r#"row sums of [[1,2],[3,4]]"#, m(&[&[1, 2], &[3, 4]]).rows_iter().map(|r| r.iter().sum::<i64>()).collect::<Vec<_>>(), vec![3, 7]);
}

#[test]
fn column_out_of_range_panics() {
    let a = m(&[&[1, 2], &[3, 4]]);
    check!(r#"a[(0, 2)] on a 2×2"#, panics(|| a[(0, 2)]), true);
}
