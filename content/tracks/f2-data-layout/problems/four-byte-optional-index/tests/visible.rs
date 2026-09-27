use solution::*;

#[test]
fn option_idx_is_free() {
    check!(r#"size_of::<Idx>(), size_of::<Option<Idx>>()"#, (std::mem::size_of::<Idx>(), std::mem::size_of::<Option<Idx>>()), (4, 4));
}

#[test]
fn entry_is_12_bytes() {
    check!(r#"size_of::<Entry>()"#, std::mem::size_of::<Entry>(), 12);
}

#[test]
fn idx_round_trips() {
    check!(r#"Idx::new(0), Idx::new(7), Idx::new(Idx::MAX): index()"#, (Idx::new(0).index(), Idx::new(7).index(), Idx::new(Idx::MAX).index()), (0, 7, Idx::MAX));
}

#[test]
fn quiz_pointers() {
    check!(r#"OPTION_SIZES[0..3]: Option<NonZeroU32>, Option<Box<u64>>, Option<&str>"#, &OPTION_SIZES[0..3], &[std::mem::size_of::<N1>(), std::mem::size_of::<N2>(), std::mem::size_of::<N3>()][..]);
}

#[test]
fn insert_and_get() {
    let mut map = ChainMap::with_buckets(8);
    let first = map.insert(5, 50);
    map.insert(9, 90);
    let again = map.insert(5, 55);
    check!(r#"with_buckets(8): insert(5, 50), insert(9, 90), insert(5, 55)"#, (first, again, map.get(5), map.get(9), map.get(6), map.len()), (None, Some(50), Some(55), Some(90), None, 2));
}

#[test]
fn new_keys_go_first() {
    let mut map = ChainMap::with_buckets(1);
    for (k, v) in [(1, 10), (2, 20), (3, 30), (1, 11)] {
        map.insert(k, v);
    }
    check!(r#"with_buckets(1): insert(1, 10), insert(2, 20), insert(3, 30), insert(1, 11)"#, map.chain_of(2), vec![3, 2, 1]);
}
