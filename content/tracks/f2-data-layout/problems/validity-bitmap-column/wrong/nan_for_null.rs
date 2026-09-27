/// Nulls as NaN, no bitmap: 8 bytes a row.
pub struct Float64Column {
    values: Vec<f64>,
}

impl Float64Column {
    pub fn with_capacity(rows: usize) -> Float64Column {
        Float64Column { values: Vec::with_capacity(rows) }
    }

    pub fn from_options(rows: &[Option<f64>]) -> Float64Column {
        let mut c = Float64Column::with_capacity(rows.len());
        for &r in rows {
            c.push(r);
        }
        c
    }

    pub fn push(&mut self, value: Option<f64>) {
        self.values.push(value.unwrap_or(f64::NAN));
    }

    pub fn len(&self) -> usize {
        self.values.len()
    }

    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }

    pub fn get(&self, i: usize) -> Option<f64> {
        let v = self.values[i];
        (!v.is_nan()).then_some(v)
    }

    pub fn null_count(&self) -> usize {
        self.values.iter().filter(|v| v.is_nan()).count()
    }

    pub fn sum(&self) -> f64 {
        self.values.iter().filter(|v| !v.is_nan()).fold(0.0, |acc, v| acc + v)
    }

    pub fn mean(&self) -> Option<f64> {
        let n = self.len() - self.null_count();
        (n > 0).then(|| self.sum() / n as f64)
    }

    pub fn count_gt(&self, t: f64) -> usize {
        self.values.iter().filter(|&&v| v > t).count()
    }
}
