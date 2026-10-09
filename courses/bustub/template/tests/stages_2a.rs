//! Tests for module 2a, typed pages. A test name starts with its stage: `s2a_03_…` belongs to stage 2a-03, and
//! `anneal course test` runs just those.
//!
//! The tests use only the public items: the `FixedSize` encodings, `Rid`, `GenericKey` and its comparators, `array_size` and
//! `PageArray`. Values are encoded into buffers at random offsets and must decode to themselves without touching their neighbours;
//! `PageArray` runs random operations against a `Vec`; `lower_bound` is compared with `partition_point`. The byte order you choose
//! for an encoding is yours: only the round trip is tested.

use std::cmp::Ordering;
use std::fmt::Debug;

use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::index::fixed_size::{array_size, FixedSize};
use bustub::storage::index::generic_key::{GenericComparator, GenericKey, KeyComparator};
use bustub::storage::index::int_comparator::IntComparator;
use bustub::storage::page::layout::HTABLE_BUCKET_PAGE_METADATA_SIZE;
use bustub::storage::page::page_array::PageArray;
use common::pool::{pool_with, Policy};
use proptest::prelude::*;

mod common;

fn config() -> ProptestConfig {
    ProptestConfig { cases: 128, max_shrink_iters: 2000, ..ProptestConfig::default() }
}

// ---- 2a-01 · Ids that survive bytes -------------------------------------------------------------------------------------

/// Encodes `value` at `offset` of a buffer full of 0xAA, checks that exactly `T::SIZE` bytes were written there, and decodes it back.
fn survives<T: FixedSize + PartialEq + Debug>(value: &T, offset: usize) -> Result<(), TestCaseError> {
    let mut buf = vec![0xAAu8; 64];
    value.encode(&mut buf[offset..offset + T::SIZE]);
    prop_assert!(buf[..offset].iter().all(|&b| b == 0xAA), "encoding {:?} wrote before its slot", value);
    prop_assert!(buf[offset + T::SIZE..].iter().all(|&b| b == 0xAA), "encoding {:?} wrote after its slot", value);
    let back = T::decode(&buf[offset..offset + T::SIZE]);
    prop_assert_eq!(&back, value, "decode(encode(x)) must be x");
    Ok(())
}

fn rid_strategy() -> impl Strategy<Value = Rid> {
    (any::<i32>(), any::<u32>()).prop_map(|(p, s)| Rid::new(PageId(p), s))
}

proptest! {
    #![proptest_config(config())]

    #[test]
    fn s2a_01_i32_survives_bytes_at_any_offset(x in any::<i32>(), offset in 0usize..56) {
        survives(&x, offset)?;
    }

    #[test]
    fn s2a_01_u32_and_i64_survive_bytes_at_any_offset(a in any::<u32>(), b in any::<i64>(), offset in 0usize..48) {
        survives(&a, offset)?;
        survives(&b, offset)?;
    }

    #[test]
    fn s2a_01_page_ids_survive_bytes_including_the_invalid_one(x in any::<i32>(), offset in 0usize..56) {
        survives(&PageId(x), offset)?;
        survives(&PageId::INVALID, offset)?;
    }

    #[test]
    fn s2a_01_rids_survive_bytes(rid in rid_strategy(), offset in 0usize..48) {
        survives(&rid, offset)?;
    }

    /// `get` packs the page id in the high 32 bits and the slot in the low 32 (BusTub's definition), `from_i64` undoes it.
    #[test]
    fn s2a_01_a_rid_packs_into_an_i64_and_back(rid in rid_strategy()) {
        let packed = rid.get();
        prop_assert_eq!(packed, ((rid.page_id().0 as i64) << 32) | rid.slot_num() as i64, "page id in the high bits, slot in the low bits");
        prop_assert_eq!(Rid::from_i64(packed), rid);
        prop_assert_eq!(Rid::from_i64(packed).page_id(), rid.page_id());
        prop_assert_eq!(Rid::from_i64(packed).slot_num(), rid.slot_num());
    }
}

#[test]
fn s2a_01_sizes_are_what_a_page_layout_can_count_on() {
    assert_eq!((<i32 as FixedSize>::SIZE, <u32 as FixedSize>::SIZE, <i64 as FixedSize>::SIZE), (4, 4, 8));
    assert_eq!((<PageId as FixedSize>::SIZE, <Rid as FixedSize>::SIZE), (4, 8));
}

