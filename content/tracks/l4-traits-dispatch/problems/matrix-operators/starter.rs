use std::ops::{Add, Index, IndexMut, Mul};

/// A rows × cols matrix, stored row by row in one Vec.
#[derive(Debug, Clone, PartialEq)]
pub struct Matrix<T> {
    rows: usize,
    cols: usize,
    data: Vec<T>,
}

impl<T: Copy + Default> Matrix<T> {
    /// Every entry `T::default()`.
    pub fn zeros(rows: usize, cols: usize) -> Self {
        todo!()
    }

    /// Panics if the rows have different lengths. No rows gives a 0 × 0 matrix.
    pub fn from_rows(rows: Vec<Vec<T>>) -> Self {
        todo!()
    }

    pub fn transpose(&self) -> Self {
        todo!()
    }
}

impl<T> Matrix<T> {
    pub fn rows(&self) -> usize {
        todo!()
    }

    pub fn cols(&self) -> usize {
        todo!()
    }

    /// Row `r` as a slice. Panics if `r` is out of range.
    pub fn row(&self, r: usize) -> &[T] {
        todo!()
    }

    /// Every row, top to bottom.
    pub fn rows_iter(&self) -> impl Iterator<Item = &[T]> {
        // TODO: replace the placeholder.
        std::iter::from_fn(|| todo!())
    }
}

/// m[(r, c)]. Panics if `r` or `c` is out of range.
impl<T> Index<(usize, usize)> for Matrix<T> {
    type Output = T;

    fn index(&self, (r, c): (usize, usize)) -> &T {
        todo!()
    }
}

impl<T> IndexMut<(usize, usize)> for Matrix<T> {
    fn index_mut(&mut self, (r, c): (usize, usize)) -> &mut T {
        todo!()
    }
}

/// Element-wise sum. Panics if the shapes differ.
impl<T: Copy + Add<Output = T>> Add for Matrix<T> {
    type Output = Matrix<T>;

    fn add(self, rhs: Matrix<T>) -> Matrix<T> {
        todo!()
    }
}

/// Matrix product. Panics unless `self.cols() == rhs.rows()`.
impl<'a, T: Copy + Default + Add<Output = T> + Mul<Output = T>> Mul for &'a Matrix<T> {
    type Output = Matrix<T>;

    fn mul(self, rhs: &'a Matrix<T>) -> Matrix<T> {
        todo!()
    }
}
