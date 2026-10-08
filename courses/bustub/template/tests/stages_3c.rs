//! Tests for the table heap, index and catalog stages (3c-01 … 3c-06). A test named `s3c_03_…` belongs to stage 3c-03.

use std::sync::Arc;
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::catalog::catalog::Catalog;
use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::index::{generic_key_from_tuple, BPlusTreeIndex, Index, IndexMetadata, IndexType, SchemaComparator};
use bustub::storage::index::generic_key::KeyComparator;
use bustub::storage::page::table_page::TablePage;
use bustub::storage::table::table_heap::TableHeap;
use bustub::storage::table::tuple::{Tuple, TupleMeta};
use bustub::types::type_id::TypeId::*;
use bustub::types::value::Value;

fn bpm(frames: usize) -> BufferPoolManager {
    BufferPoolManager::new(frames, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn meta(is_deleted: bool) -> TupleMeta {
    TupleMeta { ts: 0, is_deleted }
}

fn bytes_tuple(byte: u8, len: usize) -> Tuple {
    Tuple::from_bytes(Rid::default(), &vec![byte; len])
}

/// A tuple read straight from its page (so the insert tests do not depend on `get_tuple`).
fn raw_get(bpm: &BufferPoolManager, rid: Rid) -> (TupleMeta, Tuple) {
    TablePage::new(&bpm.read_page(rid.page_id())[..]).get_tuple(rid).unwrap()
}

fn heap_test_schema() -> Schema {
    Schema::new(vec![Column::new_varchar("a", 20), Column::new("b", SmallInt), Column::new("c", BigInt), Column::new("d", Boolean), Column::new_varchar("e", 16)])
}

fn construct_tuple(schema: &Schema, i: usize) -> Tuple {
    Tuple::new(
        &[Value::varchar(&format!("row{i}")), Value::smallint((i % 100) as i16), Value::bigint(i as i64), Value::boolean(i % 2 == 0), Value::varchar("tail")],
        schema,
    )
}

// ---- 3c-01 · A table heap: inserting ------------------------------------------------------------------------------------------------

#[test]
fn s3c_01_a_new_heap_has_an_empty_first_page() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let first = heap.get_first_page_id();
    assert!(first.is_valid());
    let guard = bpm.read_page(first);
    let page = TablePage::new(&guard[..]);
    assert_eq!((page.get_num_tuples(), page.get_next_page_id()), (0, None), "the page was formatted, not left as zeros");
}

#[test]
fn s3c_01_inserted_tuples_get_consecutive_slots_of_the_first_page() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let first = heap.get_first_page_id();
    for i in 0..5 {
        let rid = heap.insert_tuple(&meta(false), &bytes_tuple(i as u8, 20)).unwrap();
        assert_eq!(rid, Rid::new(first, i), "tuple {i}");
        let (m, t) = raw_get(&bpm, rid);
        assert_eq!((m, t.data()), (meta(false), vec![i as u8; 20].as_slice()));
    }
}

#[test]
fn s3c_01_a_full_page_makes_the_heap_start_and_link_a_new_one() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let first = heap.get_first_page_id();
    // 66 tuples of 100 bytes fill a page exactly (module 3b)
    let rids: Vec<Rid> = (0..70).map(|i| heap.insert_tuple(&meta(false), &bytes_tuple(i as u8, 100)).unwrap()).collect();
    assert!(rids[..66].iter().all(|r| r.page_id() == first));
    let second = rids[66].page_id();
    assert_ne!(second, first);
    assert_eq!(rids[66..].iter().map(|r| (r.page_id(), r.slot_num())).collect::<Vec<_>>(), (0..4).map(|s| (second, s)).collect::<Vec<_>>(), "slots restart at 0 in the new page");
    assert_eq!(TablePage::new(&bpm.read_page(first)[..]).get_next_page_id(), Some(second), "the full page points at the new one");
    assert_eq!(TablePage::new(&bpm.read_page(second)[..]).get_next_page_id(), None);
    for (i, rid) in rids.iter().enumerate() {
        assert_eq!(raw_get(&bpm, *rid).1.data(), vec![i as u8; 100].as_slice(), "tuple {i}");
    }
}

