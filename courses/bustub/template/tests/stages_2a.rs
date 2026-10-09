//! Tests for the typed page stages (2a-01 … 2a-05). A test named `s2a_05_…` belongs to stage 2a-02.

use std::cmp::Ordering;
use std::sync::Arc;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::fixed_size::{array_size, FixedSize};
use bustub::storage::index::generic_key::{GenericComparator, GenericKey, KeyComparator};
use bustub::storage::index::int_comparator::IntComparator;
use bustub::storage::page::layout::*;
use bustub::storage::page::page_array::PageArray;
use bustub::storage::page::page_bytes::*;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

// ---- 2a-01 · read_u32, write_u32, read_u64, write_u64 ----------------------------------------------------------------------

#[test]
fn s2a_01_integers_are_stored_little_endian() {
    let mut page = [0u8; 16];
    write_u32(&mut page, 0, 0x1234_5678);
    assert_eq!(&page[..4], &[0x78, 0x56, 0x34, 0x12], "integers are stored little endian");
    write_u64(&mut page, 8, 0x0102_0304_0506_0708);
    assert_eq!(&page[8..], &[8, 7, 6, 5, 4, 3, 2, 1], "integers are stored little endian");
}

#[test]
fn s2a_01_values_read_back_at_any_offset_aligned_or_not() {
    let mut page = [0u8; BUSTUB_PAGE_SIZE];
    for offset in [0, 1, 2, 3, 5, 100, BUSTUB_PAGE_SIZE - 4] {
        write_u32(&mut page, offset, 0xDEAD_BEEF ^ offset as u32);
        assert_eq!(read_u32(&page, offset), 0xDEAD_BEEF ^ offset as u32, "offset {offset}");
    }
    for offset in [0, 1, 7, 4093, BUSTUB_PAGE_SIZE - 8] {
        write_u64(&mut page, offset, u64::MAX - offset as u64);
        assert_eq!(read_u64(&page, offset), u64::MAX - offset as u64, "offset {offset}");
    }
}

#[test]
fn s2a_01_a_write_touches_only_its_own_bytes() {
    let mut page = [0xAAu8; 12];
    write_u32(&mut page, 4, 0);
    assert_eq!(page, [0xAA, 0xAA, 0xAA, 0xAA, 0, 0, 0, 0, 0xAA, 0xAA, 0xAA, 0xAA], "a write touches only its own bytes");
}

#[test]
fn s2a_01_extremes() {
    let mut page = [0u8; 16];
    write_u32(&mut page, 0, u32::MAX);
    write_u64(&mut page, 4, u64::MAX);
    assert_eq!((read_u32(&page, 0), read_u64(&page, 4)), (u32::MAX, u64::MAX), "extremes");
    write_u32(&mut page, 0, 0);
    assert_eq!(read_u32(&page, 0), 0, "extremes");
}

#[test]
#[should_panic]
fn s2a_01_reading_past_the_end_panics_instead_of_reading_garbage() {
    let page = [0u8; 8];
    read_u32(&page, 6);
}

#[test]
#[should_panic]
fn s2a_01_writing_past_the_end_panics() {
    let mut page = [0u8; 8];
    write_u64(&mut page, 1, 1);
}

// ---- 2a-01 · page ids ------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_02_page_ids_round_trip() {
    let mut page = [0u8; 16];
    write_page_id(&mut page, 4, PageId(1234));
    assert_eq!(read_page_id(&page, 4), PageId(1234), "page ids round trip");
}

#[test]
fn s2a_02_the_invalid_id_is_minus_one_and_survives() {
    let mut page = [0u8; 8];
    write_page_id(&mut page, 0, PageId::INVALID);
    assert_eq!(&page[..4], &[0xFF, 0xFF, 0xFF, 0xFF], "-1 as a signed 32-bit integer");
    assert_eq!(read_page_id(&page, 0), PageId::INVALID, "the invalid id is minus one and survives");
    assert!(!read_page_id(&page, 0).is_valid(), "the invalid id is minus one and survives: expected `!read_page_id(&page, 0).is_valid()`");
}

