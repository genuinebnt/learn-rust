//! Tests for the schema, tuple and table page stages (3b-01 … 3b-06). A test named `s3b_03_…` belongs to stage 3b-03.

use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::page::table_page::TablePage;
use bustub::storage::table::tuple::{Tuple, TupleMeta};
use bustub::types::type_id::TypeId::*;
use bustub::types::value::Value;

fn mixed_schema() -> Schema {
    Schema::new(vec![Column::new("a", Integer), Column::new_varchar("b", 20), Column::new("c", BigInt), Column::new_varchar("d", 16), Column::new("e", Boolean)])
}

fn mixed_values() -> Vec<Value> {
    vec![Value::integer(7), Value::varchar("hi"), Value::bigint(9), Value::varchar("world!"), Value::boolean(true)]
}

fn meta(is_deleted: bool) -> TupleMeta {
    TupleMeta { ts: 0, is_deleted }
}

// ---- 3b-01 · Columns --------------------------------------------------------------------------------------------------------------

#[test]
fn s3b_01_a_fixed_size_column_has_its_types_size() {
    for (t, size) in [(Boolean, 1), (TinyInt, 1), (SmallInt, 2), (Integer, 4), (BigInt, 8), (Decimal, 8), (Timestamp, 8)] {
        let c = Column::new("x", t);
        assert_eq!((c.name(), c.type_id(), c.storage_size(), c.offset()), ("x", t, size, 0), "{t:?}");
        assert!(c.is_inlined(), "{t:?}");
    }
}

#[test]
fn s3b_01_a_varchar_column_has_its_declared_length_and_is_not_inlined() {
    let c = Column::new_varchar("name", 32);
    assert_eq!((c.type_id(), c.storage_size(), c.is_inlined()), (Varchar, 32, false), "a varchar column has its declared length and is not inlined");
}

#[test]
#[should_panic]
fn s3b_01_a_varchar_needs_a_length() {
    Column::new("name", Varchar);
}

#[test]
#[should_panic]
fn s3b_01_the_invalid_type_is_not_a_column_type() {
    Column::new("x", Invalid);
}

#[test]
fn s3b_01_renaming_keeps_everything_else() {
    let c = Column::new_varchar("old", 10);
    let r = c.with_column_name("new");
    assert_eq!((r.name(), r.type_id(), r.storage_size(), r.offset()), ("new", Varchar, 10, 0), "renaming keeps everything else");
    assert_eq!(c.name(), "old", "the original is unchanged");
}

#[test]
fn s3b_01_columns_print_in_two_formats() {
    assert_eq!(Column::new("a", Integer).to_string(true), "a:INTEGER", "columns print in two formats");
    assert_eq!(Column::new_varchar("b", 20).to_string(true), "b:VARCHAR(20)", "columns print in two formats");
    assert_eq!(Column::new("c", BigInt).to_string(false), "Column[c, BIGINT, Offset:0, Length:8]", "columns print in two formats");
    assert_eq!(Column::new_varchar("d", 5).to_string(false), "Column[d, VARCHAR, Offset:0, Length:5]", "columns print in two formats");
}

// ---- 3b-02 · Schemas --------------------------------------------------------------------------------------------------------------

#[test]
fn s3b_02_columns_get_consecutive_offsets_and_a_varchar_takes_four_bytes() {
    let s = mixed_schema();
    let offsets: Vec<u32> = s.columns().iter().map(|c| c.offset()).collect();
    assert_eq!(offsets, vec![0, 4, 8, 16, 20], "a(4) b(offset: 4) c(8) d(offset: 4) e(1)");
    assert_eq!(s.inlined_storage_size(), 21, "columns get consecutive offsets and a varchar takes four bytes");
    assert_eq!(s.column_count(), 5, "columns get consecutive offsets and a varchar takes four bytes");
}

#[test]
fn s3b_02_the_schema_remembers_which_columns_are_not_inlined() {
    let s = mixed_schema();
    assert_eq!(s.uninlined_columns(), &[1, 3], "the schema remembers which columns are not inlined");
    assert_eq!(s.uninlined_column_count(), 2, "the schema remembers which columns are not inlined");
    assert!(!s.is_inlined(), "the schema remembers which columns are not inlined: expected `!s.is_inlined()`");
    let fixed = Schema::new(vec![Column::new("x", Integer), Column::new("y", Decimal)]);
    assert!(fixed.is_inlined() && fixed.uninlined_columns().is_empty(), "the schema remembers which columns are not inlined: expected `fixed.is_inlined() && fixed.uninlined_columns().is_empty()`");
    assert_eq!(fixed.inlined_storage_size(), 12, "the schema remembers which columns are not inlined");
}