#[test]
fn s3c_01_a_tuple_that_fits_no_page_is_an_error() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let biggest = BUSTUB_PAGE_SIZE - 8 - 24;
    assert!(heap.insert_tuple(&meta(false), &bytes_tuple(0, biggest + 1)).is_err(), "bigger than an empty page can take");
    assert!(heap.insert_tuple(&meta(false), &bytes_tuple(0, BUSTUB_PAGE_SIZE)).is_err());
    let rid = heap.insert_tuple(&meta(false), &bytes_tuple(7, biggest)).unwrap();
    assert_eq!(raw_get(&bpm, rid).1.get_length() as usize, biggest, "the largest tuple that fits");
    // after an error the heap still works, and the next tuple goes to a new page
    let next = heap.insert_tuple(&meta(false), &bytes_tuple(8, 10)).unwrap();
    assert_ne!(next.page_id(), rid.page_id());
}

#[test]
fn s3c_01_a_tuple_too_big_for_the_rest_of_a_page_moves_on_to_a_new_one() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let a = heap.insert_tuple(&meta(false), &bytes_tuple(1, 5000)).unwrap();
    let b = heap.insert_tuple(&meta(false), &bytes_tuple(2, 5000)).unwrap();
    assert_ne!(a.page_id(), b.page_id());
    let c = heap.insert_tuple(&meta(false), &bytes_tuple(3, 100)).unwrap();
    assert_eq!(c.page_id(), b.page_id(), "small tuples go on filling the last page (earlier pages are not revisited)");
}

#[test]
fn s3c_01_the_metadata_is_stored_with_the_tuple() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rid = heap.insert_tuple(&TupleMeta { ts: 42, is_deleted: true }, &bytes_tuple(1, 8)).unwrap();
    assert_eq!(raw_get(&bpm, rid).0, TupleMeta { ts: 42, is_deleted: true });
}

#[test]
fn s3c_01_five_thousand_tuples_in_a_small_pool() {
    let bpm = bpm(50);
    let heap = TableHeap::new(&bpm);
    let schema = heap_test_schema();
    let rids: Vec<Rid> = (0..5000).map(|i| heap.insert_tuple(&meta(false), &construct_tuple(&schema, i)).unwrap()).collect();
    let distinct: std::collections::HashSet<_> = rids.iter().collect();
    assert_eq!(distinct.len(), 5000);
    for i in (0..5000).step_by(97) {
        assert_eq!(raw_get(&bpm, rids[i]).1.get_value(&schema, 2), Value::bigint(i as i64));
    }
    let pages: std::collections::HashSet<PageId> = rids.iter().map(|r| r.page_id()).collect();
    assert!(pages.len() > 10 && pages.len() < 100, "{} pages", pages.len());
}

#[test]
fn s3c_01_threads_inserting_at_once_never_share_a_slot() {
    let bpm = bpm(30);
    let heap = TableHeap::new(&bpm);
    let rids: Vec<Vec<Rid>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..4u8).map(|t| {
            let heap = &heap;
            scope.spawn(move || (0..400).map(|i| heap.insert_tuple(&meta(false), &bytes_tuple(t, 20 + (i % 7))).unwrap()).collect::<Vec<_>>())
        }).collect();
        handles.into_iter().map(|h| h.join().unwrap()).collect()
    });
    let all: std::collections::HashSet<Rid> = rids.iter().flatten().copied().collect();
    assert_eq!(all.len(), 1600, "every rid is unique");
    for (t, mine) in rids.iter().enumerate() {
        for rid in mine {
            assert_eq!(raw_get(&bpm, *rid).1.data()[0], t as u8, "the tuple at {rid:?} is the one this thread inserted");
        }
    }
}