#[test]
fn s2a_02_none_is_stored_as_invalid() {
    let mut page = [0u8; 8];
    write_optional_page_id(&mut page, 0, None);
    assert_eq!(read_page_id(&page, 0), PageId::INVALID, "none is stored as invalid");
    assert_eq!(read_optional_page_id(&page, 0), None, "none is stored as invalid");
    write_optional_page_id(&mut page, 4, Some(PageId(7)));
    assert_eq!(read_optional_page_id(&page, 4), Some(PageId(7)), "none is stored as invalid");
    assert_eq!(read_page_id(&page, 4), PageId(7), "none is stored as invalid");
}

#[test]
fn s2a_02_page_zero_is_a_real_page_not_none() {
    let mut page = [0u8; 4];
    write_optional_page_id(&mut page, 0, Some(PageId(0)));
    assert_eq!(read_optional_page_id(&page, 0), Some(PageId(0)), "page zero is a real page not none");
}

#[test]
fn s2a_02_a_zeroed_page_reads_as_page_zero() {
    // The trap of zero-filled pages: 0 is a valid id; only -1 means "no page". New pages must write INVALID explicitly.
    let page = [0u8; 4];
    assert_eq!(read_optional_page_id(&page, 0), Some(PageId(0)), "a zeroed page reads as page zero");
}

// ---- 2a-01 · Rid -------------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_03_a_rid_has_a_page_and_a_slot() {
    let rid = Rid::new(PageId(7), 3);
    assert_eq!((rid.page_id(), rid.slot_num()), (PageId(7), 3), "a rid has a page and a slot");
}

#[test]
fn s2a_03_get_packs_the_page_in_the_high_bits() {
    assert_eq!(Rid::new(PageId(1), 2).get(), (1i64 << 32) | 2, "get packs the page in the high bits");
    assert_eq!(Rid::new(PageId(0), 5).get(), 5, "get packs the page in the high bits");
    assert_eq!(Rid::new(PageId(3), 0).get(), 3 << 32, "get packs the page in the high bits");
}

#[test]
fn s2a_03_a_negative_page_id_keeps_its_sign() {
    let rid = Rid::new(PageId(-1), 0);
    assert_eq!(rid.get(), -(1i64 << 32), "a negative page id keeps its sign");
    assert_eq!(Rid::from_i64(rid.get()), rid, "a negative page id keeps its sign");
}

#[test]
fn s2a_03_the_slot_never_leaks_into_the_page() {
    let rid = Rid::new(PageId(9), u32::MAX);
    assert_eq!(Rid::from_i64(rid.get()), rid, "the slot never leaks into the page");
    assert_eq!(rid.get() >> 32, 9, "the slot never leaks into the page");
}

#[test]
fn s2a_03_a_hundred_round_trips() {
    let mut rng = Lcg(3);
    for _ in 0..100 {
        let rid = Rid::new(PageId(rng.next(1 << 30) as i32 - (1 << 29)), rng.next(1 << 31) as u32);
        assert_eq!(Rid::from_i64(rid.get()), rid, "a hundred round trips");
    }
}

#[test]
fn s2a_03_the_default_rid_is_invalid() {
    let rid = Rid::default();
    assert_eq!(rid.page_id(), PageId::INVALID, "the default rid is invalid");
    assert_eq!(rid.slot_num(), 0, "the default rid is invalid");
}

// ---- 2a-01 · FixedSize for the basic types ----------------------------------------------------------------------------------------

fn round_trip<T: FixedSize + PartialEq + std::fmt::Debug>(value: T) {
    let mut buf = vec![0xEEu8; T::SIZE];
    value.encode(&mut buf);
    assert_eq!(T::decode(&buf), value, "in helper `round_trip`");
}

#[test]
fn s2a_04_sizes() {
    assert_eq!((i32::SIZE, u32::SIZE, i64::SIZE, PageId::SIZE, Rid::SIZE), (4, 4, 8, 4, 8), "sizes");
}

