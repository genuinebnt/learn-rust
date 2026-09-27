use solution::*;

#[test]
fn empty_mean() {
    check!(r#"Latency { samples: [] }.mean()"#, Latency { samples: vec![] }.mean(), None);
}

#[test]
fn throughput_mean() {
    check!(r#"Throughput { rps: [0, 100, 0, 200] }.mean()"#, Throughput { rps: vec![0.0, 100.0, 0.0, 200.0] }.mean(), Some(150.0));
}

#[test]
fn throughput_all_idle() {
    check!(r#"Throughput { rps: [0, 0] }.report()"#, Throughput { rps: vec![0.0, 0.0] }.report(), "throughput: no data");
}

#[test]
fn throughput_empty() {
    check!(r#"Throughput { rps: [] }.mean()"#, Throughput { rps: vec![] }.mean(), None);
}

#[test]
fn rounding() {
    check!(r#"Latency { samples: [1, 2, 2] }.report()"#, Latency { samples: vec![1.0, 2.0, 2.0] }.report(), "latency: n=3 mean=1.67");
}

#[test]
fn negatives() {
    check!(r#"Latency { samples: [-4, 1] }.mean()"#, Latency { samples: vec![-4.0, 1.0] }.mean(), Some(-1.5));
}

#[test]
fn count_where_counts_idle() {
    check!(r#"Throughput [0, 5, 0], count zeros"#, Throughput { rps: vec![0.0, 5.0, 0.0] }.count_where(|v| v == 0.0), 2);
}

#[test]
fn count_where_none() {
    check!(r#"Latency [], anything"#, Latency { samples: vec![] }.count_where(|_| true), 0);
}

#[test]
fn reports_empty() {
    check!(r#"reports(&[])"#, reports(&[]), Vec::<String>::new());
}

#[test]
fn override_seen_through_dyn() {
    // An override of `mean` must change what the default `report` prints, even through `dyn Metric`.
    struct Median(Vec<f64>);
    impl Metric for Median {
        fn name(&self) -> &str {
            "median"
        }
        fn values(&self) -> &[f64] {
            &self.0
        }
        fn mean(&self) -> Option<f64> {
            let mut v = self.0.clone();
            v.sort_by(f64::total_cmp);
            v.get(v.len() / 2).copied()
        }
    }
    let ms: Vec<Box<dyn Metric>> = vec![Box::new(Median(vec![1.0, 100.0, 3.0]))];
    check!("reports([Median [1, 100, 3]])", reports(&ms), vec!["median: n=3 mean=3.00".to_string()]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4402);
    for _ in 0..300 {
        let n = rng.below(6);
        let v: Vec<f64> = rng.vec::<i64>(n, 0, 3).into_iter().map(|x| x as f64 * 10.0).collect();
        let busy: Vec<f64> = v.iter().copied().filter(|&x| x != 0.0).collect();
        let want = if busy.is_empty() {
            "throughput: no data".to_string()
        } else {
            format!("throughput: n={} mean={:.2}", n, busy.iter().sum::<f64>() / busy.len() as f64)
        };
        check!(format!("Throughput {v:?}"), Throughput { rps: v.clone() }.report(), want);
        let want = if n == 0 { "latency: no data".to_string() } else { format!("latency: n={} mean={:.2}", n, v.iter().sum::<f64>() / n as f64) };
        check!(format!("Latency {v:?}"), Latency { samples: v.clone() }.report(), want);
    }
}