// ---- 3c-02 · Getting and updating -----------------------------------------------------------------------------------------------

#[test]
fn s3c_02_a_tuple_and_its_meta_come_back_by_rid() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rid = heap.insert_tuple(&TupleMeta { ts: 7, is_deleted: false }, &bytes_tuple(5, 30)).unwrap();
    let (m, t) = heap.get_tuple(rid).unwrap();
    assert_eq!((m, t.data(), t.get_rid()), (TupleMeta { ts: 7, is_deleted: false }, vec![5u8; 30].as_slice(), rid));
    assert_eq!(heap.get_tuple_meta(rid).unwrap(), m);
}

#[test]
fn s3c_02_a_bad_rid_is_an_error() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rid = heap.insert_tuple(&meta(false), &bytes_tuple(1, 8)).unwrap();
    let bad = Rid::new(rid.page_id(), rid.slot_num() + 1);
    assert!(heap.get_tuple(bad).is_err());
    assert!(heap.get_tuple_meta(bad).is_err());
    assert!(heap.update_tuple_meta(&meta(true), bad).is_err());
    assert!(heap.update_tuple_in_place(&meta(true), &bytes_tuple(1, 8), bad, None).is_err());
}

#[test]
fn s3c_02_marking_a_tuple_deleted_changes_only_its_meta() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rids: Vec<Rid> = (0..4).map(|i| heap.insert_tuple(&meta(false), &bytes_tuple(i, 12)).unwrap()).collect();
    heap.update_tuple_meta(&TupleMeta { ts: 3, is_deleted: true }, rids[2]).unwrap();
    assert_eq!(heap.get_tuple_meta(rids[2]).unwrap(), TupleMeta { ts: 3, is_deleted: true });
    assert_eq!(heap.get_tuple(rids[2]).unwrap().1.data(), vec![2u8; 12].as_slice(), "the bytes are still there");
    assert!(!heap.get_tuple_meta(rids[1]).unwrap().is_deleted);
}

#[test]
fn s3c_02_an_in_place_update_runs_its_check_under_the_latch() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rid = heap.insert_tuple(&TupleMeta { ts: 1, is_deleted: false }, &bytes_tuple(1, 16)).unwrap();
    // no check: always updates
    assert!(heap.update_tuple_in_place(&TupleMeta { ts: 2, is_deleted: false }, &bytes_tuple(2, 16), rid, None).unwrap());
    assert_eq!(heap.get_tuple(rid).unwrap().1.data(), vec![2u8; 16].as_slice());
    // a check that refuses: nothing changes
    let refuse = |_: &TupleMeta, _: &Tuple, _: Rid| false;
    assert!(!heap.update_tuple_in_place(&meta(true), &bytes_tuple(9, 16), rid, Some(&refuse)).unwrap());
    assert_eq!(heap.get_tuple(rid).unwrap(), (TupleMeta { ts: 2, is_deleted: false }, {
        let mut t = bytes_tuple(2, 16);
        t.set_rid(rid);
        t
    }));
    // a check that looks at the OLD tuple and meta and rid
    let only_ts_2 = |m: &TupleMeta, t: &Tuple, r: Rid| m.ts == 2 && t.data()[0] == 2 && r == rid;
    assert!(heap.update_tuple_in_place(&TupleMeta { ts: 3, is_deleted: false }, &bytes_tuple(3, 16), rid, Some(&only_ts_2)).unwrap());
    assert!(!heap.update_tuple_in_place(&meta(true), &bytes_tuple(4, 16), rid, Some(&only_ts_2)).unwrap(), "the tuple is at ts 3 now: the check fails");
}

#[test]
fn s3c_02_an_in_place_update_must_keep_the_length() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rid = heap.insert_tuple(&meta(false), &bytes_tuple(1, 16)).unwrap();
    assert!(heap.update_tuple_in_place(&meta(false), &bytes_tuple(2, 17), rid, None).is_err());
    assert_eq!(heap.get_tuple(rid).unwrap().1.data(), vec![1u8; 16].as_slice());
}

