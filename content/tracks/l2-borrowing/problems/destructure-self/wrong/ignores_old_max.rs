pub struct Stats {
    pub values: Vec<f64>,
    pub total: f64,
    pub max: f64,
}

fn update(values: &mut Vec<f64>, total: &mut f64, max: &mut f64, x: f64) {
    values.push(x);
    *total += x;
    *max = max.max(x);
}

impl Stats {
    pub fn record_all(&mut self, xs: &[f64]) {
        let Stats { values, total, max } = self;
        *max = f64::MIN;
        for &x in xs {
            update(values, total, max, x);
        }
    }
}
