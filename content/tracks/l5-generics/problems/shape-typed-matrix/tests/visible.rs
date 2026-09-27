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
fn multiply_shapes() {
    let a = Matrix::from_rows([[1, 2, 3], [4, 5, 6]]);
    let b = Matrix::from_rows([[7, 8], [9, 10], [11, 12]]);
    check!(r#"(2x3) * (3x2)"#, (a * b).into_rows(), [[58, 64], [139, 154]]);
}

#[test]
fn result_type_is_2_by_4() {
    let a = Matrix::from_rows([[1, 0, 0], [0, 1, 0]]);
    let b: Matrix<i32, 3, 4> = Matrix::from_rows([[0; 4]; 3]);
    let p: Matrix<i32, 2, 4> = a * b;
    check!(r#"(2x3) * (3x4) has type Matrix<i32, 2, 4>"#, (Matrix::<i32, 2, 4>::ROWS, Matrix::<i32, 2, 4>::COLS, p.get(1, 3).copied()), (2, 4, Some(0)));
}

#[test]
fn transpose_moves() {
    let m = Matrix::from_rows([[Cell(1), Cell(2), Cell(3)], [Cell(4), Cell(5), Cell(6)]]);
    check!(r#"transpose a 2x3 of non-Clone Cells"#, m.transpose().into_rows(), [[Cell(1), Cell(4)], [Cell(2), Cell(5)], [Cell(3), Cell(6)]]);
}

#[test]
fn identity() {
    check!(r#"Matrix::<i32, 3, 3>::identity(1)"#, Matrix::<i32, 3, 3>::identity(1).into_rows(), [[1, 0, 0], [0, 1, 0], [0, 0, 1]]);
}

#[test]
fn get_out_of_range() {
    let m = Matrix::from_rows([[1, 2], [3, 4]]);
    check!(r#"2x2: get(0, 1), get(2, 0), get(0, 2)"#, (m.get(0, 1).copied(), m.get(2, 0), m.get(0, 2)), (Some(2), None, None));
}