#[test]
fn s2a_04_integers_round_trip() {
    round_trip(0i32);
    round_trip(-1i32);
    round_trip(i32::MIN);
    round_trip(u32::MAX);
    round_trip(i64::MIN);
    round_trip(1i64 << 40);
}

#[test]
fn s2a_04_byte_order_is_little_endian() {
    let mut buf = [0u8; 4];
    0x0A0B0C0Du32.encode(&mut buf);
    assert_eq!(buf, [0x0D, 0x0C, 0x0B, 0x0A], "byte order is little endian");
}

#[test]
fn s2a_04_page_ids_and_rids_round_trip() {
    round_trip(PageId(0));
    round_trip(PageId::INVALID);
    round_trip(Rid::new(PageId(12), 34));
    round_trip(Rid::default());
}

#[test]
fn s2a_04_a_page_id_is_laid_out_like_the_raw_integer() {
    let mut a = [0u8; 4];
    let mut b = [0u8; 4];
    PageId(77).encode(&mut a);
    77i32.encode(&mut b);
    assert_eq!(a, b, "a page id is laid out like the raw integer");
}

// ---- 2a-02 · GenericKey ------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_05_a_key_holds_an_integer() {
    let mut key = GenericKey::<8>::default();
    key.set_from_integer(42);
    assert_eq!(key.get_as_integer(), 42, "a key holds an integer");
    key.set_from_integer(-7);
    assert_eq!(key.get_as_integer(), -7, "a key holds an integer");
}

#[test]
fn s2a_05_set_from_integer_clears_the_rest_of_the_key() {
    let mut key = GenericKey::<16> { data: [0xFF; 16] };
    key.set_from_integer(1);
    assert_eq!(key.data, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "set from integer clears the rest of the key");
}

#[test]
fn s2a_05_a_key_encodes_as_its_bytes() {
    let mut key = GenericKey::<8>::default();
    key.set_from_integer(0x0102030405060708);
    let mut buf = [0u8; 8];
    key.encode(&mut buf);
    assert_eq!(buf, [8, 7, 6, 5, 4, 3, 2, 1], "a key encodes as its bytes");
    assert_eq!(GenericKey::<8>::decode(&buf), key, "a key encodes as its bytes");
    assert_eq!(GenericKey::<8>::SIZE, 8, "a key encodes as its bytes");
    assert_eq!(GenericKey::<64>::SIZE, 64, "a key encodes as its bytes");
}

#[test]
fn s2a_05_keys_of_other_sizes_work() {
    let mut key = GenericKey::<32>::default();
    key.set_from_integer(i64::MAX);
    let mut buf = [0u8; 32];
    key.encode(&mut buf);
    assert_eq!(GenericKey::<32>::decode(&buf).get_as_integer(), i64::MAX, "keys of other sizes work");
}

#[test]
fn s2a_05_the_default_key_is_zero() {
    assert_eq!(GenericKey::<8>::default().get_as_integer(), 0, "the default key is zero");
}

// ---- 2a-02 · comparators --------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_06_ints_compare_numerically() {
    let cmp = IntComparator;
    assert_eq!(cmp.compare(&1, &2), Ordering::Less, "ints compare numerically");
    assert_eq!(cmp.compare(&2, &2), Ordering::Equal, "ints compare numerically");
    assert_eq!(cmp.compare(&3, &-3), Ordering::Greater, "ints compare numerically");
    assert_eq!(cmp.compare(&i32::MIN, &i32::MAX), Ordering::Less, "ints compare numerically");
}

fn key(n: i64) -> GenericKey<8> {
    let mut k = GenericKey::<8>::default();
    k.set_from_integer(n);
    k
}

#[test]
fn s2a_06_generic_keys_compare_by_their_integer() {
    let cmp = GenericComparator::<8>;
    assert_eq!(cmp.compare(&key(5), &key(9)), Ordering::Less, "generic keys compare by their integer");
    assert_eq!(cmp.compare(&key(9), &key(9)), Ordering::Equal, "generic keys compare by their integer");
    assert_eq!(cmp.compare(&key(10), &key(9)), Ordering::Greater, "generic keys compare by their integer");
}

