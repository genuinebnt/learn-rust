use solution::*;

#[test]
fn empty_key() {
    check!(r#"[("", 1), ("", 2), ("a", 3)]"#, group_runs(vec![("".to_string(), 1), ("".to_string(), 2), ("a".to_string(), 3)]), (vec![("".to_string(), vec![1, 2]), ("a".to_string(), vec![3])], 3));
}

#[test]
fn empty_key_after_other() {
    check!(r#"[("a", 1), ("", 2)]"#, group_runs(vec![("a".to_string(), 1), ("".to_string(), 2)]), (vec![("a".to_string(), vec![1]), ("".to_string(), vec![2])], 2));
}

#[test]
fn alternating() {
    check!(r#"[("a", 1), ("b", 2), ("a", 3), ("b", 4)]"#, group_runs(vec![("a".to_string(), 1), ("b".to_string(), 2), ("a".to_string(), 3), ("b".to_string(), 4)]), (vec![("a".to_string(), vec![1]), ("b".to_string(), vec![2]), ("a".to_string(), vec![3]), ("b".to_string(), vec![4])], 4));
}

#[test]
fn repeated_values() {
    check!(r#"[("a", 5), ("a", 5), ("b", 5)]"#, group_runs(vec![("a".to_string(), 5), ("a".to_string(), 5), ("b".to_string(), 5)]), (vec![("a".to_string(), vec![5, 5]), ("b".to_string(), vec![5])], 3));
}

#[test]
fn case_sensitive() {
    check!(r#"[("a", 1), ("A", 2)]"#, group_runs(vec![("a".to_string(), 1), ("A".to_string(), 2)]), (vec![("a".to_string(), vec![1]), ("A".to_string(), vec![2])], 2));
}

#[test]
fn long_last_run() {
    check!(r#"[("a", 1), ("b", 2), ("b", 3), ("b", 4)]"#, group_runs(vec![("a".to_string(), 1), ("b".to_string(), 2), ("b".to_string(), 3), ("b".to_string(), 4)]), (vec![("a".to_string(), vec![1]), ("b".to_string(), vec![2, 3, 4])], 4));
}

#[test]
fn unicode_keys() {
    check!(r#"[("é", 1), ("é", 2), ("e", 3)]"#, group_runs(vec![("é".to_string(), 1), ("é".to_string(), 2), ("e".to_string(), 3)]), (vec![("é".to_string(), vec![1, 2]), ("e".to_string(), vec![3])], 3));
}

#[test]
fn extreme_values() {
    check!(r#"[("m", 0), ("m", u32::MAX)]"#, group_runs(vec![("m".to_string(), 0), ("m".to_string(), u32::MAX)]), (vec![("m".to_string(), vec![0, u32::MAX])], 2));
}

#[test]
fn keys_are_not_copied() {
    let records: Vec<(String, u32)> = vec![("left".to_string(), 1), ("right".to_string(), 2)];
    let ptrs: Vec<*const u8> = records.iter().map(|(k, _)| k.as_ptr()).collect();
    let (groups, _) = group_runs(records);
    let got: Vec<*const u8> = groups.iter().map(|(k, _)| k.as_ptr()).collect();
    check!("[(\"left\", 1), (\"right\", 2)]: each key is the record's own String", got == ptrs, true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6103);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut records = Vec::new();
        for _ in 0..n {
            let len = rng.below(2);
            records.push((rng.string(len, "ab"), rng.below(10) as u32));
        }
        let mut want: Vec<(String, Vec<u32>)> = Vec::new();
        for (k, v) in &records {
            match want.last_mut() {
                Some((last, vs)) if last == k => vs.push(*v),
                _ => want.push((k.clone(), vec![*v])),
            }
        }
        check!(format!("records = {records:?}"), group_runs(records.clone()), (want, n));
    }
}

#[test]
fn many_records() {
    let records: Vec<(String, u32)> = (0..200_000u32).map(|i| (format!("k{}", i / 4), i)).collect();
    let (groups, n) = group_runs(records);
    check!("200000 records, 4 per key", (groups.len(), n, groups[49_999].1.clone()), (50_000, 200_000, vec![199_996, 199_997, 199_998, 199_999]));
}
