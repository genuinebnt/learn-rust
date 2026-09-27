pub struct Latency {
    pub samples: Vec<f64>,
}

/// Requests per second, one value per second. Idle seconds (0.0) don't count toward the mean.
pub struct Throughput {
    pub rps: Vec<f64>,
}

pub trait Metric {
    fn name(&self) -> &str;
    fn values(&self) -> &[f64];

    /// The mean of the values, or None when there are none.
    fn mean(&self) -> Option<f64> {
        let v = self.values();
        if v.is_empty() {
            None
        } else {
            Some(v.iter().sum::<f64>() / v.len() as f64)
        }
    }

    /// "<name>: n=<number of values> mean=<mean, 2 decimals>", or "<name>: no data" when `mean` is None.
    fn report(&self) -> String {
        match self.mean() {
            Some(m) => format!("{}: n={} mean={:.2}", self.name(), self.values().len(), m),
            None => format!("{}: no data", self.name()),
        }
    }

    /// How many values `pred` accepts.
    fn count_where<F: Fn(f64) -> bool>(&self, pred: F) -> usize
    where
        Self: Sized,
    {
        self.values().iter().filter(|&&v| pred(v)).count()
    }
}

impl Metric for Latency {
    fn name(&self) -> &str {
        "latency"
    }

    fn values(&self) -> &[f64] {
        &self.samples
    }
}

impl Metric for Throughput {
    fn name(&self) -> &str {
        "throughput"
    }

    fn values(&self) -> &[f64] {
        &self.rps
    }

}

/// Every metric's report, in order.
pub fn reports(metrics: &[Box<dyn Metric>]) -> Vec<String> {
    metrics.iter().map(|m| m.report()).collect()
}