#[test]
fn s2a_06_negative_numbers_sort_before_positive_ones_unlike_their_bytes() {
    // As unsigned little-endian bytes -1 would sort after everything. The comparator must read signed integers.
    let cmp = GenericComparator::<8>;
    assert_eq!(cmp.compare(&key(-1), &key(0)), Ordering::Less, "negative numbers sort before positive ones unlike their bytes");
    assert_eq!(cmp.compare(&key(-100), &key(-2)), Ordering::Less, "negative numbers sort before positive ones unlike their bytes");
    // And 256 > 1 although its first byte (little-endian) is 0 < 1.
    assert_eq!(cmp.compare(&key(256), &key(1)), Ordering::Greater, "negative numbers sort before positive ones unlike their bytes");
}

#[test]
fn s2a_06_a_comparator_can_drive_a_sort() {
    let cmp = GenericComparator::<16>;
    let mut keys: Vec<GenericKey<16>> = [5, -3, 12, 0, -9, 7].iter().map(|&n| {
        let mut k = GenericKey::<16>::default();
        k.set_from_integer(n);
        k
    }).collect();
    keys.sort_by(|a, b| cmp.compare(a, b));
    assert_eq!(keys.iter().map(|k| k.get_as_integer()).collect::<Vec<_>>(), [-9, -3, 0, 5, 7, 12], "a comparator can drive a sort");
}

// ---- 2a-02 · pairs and array_size ------------------------------------------------------------------------------------------------------

#[test]
fn s2a_07_a_pair_is_the_sizes_added() {
    assert_eq!(<(i32, i32)>::SIZE, 8, "a pair is the sizes added");
    assert_eq!(<(GenericKey<8>, Rid)>::SIZE, 16, "a pair is the sizes added");
    assert_eq!(<(GenericKey<64>, PageId)>::SIZE, 68, "a pair is the sizes added");
}

#[test]
fn s2a_07_a_pair_round_trips_and_lays_the_first_value_first() {
    let pair = (7i32, 9i32);
    let mut buf = [0u8; 8];
    pair.encode(&mut buf);
    assert_eq!(buf, [7, 0, 0, 0, 9, 0, 0, 0], "a pair round trips and lays the first value first");
    assert_eq!(<(i32, i32)>::decode(&buf), pair, "a pair round trips and lays the first value first");
    round_trip((key(5), Rid::new(PageId(2), 1)));
}

#[test]
fn s2a_07_nested_pairs_work() {
    round_trip(((1i32, 2i32), 3i64));
}

#[test]
fn s2a_07_array_size_is_what_fits_after_the_metadata() {
    assert_eq!(array_size(8, 8), (8192 - 8) / 8, "array size is what fits after the metadata");
    assert_eq!(array_size(8, 16), 511, "array size is what fits after the metadata");
    assert_eq!(array_size(0, 4096), 2, "array size is what fits after the metadata");
    assert_eq!(array_size(8, 8192), 0, "array size is what fits after the metadata");
}

#[test]
fn s2a_07_array_size_works_at_compile_time() {
    const N: usize = array_size(8, <(GenericKey<8>, Rid)>::SIZE);
    assert_eq!(N, 511, "array size works at compile time");
    let table = [0u8; array_size(8, 1024)];
    assert_eq!(table.len(), 7, "array size works at compile time");
}

// ---- 2a-03 · PageArray: get and set ----------------------------------------------------------------------------------------------------

#[test]
fn s2a_08_set_then_get() {
    let mut bytes = vec![0u8; 40];
    let mut array = PageArray::<_, i32>::new(&mut bytes[..]);
    assert_eq!(array.capacity(), 10, "set then get");
    array.set(0, &11);
    array.set(9, &-99);
    assert_eq!((array.get(0), array.get(9)), (11, -99), "set then get");
}