#[test]
fn s3b_02_columns_are_found_by_name() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new("b", Integer), Column::new("a", BigInt)]);
    assert_eq!(s.try_col_idx("b"), Some(1), "columns are found by name");
    assert_eq!(s.try_col_idx("a"), Some(0), "the first column with the name");
    assert_eq!(s.try_col_idx("zzz"), None, "columns are found by name");
    assert_eq!(s.col_idx("b"), 1, "columns are found by name");
    assert_eq!(s.column(2).type_id(), BigInt, "columns are found by name");
}

#[test]
#[should_panic]
fn s3b_02_asking_for_a_missing_column_by_name_is_a_bug() {
    mixed_schema().col_idx("nope");
}

#[test]
fn s3b_02_copy_schema_picks_columns_and_recomputes_the_offsets() {
    let s = mixed_schema();
    let k = Schema::copy_schema(&s, &[2, 0]);
    assert_eq!(k.columns().iter().map(|c| c.name()).collect::<Vec<_>>(), vec!["c", "a"], "copy schema picks columns and recomputes the offsets");
    assert_eq!(k.columns().iter().map(|c| c.offset()).collect::<Vec<_>>(), vec![0, 8], "offsets are those of the new schema");
    assert_eq!(k.inlined_storage_size(), 12, "copy schema picks columns and recomputes the offsets");
    assert!(k.is_inlined(), "copy schema picks columns and recomputes the offsets: expected `k.is_inlined()`");
    assert_eq!(s.column(2).offset(), 8, "the source schema is unchanged");
}

#[test]
fn s3b_02_schemas_print_in_two_formats_and_an_empty_schema_is_fine() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new_varchar("b", 20)]);
    assert_eq!(s.to_string(true), "(a:INTEGER, b:VARCHAR(20))", "schemas print in two formats and an empty schema is fine");
    assert_eq!(
        s.to_string(false),
        "Schema[NumColumns:2, IsInlined:0, Length:8] :: (Column[a, INTEGER, Offset:0, Length:4], Column[b, VARCHAR, Offset:4, Length:20])", "schemas print in two formats and an empty schema is fine"
    );
    let e = Schema::new(vec![]);
    assert_eq!((e.column_count(), e.inlined_storage_size(), e.is_inlined()), (0, 0, true), "schemas print in two formats and an empty schema is fine");
    assert_eq!(e.to_string(true), "()", "schemas print in two formats and an empty schema is fine");
}

// ---- 3b-03 · Building a tuple -----------------------------------------------------------------------------------------------------

#[test]
fn s3b_03_a_fixed_size_tuple_is_its_values_one_after_another() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new("b", BigInt), Column::new("c", Boolean)]);
    let t = Tuple::new(&[Value::integer(1), Value::bigint(2), Value::boolean(true)], &s);
    assert_eq!(t.get_length(), 13, "a fixed size tuple is its values one after another");
    assert_eq!(t.data(), &[1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1], "a fixed size tuple is its values one after another");
}

#[test]
fn s3b_03_a_varchar_is_stored_after_the_fixed_part_and_its_slot_holds_where() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new_varchar("b", 20), Column::new("c", BigInt)]);
    let t = Tuple::new(&[Value::integer(7), Value::varchar("hi"), Value::bigint(9)], &s);
    // fixed part: a(4) + offset(4) + c(8) = 16; then the string: length 3 (text + zero byte), 'h', 'i', 0
    assert_eq!(t.get_length(), 16 + 4 + 3, "a varchar is stored after the fixed part and its slot holds where");
    assert_eq!(&t.data()[0..4], &[7, 0, 0, 0], "a varchar is stored after the fixed part and its slot holds where");
    assert_eq!(&t.data()[4..8], &16u32.to_le_bytes(), "the string starts at byte 16");
    assert_eq!(&t.data()[8..16], &9i64.to_le_bytes(), "a varchar is stored after the fixed part and its slot holds where");
    assert_eq!(&t.data()[16..], &[3, 0, 0, 0, b'h', b'i', 0], "a varchar is stored after the fixed part and its slot holds where");
}

