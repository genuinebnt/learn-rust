use solution::*;

#[test]
fn calibrate_empty() {
    check!(r#"no readings"#, { let mut m = Meter { readings: vec![], offset: 5, log: vec![] }; m.calibrate(); m.readings.len() }, 0);
}

#[test]
fn calibrate_twice() {
    check!(r#"readings [0], offset 3; calibrate twice"#, { let mut m = Meter { readings: vec![0], offset: 3, log: vec![] }; m.calibrate(); m.calibrate(); m.readings }, vec![6]);
}

#[test]
fn record_appends() {
    check!(r#"readings [9]; record [[1]] limit 5"#, { let mut m = Meter { readings: vec![9], offset: 0, log: vec!["x".to_string()] }; m.record(&[&[1]], 5); (m.readings, m.log.len()) }, (vec![9, 1], 2));
}

#[test]
fn record_negative_limit() {
    check!(r#"batch [-3, -1, 0], limit -2"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; m.record(&[&[-3, -1, 0]], -2) }, 2);
}

#[test]
fn nested_empty() {
    check!(r#"[[], [[]]]"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; (m.record_nested(&[Item::Many(vec![]), Item::Many(vec![Item::Many(vec![])])]), m.readings.len()) }, (0, 0));
}

#[test]
fn nested_sum_is_i64() {
    check!(r#"[i32::MAX, i32::MAX]"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; m.record_nested(&[Item::One(i32::MAX), Item::Many(vec![Item::One(i32::MAX)])]) }, 2 * i32::MAX as i64);
}

#[test]
fn nested_order() {
    check!(r#"[[3, 1], 2]"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; m.record_nested(&[Item::Many(vec![Item::One(3), Item::One(1)]), Item::One(2)]); m.readings }, vec![3, 1, 2]);
}

#[test]
fn record_count_carries_over() {
    check!(r#"batches [[11], [1], [12]], limit 10"#, { let mut m = Meter { readings: vec![], offset: 0, log: vec![] }; m.record(&[&[11], &[1], &[12]], 10); m.log }, ["batch 0: 1 above", "batch 1: 1 above", "batch 2: 2 above"].map(String::from).to_vec());
}

fn nest(depth: usize, leaf: i32) -> Item {
    let mut it = Item::One(leaf);
    for _ in 0..depth {
        it = Item::Many(vec![it]);
    }
    it
}

#[test]
fn deep_and_wide() {
    let mut m = Meter { readings: vec![], offset: 1, log: vec![] };
    let items: Vec<Item> = (0..20_000).map(|i| nest(i % 5, i as i32)).collect();
    let s = m.record_nested(&items);
    m.calibrate();
    check!("20000 items nested up to 4 deep, then calibrate", (s, m.readings.len(), m.readings[19_999]), (199_990_000, 20_000, 20_000));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6212);
    for _ in 0..300 {
        let nb = rng.below(4);
        let mut batches: Vec<Vec<i32>> = Vec::new();
        for _ in 0..nb {
            let len = rng.below(4);
            batches.push(rng.vec(len, -5, 5));
        }
        let limit = rng.int(-3, 3) as i32;
        let offset = rng.int(-2, 2) as i32;
        let refs: Vec<&[i32]> = batches.iter().map(|b| b.as_slice()).collect();
        let mut m = Meter { readings: vec![], offset, log: vec![] };
        let n = m.record(&refs, limit);
        m.calibrate();
        let mut above = 0;
        let mut log = Vec::new();
        for (i, b) in batches.iter().enumerate() {
            above += b.iter().filter(|&&x| x > limit).count();
            log.push(format!("batch {i}: {above} above"));
        }
        let readings: Vec<i32> = batches.concat().iter().map(|x| x + offset).collect();
        check!(format!("batches {batches:?}, limit {limit}, offset {offset}"), (n, m.readings, m.log), (above, readings, log));
    }
}