#[test]
fn s2a_08_entries_do_not_overlap() {
    let mut bytes = vec![0u8; 64];
    let mut array = PageArray::<_, (i32, i32)>::new(&mut bytes[..]);
    for i in 0..8 {
        array.set(i, &(i as i32, -(i as i32)));
    }
    for i in 0..8 {
        assert_eq!(array.get(i), (i as i32, -(i as i32)), "entries do not overlap");
    }
}

#[test]
fn s2a_08_the_capacity_is_whole_entries_only() {
    let bytes = vec![0u8; 35];
    assert_eq!(PageArray::<_, (i32, i32)>::new(&bytes[..]).capacity(), 4);
    assert_eq!(PageArray::<_, i64>::new(&bytes[..]).capacity(), 4);
}

#[test]
fn s2a_08_a_read_only_view_over_shared_bytes() {
    let mut bytes = vec![0u8; 16];
    PageArray::<_, i32>::new(&mut bytes[..]).set(2, &123);
    let view = PageArray::<_, i32>::new(&bytes[..]);
    assert_eq!(view.get(2), 123, "a read only view over shared bytes");
}

#[test]
fn s2a_08_it_works_on_an_owned_buffer_too() {
    let mut array = PageArray::<_, Rid>::new(vec![0u8; 80]);
    array.set(3, &Rid::new(PageId(5), 6));
    assert_eq!(array.get(3), Rid::new(PageId(5), 6), "it works on an owned buffer too");
}

#[test]
#[should_panic(expected = "past the capacity")]
fn s2a_08_get_past_the_capacity_panics() {
    let bytes = vec![0u8; 16];
    PageArray::<_, i32>::new(&bytes[..]).get(4);
}

#[test]
#[should_panic(expected = "past the capacity")]
fn s2a_08_set_past_the_capacity_panics() {
    let mut bytes = vec![0u8; 16];
    PageArray::<_, i32>::new(&mut bytes[..]).set(4, &1);
}

// ---- 2a-03 · insert_at ---------------------------------------------------------------------------------------------------------------------

fn load(values: &[i32], capacity: usize) -> PageArray<Vec<u8>, i32> {
    let mut array = PageArray::new(vec![0u8; capacity * 4]);
    for (i, v) in values.iter().enumerate() {
        array.set(i, v);
    }
    array
}

fn dump(array: &PageArray<Vec<u8>, i32>, len: usize) -> Vec<i32> {
    (0..len).map(|i| array.get(i)).collect()
}

#[test]
fn s2a_09_insert_in_the_middle_shifts_the_rest_right() {
    let mut a = load(&[1, 2, 4, 5], 8);
    a.insert_at(2, 4, &3);
    assert_eq!(dump(&a, 5), [1, 2, 3, 4, 5], "insert in the middle shifts the rest right");
}

#[test]
fn s2a_09_insert_at_the_front_and_at_the_end() {
    let mut a = load(&[2, 3], 8);
    a.insert_at(0, 2, &1);
    a.insert_at(3, 3, &4);
    assert_eq!(dump(&a, 4), [1, 2, 3, 4], "insert at the front and at the end");
}

#[test]
fn s2a_09_insert_into_an_empty_array() {
    let mut a = load(&[], 4);
    a.insert_at(0, 0, &9);
    assert_eq!(dump(&a, 1), [9], "insert into an empty array");
}

#[test]
fn s2a_09_overlapping_moves_do_not_smear() {
    // A forward copy loop would write entry 0 over entry 1 over entry 2 ...; copy_within is memmove.
    let mut a = load(&[10, 20, 30, 40, 50, 60], 8);
    a.insert_at(0, 6, &0);
    assert_eq!(dump(&a, 7), [0, 10, 20, 30, 40, 50, 60], "overlapping moves do not smear");
}

#[test]
fn s2a_09_filling_the_array_exactly() {
    let mut a = load(&[1, 2, 3], 4);
    a.insert_at(1, 3, &9);
    assert_eq!(dump(&a, 4), [1, 9, 2, 3], "filling the array exactly");
}

#[test]
#[should_panic(expected = "no room")]
fn s2a_09_inserting_into_a_full_array_panics() {
    let mut a = load(&[1, 2, 3, 4], 4);
    a.insert_at(0, 4, &0);
}

