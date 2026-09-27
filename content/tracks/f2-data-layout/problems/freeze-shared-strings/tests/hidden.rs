use solution::*;

#[test]
fn labels_of_twice() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    let ((a, b), n) = anneal_prelude::allocs(|| (head.labels_of(SeriesId(0)), head.labels_of(SeriesId(0))));
    check!(r#"labels_of the same series twice: allocations, equal, len"#, (n.count, a == b, a.len()), (0, true, 2));
}

#[test]
fn no_labels() {
    let mut head = Head::with_capacity(4, 4);
    let a = head.add_series("up", &[]);
    let (b, n) = anneal_prelude::allocs(|| head.add_series("up", &[]));
    check!(r#"add_series("up", []) twice"#, (head.label(a, "job"), head.labels_of(b).len(), head.name(b), n.count <= 1), (None, 0, "up", true));
}

#[test]
fn value_equal_to_a_name() {
    let mut head = Head::with_capacity(4, 4);
    head.add_series("up", &[("job", "job")]);
    check!(r#"a value that is also a label name is one symbol: up{job=job}"#, head.symbols(), 2);
}

#[test]
fn thousand_series_known_strings() {
    let mut head = Head::with_capacity(2000, 64);
    head.add_series("rpc_seconds", &[("method", "get"), ("service", "users"), ("zone", "eu")]);
    head.add_series("rpc_seconds", &[("method", "put"), ("service", "orders"), ("zone", "us")]);
    let (_, n) = anneal_prelude::allocs(|| {
        for i in 0..1000 {
            let m = if i % 2 == 0 { "get" } else { "put" };
            head.add_series("rpc_seconds", &[("method", m), ("service", "users"), ("zone", "us")]);
        }
    });
    check!(r#"1000 series over already-seen strings: allocations"#, n.count, 1000);
}

#[test]
fn append_grows_amortised() {
    let mut head = Head::with_capacity(1, 4);
    let id = head.add_series("up", &[]);
    let (_, n) = anneal_prelude::allocs(|| {
        for t in 0..1000 {
            head.append(id, t, 0.5);
        }
    });
    check!(r#"1000 appends to one series: allocations at most 12"#, (n.count <= 12, head.samples(id).len(), head.samples(id)[999]), (true, 1000, (999, 0.5)));
}

#[test]
fn label_missing_key() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    check!(r#"label of a key between, before and after the stored ones"#, (head.label(SeriesId(0), "a"), head.label(SeriesId(0), "instance"), head.label(SeriesId(0), "zz")), (None, None, None));
}

#[test]
fn select_nothing() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    check!(r#"select on a missing value and on an empty head"#, (head.select("job", "db"), Head::with_capacity(0, 0).select("job", "api")), (vec![], vec![]));
}

#[test]
fn unicode_labels() {
    let mut head = Head::with_capacity(4, 4);
    head.add_series("up", &[("city", "Zürich")]);
    check!(r#"up{city=Zürich}: label and symbols"#, (head.label(SeriesId(0), "city"), head.symbols()), (Some("Zürich"), 3));
}

#[test]
fn labels_are_send_and_sync() {
    let mut head = Head::with_capacity(16, 64);
    head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);
    let labels = head.labels_of(SeriesId(0));
    check!(r#"Labels can go to another thread"#, std::thread::spawn(move || labels.len()).join().unwrap(), 2);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8205);
    let names = ["up", "http_requests_total", "cpu_seconds_total"];
    let keys = ["env", "instance", "job"];
    let values = ["prod", "dev", "a:9090", "b:9090", "api", "db", "env"];
    for _ in 0..100 {
        let mut head = Head::with_capacity(4, 4);
        let mut model: Vec<(String, Vec<(String, String)>)> = Vec::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(10) {
            let name = *rng.pick(&names);
            let mut labels: Vec<(&str, &str)> = Vec::new();
            for &k in &keys {
                if rng.bool() {
                    labels.push((k, *rng.pick(&values)));
                }
            }
            log.push(format!("{name}{labels:?}"));
            let id = head.add_series(name, &labels);
            check!(format!("add_series: {}", log.join(", ")), id, SeriesId(model.len() as u32));
            model.push((name.to_string(), labels.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect()));
        }
        let ctx = log.join(", ");
        for (i, (name, labels)) in model.iter().enumerate() {
            let id = SeriesId(i as u32);
            let got: Vec<(String, String)> = head.labels_of(id).iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();
            check!(format!("{ctx}: name and labels_of {id:?}"), (head.name(id).to_string(), got), (name.clone(), labels.clone()));
            let k = *rng.pick(&keys);
            let want = labels.iter().find(|(lk, _)| lk == k).map(|(_, v)| v.as_str());
            check!(format!("{ctx}: label({id:?}, {k:?})"), head.label(id, k), want);
        }
        let (k, v) = (*rng.pick(&keys), *rng.pick(&values));
        let want: Vec<SeriesId> = (0..model.len()).filter(|&i| model[i].1.iter().any(|(lk, lv)| lk == k && lv == v)).map(|i| SeriesId(i as u32)).collect();
        check!(format!("{ctx}: select({k:?}, {v:?})"), head.select(k, v), want);
        let mut distinct = std::collections::HashSet::new();
        for (name, labels) in &model {
            distinct.insert(name.clone());
            for (lk, lv) in labels {
                distinct.insert(lk.clone());
                distinct.insert(lv.clone());
            }
        }
        check!(format!("{ctx}: symbols()"), head.symbols(), distinct.len());
    }
}