#[test]
fn s3c_02_every_tuple_of_a_big_table_is_found_by_its_rid() {
    let bpm = bpm(20);
    let heap = TableHeap::new(&bpm);
    let schema = heap_test_schema();
    let rids: Vec<Rid> = (0..2000).map(|i| heap.insert_tuple(&meta(false), &construct_tuple(&schema, i)).unwrap()).collect();
    for (i, rid) in rids.iter().enumerate().rev() {
        let (_, t) = heap.get_tuple(*rid).unwrap();
        assert_eq!(t.get_value(&schema, 0), Value::varchar(&format!("row{i}")));
    }
}

// ---- 3c-03 · The iterator -------------------------------------------------------------------------------------------------------

#[test]
fn s3c_03_an_empty_table_has_nothing_to_iterate() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let mut it = heap.make_iterator();
    assert!(it.is_end());
    assert!(it.next().is_none());
    assert!(heap.make_eager_iterator().is_end());
}

#[test]
fn s3c_03_the_iterator_visits_every_tuple_in_insertion_order_across_pages() {
    let bpm = bpm(20);
    let heap = TableHeap::new(&bpm);
    let schema = heap_test_schema();
    let rids: Vec<Rid> = (0..3000).map(|i| heap.insert_tuple(&meta(false), &construct_tuple(&schema, i)).unwrap()).collect();
    let mut seen = 0;
    for (i, (m, t)) in heap.make_iterator().enumerate() {
        assert_eq!(t.get_rid(), rids[i], "tuple {i} is where insert said");
        assert_eq!(t.get_value(&schema, 2), Value::bigint(i as i64));
        assert!(!m.is_deleted);
        seen += 1;
    }
    assert_eq!(seen, 3000);
}

#[test]
fn s3c_03_a_cursor_can_be_driven_by_hand() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rids: Vec<Rid> = (0..3).map(|i| heap.insert_tuple(&meta(false), &bytes_tuple(i, 10)).unwrap()).collect();
    let mut it = heap.make_iterator();
    for rid in &rids {
        assert!(!it.is_end());
        assert_eq!(it.get_rid(), *rid);
        assert_eq!(it.get_tuple().unwrap().1.get_rid(), *rid);
        it.advance();
    }
    assert!(it.is_end(), "past the last tuple");
    assert!(it.get_tuple().is_err());
}

#[test]
fn s3c_03_deleted_tuples_are_returned_with_their_meta() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    let rids: Vec<Rid> = (0..6).map(|i| heap.insert_tuple(&meta(false), &bytes_tuple(i, 10)).unwrap()).collect();
    for i in [1, 4] {
        heap.update_tuple_meta(&meta(true), rids[i]).unwrap();
    }
    let flags: Vec<bool> = heap.make_iterator().map(|(m, _)| m.is_deleted).collect();
    assert_eq!(flags, vec![false, true, false, false, true, false], "skipping them is the scan executor's job");
}

#[test]
fn s3c_03_an_iterator_stops_where_the_table_ended_when_it_was_made() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    for i in 0..5 {
        heap.insert_tuple(&meta(false), &bytes_tuple(i, 10)).unwrap();
    }
    let mut seen = 0;
    for (_, t) in heap.make_iterator() {
        seen += 1;
        // the Halloween problem: a statement that inserts into the table it scans must not see what it inserts
        heap.insert_tuple(&meta(false), &bytes_tuple(100, 10)).unwrap();
        assert!(t.data()[0] < 100);
    }
    assert_eq!(seen, 5);
    assert_eq!(heap.make_iterator().count(), 10);
}

