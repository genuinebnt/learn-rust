/// Sorts readings ascending. NaN readings go last.
pub fn sort_readings(readings: &mut Vec<f64>) {
    readings.sort_by(|a, b| b.is_nan().cmp(&a.is_nan()).then(a.total_cmp(b)));
}