#[test]
#[should_panic(expected = "no room")]
fn s2a_09_inserting_beyond_len_panics() {
    let mut a = load(&[1, 2], 8);
    a.insert_at(5, 2, &0);
}

#[test]
fn s2a_09_a_model_with_random_inserts() {
    let mut rng = Lcg(21);
    let mut a = load(&[], 64);
    let mut model: Vec<i32> = Vec::new();
    for step in 0..64 {
        let at = rng.next(model.len() + 1);
        a.insert_at(at, model.len(), &(step as i32));
        model.insert(at, step as i32);
        assert_eq!(dump(&a, model.len()), model, "step {step}");
    }
}

// ---- 2a-03 · remove_at ---------------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_10_remove_from_the_middle_shifts_the_rest_left() {
    let mut a = load(&[1, 2, 3, 4, 5], 8);
    a.remove_at(2, 5);
    assert_eq!(dump(&a, 4), [1, 2, 4, 5], "remove from the middle shifts the rest left");
}

#[test]
fn s2a_10_remove_the_first_and_the_last() {
    let mut a = load(&[1, 2, 3, 4], 8);
    a.remove_at(0, 4);
    assert_eq!(dump(&a, 3), [2, 3, 4], "remove the first and the last");
    a.remove_at(2, 3);
    assert_eq!(dump(&a, 2), [2, 3], "remove the first and the last");
}

#[test]
fn s2a_10_remove_the_only_entry() {
    let mut a = load(&[7], 4);
    a.remove_at(0, 1);
}

#[test]
#[should_panic(expected = "no entry")]
fn s2a_10_removing_past_len_panics() {
    let mut a = load(&[1, 2], 4);
    a.remove_at(2, 2);
}

#[test]
fn s2a_10_insert_and_remove_undo_each_other() {
    let mut a = load(&[1, 2, 3, 4], 8);
    a.insert_at(2, 4, &99);
    a.remove_at(2, 5);
    assert_eq!(dump(&a, 4), [1, 2, 3, 4], "insert and remove undo each other");
}

#[test]
fn s2a_10_a_model_with_random_inserts_and_removes() {
    let mut rng = Lcg(77);
    let mut a = load(&[], 32);
    let mut model: Vec<i32> = Vec::new();
    for step in 0..500 {
        if !model.is_empty() && (model.len() == 32 || rng.next(2) == 0) {
            let at = rng.next(model.len());
            a.remove_at(at, model.len());
            model.remove(at);
        } else {
            let at = rng.next(model.len() + 1);
            a.insert_at(at, model.len(), &(step as i32));
            model.insert(at, step as i32);
        }
        assert_eq!(dump(&a, model.len()), model, "step {step}");
    }
}

// ---- 2a-04 · lower_bound -------------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_11_finds_an_existing_entry() {
    let a = load(&[10, 20, 30, 40], 8);
    assert_eq!(a.lower_bound(4, |e| e.cmp(&30)), 2, "finds an existing entry");
    assert_eq!(a.lower_bound(4, |e| e.cmp(&10)), 0, "finds an existing entry");
    assert_eq!(a.lower_bound(4, |e| e.cmp(&40)), 3, "finds an existing entry");
}

#[test]
fn s2a_11_for_a_missing_entry_it_is_where_it_would_go() {
    let a = load(&[10, 20, 30, 40], 8);
    assert_eq!(a.lower_bound(4, |e| e.cmp(&25)), 2, "for a missing entry it is where it would go");
    assert_eq!(a.lower_bound(4, |e| e.cmp(&5)), 0, "for a missing entry it is where it would go");
    assert_eq!(a.lower_bound(4, |e| e.cmp(&99)), 4, "len when every entry is smaller");
}

#[test]
fn s2a_11_an_empty_range() {
    let a = load(&[], 4);
    assert_eq!(a.lower_bound(0, |e| e.cmp(&1)), 0, "an empty range");
}

