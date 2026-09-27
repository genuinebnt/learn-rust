pub struct Latency {
    pub samples: Vec<f64>,
}

/// Requests per second, one value per second. Idle seconds (0.0) don't count toward the mean.
pub struct Throughput {
    pub rps: Vec<f64>,
}

// TODO: the Metric trait and its impls for Latency and Throughput.

/// Every metric's report, in order.
pub fn reports(metrics: &[Box<dyn Metric>]) -> Vec<String> {
    metrics.iter().map(|m| m.report()).collect()
}
