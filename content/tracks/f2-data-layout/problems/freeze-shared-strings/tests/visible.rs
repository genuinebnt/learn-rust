use solution::*;

#[test]
fn series_fits_56_bytes() {
    check!(r#"size_of::<Series>() <= 56"#, std::mem::size_of::<Series>() <= 56, true);
}

#[test]
fn known_strings_one_allocation() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    let (id, n) = anneal_prelude::allocs(|| head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]));
    check!(r#"add http_requests_total{env=prod, job=api}, then the same metric with job=api, env=prod again"#, (n.count, head.name(id), head.label(id, "job")), (1, "http_requests_total", Some("api")));
}

#[test]
fn new_strings_one_each() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    let (_, n) = anneal_prelude::allocs(|| head.add_series("up", &[("env", "dev"), ("instance", "a:9090")]));
    check!(r#"then add up{env=dev, instance=a:9090}: 4 new strings"#, (n.count, head.symbols()), (5, 9));
}

#[test]
fn labels_of_is_free() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    let (labels, n) = anneal_prelude::allocs(|| head.labels_of(SeriesId(0)));
    drop(head);
    let pairs: Vec<(String, String)> = labels.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();
    check!(r#"labels_of(first series), allocations; it outlives the head"#, (n.count, pairs), (0, vec![("env".to_string(), "prod".to_string()), ("job".to_string(), "api".to_string())]));
}

#[test]
fn select_and_samples() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    head.add_series("up", &[("job", "db")]);
    head.add_series("up", &[("job", "api")]);
    head.append(SeriesId(0), 1000, 1.5);
    head.append(SeriesId(0), 2000, 2.5);
    check!(r#"three series; select job=api; append two samples to the first"#, (head.select("job", "api"), head.samples(SeriesId(0)).to_vec()), (vec![SeriesId(0), SeriesId(2)], vec![(1000, 1.5), (2000, 2.5)]));
}