#[test]
fn s3b_03_several_varchars_follow_each_other_in_column_order() {
    let s = Schema::new(vec![Column::new_varchar("x", 10), Column::new("n", SmallInt), Column::new_varchar("y", 10)]);
    let t = Tuple::new(&[Value::varchar("ab"), Value::smallint(5), Value::varchar("c")], &s);
    assert_eq!(s.inlined_storage_size(), 10, "several varchars follow each other in column order");
    assert_eq!(&t.data()[0..4], &10u32.to_le_bytes(), "several varchars follow each other in column order");
    assert_eq!(&t.data()[6..10], &17u32.to_le_bytes(), "the second string starts after the first: 10 + (4 + 3)");
    assert_eq!(t.get_length(), 10 + 7 + 6, "several varchars follow each other in column order");
}

#[test]
fn s3b_03_a_null_varchar_takes_only_its_four_byte_marker() {
    let s = Schema::new(vec![Column::new_varchar("x", 10), Column::new("n", Integer)]);
    let t = Tuple::new(&[Value::null(Varchar), Value::integer(1)], &s);
    assert_eq!(t.get_length(), 8 + 4, "a null varchar takes only its four byte marker");
    assert_eq!(&t.data()[8..], &u32::MAX.to_le_bytes(), "a null varchar takes only its four byte marker");
    let u = Tuple::new(&[Value::varchar(""), Value::integer(1)], &s);
    assert_eq!(u.get_length(), 8 + 5, "an empty string is a length and a zero byte; a NULL is not");
}

#[test]
fn s3b_03_a_nulls_slot_holds_its_reserved_pattern() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new("b", Decimal)]);
    let t = Tuple::new(&[Value::null(Integer), Value::null(Decimal)], &s);
    assert_eq!(&t.data()[0..4], &i32::MIN.to_le_bytes(), "a nulls slot holds its reserved pattern");
    assert_eq!(&t.data()[4..12], &f64::MIN.to_le_bytes(), "a nulls slot holds its reserved pattern");
}

#[test]
#[should_panic]
fn s3b_03_a_tuple_needs_one_value_per_column() {
    Tuple::new(&[Value::integer(1)], &mixed_schema());
}

#[test]
#[should_panic]
fn s3b_03_a_value_must_have_its_columns_type() {
    let s = Schema::new(vec![Column::new("a", Integer)]);
    Tuple::new(&[Value::varchar("x")], &s);
}

#[test]
fn s3b_03_a_new_tuple_has_no_record_id_and_can_be_made_from_bytes() {
    let s = Schema::new(vec![Column::new("a", Integer)]);
    let t = Tuple::new(&[Value::integer(5)], &s);
    assert_eq!(t.get_rid(), Rid::default(), "a new tuple has no record id and can be made from bytes");
    let c = Tuple::from_bytes(Rid::new(PageId(3), 4), t.data());
    assert_eq!(c.get_rid(), Rid::new(PageId(3), 4), "a new tuple has no record id and can be made from bytes");
    assert_eq!(c.data(), t.data(), "a new tuple has no record id and can be made from bytes");
    assert_eq!(Tuple::empty().get_length(), 0, "a new tuple has no record id and can be made from bytes");
}

// ---- 3b-04 · Reading a tuple ------------------------------------------------------------------------------------------------------

#[test]
fn s3b_04_every_value_comes_back() {
    let s = mixed_schema();
    let values = mixed_values();
    let t = Tuple::new(&values, &s);
    for (i, v) in values.iter().enumerate() {
        assert_eq!(&t.get_value(&s, i as u32), v, "column {i}");
    }
}

#[test]
fn s3b_04_every_type_and_null_round_trips_through_a_tuple() {
    let s = Schema::new(vec![
        Column::new("b", Boolean),
        Column::new("t", TinyInt),
        Column::new("s", SmallInt),
        Column::new("i", Integer),
        Column::new("l", BigInt),
        Column::new("d", Decimal),
        Column::new("ts", Timestamp),
        Column::new_varchar("v", 50),
    ]);
    let rows = [
        vec![Value::boolean(false), Value::tinyint(-5), Value::smallint(300), Value::integer(-70_000), Value::bigint(1 << 40), Value::decimal(2.5), Value::timestamp(99), Value::varchar("héllo")],
        vec![Value::null(Boolean), Value::null(TinyInt), Value::null(SmallInt), Value::null(Integer), Value::null(BigInt), Value::null(Decimal), Value::null(Timestamp), Value::null(Varchar)],
    ];
    for row in rows {
        let t = Tuple::new(&row, &s);
        let back: Vec<Value> = (0..8).map(|i| t.get_value(&s, i)).collect();
        assert_eq!(back, row, "every type and null round trips through a tuple");
    }
}