#[test]
fn s2a_01_the_default_rid_names_no_page_and_page_zero_is_a_real_page() {
    assert!(!Rid::default().page_id().is_valid(), "the default rid is invalid");
    let zero = Rid::new(PageId(0), 7);
    assert!(zero.page_id().is_valid());
    assert_eq!(Rid::from_i64(zero.get()), zero, "page 0, slot 7 is not confused with an invalid rid");
}

// ---- 2a-02 · Keys and how to order them ------------------------------------------------------------------------------------

fn key<const N: usize>(n: i64) -> GenericKey<N> {
    let mut k = GenericKey::<N>::default();
    k.set_from_integer(n);
    k
}

proptest! {
    #![proptest_config(config())]

    #[test]
    fn s2a_02_a_generic_key_holds_any_integer_and_the_rest_of_it_is_zero(n in any::<i64>(), junk in any::<u8>()) {
        let mut k = GenericKey::<16>::default();
        k.data = [junk; 16];
        k.set_from_integer(n);
        prop_assert_eq!(k.get_as_integer(), n);
        prop_assert!(k.data[8..].iter().all(|&b| b == 0), "set_from_integer clears the key before storing the integer");
    }

    #[test]
    fn s2a_02_generic_keys_survive_bytes(n in any::<i64>(), offset in 0usize..32) {
        let k = key::<8>(n);
        let mut buf = vec![0x55u8; 64];
        k.encode(&mut buf[offset..offset + <GenericKey<8> as FixedSize>::SIZE]);
        prop_assert_eq!(<GenericKey<8>>::decode(&buf[offset..offset + 8]), k);
        let big = key::<24>(n);
        big.encode(&mut buf[offset..offset + 24]);
        prop_assert_eq!(<GenericKey<24>>::decode(&buf[offset..offset + 24]).get_as_integer(), n);
    }

    /// The comparators order keys exactly as the integers inside them are ordered, so sorting by a comparator sorts the integers
    /// (negative numbers before positive ones, which their raw bytes would not).
    #[test]
    fn s2a_02_comparators_agree_with_integer_order(a in any::<i64>(), b in any::<i64>(), c in any::<i32>(), d in any::<i32>()) {
        let g = GenericComparator::<8>;
        prop_assert_eq!(g.compare(&key(a), &key(b)), a.cmp(&b));
        prop_assert_eq!(IntComparator.compare(&c, &d), c.cmp(&d));
    }

    #[test]
    fn s2a_02_a_comparator_can_drive_a_sort(mut xs in prop::collection::vec(any::<i64>(), 0..60)) {
        let g = GenericComparator::<8>;
        let mut keys: Vec<GenericKey<8>> = xs.iter().map(|&n| key(n)).collect();
        keys.sort_by(|a, b| g.compare(a, b));
        xs.sort();
        prop_assert_eq!(keys.iter().map(|k| k.get_as_integer()).collect::<Vec<_>>(), xs);
    }

    #[test]
    fn s2a_02_a_pair_is_its_two_halves_side_by_side(n in any::<i64>(), rid in rid_strategy(), offset in 0usize..32) {
        type Entry = (GenericKey<8>, Rid);
        prop_assert_eq!(Entry::SIZE, 16);
        survives::<Entry>(&(key(n), rid), offset)?;
        survives::<((i32, u32), (i64, PageId))>(&((n as i32, 7), (n, PageId(n as i32))), offset)?;
    }
}

#[test]
fn s2a_02_array_size_is_what_fits_after_the_metadata() {
    assert_eq!(array_size(8, 16), (BUSTUB_PAGE_SIZE - 8) / 16);
    assert_eq!(array_size(0, 8192), 1);
    assert_eq!(array_size(HTABLE_BUCKET_PAGE_METADATA_SIZE, <(GenericKey<8>, Rid) as FixedSize>::SIZE), 511);
    const AT_COMPILE_TIME: usize = array_size(8, 12);
    assert_eq!(AT_COMPILE_TIME, 682);
}

#[test]
fn s2a_02_keys_of_other_sizes_and_a_zero_key() {
    assert_eq!(GenericKey::<8>::default().get_as_integer(), 0);
    assert_eq!(<GenericKey<64> as FixedSize>::SIZE, 64);
    assert_eq!(key::<64>(-5).get_as_integer(), -5);
}

// ---- 2a-03 · A sorted array inside a page -----------------------------------------------------------------------------------

