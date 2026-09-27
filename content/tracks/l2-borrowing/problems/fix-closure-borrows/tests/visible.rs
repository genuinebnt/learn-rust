use solution::*;

#[test]
fn calibrate_example() {
    check!(r#"readings [1, 2], offset 10; calibrate"#, { let mut m = Meter { readings: vec![1, 2], offset: 10, log: vec![] }; m.calibrate(); m.readings }, vec![11, 12]);
}

#[test]
fn record_logs_each_batch() {
    check!(r#"batches [[5, 20], [30], []], limit 10"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; let n = m.record(&[&[5, 20], &[30], &[]], 10); (n, m.readings, m.log) }, (2, vec![5, 20, 30], ["batch 0: 1 above", "batch 1: 2 above", "batch 2: 2 above"].map(String::from).to_vec()));
}

#[test]
fn record_nested_depth_first() {
    check!(r#"[1, [2, [3]], 4]"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; let s = m.record_nested(&[Item::One(1), Item::Many(vec![Item::One(2), Item::Many(vec![Item::One(3)])]), Item::One(4)]); (s, m.readings) }, (10, vec![1, 2, 3, 4]));
}

#[test]
fn record_nothing() {
    check!(r#"no batches"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; (m.record(&[], 0), m.log.len()) }, (0, 0));
}

#[test]
fn limit_is_strict() {
    check!(r#"batch [10, 11], limit 10"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; m.record(&[&[10, 11]], 10) }, 1);
}

#[test]
fn record_then_calibrate() {
    check!(r#"offset -1; record [[3]] limit 0; calibrate"#, { let mut m = Meter { readings: vec![], offset: -1, log: vec![] }; m.record(&[&[3]], 0); m.calibrate(); m.readings }, vec![2]);
}