#[test]
fn s3b_04_is_null_and_to_string() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new_varchar("b", 10), Column::new("c", Decimal)]);
    let t = Tuple::new(&[Value::integer(4), Value::null(Varchar), Value::decimal(1.5)], &s);
    assert!(!t.is_null(&s, 0) && t.is_null(&s, 1) && !t.is_null(&s, 2), "is null and to string: expected `!t.is_null(&s, 0) && t.is_null(&s, 1) && !t.is_null(&s, 2)`");
    assert_eq!(t.to_string(&s), "(4, <NULL>, 1.500000)", "is null and to string");
    let u = Tuple::new(&[Value::integer(-1), Value::varchar("x y"), Value::decimal(0.0)], &s);
    assert_eq!(u.to_string(&s), "(-1, x y, 0.000000)", "is null and to string");
}

#[test]
fn s3b_04_a_key_tuple_has_the_chosen_columns_under_the_key_schema() {
    let s = mixed_schema();
    let t = Tuple::new(&mixed_values(), &s);
    let key_schema = Schema::copy_schema(&s, &[2, 1]);
    let key = t.key_from_tuple(&s, &key_schema, &[2, 1]);
    assert_eq!(key.get_value(&key_schema, 0), Value::bigint(9), "a key tuple has the chosen columns under the key schema");
    assert_eq!(key.get_value(&key_schema, 1), Value::varchar("hi"), "a key tuple has the chosen columns under the key schema");
    assert_eq!(key.to_string(&key_schema), "(9, hi)", "a key tuple has the chosen columns under the key schema");
}

#[test]
fn s3b_04_a_tuple_serialises_with_a_length_prefix() {
    let s = mixed_schema();
    let t = Tuple::new(&mixed_values(), &s);
    let mut buf = vec![0xEEu8; t.data().len() + 10];
    t.serialize_to(&mut buf);
    assert_eq!(&buf[..4], &(t.get_length() as i32).to_le_bytes(), "a tuple serialises with a length prefix");
    let back = Tuple::deserialize_from(&buf);
    assert_eq!(back.data(), t.data(), "a tuple serialises with a length prefix");
    assert_eq!(back.get_value(&s, 3), Value::varchar("world!"), "a tuple serialises with a length prefix");
}

#[test]
fn s3b_04_many_random_tuples_round_trip() {
    let s = Schema::new(vec![Column::new("a", Integer), Column::new_varchar("b", 30), Column::new("c", BigInt), Column::new_varchar("d", 30)]);
    let mut x = 12345u64;
    let mut next = || { x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407); (x >> 33) as usize };
    for _ in 0..300 {
        let (a, c) = (next() as i32 / 2, next() as i64 * 1_000);
        let (b, d) = ("x".repeat(next() % 20), "é".repeat(next() % 5));
        let row = vec![Value::integer(a), if next() % 4 == 0 { Value::null(Varchar) } else { Value::varchar(&b) }, Value::bigint(c), Value::varchar(&d)];
        let t = Tuple::new(&row, &s);
        assert_eq!((0..4).map(|i| t.get_value(&s, i)).collect::<Vec<_>>(), row, "many random tuples round trip");
    }
}

// ---- 3b-05 · A table page: inserting tuples ---------------------------------------------------------------------------------------

fn fixed_tuple(n: i64, len: usize) -> Tuple {
    Tuple::from_bytes(Rid::default(), &vec![n as u8; len])
}

