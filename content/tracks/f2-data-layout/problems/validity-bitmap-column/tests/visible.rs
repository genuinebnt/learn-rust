use solution::*;

#[test]
fn bytes_per_row() {
    let (c, n) = anneal_prelude::allocs(|| {
        let mut c = Float64Column::with_capacity(100_000);
        for i in 0..100_000 {
            c.push(if i % 3 == 0 { None } else { Some(i as f64) });
        }
        c
    });
    check!(r#"with_capacity(100_000), push 100_000 rows (every 3rd null): allocations and bytes"#, (n.count <= 2, n.bytes <= 8 * 100_000 + 100_000 / 8 + 64, c.null_count()), (true, true, 33_334));
}

#[test]
fn get_rows() {
    let c = Float64Column::from_options(&[Some(1.5), None, Some(-2.0)]);
    check!(r#"[Some(1.5), None, Some(-2.0)]: get 0, 1, 2"#, (c.get(0), c.get(1), c.get(2), c.len()), (Some(1.5), None, Some(-2.0), 3));
}

#[test]
fn nan_is_a_value() {
    let mut c = Float64Column::with_capacity(2);
    c.push(Some(f64::NAN));
    c.push(None);
    check!(r#"push Some(NaN), then None"#, (c.get(0).map(f64::is_nan), c.get(1), c.null_count()), (Some(true), None, 1));
}

#[test]
fn aggregates_skip_nulls() {
    let c = Float64Column::from_options(&[Some(4.0), None, Some(2.0), None]);
    check!(r#"[Some(4.0), None, Some(2.0), None]: sum, mean"#, (c.sum(), c.mean()), (6.0, Some(3.0)));
}

#[test]
fn count_gt_skips_nulls() {
    let c = Float64Column::from_options(&[Some(-1.0), None, Some(2.0)]);
    check!(r#"[Some(-1.0), None, Some(2.0)]: count_gt(-5.0), count_gt(0.0)"#, (c.count_gt(-5.0), c.count_gt(0.0)), (2, 1));
}