#[derive(Clone, Copy, Debug)]
enum ArrayOp {
    Insert(usize, i32),
    Remove(usize),
    Set(usize, i32),
}

fn array_ops() -> impl Strategy<Value = Vec<ArrayOp>> {
    prop::collection::vec(
        prop_oneof![
            4 => (0..40usize, any::<i32>()).prop_map(|(i, v)| ArrayOp::Insert(i, v)),
            3 => (0..40usize).prop_map(ArrayOp::Remove),
            2 => (0..40usize, any::<i32>()).prop_map(|(i, v)| ArrayOp::Set(i, v)),
        ],
        1..150,
    )
}

const CAP: usize = 16;

proptest! {
    #![proptest_config(config())]

    /// Insert, remove and set at arbitrary positions: the array always reads as the `Vec` model, whatever the buffer holds around it.
    #[test]
    fn s2a_03_an_array_in_a_page_behaves_like_a_vec(ops in array_ops(), pad in 0usize..8) {
        let mut page = vec![0xEEu8; pad + CAP * 4 + 8];
        let mut model: Vec<i32> = Vec::new();
        {
            let mut array = PageArray::<_, i32>::new(&mut page[pad..pad + CAP * 4]);
            prop_assert_eq!(array.capacity(), CAP);
            for op in ops {
                match op {
                    ArrayOp::Insert(i, v) if model.len() < CAP => { let at = i % (model.len() + 1); array.insert_at(at, model.len(), &v); model.insert(at, v); }
                    ArrayOp::Remove(i) if !model.is_empty() => { let at = i % model.len(); array.remove_at(at, model.len()); model.remove(at); }
                    ArrayOp::Set(i, v) if !model.is_empty() => { let at = i % model.len(); array.set(at, &v); model[at] = v; }
                    _ => {}
                }
                let got: Vec<i32> = (0..model.len()).map(|i| array.get(i)).collect();
                prop_assert_eq!(&got, &model, "the array must read as the model after {:?}", op);
            }
        }
        prop_assert!(page[..pad].iter().all(|&b| b == 0xEE), "the array wrote before its bytes");
        prop_assert!(page[pad + CAP * 4..].iter().all(|&b| b == 0xEE), "the array wrote after its bytes");
    }

    #[test]
    fn s2a_03_pairs_move_whole_and_overlapping_shifts_do_not_smear(values in prop::collection::vec((any::<i64>(), any::<u32>()), 1..14), at in 0usize..14) {
        type E = (i64, Rid);
        let entries: Vec<E> = values.iter().map(|&(a, s)| (a, Rid::new(PageId(a as i32), s))).collect();
        let mut array = PageArray::<_, E>::new(vec![0u8; 16 * E::SIZE]);
        for (i, e) in entries.iter().enumerate() { array.set(i, e); }
        let at = at % (entries.len() + 1);
        let extra = (-1i64, Rid::new(PageId(-1), 99));
        array.insert_at(at, entries.len(), &extra);
        let mut model = entries.clone();
        model.insert(at, extra);
        prop_assert_eq!((0..model.len()).map(|i| array.get(i)).collect::<Vec<_>>(), model.clone());
        array.remove_at(at, model.len());
        prop_assert_eq!((0..entries.len()).map(|i| array.get(i)).collect::<Vec<_>>(), entries);
    }
}

#[test]
fn s2a_03_capacity_counts_whole_entries_only() {
    assert_eq!(PageArray::<_, i64>::new(vec![0u8; 100]).capacity(), 12);
    assert_eq!(PageArray::<_, i32>::new(&[0u8; 3][..]).capacity(), 0);
}

#[test]
fn s2a_03_it_works_over_a_read_only_view_and_an_owned_buffer() {
    let mut owned = PageArray::<_, u32>::new(vec![0u8; 16]);
    owned.set(2, &77);
    let bytes: Vec<u8> = (0..16).map(|i| i as u8).collect();
    let view = PageArray::<_, u32>::new(&bytes[..]);
    assert_eq!(owned.get(2), 77);
    assert_eq!(view.capacity(), 4);
}