#[test]
fn s3b_05_a_fresh_page_is_empty() {
    let mut bytes = [0xFFu8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    assert_eq!((page.get_num_tuples(), page.get_num_deleted_tuples(), page.get_next_page_id()), (0, 0, None), "a fresh page is empty");
}

#[test]
fn s3b_05_inserted_tuples_get_consecutive_slots_and_grow_from_the_end_of_the_page() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    assert_eq!(page.get_next_tuple_offset(&meta(false), &fixed_tuple(0, 100)), Some(8092), "inserted tuples get consecutive slots and grow from the end of the page");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(1, 100)), Some(0), "inserted tuples get consecutive slots and grow from the end of the page");
    assert_eq!(page.get_next_tuple_offset(&meta(false), &fixed_tuple(0, 50)), Some(8092 - 50), "inserted tuples get consecutive slots and grow from the end of the page");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(2, 50)), Some(1), "inserted tuples get consecutive slots and grow from the end of the page");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(3, 10)), Some(2), "inserted tuples get consecutive slots and grow from the end of the page");
    assert_eq!(page.get_num_tuples(), 3, "inserted tuples get consecutive slots and grow from the end of the page");
    drop(page);
    assert_eq!(&bytes[8092..8192], &[1u8; 100][..], "the first tuple is at the very end of the page");
    assert_eq!(&bytes[8042..8092], &[2u8; 50][..], "inserted tuples get consecutive slots and grow from the end of the page");
}

#[test]
fn s3b_05_a_page_is_full_when_the_slots_and_the_tuples_would_meet() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    // header 8 + n * (24 + 100) <= 8192  =>  n = 66
    for i in 0..66 {
        assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(i, 100)), Some(i as u16), "tuple {i}");
    }
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(66, 100)), None, "no room for a 67th");
    assert_eq!(page.get_num_tuples(), 66, "a failed insert changes nothing");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(66, 1)), None, "66 tuples of 100 bytes fill the page exactly: not even one byte more");
}

#[test]
fn s3b_05_the_free_space_is_what_is_between_the_slots_and_the_tuples() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    for i in 0..60 {
        page.insert_tuple(&meta(false), &fixed_tuple(i, 100));
    }
    // 8 + 60 * 124 = 7448 used: 744 bytes left, of which a new slot takes 24
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(60, 721)), None, "the free space is what is between the slots and the tuples");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(60, 720)), Some(60), "the free space is what is between the slots and the tuples");
}

#[test]
fn s3b_05_a_tuple_too_big_for_any_page_is_refused_and_the_boundary_is_exact() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(0, 9000)), None, "bigger than the page: not an underflow panic");
    let biggest = BUSTUB_PAGE_SIZE - 8 - 24;
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(0, biggest + 1)), None, "a tuple too big for any page is refused and the boundary is exact");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(0, biggest)), Some(0), "the largest tuple that fits an empty page: 8160 bytes");
    assert_eq!(page.insert_tuple(&meta(false), &fixed_tuple(1, 1)), None, "a tuple too big for any page is refused and the boundary is exact");
}

#[test]
fn s3b_05_the_next_page_id_is_stored_in_the_header() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    page.set_next_page_id(Some(PageId(0)));
    assert_eq!(page.get_next_page_id(), Some(PageId(0)), "page 0 is a real page");
    page.insert_tuple(&meta(false), &fixed_tuple(1, 10));
    assert_eq!(page.get_next_page_id(), Some(PageId(0)), "the next page id is stored in the header");
    page.set_next_page_id(None);
    assert_eq!(page.get_next_page_id(), None, "the next page id is stored in the header");
}

// ---- 3b-06 · Reading and updating tuples in a page --------------------------------------------------------------------------------

fn page_with_three(bytes: &mut [u8; BUSTUB_PAGE_SIZE]) -> TablePage<&mut [u8]> {
    let mut page = TablePage::new(&mut bytes[..]);
    page.init();
    for (i, len) in [30, 12, 77].into_iter().enumerate() {
        page.insert_tuple(&TupleMeta { ts: i as i64, is_deleted: false }, &fixed_tuple(i as i64 + 1, len));
    }
    page
}

#[test]
fn s3b_06_a_tuple_and_its_meta_come_back_by_slot() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let page = page_with_three(&mut bytes);
    for (slot, (len, byte)) in [(30, 1u8), (12, 2), (77, 3)].into_iter().enumerate() {
        let rid = Rid::new(PageId(5), slot as u32);
        let (m, t) = page.get_tuple(rid).unwrap();
        assert_eq!(m, TupleMeta { ts: slot as i64, is_deleted: false }, "a tuple and its meta come back by slot");
        assert_eq!(t.data(), vec![byte; len].as_slice(), "a tuple and its meta come back by slot");
        assert_eq!(t.get_rid(), rid, "the tuple knows where it came from");
        assert_eq!(page.get_tuple_meta(rid).unwrap(), m, "a tuple and its meta come back by slot");
    }
}

