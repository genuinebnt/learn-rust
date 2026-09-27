use solution::*;

#[test]
fn quiz_no_niche() {
    check!(r#"OPTION_SIZES[3]: Option<f64>"#, OPTION_SIZES[3], std::mem::size_of::<N4>());
}

#[test]
fn quiz_char_and_nested() {
    check!(r#"OPTION_SIZES[4..6]: Option<char>, Option<Option<bool>>"#, &OPTION_SIZES[4..6], &[std::mem::size_of::<N5>(), std::mem::size_of::<N6>()][..]);
}

#[test]
fn quiz_padding_is_not_a_niche() {
    check!(r#"OPTION_SIZES[6]: Option<(u8, u32)>"#, OPTION_SIZES[6], std::mem::size_of::<N7>());
}

#[test]
fn quiz_vec() {
    check!(r#"OPTION_SIZES[7]: Option<Vec<u8>>"#, OPTION_SIZES[7], std::mem::size_of::<N8>());
}

#[test]
fn heads_array() {
    check!(r#"size_of::<[Option<Idx>; 1024]>()"#, std::mem::size_of::<[Option<Idx>; 1024]>(), 4096);
}

#[test]
fn idx_distinct() {
    check!(r#"Idx::new(0) != Idx::new(1), Some(Idx::new(0)) != None"#, (Idx::new(0) != Idx::new(1), Some(Idx::new(0)).is_some(), Idx::new(Idx::MAX - 1).index()), (true, true, Idx::MAX - 1));
}

#[test]
#[should_panic]
fn idx_above_max_panics() {
    Idx::new(Idx::MAX + 1);
}

#[test]
fn empty_map() {
    let map = ChainMap::with_buckets(4);
    check!(r#"with_buckets(4), nothing inserted"#, (map.get(0), map.len(), map.is_empty(), map.chain_of(0)), (None, 0, true, Vec::<u32>::new()));
}

#[test]
fn zero_and_max_keys() {
    let mut map = ChainMap::with_buckets(2);
    map.insert(0, 1);
    map.insert(u32::MAX, 2);
    check!(r#"with_buckets(2): insert(0, 1), insert(u32::MAX, 2)"#, (map.get(0), map.get(u32::MAX), map.get(1)), (Some(1), Some(2), None));
}

#[test]
fn update_keeps_chain_order() {
    let mut map = ChainMap::with_buckets(1);
    for k in 1..=4 {
        map.insert(k, k * 10);
    }
    map.insert(2, 0);
    check!(r#"with_buckets(1): insert 1..=4, then insert(2, 0)"#, (map.chain_of(9), map.get(2), map.len()), (vec![4, 3, 2, 1], Some(0), 4));
}

#[test]
fn many_keys_one_bucket_each() {
    let mut map = ChainMap::with_buckets(1024);
    for k in 0..20_000u32 {
        map.insert(k * 7, k);
    }
    let wrong = (0..20_000u32).filter(|&k| map.get(k * 7) != Some(k)).count();
    let misses = (0..20_000u32).filter(|&k| map.get(k * 7 + 1).is_some()).count();
    check!("20000 keys k * 7 in 1024 buckets: wrong lookups, false hits on k * 7 + 1, len", (wrong, misses, map.len()), (0, 0, 20_000));
}

#[test]
fn random_vs_hashmap() {
    let mut rng = anneal_prelude::Rng::new(8202);
    for _ in 0..200 {
        let buckets = 1usize << rng.below(5);
        let mut map = ChainMap::with_buckets(buckets);
        let mut model = std::collections::HashMap::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(60) {
            let key = rng.int(0, 40) as u32;
            if rng.below(3) < 2 {
                let value = rng.int(0, 999) as u32;
                log.push(format!("insert({key}, {value})"));
                check!(format!("with_buckets({buckets}): {}", log.join(", ")), map.insert(key, value), model.insert(key, value));
            } else {
                log.push(format!("get({key})"));
                check!(format!("with_buckets({buckets}): {}", log.join(", ")), map.get(key), model.get(&key).copied());
            }
        }
        check!(format!("with_buckets({buckets}): {}; len", log.join(", ")), map.len(), model.len());
    }
}