#[test]
fn s2a_03_going_past_the_capacity_is_a_bug_and_panics() {
    let get = std::panic::catch_unwind(|| PageArray::<_, i32>::new(vec![0u8; 8]).get(2));
    assert!(get.is_err(), "get(2) on a capacity of 2");
    let set = std::panic::catch_unwind(|| PageArray::<_, i32>::new(vec![0u8; 8]).set(2, &1));
    assert!(set.is_err(), "set(2) on a capacity of 2");
    let full = std::panic::catch_unwind(|| {
        let mut a = PageArray::<_, i32>::new(vec![0u8; 8]);
        a.insert_at(0, 2, &1); // already holds 2 = full
    });
    assert!(full.is_err(), "inserting into a full array");
    let past_len = std::panic::catch_unwind(|| {
        let mut a = PageArray::<_, i32>::new(vec![0u8; 16]);
        a.insert_at(3, 1, &1); // beyond len
    });
    assert!(past_len.is_err(), "inserting beyond len");
    let remove = std::panic::catch_unwind(|| PageArray::<_, i32>::new(vec![0u8; 16]).remove_at(1, 1));
    assert!(remove.is_err(), "removing entry 1 of a length 1");
}

// ---- 2a-04 · Searching a page -----------------------------------------------------------------------------------------------

fn sorted_array(values: &[i32]) -> PageArray<Vec<u8>, i32> {
    let mut array = PageArray::new(vec![0u8; values.len().max(1) * 4 + 16]);
    for (i, v) in values.iter().enumerate() {
        array.set(i, v);
    }
    array
}

proptest! {
    #![proptest_config(config())]

    /// `lower_bound` is the first position whose entry is not less than the target: exactly `partition_point`, duplicates included.
    #[test]
    fn s2a_04_lower_bound_is_the_partition_point(mut values in prop::collection::vec(-20i32..20, 0..30), target in -22i32..22) {
        values.sort();
        let array = sorted_array(&values);
        let got = array.lower_bound(values.len(), |e| e.cmp(&target));
        prop_assert_eq!(got, values.partition_point(|&v| v < target), "lower_bound({}) in {:?}", target, values);
    }

    /// Only the first `len` entries count: stale bytes after them must not be searched.
    #[test]
    fn s2a_04_entries_past_len_are_not_searched(mut values in prop::collection::vec(-20i32..20, 1..30), cut in 0usize..30, target in -22i32..22) {
        values.sort();
        let len = cut % (values.len() + 1);
        let array = sorted_array(&values);
        prop_assert_eq!(array.lower_bound(len, |e| e.cmp(&target)), values[..len].partition_point(|&v| v < target));
    }

    /// Inserting at `lower_bound` keeps an array sorted: the page-sized version of a sorted set.
    #[test]
    fn s2a_04_inserting_at_the_lower_bound_keeps_the_array_sorted(inserts in prop::collection::vec(-50i32..50, 1..40)) {
        let mut array = PageArray::<_, i32>::new(vec![0u8; 64 * 4]);
        let mut model: Vec<i32> = Vec::new();
        for v in inserts {
            let at = array.lower_bound(model.len(), |e| e.cmp(&v));
            if at < model.len() && array.get(at) == v { continue; }
            array.insert_at(at, model.len(), &v);
            model.insert(model.partition_point(|&m| m < v), v);
            prop_assert_eq!((0..model.len()).map(|i| array.get(i)).collect::<Vec<_>>(), model.clone());
        }
    }

    /// Searching entries that are `(GenericKey, Rid)` with the key comparator, the way a bucket page does.
    #[test]
    fn s2a_04_a_search_by_key_finds_the_right_entry(mut keys in prop::collection::vec(-100i64..100, 1..25), probe in -102i64..102) {
        type E = (GenericKey<8>, Rid);
        keys.sort();
        keys.dedup();
        let mut array = PageArray::<_, E>::new(vec![0u8; 32 * E::SIZE]);
        for (i, &k) in keys.iter().enumerate() { array.set(i, &(key(k), Rid::new(PageId(k as i32), i as u32))); }
        let cmp = GenericComparator::<8>;
        let target = key::<8>(probe);
        let at = array.lower_bound(keys.len(), |(k, _)| cmp.compare(k, &target));
        prop_assert_eq!(at, keys.partition_point(|&k| k < probe));
        if let Some(pos) = keys.iter().position(|&k| k == probe) {
            prop_assert_eq!(pos, at);
            prop_assert_eq!(array.get(at).1, Rid::new(PageId(probe as i32), at as u32));
        }
    }
}