#[test]
fn s3c_03_the_stopping_point_can_be_a_page_boundary_and_the_eager_iterator_has_none() {
    let bpm = bpm(10);
    let heap = TableHeap::new(&bpm);
    for i in 0..66 {
        heap.insert_tuple(&meta(false), &bytes_tuple(i, 100)).unwrap(); // the first page is exactly full
    }
    let snapshot = heap.make_iterator();
    heap.insert_tuple(&meta(false), &bytes_tuple(200, 100)).unwrap(); // starts the second page
    assert_eq!(snapshot.count(), 66, "the new page's tuple is not part of the snapshot");
    let mut eager = heap.make_eager_iterator();
    let mut n = 0;
    while !eager.is_end() {
        n += 1;
        if n == 10 {
            heap.insert_tuple(&meta(false), &bytes_tuple(201, 100)).unwrap();
        }
        eager.advance();
    }
    assert_eq!(n, 68, "the eager iterator also sees a tuple inserted while it runs");
}

// ---- 3c-04 · Indexes --------------------------------------------------------------------------------------------------------------

fn three_ints() -> Schema {
    Schema::new(vec![Column::new("a", Integer), Column::new("b", Integer), Column::new("c", Integer)])
}

fn key(schema: &Schema, values: &[i32]) -> Tuple {
    Tuple::new(&values.iter().map(|&v| Value::integer(v)).collect::<Vec<_>>(), schema)
}

#[test]
fn s3c_04_index_metadata_knows_its_key_schema() {
    let table = three_ints();
    let m = IndexMetadata::new("idx", "t", &table, vec![2, 0], false);
    assert_eq!((m.get_name(), m.get_table_name(), m.get_key_attrs(), m.get_index_column_count(), m.is_primary_key()), ("idx", "t", &[2u32, 0][..], 2, false));
    let ks = m.get_key_schema();
    assert_eq!(ks.columns().iter().map(|c| c.name()).collect::<Vec<_>>(), vec!["c", "a"]);
    assert_eq!(ks.columns().iter().map(|c| c.offset()).collect::<Vec<_>>(), vec![0, 4], "offsets of the key schema, not the table's");
}

