use std::ops::{Add, Mul};

#[derive(Debug, Clone, PartialEq)]
pub struct Matrix<T, const R: usize, const C: usize> {
    rows: [[T; C]; R],
}

impl<T, const R: usize, const C: usize> Matrix<T, R, C> {
    pub const ROWS: usize = R;
    pub const COLS: usize = C;

    pub fn from_rows(rows: [[T; C]; R]) -> Self {
        todo!()
    }

    pub fn into_rows(self) -> [[T; C]; R] {
        todo!()
    }

    pub fn get(&self, r: usize, c: usize) -> Option<&T> {
        todo!()
    }

    /// Moves every element; needs nothing from T.
    pub fn transpose(self) -> Matrix<T, C, R> {
        todo!()
    }
}

/// Only square matrices have an identity.
impl<T: Clone + Default, const N: usize> Matrix<T, N, N> {
    pub fn identity(one: T) -> Self {
        todo!()
    }
}

impl<T: Add<Output = T>, const R: usize, const C: usize> Add for Matrix<T, R, C> {
    type Output = Matrix<T, R, C>;

    fn add(self, rhs: Self) -> Self::Output {
        todo!()
    }
}

/// (R x K) * (K x C) = (R x C). A shape mismatch is a type error.
impl<T, const R: usize, const K: usize, const C: usize> Mul<Matrix<T, K, C>> for Matrix<T, R, K>
where
    T: Clone + Default + Add<Output = T> + Mul<Output = T>,
{
    type Output = Matrix<T, R, C>;

    fn mul(self, rhs: Matrix<T, K, C>) -> Self::Output {
        todo!()
    }
}