#[test]
fn s2a_04_a_target_larger_than_everything_gives_len() {
    let array = sorted_array(&[1, 3, 5]);
    assert_eq!(array.lower_bound(3, |e| e.cmp(&9)), 3);
    assert_eq!(array.lower_bound(3, |e| e.cmp(&0)), 0);
    assert_eq!(array.lower_bound(0, |e| e.cmp(&0)), 0, "an empty array");
}

#[test]
fn s2a_04_the_comparison_closure_is_called_logarithmically_often() {
    let values: Vec<i32> = (0..1024).collect();
    let array = sorted_array(&values);
    let mut calls = 0;
    let at = array.lower_bound(values.len(), |e| {
        calls += 1;
        e.cmp(&700)
    });
    assert_eq!(at, 700);
    assert!(calls <= 12, "binary search on 1024 entries needs about 10 comparisons, yours made {calls}");
}

// ---- 2a-05 · Boss: the pieces on a real page ---------------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 24, ..config() })]

    /// A sorted bucket page (a length, a capacity, then `(key, rid)` entries kept sorted) built only from the pieces of this module,
    /// living in the buffer pool: after any sequence of inserts and removes, and after the page has been evicted and read back, it still
    /// holds exactly the keys of a `BTreeMap` model.
    #[test]
    fn s2a_05_a_sorted_bucket_survives_the_buffer_pool(ops in prop::collection::vec((any::<bool>(), 0i64..60), 1..120)) {
        type Entry = (GenericKey<8>, Rid);
        let (bpm, _disk) = pool_with(Policy::Fifo, 2);
        let page = bpm.new_page();
        let cmp = GenericComparator::<8>;
        let max = array_size(HTABLE_BUCKET_PAGE_METADATA_SIZE, Entry::SIZE);
        let mut model = std::collections::BTreeMap::new();
        {
            let mut guard = bpm.write_page(page);
            let data = guard.get_data_mut();
            data[..4].copy_from_slice(&0u32.to_le_bytes());
            data[4..8].copy_from_slice(&(max as u32).to_le_bytes());
        }
        for (i, (insert, n)) in ops.into_iter().enumerate() {
            let mut guard = bpm.write_page(page);
            let data = guard.get_data_mut();
            let len = u32::from_le_bytes(data[..4].try_into().unwrap()) as usize;
            let mut array = PageArray::<_, Entry>::new(&mut data[HTABLE_BUCKET_PAGE_METADATA_SIZE..]);
            let target = key::<8>(n);
            let at = array.lower_bound(len, |(k, _)| cmp.compare(k, &target));
            let present = at < len && array.get(at).0.get_as_integer() == n;
            let new_len = if insert && !present {
                array.insert_at(at, len, &(target, Rid::new(PageId(n as i32), i as u32)));
                model.insert(n, i as u32);
                len + 1
            } else if !insert && present {
                array.remove_at(at, len);
                model.remove(&n);
                len - 1
            } else { len };
            data[..4].copy_from_slice(&(new_len as u32).to_le_bytes());
            drop(guard);
            if i % 17 == 0 { // push the page out of the two-frame pool
                for _ in 0..3 { let other = bpm.new_page(); drop(bpm.write_page(other)); }
            }
        }
        let guard = bpm.read_page(page);
        let data = guard.get_data();
        let len = u32::from_le_bytes(data[..4].try_into().unwrap()) as usize;
        let array = PageArray::<_, Entry>::new(&data[HTABLE_BUCKET_PAGE_METADATA_SIZE..]);
        let got: Vec<(i64, u32)> = (0..len).map(|i| { let (k, r) = array.get(i); (k.get_as_integer(), r.slot_num()) }).collect();
        let want: Vec<(i64, u32)> = model.into_iter().collect();
        prop_assert_eq!(got, want);
    }
}

#[test]
fn s2a_05_an_ordering_is_a_total_order_on_the_keys_it_will_index() {
    let g = GenericComparator::<8>;
    let ks: Vec<GenericKey<8>> = [-3i64, -1, 0, 0, 5, i64::MIN, i64::MAX].iter().map(|&n| key(n)).collect();
    for a in &ks {
        assert_eq!(g.compare(a, a), Ordering::Equal);
        for b in &ks {
            assert_eq!(g.compare(a, b), g.compare(b, a).reverse(), "antisymmetry");
            for c in &ks {
                if g.compare(a, b) != Ordering::Greater && g.compare(b, c) != Ordering::Greater {
                    assert_ne!(g.compare(a, c), Ordering::Greater, "transitivity");
                }
            }
        }
    }
}