#[test]
fn s3c_04_a_key_tuple_becomes_the_bytes_of_a_fixed_size_key() {
    let ks = Schema::new(vec![Column::new("a", Integer)]);
    let k4 = generic_key_from_tuple::<4>(&key(&ks, &[0x0102_0304]));
    assert_eq!(k4.data, [4, 3, 2, 1]);
    let k16 = generic_key_from_tuple::<16>(&key(&ks, &[7]));
    assert_eq!(k16.data, [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "padded with zeros");
}

#[test]
#[should_panic]
fn s3c_04_a_key_bigger_than_the_index_key_is_a_bug() {
    let ks = Schema::new(vec![Column::new("a", Integer), Column::new("b", Integer)]);
    generic_key_from_tuple::<4>(&key(&ks, &[1, 2]));
}

#[test]
fn s3c_04_keys_compare_column_by_column_as_numbers() {
    let ks = Arc::new(Schema::new(vec![Column::new("a", Integer), Column::new("b", Integer)]));
    let cmp = SchemaComparator::<8>::new(ks.clone());
    let k = |a, b| generic_key_from_tuple::<8>(&key(&ks, &[a, b]));
    use std::cmp::Ordering::*;
    assert_eq!(cmp.compare(&k(1, 5), &k(1, 6)), Less);
    assert_eq!(cmp.compare(&k(1, 6), &k(2, 0)), Less, "the first column decides");
    assert_eq!(cmp.compare(&k(2, 0), &k(1, 100)), Greater);
    assert_eq!(cmp.compare(&k(3, 3), &k(3, 3)), Equal);
    assert_eq!(cmp.compare(&k(-3, 0), &k(2, 0)), Less, "numbers, not bytes: -3 is stored as 0xFFFFFFFD");
    assert_eq!(cmp.compare(&k(0, -1), &k(0, 1)), Less);
}

#[test]
fn s3c_04_an_index_inserts_scans_and_deletes() {
    let bpm = bpm(50);
    let table = three_ints();
    let index = BPlusTreeIndex::<4>::new(IndexMetadata::new("i", "t", &table, vec![0], false), &bpm);
    let ks = index.metadata().get_key_schema().clone();
    for i in 0..500 {
        assert!(index.insert_entry(&key(&ks, &[i * 3]), Rid::new(PageId(1), i as u32)));
    }
    assert!(!index.insert_entry(&key(&ks, &[30]), Rid::new(PageId(9), 9)), "a key is in the index once");
    assert_eq!(index.scan_key(&key(&ks, &[30])), vec![Rid::new(PageId(1), 10)]);
    assert!(index.scan_key(&key(&ks, &[31])).is_empty());
    index.delete_entry(&key(&ks, &[30]));
    assert!(index.scan_key(&key(&ks, &[30])).is_empty());
    index.delete_entry(&key(&ks, &[30])); // deleting a missing key is not an error
    assert_eq!(index.scan_all().len(), 499);
}

#[test]
fn s3c_04_a_scan_returns_rids_in_key_order_even_for_negative_and_composite_keys() {
    let bpm = bpm(50);
    let table = three_ints();
    let index = BPlusTreeIndex::<8>::new(IndexMetadata::new("i", "t", &table, vec![0, 1], false), &bpm);
    let ks = index.metadata().get_key_schema().clone();
    let keys = [(2, 1), (-5, 9), (2, -1), (0, 0), (-5, -9), (7, 7)];
    for (n, (a, b)) in keys.iter().enumerate() {
        index.insert_entry(&key(&ks, &[*a, *b]), Rid::new(PageId(0), n as u32));
    }
    let order: Vec<u32> = index.scan_all().iter().map(|r| r.slot_num()).collect();
    let mut expected: Vec<(usize, (i32, i32))> = keys.iter().copied().enumerate().collect();
    expected.sort_by_key(|(_, k)| *k);
    assert_eq!(order, expected.iter().map(|(n, _)| *n as u32).collect::<Vec<_>>());
    let from: Vec<u32> = index.scan_from(&key(&ks, &[0, 0])).iter().map(|r| r.slot_num()).collect();
    assert_eq!(from, vec![3, 2, 0, 5], "keys from (0, 0) on: (0,0) (2,-1) (2,1) (7,7) are slots 3, 2, 0, 5");
}

// ---- 3c-05 · The catalog: tables --------------------------------------------------------------------------------------------------

#[test]
fn s3c_05_a_created_table_can_be_found_by_name_and_by_oid() {
    let bpm = bpm(20);
    let mut catalog = Catalog::new(&bpm);
    let schema = three_ints();
    let t = catalog.create_table("t1", &schema).unwrap();
    assert_eq!((t.name.as_str(), t.oid, &t.schema), ("t1", 0, &schema));
    assert!(Arc::ptr_eq(&catalog.get_table("t1").unwrap(), &t));
    assert!(Arc::ptr_eq(&catalog.get_table_by_oid(0).unwrap(), &t));
    assert!(catalog.get_table("nope").is_none() && catalog.get_table_by_oid(5).is_none());
}

#[test]
fn s3c_05_oids_are_handed_out_in_creation_order_and_names_are_unique() {
    let bpm = bpm(20);
    let mut catalog = Catalog::new(&bpm);
    let schema = three_ints();
    let oids: Vec<u32> = ["a", "b", "c"].iter().map(|n| catalog.create_table(n, &schema).unwrap().oid).collect();
    assert_eq!(oids, vec![0, 1, 2]);
    assert!(catalog.create_table("b", &schema).is_none(), "the name is taken");
    assert_eq!(catalog.create_table("d", &schema).unwrap().oid, 3, "a refused creation does not use an oid");
    let mut names = catalog.get_table_names();
    names.sort();
    assert_eq!(names, vec!["a", "b", "c", "d"]);
}

#[test]
fn s3c_05_every_table_has_its_own_heap() {
    let bpm = bpm(20);
    let mut catalog = Catalog::new(&bpm);
    let schema = three_ints();
    let (a, b) = (catalog.create_table("a", &schema).unwrap(), catalog.create_table("b", &schema).unwrap());
    assert_ne!(a.table.get_first_page_id(), b.table.get_first_page_id());
    let ra = a.table.insert_tuple(&meta(false), &key(&schema, &[1, 2, 3])).unwrap();
    assert_eq!(a.table.get_tuple(ra).unwrap().1.get_value(&schema, 1), Value::integer(2));
    assert_eq!(b.table.make_iterator().count(), 0);
    assert_eq!(a.table.make_iterator().count(), 1);
}

#[test]
fn s3c_05_a_new_catalog_has_no_tables_and_names_are_case_sensitive() {
    let bpm = bpm(20);
    let mut catalog = Catalog::new(&bpm);
    assert!(catalog.get_table_names().is_empty());
    assert!(catalog.get_table("t").is_none() && catalog.get_table_by_oid(0).is_none());
    let schema = three_ints();
    catalog.create_table("People", &schema).unwrap();
    assert!(catalog.get_table("people").is_none(), "names are compared exactly");
    assert!(catalog.create_table("people", &schema).is_some(), "so People and people are two tables");
    assert_eq!(catalog.get_table("people").unwrap().oid, 1);
}

#[test]
fn s3c_05_many_tables_are_each_found_by_name_and_by_oid() {
    let bpm = bpm(20);
    let mut catalog = Catalog::new(&bpm);
    let schema = three_ints();
    for i in 0..100u32 {
        let t = catalog.create_table(&format!("t{i}"), &schema).unwrap();
        assert_eq!(t.oid, i);
    }
    for i in (0..100u32).rev() {
        let by_name = catalog.get_table(&format!("t{i}")).unwrap();
        let by_oid = catalog.get_table_by_oid(i).unwrap();
        assert!(Arc::ptr_eq(&by_name, &by_oid) && by_oid.name == format!("t{i}"));
    }
    assert_eq!(catalog.get_table_names().len(), 100);
}

// ---- 3c-06 · The catalog: indexes -------------------------------------------------------------------------------------------------

fn table_with_rows<'a>(catalog: &mut Catalog<'a>, name: &str, n: i32) -> Schema {
    let schema = three_ints();
    let info = catalog.create_table(name, &schema).unwrap();
    for i in 0..n {
        info.table.insert_tuple(&meta(false), &key(&schema, &[i, i % 10, i * 2])).unwrap();
    }
    schema
}

