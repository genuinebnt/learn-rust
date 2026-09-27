use solution::*;

#[test]
fn empty() {
    let c = Float64Column::with_capacity(0);
    check!(r#"an empty column"#, (c.len(), c.is_empty(), c.sum(), c.mean(), c.null_count(), c.count_gt(-1.0)), (0, true, 0.0, None, 0, 0));
}

#[test]
fn all_null() {
    let c = Float64Column::from_options(&[None; 70]);
    check!(r#"70 nulls (more than one bitmap word)"#, (c.null_count(), c.mean(), c.count_gt(f64::NEG_INFINITY), c.get(69)), (70, None, 0, None));
}

#[test]
fn word_boundaries() {
    let rows: Vec<Option<f64>> = (0..200).map(|i| [63, 64, 127, 128, 199].contains(&i).then_some(i as f64)).collect();
    let c = Float64Column::from_options(&rows);
    check!(r#"rows 0..200 present only at 63, 64, 127, 128, 199"#, (0..200).filter(|&i| c.get(i).is_some()).collect::<Vec<_>>(), vec![63, 64, 127, 128, 199]);
}

#[test]
fn zero_is_not_null() {
    let c = Float64Column::from_options(&[Some(0.0), Some(-0.0), None]);
    check!(r#"[Some(0.0), Some(-0.0), None]"#, (c.get(0), c.get(1).map(|v| v == 0.0), c.get(2), c.null_count()), (Some(0.0), Some(true), None, 1));
}

#[test]
fn infinities() {
    let c = Float64Column::from_options(&[Some(f64::INFINITY), None, Some(f64::NEG_INFINITY)]);
    check!(r#"[Some(inf), None, Some(-inf)]: count_gt(1e308), sum"#, (c.count_gt(1e308), c.sum().is_nan()), (1, true));
}

#[test]
fn nan_never_greater() {
    let c = Float64Column::from_options(&[Some(f64::NAN), Some(1.0)]);
    check!(r#"[Some(NaN), Some(1.0)]: count_gt(0.0)"#, c.count_gt(0.0), 1);
}

#[test]
fn million_rows_memory() {
    let (_c, n) = anneal_prelude::allocs(|| {
        let mut c = Float64Column::with_capacity(1_000_000);
        for i in 0..1_000_000 {
            c.push(if i % 10 == 0 { None } else { Some(1.0) });
        }
        c
    });
    check!(r#"with_capacity(1_000_000) + pushes: bytes requested"#, n.bytes <= 8_000_000 + 125_000 + 64, true);
}

#[test]
#[should_panic]
fn get_out_of_range_panics() {
    Float64Column::from_options(&[Some(1.0)]).get(1);
}

#[test]
fn count_gt_large() {
    let rows: Vec<Option<f64>> = (0..10_000).map(|i| (i % 2 == 0).then_some((i / 2) as f64)).collect();
    let c = Float64Column::from_options(&rows);
    check!(r#"10 000 rows i/2 for even i, null for odd; count_gt(-1.0), count_gt(2499.0)"#, (c.count_gt(-1.0), c.count_gt(2499.0)), (5000, 2500));
}

#[test]
fn random_vs_options() {
    let mut rng = anneal_prelude::Rng::new(8213);
    let specials = [0.0, -0.0, 1.5, -2.25, 1e300, -1e-300, f64::INFINITY];
    for _ in 0..200 {
        let n = rng.below(200);
        let mut rows = Vec::new();
        for _ in 0..n {
            rows.push(match rng.below(4) {
                0 => None,
                1 => Some(*rng.pick(&specials)),
                _ => Some(rng.int(-1000, 1000) as f64 / 8.0),
            });
        }
        let c = Float64Column::from_options(&rows);
        let present: Vec<f64> = rows.iter().flatten().copied().collect();
        let t = rng.int(-20, 20) as f64 / 2.0;
        let ctx = format!("{n} rows, {} null", n - present.len());
        // Compared as bits, so -0.0 must come back as -0.0.
        let got: Vec<Option<u64>> = (0..n).map(|i| c.get(i).map(f64::to_bits)).collect();
        check!(format!("{ctx}: get(i) for every row, as bits"), got, rows.iter().map(|r| r.map(f64::to_bits)).collect::<Vec<_>>());
        check!(format!("{ctx}: len, null_count"), (c.len(), c.null_count()), (n, n - present.len()));
        check!(format!("{ctx}: sum"), c.sum(), present.iter().fold(0.0, |acc, v| acc + v));
        check!(format!("{ctx}: count_gt({t})"), c.count_gt(t), present.iter().filter(|&&v| v > t).count());
    }
}
