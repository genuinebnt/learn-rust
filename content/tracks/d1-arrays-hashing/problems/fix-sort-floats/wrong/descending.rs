/// Sorts readings ascending. NaN readings go last.
pub fn sort_readings(readings: &mut Vec<f64>) {
    readings.sort_by(|a, b| b.total_cmp(a));
}