#[test]
fn s3b_06_a_slot_past_the_last_tuple_is_an_error_not_a_panic() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = page_with_three(&mut bytes);
    let bad = Rid::new(PageId(1), 3);
    assert!(page.get_tuple(bad).is_err(), "a slot past the last tuple is an error not a panic: expected `page.get_tuple(bad).is_err()`");
    assert!(page.get_tuple_meta(bad).is_err(), "a slot past the last tuple is an error not a panic: expected `page.get_tuple_meta(bad).is_err()`");
    assert!(page.update_tuple_meta(&meta(true), bad).is_err(), "a slot past the last tuple is an error not a panic: expected `page.update_tuple_meta(&meta(true), bad).is_err()`");
    assert!(page.update_tuple_in_place_unsafe(&meta(false), &fixed_tuple(0, 30), bad).is_err(), "a slot past the last tuple is an error not a panic: expected `page.update_tuple_in_place_unsafe(&meta(false), &fixed_tuple(0, 30), bad).is_err()`");
}

#[test]
fn s3b_06_marking_a_tuple_deleted_counts_it_once_and_keeps_its_bytes() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = page_with_three(&mut bytes);
    let rid = Rid::new(PageId(1), 1);
    page.update_tuple_meta(&TupleMeta { ts: 9, is_deleted: true }, rid).unwrap();
    assert_eq!(page.get_num_deleted_tuples(), 1, "marking a tuple deleted counts it once and keeps its bytes");
    assert_eq!(page.get_tuple_meta(rid).unwrap(), TupleMeta { ts: 9, is_deleted: true }, "marking a tuple deleted counts it once and keeps its bytes");
    page.update_tuple_meta(&TupleMeta { ts: 10, is_deleted: true }, rid).unwrap();
    assert_eq!(page.get_num_deleted_tuples(), 1, "deleting a deleted tuple does not count twice");
    let (_, t) = page.get_tuple(rid).unwrap();
    assert_eq!(t.data(), vec![2u8; 12].as_slice(), "the bytes stay: only the flag changed");
    assert_eq!(page.get_num_tuples(), 3, "a deleted tuple still has its slot: record ids stay valid");
    assert!(!page.get_tuple_meta(Rid::new(PageId(1), 0)).unwrap().is_deleted, "marking a tuple deleted counts it once and keeps its bytes: expected `!page.get_tuple_meta(Rid::new(PageId(1), 0)).unwrap().is_deleted`");
}

#[test]
fn s3b_06_a_tuple_of_the_same_length_can_be_replaced_in_place() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = page_with_three(&mut bytes);
    let rid = Rid::new(PageId(1), 2);
    page.update_tuple_in_place_unsafe(&TupleMeta { ts: 5, is_deleted: false }, &fixed_tuple(9, 77), rid).unwrap();
    let (m, t) = page.get_tuple(rid).unwrap();
    assert_eq!((m.ts, t.data()), (5, vec![9u8; 77].as_slice()), "a tuple of the same length can be replaced in place");
    assert_eq!(page.get_tuple(Rid::new(PageId(1), 1)).unwrap().1.data(), vec![2u8; 12].as_slice(), "its neighbours are untouched");
    page.update_tuple_in_place_unsafe(&meta(true), &fixed_tuple(9, 77), rid).unwrap();
    assert_eq!(page.get_num_deleted_tuples(), 1, "a tuple of the same length can be replaced in place");
}

#[test]
fn s3b_06_a_tuple_of_another_length_is_refused_and_changes_nothing() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = page_with_three(&mut bytes);
    let rid = Rid::new(PageId(1), 0);
    let before = page.get_tuple(rid).unwrap();
    assert!(page.update_tuple_in_place_unsafe(&meta(true), &fixed_tuple(7, 31), rid).is_err(), "a tuple of another length is refused and changes nothing: expected `page.update_tuple_in_place_unsafe(&meta(true), &fixed_tuple(7, 31), rid).is_err()`");
    assert!(page.update_tuple_in_place_unsafe(&meta(true), &fixed_tuple(7, 29), rid).is_err(), "a tuple of another length is refused and changes nothing: expected `page.update_tuple_in_place_unsafe(&meta(true), &fixed_tuple(7, 29), rid).is_err()`");
    assert_eq!(page.get_tuple(rid).unwrap(), before, "a tuple of another length is refused and changes nothing");
    assert_eq!(page.get_num_deleted_tuples(), 0, "a refused update does not mark anything deleted");
}