#[test]
fn s2a_11_duplicates_give_the_first() {
    let a = load(&[1, 2, 2, 2, 3], 8);
    assert_eq!(a.lower_bound(5, |e| e.cmp(&2)), 1, "duplicates give the first");
}

#[test]
fn s2a_11_only_len_entries_are_looked_at() {
    // The bytes after len hold garbage (here: 0, smaller than everything): they must not be searched.
    let a = load(&[10, 20, 30], 8);
    assert_eq!(a.lower_bound(3, |e| e.cmp(&25)), 2, "only len entries are looked at");
    assert_eq!(a.lower_bound(3, |e| e.cmp(&1000)), 3, "only len entries are looked at");
}

#[test]
fn s2a_11_it_takes_a_comparator_for_keyed_entries() {
    let cmp = GenericComparator::<8>;
    let mut array = PageArray::<_, (GenericKey<8>, Rid)>::new(vec![0u8; 16 * 10]);
    for (i, n) in [-5i64, 0, 3, 8, 20].iter().enumerate() {
        array.set(i, &(key(*n), Rid::new(PageId(*n as i32), 0)));
    }
    let target = key(8);
    assert_eq!(array.lower_bound(5, |(k, _)| cmp.compare(k, &target)), 3, "it takes a comparator for keyed entries");
    let target = key(-100);
    assert_eq!(array.lower_bound(5, |(k, _)| cmp.compare(k, &target)), 0, "it takes a comparator for keyed entries");
}

#[test]
fn s2a_11_it_agrees_with_partition_point_on_random_arrays() {
    let mut rng = Lcg(5);
    for _ in 0..200 {
        let mut values: Vec<i32> = (0..rng.next(20)).map(|_| rng.next(30) as i32).collect();
        values.sort();
        let a = load(&values, 32);
        let target = rng.next(32) as i32;
        assert_eq!(a.lower_bound(values.len(), |e| e.cmp(&target)), values.partition_point(|&v| v < target), "{values:?} {target}");
    }
}

#[test]
fn s2a_11_it_probes_only_log_n_entries() {
    let a = load(&(0..1024).collect::<Vec<_>>(), 1024);
    let mut probes = 0;
    a.lower_bound(1024, |e| {
        probes += 1;
        e.cmp(&700)
    });
    assert!(probes <= 11, "{probes} probes for 1024 entries");
}

// ---- 2a-04 · page layouts ----------------------------------------------------------------------------------------------------------------------

#[test]
fn s2a_12_the_directory_page_layout() {
    assert_eq!(DIRECTORY_MAX_DEPTH_OFFSET, 0, "the directory page layout");
    assert_eq!(DIRECTORY_GLOBAL_DEPTH_OFFSET, 4, "the directory page layout");
    assert_eq!(DIRECTORY_LOCAL_DEPTHS_OFFSET, 8, "the directory page layout");
    assert_eq!(DIRECTORY_BUCKET_PAGE_IDS_OFFSET, 8 + 512, "the directory page layout");
    assert_eq!(DIRECTORY_PAGE_SIZE, 8 + 512 + 2048, "the directory page layout");
}

#[test]
fn s2a_12_the_header_page_layout() {
    assert_eq!(HEADER_DIRECTORY_PAGE_IDS_OFFSET, 0, "the header page layout");
    assert_eq!(HEADER_MAX_DEPTH_OFFSET, 2048, "the header page layout");
    assert_eq!(HEADER_PAGE_SIZE, 2052, "the header page layout");
}

#[test]
fn s2a_12_the_array_sizes_are_two_to_the_depth() {
    assert_eq!(HTABLE_DIRECTORY_ARRAY_SIZE, 512, "the array sizes are two to the depth");
    assert_eq!(HTABLE_HEADER_ARRAY_SIZE, 512, "the array sizes are two to the depth");
    assert_eq!(HTABLE_BUCKET_PAGE_METADATA_SIZE, 8, "the array sizes are two to the depth");
}

