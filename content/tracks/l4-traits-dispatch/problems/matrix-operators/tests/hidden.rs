use solution::*;

fn m(rows: &[&[i64]]) -> Matrix<i64> {
    Matrix::from_rows(rows.iter().map(|r| r.to_vec()).collect())
}

fn panics<R>(f: impl FnOnce() -> R) -> bool {
    std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).is_err()
}

#[test]
fn row_out_of_range_panics() {
    let a = m(&[&[1, 2], &[3, 4]]);
    check!(r#"a[(2, 0)] on a 2×2"#, panics(|| a[(2, 0)]), true);
}

#[test]
fn mul_shape_mismatch_panics() {
    let a = m(&[&[1, 2], &[3, 4]]);
    let b = m(&[&[1], &[2], &[3]]);
    check!(r#"2×2 times 3×1"#, panics(|| &a * &b), true);
}

#[test]
fn add_shape_mismatch_panics() {
    check!(r#"2×1 + 1×2"#, panics(|| m(&[&[1], &[2]]) + m(&[&[1, 2]])), true);
}

#[test]
fn ragged_panics() {
    check!(r#"from_rows [[1, 2], [3]]"#, panics(|| m(&[&[1, 2], &[3]])), true);
}

#[test]
fn non_square_product() {
    check!(r#"2×3 times 3×1"#, &m(&[&[1, 2, 3], &[4, 5, 6]]) * &m(&[&[1], &[0], &[-1]]), m(&[&[-2], &[-2]]));
}

#[test]
fn empty() {
    let e: Matrix<i64> = Matrix::from_rows(vec![]);
    check!(r#"from_rows(vec![])"#, (e.rows(), e.cols(), e.rows_iter().count()), (0, 0, 0));
}

#[test]
fn zero_width_rows() {
    let z: Matrix<i64> = Matrix::zeros(3, 0);
    check!(r#"zeros(3, 0).rows_iter()"#, z.rows_iter().map(|r| r.len()).collect::<Vec<_>>(), vec![0, 0, 0]);
}

#[test]
fn inner_dimension_zero() {
    check!(r#"(2×0) * (0×3)"#, &Matrix::<i64>::zeros(2, 0) * &Matrix::zeros(0, 3), Matrix::zeros(2, 3));
}

#[test]
fn floats() {
    check!(r#"&[[0.5, 1.5]] * &[[2.0], [4.0]]"#, &Matrix::from_rows(vec![vec![0.5, 1.5]]) * &Matrix::from_rows(vec![vec![2.0], vec![4.0]]), Matrix::from_rows(vec![vec![7.0]]));
}

#[test]
fn transpose_twice() {
    let a = m(&[&[1, 2, 3], &[4, 5, 6]]);
    check!(r#"transpose of transpose"#, a.transpose().transpose() == a, true);
}

#[test]
fn any_ring_type() {
    // T only needs Copy + Default + Add + Mul.
    #[derive(Debug, Clone, Copy, PartialEq, Default)]
    struct Mod7(u8);
    impl std::ops::Add for Mod7 {
        type Output = Mod7;
        fn add(self, o: Mod7) -> Mod7 {
            Mod7((self.0 + o.0) % 7)
        }
    }
    impl std::ops::Mul for Mod7 {
        type Output = Mod7;
        fn mul(self, o: Mod7) -> Mod7 {
            Mod7((self.0 * o.0) % 7)
        }
    }
    let a = Matrix::from_rows(vec![vec![Mod7(3), Mod7(4)], vec![Mod7(5), Mod7(6)]]);
    let b = Matrix::from_rows(vec![vec![Mod7(2), Mod7(0)], vec![Mod7(1), Mod7(3)]]);
    check!("[[3,4],[5,6]] * [[2,0],[1,3]] mod 7", &a * &b, Matrix::from_rows(vec![vec![Mod7(3), Mod7(5)], vec![Mod7(2), Mod7(4)]]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4416);
    for _ in 0..200 {
        let (r, k, c) = (rng.below(4) + 1, rng.below(4) + 1, rng.below(4) + 1);
        let a: Vec<Vec<i64>> = (0..r).map(|_| rng.vec(k, -5, 5)).collect();
        let b: Vec<Vec<i64>> = (0..k).map(|_| rng.vec(c, -5, 5)).collect();
        let mut want = vec![vec![0i64; c]; r];
        for i in 0..r {
            for j in 0..c {
                for x in 0..k {
                    want[i][j] += a[i][x] * b[x][j];
                }
            }
        }
        let (ma, mb) = (Matrix::from_rows(a.clone()), Matrix::from_rows(b.clone()));
        check!(format!("{a:?} * {b:?}"), &ma * &mb, Matrix::from_rows(want));
        let at: Vec<Vec<i64>> = (0..k).map(|j| (0..r).map(|i| a[i][j]).collect()).collect();
        check!(format!("transpose {a:?}"), ma.transpose(), Matrix::from_rows(at));
        let doubled: Vec<Vec<i64>> = a.iter().map(|row| row.iter().map(|x| 2 * x).collect()).collect();
        check!(format!("{a:?} + itself"), ma.clone() + ma.clone(), Matrix::from_rows(doubled));
        let (i, j) = (rng.below(r), rng.below(k));
        check!(format!("{a:?}[({i}, {j})]"), ma[(i, j)], a[i][j]);
    }
}

#[test]
fn scale_200x200() {
    let n = 200;
    let a: Matrix<i64> = Matrix::from_rows((0..n).map(|i| (0..n).map(|j| ((i * 7 + j * 3) % 11) as i64).collect()).collect());
    let mut id = Matrix::zeros(n, n);
    for i in 0..n {
        id[(i, i)] = 1;
    }
    check!("A * I == A for 200 × 200", &a * &id == a, true);
    let ones: Matrix<i64> = Matrix::from_rows(vec![vec![1; n]; n]);
    let sq = &ones * &ones;
    check!("ones * ones, every entry", sq.rows_iter().all(|r| r.iter().all(|&x| x == n as i64)), true);
}