#[test]
fn s3c_06_a_new_index_is_filled_with_the_rows_the_table_already_has() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    let schema = table_with_rows(&mut catalog, "t", 300);
    let index = catalog.create_index("t_a", "t", vec![0], false).unwrap().unwrap();
    assert_eq!((index.name.as_str(), index.table_name.as_str(), index.key_size, index.is_primary_key, index.index_oid), ("t_a", "t", 4, false, 0));
    let table = catalog.get_table("t").unwrap();
    let ks = &index.key_schema;
    for i in [0, 17, 299] {
        let rids = index.index.scan_key(&key(ks, &[i]));
        assert_eq!(rids.len(), 1);
        assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&schema, 2), Value::integer(i * 2));
    }
    assert_eq!(index.index.scan_all().len(), 300);
}

#[test]
fn s3c_06_deleted_rows_are_not_indexed_and_duplicate_keys_keep_the_first() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    let schema = three_ints();
    let table = catalog.create_table("t", &schema).unwrap();
    let rids: Vec<Rid> = [5, 6, 7, 5].iter().map(|&v| table.table.insert_tuple(&meta(false), &key(&schema, &[v, 0, 0])).unwrap()).collect();
    table.table.update_tuple_meta(&meta(true), rids[1]).unwrap();
    let index = catalog.create_index("i", "t", vec![0], false).unwrap().unwrap();
    assert_eq!(index.index.scan_all().len(), 2, "5 (once) and 7");
    assert_eq!(index.index.scan_key(&key(&index.key_schema, &[5])), vec![rids[0]], "the later row with key 5 was ignored");
    assert!(index.index.scan_key(&key(&index.key_schema, &[6])).is_empty());
}