#[test]
fn s2a_12_both_pages_fit_in_a_page_with_room_to_spare() {
    assert!(DIRECTORY_PAGE_SIZE <= BUSTUB_PAGE_SIZE, "both pages fit in a page with room to spare: expected `DIRECTORY_PAGE_SIZE <= BUSTUB_PAGE_SIZE`");
    assert!(HEADER_PAGE_SIZE <= BUSTUB_PAGE_SIZE, "both pages fit in a page with room to spare: expected `HEADER_PAGE_SIZE <= BUSTUB_PAGE_SIZE`");
    assert_eq!(BUSTUB_PAGE_SIZE - DIRECTORY_PAGE_SIZE, 5624, "both pages fit in a page with room to spare");
}

#[test]
fn s2a_12_the_offsets_agree_with_the_toolkit() {
    // Writing a local depth and a bucket page id by offset, with the page_bytes helpers, lands where the layout says.
    let mut page = [0u8; BUSTUB_PAGE_SIZE];
    write_u32(&mut page, DIRECTORY_GLOBAL_DEPTH_OFFSET, 3);
    page[DIRECTORY_LOCAL_DEPTHS_OFFSET + 5] = 2;
    write_page_id(&mut page, DIRECTORY_BUCKET_PAGE_IDS_OFFSET + 4 * 5, PageId(42));
    assert_eq!(read_u32(&page, 4), 3, "the offsets agree with the toolkit");
    assert_eq!(page[13], 2, "the offsets agree with the toolkit");
    assert_eq!(read_page_id(&page, 520 + 20), PageId(42), "the offsets agree with the toolkit");
}

// ---- 2a-05 · the toolkit on a real page ----------------------------------------------------------------------------------------------------

#[test]
fn s2a_13_a_sorted_bucket_built_from_the_pieces_survives_the_buffer_pool() {
    // A page with a u32 length at offset 0 and (key, rid) entries after 8 bytes of metadata: a bucket page in all but name.
    type Entry = (GenericKey<8>, Rid);
    let disk = Arc::new(DiskManagerUnlimitedMemory::new());
    let bpm = BufferPoolManager::new(2, disk);
    let page = bpm.new_page();
    let cmp = GenericComparator::<8>;
    let max = array_size(HTABLE_BUCKET_PAGE_METADATA_SIZE, Entry::SIZE);
    let mut rng = Lcg(9);
    let mut model: Vec<i64> = Vec::new();
    {
        let mut guard = bpm.write_page(page);
        let data = guard.get_data_mut();
        write_u32(data, 0, 0);
        write_u32(data, 4, max as u32);
        for _ in 0..200 {
            let n = rng.next(1000) as i64;
            let len = read_u32(data, 0) as usize;
            let mut array = PageArray::<_, Entry>::new(&mut data[HTABLE_BUCKET_PAGE_METADATA_SIZE..]);
            let target = key(n);
            let at = array.lower_bound(len, |(k, _)| cmp.compare(k, &target));
            if at < len && array.get(at).0.get_as_integer() == n {
                continue; // already there
            }
            array.insert_at(at, len, &(key(n), Rid::new(PageId(n as i32), n as u32)));
            write_u32(data, 0, len as u32 + 1);
            model.push(n);
        }
    }
    model.sort();
    // push the page out and bring it back
    let other = bpm.new_page();
    drop(bpm.write_page(other));
    let third = bpm.new_page();
    drop(bpm.write_page(third));
    let guard = bpm.read_page(page);
    let data = guard.get_data();
    let len = read_u32(data, 0) as usize;
    assert_eq!(len, model.len(), "a sorted bucket built from the pieces survives the buffer pool");
    let array = PageArray::<_, Entry>::new(&data[HTABLE_BUCKET_PAGE_METADATA_SIZE..]);
    let got: Vec<i64> = (0..len).map(|i| array.get(i).0.get_as_integer()).collect();
    assert_eq!(got, model, "a sorted bucket built from the pieces survives the buffer pool");
    assert_eq!(array.get(0).1, Rid::new(PageId(model[0] as i32), model[0] as u32), "a sorted bucket built from the pieces survives the buffer pool");
}
