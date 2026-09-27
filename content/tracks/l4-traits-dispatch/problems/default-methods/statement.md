Write the `Metric` trait that `reports` uses, and implement it for `Latency` (name `"latency"`) and
`Throughput` (name `"throughput"`).

- Required: `fn name(&self) -> &str` and `fn values(&self) -> &[f64]`.
- Default `mean(&self) -> Option<f64>`: the mean of the values, `None` when there are none.
  `Throughput` overrides it to ignore idle (`0.0`) seconds.
- Default `report(&self) -> String`: `"<name>: n=<number of values> mean=<mean, 2 decimals>"`, or
  `"<name>: no data"` when `mean` is `None`.
- Default generic `count_where<F: Fn(f64) -> bool>(&self, pred: F) -> usize`.