#[test]
fn s3c_06_creating_an_index_can_fail_without_an_error() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    table_with_rows(&mut catalog, "t", 10);
    assert!(catalog.create_index("i", "nope", vec![0], false).unwrap().is_none(), "no such table");
    assert!(catalog.create_index("i", "t", vec![0], false).unwrap().is_some());
    assert!(catalog.create_index("i", "t", vec![1], false).unwrap().is_none(), "the table already has an index called i");
    table_with_rows(&mut catalog, "u", 1);
    assert!(catalog.create_index("i", "u", vec![0], false).unwrap().is_some(), "index names are per table");
}

#[test]
fn s3c_06_only_integer_keys_of_at_most_64_bytes() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    let schema = Schema::new(vec![Column::new("n", Integer), Column::new_varchar("s", 10), Column::new("d", Decimal)]);
    catalog.create_table("t", &schema).unwrap();
    assert!(catalog.create_index("i", "t", vec![1], false).is_err(), "a VARCHAR column");
    assert!(catalog.create_index("i", "t", vec![2], false).is_err(), "a DECIMAL column");
    assert!(catalog.create_index("i", "t", vec![], false).is_err(), "no columns");
    let wide = Schema::new((0..17).map(|i| Column::new(&format!("c{i}"), Integer)).collect());
    catalog.create_table("w", &wide).unwrap();
    assert!(catalog.create_index("i", "w", (0..17).collect(), false).is_err(), "17 integers are 68 bytes");
    assert_eq!(catalog.create_index("i", "w", (0..16).collect(), false).unwrap().unwrap().key_size, 64);
}

#[test]
fn s3c_06_indexes_are_found_by_name_by_oid_and_by_table() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    table_with_rows(&mut catalog, "t", 5);
    table_with_rows(&mut catalog, "u", 5);
    let a = catalog.create_index("a", "t", vec![0], false).unwrap().unwrap();
    let b = catalog.create_index("b", "u", vec![0, 1], true).unwrap().unwrap();
    let c = catalog.create_index("c", "t", vec![1], false).unwrap().unwrap();
    assert_eq!((a.index_oid, b.index_oid, c.index_oid), (0, 1, 2));
    assert!(Arc::ptr_eq(&catalog.get_index("a", "t").unwrap(), &a));
    assert!(Arc::ptr_eq(&catalog.get_index_by_oid(1).unwrap(), &b));
    assert!(catalog.get_index("a", "u").is_none() && catalog.get_index("zzz", "t").is_none() && catalog.get_index("a", "nope").is_none());
    assert!(catalog.get_index_by_oid(9).is_none());
    let names: Vec<String> = catalog.get_table_indexes("t").iter().map(|i| i.name.clone()).collect();
    assert_eq!(names, vec!["a", "c"], "in creation order");
    assert!(catalog.get_table_indexes("nope").is_empty());
    assert_eq!((b.key_size, b.is_primary_key, b.index.metadata().get_index_column_count()), (8, true, 2));
}

#[test]
fn s3c_06_a_composite_index_scans_in_key_order() {
    let bpm = bpm(50);
    let mut catalog = Catalog::new(&bpm);
    let schema = table_with_rows(&mut catalog, "t", 100);
    let index = catalog.create_index("ix", "t", vec![1, 0], false).unwrap().unwrap(); // (i % 10, i)
    let table = catalog.get_table("t").unwrap();
    let order: Vec<i64> = index.index.scan_all().iter().map(|r| table.table.get_tuple(*r).unwrap().1.get_value(&schema, 0).as_i64().unwrap()).collect();
    let mut expected: Vec<i64> = (0..100).collect();
    expected.sort_by_key(|i| (i % 10, *i));
    assert_eq!(order, expected);
    let _ = IndexType::BPlusTreeIndex;
}
