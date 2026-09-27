use solution::*;

/// Neither Clone nor Copy nor Default.
#[allow(dead_code)]
#[derive(Debug, PartialEq)]
struct Cell(u32);

/// A number that is Clone but not Copy.
#[allow(dead_code)]
#[derive(Debug, Clone, PartialEq, Default)]
struct Big(i128);

impl std::ops::Add for Big {
    type Output = Big;
    fn add(self, o: Big) -> Big {
        Big(self.0 + o.0)
    }
}

impl std::ops::Mul for Big {
    type Output = Big;
    fn mul(self, o: Big) -> Big {
        Big(self.0 * o.0)
    }
}

#[test]
fn add() {
    check!(r#"[[1, 2]] + [[10, 20]]"#, (Matrix::from_rows([[1, 2]]) + Matrix::from_rows([[10, 20]])).into_rows(), [[11, 22]]);
}

#[test]
fn identity_is_neutral() {
    let a = Matrix::from_rows([[1.5, -2.0], [0.25, 4.0]]);
    check!(r#"I * A == A for a 2x2 of f64"#, (Matrix::<f64, 2, 2>::identity(1.0) * a.clone()) == a, true);
}

#[test]
fn big_numbers() {
    let a = Matrix::from_rows([[Big(1), Big(2)], [Big(3), Big(4)]]);
    let b = Matrix::from_rows([[Big(5), Big(6)], [Big(7), Big(8)]]);
    check!(r#"Big (non-Copy) 2x2 product"#, (a * b).into_rows(), [[Big(19), Big(22)], [Big(43), Big(50)]]);
}

#[test]
fn row_times_column() {
    check!(r#"(1x3) * (3x1)"#, (Matrix::from_rows([[1, 2, 3]]) * Matrix::from_rows([[4], [5], [6]])).into_rows(), [[32]]);
}

#[test]
fn column_times_row() {
    check!(r#"(2x1) * (1x2)"#, (Matrix::from_rows([[1], [2]]) * Matrix::from_rows([[3, 4]])).into_rows(), [[3, 4], [6, 8]]);
}

#[test]
fn transpose_twice() {
    let m = Matrix::from_rows([["a", "b", "c"], ["d", "e", "f"]]);
    check!(r#"transpose twice gives the original"#, m.clone().transpose().transpose() == m, true);
}

#[test]
fn empty_shapes() {
    let m: Matrix<u8, 0, 3> = Matrix::from_rows([]);
    check!(r#"a 0x3 matrix transposed is 3x0"#, (Matrix::<u8, 3, 0>::ROWS, m.transpose().into_rows().len()), (3, 3));
}

#[test]
fn zero_inner_dimension() {
    let a: Matrix<i32, 2, 0> = Matrix::from_rows([[], []]);
    let b: Matrix<i32, 0, 2> = Matrix::from_rows([]);
    check!(r#"(2x0) * (0x2) is all zeros"#, (a * b).into_rows(), [[0, 0], [0, 0]]);
}

#[test]
fn identity_of_big() {
    check!(r#"Matrix::<Big, 2, 2>::identity(Big(1))"#, Matrix::<Big, 2, 2>::identity(Big(1)).into_rows(), [[Big(1), Big(0)], [Big(0), Big(1)]]);
}

#[test]
fn wrapping() {
    use std::num::Wrapping;
    let a = Matrix::from_rows([[Wrapping(16u8), Wrapping(16u8)]]);
    let b = Matrix::from_rows([[Wrapping(8u8)], [Wrapping(8u8)]]);
    check!(r#"Wrapping<u8> product overflows per cell"#, (a * b).into_rows(), [[Wrapping(0u8)]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4514);
    for _ in 0..300 {
        let mut a = [[0i64; 3]; 2];
        let mut b = [[0i64; 4]; 3];
        for row in a.iter_mut() {
            for x in row.iter_mut() {
                *x = rng.int(-9, 9);
            }
        }
        for row in b.iter_mut() {
            for x in row.iter_mut() {
                *x = rng.int(-9, 9);
            }
        }
        let mut want = [[0i64; 4]; 2];
        for i in 0..2 {
            for j in 0..4 {
                for k in 0..3 {
                    want[i][j] += a[i][k] * b[k][j];
                }
            }
        }
        let mut want_t = [[0i64; 2]; 3];
        for i in 0..2 {
            for j in 0..3 {
                want_t[j][i] = a[i][j];
            }
        }
        let ma = Matrix::from_rows(a);
        check!(format!("a = {a:?}, b = {b:?}"), ((ma.clone() * Matrix::from_rows(b)).into_rows(), ma.clone().transpose().into_rows(), (ma.clone() + ma).into_rows()),
               (want, want_t, a.map(|row| row.map(|x| 2 * x))));
    }
}
