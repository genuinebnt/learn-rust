use solution::*;

#[test]
fn latency_report() {
    check!(r#"Latency { samples: [10, 20, 30] }.report()"#, Latency { samples: vec![10.0, 20.0, 30.0] }.report(), "latency: n=3 mean=20.00");
}

#[test]
fn no_data() {
    check!(r#"Latency { samples: [] }.report()"#, Latency { samples: vec![] }.report(), "latency: no data");
}

#[test]
fn report_uses_the_override() {
    check!(r#"Throughput { rps: [0, 100, 0, 200] }.report()"#, Throughput { rps: vec![0.0, 100.0, 0.0, 200.0] }.report(), "throughput: n=4 mean=150.00");
}

#[test]
fn reports_through_dyn() {
    let ms: Vec<Box<dyn Metric>> = vec![Box::new(Latency { samples: vec![5.0] }), Box::new(Throughput { rps: vec![0.0] })];
    check!(r#"reports([Latency [5], Throughput [0]])"#, reports(&ms), vec!["latency: n=1 mean=5.00", "throughput: no data"]);
}

#[test]
fn count_where_closure() {
    let limit = 100.0;
    check!(r#"Latency [120, 80, 300], count values > limit (100)"#, Latency { samples: vec![120.0, 80.0, 300.0] }.count_where(|v| v > limit), 2);
}

#[test]
fn defaults_for_a_new_type() {
    struct Temps(Vec<f64>);
    impl Metric for Temps {
        fn name(&self) -> &str {
            "temps"
        }
        fn values(&self) -> &[f64] {
            &self.0
        }
    }
    check!("Temps([21.5, 22.5, 23.0, 25.0]).report()", Temps(vec![21.5, 22.5, 23.0, 25.0]).report(), "temps: n=4 mean=23.00");
}
