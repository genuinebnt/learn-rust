from _c import C
M3F, M3G, M3H = "17-aggregation-and-joins", "18-sorting-limits-and-windows", "19-optimizer-rules"
CH = []

CH.append(C("3f-c1", M3F, "90-challenge-merge-join", "build", "Challenge: merge join", "medium", "stages_3f::s3f_c1",
  ["joining two sorted inputs in one pass, including many-to-many matches","producing output in a deterministic order"],
  ["join-algorithms","model-based-testing"],
  "`merge_join` in `src/execution/merge_join.rs`: join two lists of `(key, payload)` that are both **sorted by key** (duplicates allowed) and return the pairs of payloads whose keys are equal. A key that appears `a` times on the left and `b` times on the right produces `a * b` pairs. Output order: by left row, and within one left row by right row.",
  "A merge join needs no hash table and no random access, which is why it wins when the inputs are already sorted (an index scan, the output of a sort) and why every database has one. The part that goes wrong is the duplicates: a naive two-pointer merge advances both sides on a match and misses the cross product.",
  ["Both inputs are non-decreasing in key.","The output lists `(left_payload, right_payload)` for every pair of rows with equal keys, ordered as a nested loop over the left then the right would produce them.","It runs in `O(|left| + |right| + |output|)`."],
  ["Every output pair has equal keys; every equal-key pair is output exactly once.","The output length is the sum over keys of `count_left * count_right`."],
  ["The result equals a nested-loop join on the same inputs, in the same order.","Swapping the inputs swaps each pair.","Adding a row with a key the other side lacks changes nothing."],
  ["L=[(1,a),(2,b),(2,c)], R=[(2,x),(2,y),(3,z)] -> (b,x) (b,y) (c,x) (c,y)"],
  ["Matches with duplicates on one and both sides.","Empty inputs and disjoint keys.","A large merge finishing quickly.","A property against a nested loop."],
  src=("src/execution/merge_join.rs", '''
//! Joining two key-sorted inputs.

/// `(key, payload)` rows, sorted by key. Returns `(left payload, right payload)` for every pair with equal keys, ordered by left row then right row.
pub fn merge_join(left: &[(i64, u32)], right: &[(i64, u32)]) -> Vec<(u32, u32)> {
    // @begin 3f-c1
    let mut out = Vec::new();
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        match left[i].0.cmp(&right[j].0) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                let key = left[i].0;
                let j_end = j + right[j..].iter().take_while(|r| r.0 == key).count();
                while i < left.len() && left[i].0 == key {
                    for r in &right[j..j_end] {
                        out.push((left[i].1, r.1));
                    }
                    i += 1;
                }
                j = j_end;
            }
        }
    }
    out
    //~ todo!("3f-c1: advance the smaller side; on equal keys output the cross product of the two runs of equal keys")
    // @end
}
'''),
  test=("tests/stages_3f.rs", '''
use bustub::execution::merge_join::merge_join;

#[test]
fn s3f_c1_duplicates_on_both_sides_give_the_cross_product() {
    let l = [(1, 10), (2, 11), (2, 12)];
    let r = [(2, 20), (2, 21), (3, 22)];
    assert_eq!(merge_join(&l, &r), vec![(11, 20), (11, 21), (12, 20), (12, 21)]);
}

#[test]
fn s3f_c1_disjoint_and_empty_inputs() {
    assert_eq!(merge_join(&[(1, 1)], &[(2, 2)]), vec![]);
    assert_eq!(merge_join(&[], &[(2, 2)]), vec![]);
    assert_eq!(merge_join(&[(1, 1)], &[]), vec![]);
}

#[test]
fn s3f_c1_every_key_matches_in_turn() {
    let l: Vec<_> = (0..5).map(|k| (k, k as u32)).collect();
    let r: Vec<_> = (0..5).map(|k| (k, 100 + k as u32)).collect();
    assert_eq!(merge_join(&l, &r), (0..5u32).map(|k| (k, 100 + k)).collect::<Vec<_>>());
}

#[test]
fn s3f_c1_a_large_join_is_linear_not_quadratic() {
    let l: Vec<_> = (0..200_000i64).map(|k| (k, k as u32)).collect();
    let r: Vec<_> = (0..200_000i64).map(|k| (k * 2, k as u32)).collect();
    let t = std::time::Instant::now();
    let out = merge_join(&l, &r);
    assert_eq!(out.len(), 100_000);
    assert!(t.elapsed() < std::time::Duration::from_secs(3), "took {:?}", t.elapsed());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the same pairs, in the same order, as a nested-loop join.
    #[test]
    fn s3f_c1_property_equals_a_nested_loop(mut l in proptest::collection::vec(0i64..6, 0..12), mut r in proptest::collection::vec(0i64..6, 0..12)) {
        l.sort();
        r.sort();
        let left: Vec<(i64, u32)> = l.iter().enumerate().map(|(i, &k)| (k, i as u32)).collect();
        let right: Vec<(i64, u32)> = r.iter().enumerate().map(|(i, &k)| (k, 100 + i as u32)).collect();
        let mut want = Vec::new();
        for a in &left { for b in &right { if a.0 == b.0 { want.push((a.1, b.1)); } } }
        prop_assert_eq!(merge_join(&left, &right), want);
    }
}
''')))

CH.append(C("3f-c2", M3F, "91-challenge-not-in-and-the-null", "build", "Challenge: NOT IN and the NULL", "medium", "stages_3f::s3f_c2",
  ["semi and anti joins","the NULL trap of NOT IN, against NOT EXISTS"],
  ["sql-types-and-three-valued-logic","join-algorithms","model-based-testing"],
  "`semi_join`, `anti_join` and `not_in` in `src/execution/semi_join.rs`: given a list of left keys and a list of right keys (both `Option<i64>`, `None` is NULL), return the **indexes of the left rows** that survive. `semi_join` is `x IN (right)` and `EXISTS`; `anti_join` is `NOT EXISTS (... WHERE r = x)`; `not_in` is `x NOT IN (right)`, which is **not** the same.",
  "`NOT IN` with a NULL in the subquery returns no rows at all: for every `x`, `x <> NULL` is unknown, so no row can be proven to be absent. This is the most famous trap in SQL, and the reason `NOT EXISTS` exists. A hash anti join must implement both, and know which one the query asked for.",
  ["`semi_join(left, right)`: rows whose key is non-NULL and equals some non-NULL right key.","`anti_join(left, right)` (NOT EXISTS): rows with **no** matching right key; a NULL left key matches nothing, so it is kept.","`not_in(left, right)`: if `right` is empty, every row (even NULL keys) is kept; otherwise, if `right` contains a NULL, no row is kept; otherwise rows with a non-NULL key that is not in `right`."],
  ["Results are indexes in increasing order, without repeats.","`semi_join` and `anti_join` partition the left rows."],
  ["`anti_join` and `not_in` agree when `right` has no NULLs and `left` has no NULLs.","Adding a NULL to `right` never changes `semi_join` or `anti_join`, and makes `not_in` empty (unless `right` was empty).","`semi_join(left, right)` is a subset of `semi_join(left, right + more)`."],
  ["left [1, 2, NULL], right [2, 3]: semi [1]; anti [0, 2]; not_in [0]","right [2, NULL]: semi [1]; anti [0, 2]; not_in []"],
  ["Each operation with and without NULLs.","The empty right side.","A property against a three-valued-logic model."],
  src=("src/execution/semi_join.rs", '''
//! Semi and anti joins, and the NULL trap of NOT IN.

use std::collections::HashSet;

pub fn semi_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| left[i].is_some_and(|k| keys.contains(&k))).collect()
    //~ todo!("3f-c2: left rows with a non-NULL key found among the non-NULL right keys")
    // @end
}

pub fn anti_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| !left[i].is_some_and(|k| keys.contains(&k))).collect()
    //~ todo!("3f-c2: left rows with no match (NULL keys never match, so they stay)")
    // @end
}

pub fn not_in(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    if right.is_empty() {
        return (0..left.len()).collect();
    }
    if right.iter().any(|r| r.is_none()) {
        return Vec::new();
    }
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| left[i].is_some_and(|k| !keys.contains(&k))).collect()
    //~ todo!("3f-c2: NOT IN: everything for an empty right side, nothing if it has a NULL, else the non-NULL keys that are absent")
    // @end
}
'''),
  test=("tests/stages_3f.rs", '''
use bustub::execution::semi_join::{anti_join, not_in, semi_join};

#[test]
fn s3f_c2_without_nulls_in_the_subquery() {
    let left = [Some(1), Some(2), None];
    let right = [Some(2), Some(3)];
    assert_eq!(semi_join(&left, &right), vec![1]);
    assert_eq!(anti_join(&left, &right), vec![0, 2]);
    assert_eq!(not_in(&left, &right), vec![0], "a NULL left key is not provably absent");
}

#[test]
fn s3f_c2_a_null_in_the_subquery_empties_not_in_but_not_not_exists() {
    let left = [Some(1), Some(2), None];
    let right = [Some(2), None];
    assert_eq!(semi_join(&left, &right), vec![1]);
    assert_eq!(anti_join(&left, &right), vec![0, 2]);
    assert_eq!(not_in(&left, &right), Vec::<usize>::new());
}

#[test]
fn s3f_c2_an_empty_subquery_keeps_everything_for_not_in() {
    let left = [Some(1), None];
    assert_eq!(not_in(&left, &[]), vec![0, 1], "NOT IN over nothing is true for every row, NULL or not");
    assert_eq!(semi_join(&left, &[]), Vec::<usize>::new());
    assert_eq!(anti_join(&left, &[]), vec![0, 1]);
}

#[test]
fn s3f_c2_no_left_rows() {
    assert!(semi_join(&[], &[Some(1)]).is_empty());
    assert!(not_in(&[], &[Some(1)]).is_empty());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against three-valued logic written out: IN is true/unknown/false, and NOT IN keeps a row only when `NOT (x IN right)` is true.
    #[test]
    fn s3f_c2_property_matches_three_valued_logic(left in proptest::collection::vec(proptest::option::of(0i64..4), 0..8), right in proptest::collection::vec(proptest::option::of(0i64..4), 0..5)) {
        // x IN right: Some(true) if equal to some non-NULL; Some(false) if right is empty or (x non-NULL and all non-NULL differ and no NULL); None (unknown) otherwise
        let in_result = |x: Option<i64>| -> Option<bool> {
            if right.is_empty() { return Some(false); }
            let Some(x) = x else { return None };
            if right.iter().any(|r| *r == Some(x)) { Some(true) }
            else if right.iter().any(|r| r.is_none()) { None } else { Some(false) }
        };
        let want_not_in: Vec<usize> = (0..left.len()).filter(|&i| in_result(left[i]) == Some(false)).collect();
        prop_assert_eq!(not_in(&left, &right), want_not_in);
        let want_semi: Vec<usize> = (0..left.len()).filter(|&i| in_result(left[i]) == Some(true)).collect();
        prop_assert_eq!(semi_join(&left, &right), want_semi.clone());
        let want_anti: Vec<usize> = (0..left.len()).filter(|i| !want_semi.contains(i)).collect();
        prop_assert_eq!(anti_join(&left, &right), want_anti);
    }
}
''')))

CH.append(C("3f-c3", M3F, "92-challenge-grace-hash-join", "build", "Challenge: Grace hash join", "medium", "stages_3f::s3f_c3",
  ["partitioning both inputs by a hash of the join key so each partition fits in memory","joining partition by partition"],
  ["join-algorithms","hash-aggregation","hashing-values-and-keys"],
  "`partition` and `grace_join` in `src/execution/grace_join.rs`: `partition(rows, k)` splits rows of `(key, payload)` into `k` buckets by a hash of the key (given: `bucket_of(key, k)`); `grace_join(left, right, k)` joins corresponding buckets of the two inputs with an in-memory hash table and returns all pairs of payloads with equal keys.",
  "When a hash table does not fit in memory, a hash join spills: both inputs are partitioned to disk by the same hash function, and then each pair of partitions (which does fit) is joined on its own. The one fact that makes it work is that rows with equal keys land in the same partition on both sides.",
  ["`bucket_of(key, k)` is deterministic and below `k`.","`partition(rows, k)` returns `k` vectors; row order within a bucket is the input order.","`grace_join(left, right, k)` returns every `(left payload, right payload)` with equal keys, once, in any order."],
  ["Every input row is in exactly one bucket, the one `bucket_of` names.","Rows with equal keys are in the same bucket.","`grace_join` never builds a hash table over more than one bucket's rows at a time."],
  ["The result (as a multiset) equals a nested-loop join, for every `k >= 1`.","Changing `k` changes the buckets but never the result.","The sizes of the buckets add up to the input size."],
  ["k = 3: rows with key 5 on both sides are in the same bucket and joined there"],
  ["Partitioning properties.","Join results for several `k`.","A property against a nested loop."],
  src=("src/execution/grace_join.rs", '''
//! A Grace hash join: partition both sides, then join each pair of partitions in memory.

use std::collections::HashMap;

pub type Row = (i64, u32);

/// The bucket of `key` among `k` buckets (`k >= 1`).
pub fn bucket_of(key: i64, k: usize) -> usize {
    let mut x = key as u64 ^ 0x9E37_79B9_7F4A_7C15;
    x = (x ^ (x >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    ((x ^ (x >> 31)) % k as u64) as usize
}

pub fn partition(rows: &[Row], k: usize) -> Vec<Vec<Row>> {
    // @begin 3f-c3
    let mut buckets = vec![Vec::new(); k];
    for &r in rows {
        buckets[bucket_of(r.0, k)].push(r);
    }
    buckets
    //~ todo!("3f-c3: send each row to the bucket of its key")
    // @end
}

pub fn grace_join(left: &[Row], right: &[Row], k: usize) -> Vec<(u32, u32)> {
    // @begin 3f-c3
    let (lp, rp) = (partition(left, k), partition(right, k));
    let mut out = Vec::new();
    for (l, r) in lp.iter().zip(&rp) {
        let mut table: HashMap<i64, Vec<u32>> = HashMap::new();
        for &(key, payload) in l {
            table.entry(key).or_default().push(payload);
        }
        for &(key, rp) in r {
            if let Some(ls) = table.get(&key) {
                out.extend(ls.iter().map(|&lp| (lp, rp)));
            }
        }
    }
    out
    //~ todo!("3f-c3: for each pair of buckets, build a table on the left and probe with the right")
    // @end
}
'''),
  test=("tests/stages_3f.rs", '''
use bustub::execution::grace_join::{bucket_of, grace_join, partition};

#[test]
fn s3f_c3_equal_keys_share_a_bucket_and_nothing_is_lost() {
    let rows: Vec<(i64, u32)> = (0..100).map(|i| ((i % 7) as i64, i as u32)).collect();
    let parts = partition(&rows, 5);
    assert_eq!(parts.len(), 5);
    assert_eq!(parts.iter().map(Vec::len).sum::<usize>(), 100);
    for (b, p) in parts.iter().enumerate() {
        assert!(p.iter().all(|r| bucket_of(r.0, 5) == b));
    }
    assert!(parts.iter().all(|p| p.windows(2).all(|w| w[0].1 < w[1].1)), "input order is kept inside a bucket");
}

#[test]
fn s3f_c3_the_join_of_two_small_inputs() {
    let l = [(1, 10), (2, 11), (2, 12)];
    let r = [(2, 20), (3, 21), (2, 22)];
    let mut got = grace_join(&l, &r, 3);
    got.sort();
    assert_eq!(got, vec![(11, 20), (11, 22), (12, 20), (12, 22)]);
}

#[test]
fn s3f_c3_a_single_partition_is_a_plain_hash_join() {
    let l = [(1, 1), (1, 2)];
    let r = [(1, 9)];
    let mut got = grace_join(&l, &r, 1);
    got.sort();
    assert_eq!(got, vec![(1, 9), (2, 9)]);
}

#[test]
fn s3f_c3_disjoint_keys_join_to_nothing_whatever_the_partition_count() {
    let l = [(1, 1), (2, 2)];
    let r = [(3, 3), (4, 4)];
    for k in [1, 2, 7, 64] {
        assert_eq!(grace_join(&l, &r, k), Vec::<(u32, u32)>::new(), "k = {k}");
    }
    assert_eq!(grace_join(&[], &r, 4), Vec::<(u32, u32)>::new());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the multiset of pairs equals a nested-loop join, whatever the number of partitions.
    #[test]
    fn s3f_c3_property_equals_a_nested_loop_for_every_k(l in proptest::collection::vec(0i64..6, 0..12), r in proptest::collection::vec(0i64..6, 0..12), k in 1usize..7) {
        let left: Vec<(i64, u32)> = l.iter().enumerate().map(|(i, &x)| (x, i as u32)).collect();
        let right: Vec<(i64, u32)> = r.iter().enumerate().map(|(i, &x)| (x, 100 + i as u32)).collect();
        let mut want = Vec::new();
        for a in &left { for b in &right { if a.0 == b.0 { want.push((a.1, b.1)); } } }
        want.sort();
        let mut got = grace_join(&left, &right, k);
        got.sort();
        prop_assert_eq!(got, want);
    }
}
''')))

CH.append(C("3f-c4", M3F, "93-challenge-the-average-that-counts-nulls", "debug", "Challenge: the average that counts NULLs", "easy", "stages_3f::s3f_c4",
  ["finding the SQL rule that aggregates skip NULLs, broken in one place"],
  ["hash-aggregation","sql-types-and-three-valued-logic","property-testing-and-fuzzing"],
  "`src/execution/aggregates.rs` has `count_star`, `count_col`, `sum` and `avg` over a column that may contain NULLs. Three are right; `avg` is wrong on columns with NULLs. Find the bug and fix it.",
  "The rule is one sentence: every aggregate except `COUNT(*)` ignores NULLs, and the aggregate of nothing but NULLs is NULL (zero for counts). An average computed as `SUM / COUNT(*)` is wrong exactly when the column has NULLs, which is exactly when a report is wrong without anyone noticing.",
  ["`count_star` counts all rows. `count_col` counts non-NULL values.","`sum` adds the non-NULL values; `None` when there are none.","`avg` is the sum of the non-NULL values divided by their count; `None` when there are none."],
  ["`avg * count_col == sum` (up to floating-point error) when `count_col > 0`.","`count_col <= count_star`."],
  ["Adding NULLs to the column changes `count_star` and nothing else.","Removing the NULLs first gives the same `sum`, `count_col` and `avg`.","A column of only NULLs: `sum` and `avg` are `None`, `count_col` is 0."],
  ["[1, NULL, 3] -> count_star 3, count_col 2, sum 4, avg 2.0","[NULL, NULL] -> 2, 0, None, None"],
  ["Columns with and without NULLs.","All NULLs and empty.","A property: NULLs are invisible to everything but `count_star`."],
  src=("src/execution/aggregates.rs", '''
//! The standard aggregates over a nullable column.

pub fn count_star(values: &[Option<i64>]) -> usize {
    values.len()
}

pub fn count_col(values: &[Option<i64>]) -> usize {
    values.iter().flatten().count()
}

pub fn sum(values: &[Option<i64>]) -> Option<i64> {
    values.iter().flatten().copied().reduce(|a, b| a.wrapping_add(b))
}

pub fn avg(values: &[Option<i64>]) -> Option<f64> {
    // @begin 3f-c4
    let n = count_col(values);
    if n == 0 {
        return None;
    }
    Some(sum(values)? as f64 / n as f64)
    //~ let total = sum(values)?;
    //~ Some(total as f64 / count_star(values) as f64)
    // @end
}
'''),
  test=("tests/stages_3f.rs", '''
use bustub::execution::aggregates::{avg, count_col, count_star, sum};

#[test]
fn s3f_c4_nulls_are_skipped_by_everything_but_count_star() {
    let v = [Some(1), None, Some(3)];
    assert_eq!((count_star(&v), count_col(&v), sum(&v)), (3, 2, Some(4)));
    assert_eq!(avg(&v), Some(2.0));
}

#[test]
fn s3f_c4_a_column_of_nulls_has_no_sum_and_no_average() {
    let v = [None, None];
    assert_eq!((count_star(&v), count_col(&v), sum(&v), avg(&v)), (2, 0, None, None));
    assert_eq!(avg(&[]), None);
}

#[test]
fn s3f_c4_no_nulls_is_the_ordinary_mean() {
    assert_eq!(avg(&[Some(2), Some(4), Some(9)]), Some(5.0));
}

#[test]
fn s3f_c4_the_average_is_not_rounded_and_a_zero_sum_is_not_null() {
    assert_eq!(avg(&[Some(1), Some(2)]), Some(1.5));
    assert_eq!(avg(&[Some(-1), None, Some(-2)]), Some(-1.5));
    assert_eq!(sum(&[Some(-3), Some(3)]), Some(0));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: removing the NULLs first changes nothing but `count_star`, and the average is sum over non-NULL count.
    #[test]
    fn s3f_c4_property_nulls_are_invisible_except_to_count_star(v in proptest::collection::vec(proptest::option::of(-50i64..50), 0..12)) {
        let clean: Vec<Option<i64>> = v.iter().flatten().map(|&x| Some(x)).collect();
        prop_assert_eq!(sum(&v), sum(&clean));
        prop_assert_eq!(count_col(&v), clean.len());
        prop_assert_eq!(avg(&v), avg(&clean));
        prop_assert!(count_col(&v) <= count_star(&v));
        if let Some(a) = avg(&v) { prop_assert!((a * count_col(&v) as f64 - sum(&v).unwrap() as f64).abs() < 1e-6); }
    }
}
''')))

CH.append(C("3f-c5", M3F, "94-challenge-grouping-sorted-input", "build", "Challenge: grouping sorted input", "easy", "stages_3f::s3f_c5",
  ["a streaming (sort-based) group by that holds one group at a time","detecting that the input was not sorted"],
  ["hash-aggregation","iterators-and-closures"],
  "`stream_group_sums` in `src/execution/stream_group.rs`: given rows `(key, value)` **sorted by key**, return one `(key, sum, count)` per group, in key order, using memory for one group only. If the keys ever decrease, return `Err(NotSorted { at })` with the index of the first row that is out of order.",
  "When the input is already sorted (an index scan, the output of a sort or of a merge join), grouping does not need a hash table: a group ends when the key changes. It uses constant memory and can start emitting at once. The price is a precondition, and a good implementation checks it rather than quietly returning wrong groups.",
  ["Equal keys must be adjacent; a key that decreases is an error at that row's index.","The output has one entry per distinct key, in input order.","Sums wrap on overflow."],
  ["The counts add up to the number of rows; each key appears once in the output.","Output keys are strictly increasing."],
  ["The result equals a hash group-by followed by sorting by key.","Splitting the input between two groups and grouping each part gives the same entries (apart from the shared key).","An unsorted input is reported at its first decrease, never grouped."],
  ["[(1,5),(1,7),(2,1)] -> [(1,12,2),(2,1,1)]","[(2,1),(1,1)] -> NotSorted { at: 1 }"],
  ["Groups of various sizes.","Unsorted input.","A property against a hash group-by."],
  src=("src/execution/stream_group.rs", '''
//! Grouping rows that arrive sorted by key.

#[derive(Debug, PartialEq, Eq)]
pub struct NotSorted {
    pub at: usize,
}

/// `(key, sum, count)` per group.
pub fn stream_group_sums(rows: &[(i64, i64)]) -> Result<Vec<(i64, i64, usize)>, NotSorted> {
    // @begin 3f-c5
    let mut out: Vec<(i64, i64, usize)> = Vec::new();
    for (i, &(key, value)) in rows.iter().enumerate() {
        match out.last_mut() {
            Some(g) if g.0 == key => {
                g.1 = g.1.wrapping_add(value);
                g.2 += 1;
            }
            Some(g) if g.0 > key => return Err(NotSorted { at: i }),
            _ => out.push((key, value, 1)),
        }
    }
    Ok(out)
    //~ todo!("3f-c5: extend the current group while the key repeats; start a new one when it grows; refuse a key that shrinks")
    // @end
}
'''),
  test=("tests/stages_3f.rs", '''
use bustub::execution::stream_group::{stream_group_sums, NotSorted};
use std::collections::BTreeMap;

#[test]
fn s3f_c5_groups_of_adjacent_equal_keys() {
    assert_eq!(stream_group_sums(&[(1, 5), (1, 7), (2, 1)]), Ok(vec![(1, 12, 2), (2, 1, 1)]));
}

#[test]
fn s3f_c5_empty_and_single_row_inputs() {
    assert_eq!(stream_group_sums(&[]), Ok(vec![]));
    assert_eq!(stream_group_sums(&[(9, -4)]), Ok(vec![(9, -4, 1)]));
}

#[test]
fn s3f_c5_a_decreasing_key_is_reported_at_its_row() {
    assert_eq!(stream_group_sums(&[(2, 1), (1, 1)]), Err(NotSorted { at: 1 }));
    assert_eq!(stream_group_sums(&[(1, 1), (2, 1), (2, 1), (1, 1)]), Err(NotSorted { at: 3 }));
}

#[test]
fn s3f_c5_negative_keys_and_a_long_run() {
    let mut rows: Vec<(i64, i64)> = vec![(-3, 1); 50];
    rows.push((-1, 7));
    assert_eq!(stream_group_sums(&rows), Ok(vec![(-3, 50, 50), (-1, 7, 1)]));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals a hash group-by sorted by key, whenever the input is sorted.
    #[test]
    fn s3f_c5_property_equals_a_hash_group_by(mut rows in proptest::collection::vec((0i64..5, -9i64..9), 0..20)) {
        rows.sort_by_key(|r| r.0);
        let mut m: BTreeMap<i64, (i64, usize)> = BTreeMap::new();
        for &(k, v) in &rows { let e = m.entry(k).or_insert((0, 0)); e.0 += v; e.1 += 1; }
        let want: Vec<_> = m.into_iter().map(|(k, (s, c))| (k, s, c)).collect();
        prop_assert_eq!(stream_group_sums(&rows), Ok(want));
    }
}
''')))

CH.append(C("3g-c1", M3G, "90-challenge-planning-an-external-sort", "build", "Challenge: planning an external sort", "easy", "stages_3g::s3g_c1",
  ["the cost model of an external merge sort","computing passes without floating-point logarithms"],
  ["external-merge-sort","performance-tests-and-measuring"],
  "`plan_sort` in `src/execution/sort_plan.rs`: given `pages` (the size of the input) and `buffer` (pages of memory), return how an external merge sort would go: the number of initial sorted runs (`ceil(pages / buffer)`), the number of **passes** (pass 0 makes the runs; each merge pass merges up to `buffer - 1` runs at a time), and the total pages read plus written (`2 * pages * passes`). `None` if `buffer < 3` (nothing can be merged) or `pages == 0` has zero passes.",
  "A query optimiser must know what a sort will cost before it chooses a plan, and the formula `1 + ceil(log_{B-1}(ceil(N/B)))` is easy to get wrong with floating point (`log` of an exact power of the base rounds the wrong way and costs an extra pass). Counting passes by simulation is exact and shows what the algorithm does.",
  ["`runs0 = ceil(pages / buffer)`.","`passes` = 1 (the run-creation pass) plus the number of merge passes: repeatedly replace `r` runs by `ceil(r / (buffer - 1))` until one run is left.","`io_pages = 2 * pages * passes`. For `pages == 0`: no runs, zero passes, zero I/O."],
  ["The last merge pass ends with exactly one run.","`passes >= 1` for any non-empty input."],
  ["More memory never needs more passes.","A larger input never needs fewer passes.","If `pages <= buffer`, there is one pass (the sort happens in memory)."],
  ["pages 100, buffer 10: runs 10, merge fan-in 9 -> 10 -> 2 -> 1: passes 1 + 3 = 4, io 800","pages 8, buffer 10: passes 1"],
  ["Exact plans for small cases and for powers of the fan-in.","Monotonicity.","A property against a simulation."],
  src=("src/execution/sort_plan.rs", '''
//! The cost of an external merge sort.

#[derive(Debug, PartialEq, Eq)]
pub struct SortPlan {
    pub initial_runs: u64,
    pub passes: u32,
    pub io_pages: u64,
}

pub fn plan_sort(pages: u64, buffer: u64) -> Option<SortPlan> {
    // @begin 3g-c1
    if pages == 0 {
        return Some(SortPlan { initial_runs: 0, passes: 0, io_pages: 0 });
    }
    if buffer < 3 {
        return None;
    }
    let initial_runs = pages.div_ceil(buffer);
    let mut runs = initial_runs;
    let mut passes = 1u32;
    while runs > 1 {
        runs = runs.div_ceil(buffer - 1);
        passes += 1;
    }
    Some(SortPlan { initial_runs, passes, io_pages: 2 * pages * passes as u64 })
    //~ todo!("3g-c1: runs after the first pass, then merge passes until one run is left")
    // @end
}
'''),
  test=("tests/stages_3g.rs", '''
use bustub::execution::sort_plan::{plan_sort, SortPlan};

#[test]
fn s3g_c1_a_typical_plan() {
    assert_eq!(plan_sort(100, 10), Some(SortPlan { initial_runs: 10, passes: 3, io_pages: 600 }));
}

#[test]
fn s3g_c1_an_input_that_fits_in_memory_is_one_pass() {
    assert_eq!(plan_sort(8, 10), Some(SortPlan { initial_runs: 1, passes: 1, io_pages: 16 }));
    assert_eq!(plan_sort(10, 10), Some(SortPlan { initial_runs: 1, passes: 1, io_pages: 20 }));
}

#[test]
fn s3g_c1_exact_powers_of_the_fan_in_do_not_cost_an_extra_pass() {
    // buffer 5: fan-in 4. 5 * 4^3 pages -> 64 runs -> 16 -> 4 -> 1: three merge passes
    assert_eq!(plan_sort(5 * 64, 5).unwrap().passes, 4);
    assert_eq!(plan_sort(5 * 64 + 1, 5).unwrap().passes, 5, "one page more makes 65 runs and one more pass");
}

#[test]
fn s3g_c1_no_pages_and_not_enough_memory() {
    assert_eq!(plan_sort(0, 10), Some(SortPlan { initial_runs: 0, passes: 0, io_pages: 0 }));
    assert_eq!(plan_sort(100, 2), None);
    assert_eq!(plan_sort(100, 0), None);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: monotone in both arguments, one pass when it fits, and equal to simulating the merges.
    #[test]
    fn s3g_c1_property_the_plan_is_monotone_and_matches_a_simulation(pages in 1u64..5000, buffer in 3u64..40) {
        let p = plan_sort(pages, buffer).unwrap();
        let mut runs = pages.div_ceil(buffer);
        let mut passes = 1;
        while runs > 1 { runs = runs.div_ceil(buffer - 1); passes += 1; }
        prop_assert_eq!(p.passes, passes);
        prop_assert_eq!(p.io_pages, 2 * pages * passes as u64);
        prop_assert!(plan_sort(pages, buffer + 1).unwrap().passes <= p.passes);
        prop_assert!(plan_sort(pages + 1, buffer).unwrap().passes >= p.passes);
        if pages <= buffer { prop_assert_eq!(p.passes, 1); }
    }
}
''')))

CH.append(C("3g-c2", M3G, "91-challenge-top-n-in-bounded-memory", "build", "Challenge: top-N in bounded memory", "easy", "stages_3g::s3g_c2",
  ["selecting the N smallest rows of a stream while holding only N","a stable tie-break by arrival"],
  ["ordered-sets-as-priority-queues","external-merge-sort"],
  "`TopN` in `src/execution/top_n.rs`: `ORDER BY key LIMIT n` without sorting everything. `push(key, payload)` offers a row; the structure never holds more than `n` rows; `finish()` returns the `n` smallest by key (ties by arrival: earlier rows win), in key order.",
  "A full sort of a hundred million rows to return ten is the classic way to make a query slow and out of memory. A bounded max-heap of size `n` reads each row once, throws almost all of them away at once, and needs `O(n)` memory. The tie-break matters because `ORDER BY` without a total key must still be deterministic.",
  ["`TopN::new(n)`; `push(key, payload)` returns nothing; `len()` is the number of rows held (at most `n`).","`finish()` returns `(key, payload)` for the `n` smallest keys, ascending by key; among equal keys, rows that arrived earlier come first. With `n == 0` it returns nothing."],
  ["`len() <= n` at all times.","The rows held are always the `n` smallest seen so far (ties: earliest)."],
  ["The result equals stable-sorting everything by key and taking `n`.","Pushing a row larger than everything held when `len() == n` changes nothing.","The result does not depend on how the stream is split across `push` calls."],
  ["n = 2; push (5,a) (1,b) (5,c) (1,d) -> [(1,b), (1,d)]"],
  ["Small cases; `n = 0`; ties.","The bound on `len()`.","A property against a stable sort."],
  src=("src/execution/top_n.rs", '''
//! ORDER BY ... LIMIT n with memory for n rows.

use std::collections::BinaryHeap;

pub struct TopN {
    // @begin 3g-c2
    n: usize,
    /// A max-heap on (key, arrival): the worst row held is on top.
    heap: BinaryHeap<(i64, u64, u32)>,
    arrivals: u64,
    //~ _topn: (),
    // @end
}

impl TopN {
    pub fn new(n: usize) -> TopN {
        // @begin 3g-c2
        TopN { n, heap: BinaryHeap::new(), arrivals: 0 }
        //~ todo!("3g-c2: an empty selector for `n` rows")
        // @end
    }

    pub fn push(&mut self, key: i64, payload: u32) {
        // @begin 3g-c2
        let item = (key, self.arrivals, payload);
        self.arrivals += 1;
        if self.n == 0 {
            return;
        }
        if self.heap.len() < self.n {
            self.heap.push(item);
        } else if let Some(worst) = self.heap.peek() {
            if (item.0, item.1) < (worst.0, worst.1) {
                self.heap.pop();
                self.heap.push(item);
            }
        }
        //~ todo!("3g-c2: keep the `n` best seen so far")
        // @end
    }

    pub fn len(&self) -> usize {
        // @begin 3g-c2
        self.heap.len()
        //~ todo!("3g-c2: rows held")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn finish(self) -> Vec<(i64, u32)> {
        // @begin 3g-c2
        let mut v = self.heap.into_vec();
        v.sort();
        v.into_iter().map(|(k, _, p)| (k, p)).collect()
        //~ todo!("3g-c2: the held rows in key order, earlier arrivals first among equals")
        // @end
    }
}
'''),
  test=("tests/stages_3g.rs", '''
use bustub::execution::top_n::TopN;

#[test]
fn s3g_c2_the_smallest_n_with_ties_by_arrival() {
    let mut t = TopN::new(2);
    for (k, p) in [(5, 0), (1, 1), (5, 2), (1, 3)] {
        t.push(k, p);
    }
    assert_eq!(t.finish(), vec![(1, 1), (1, 3)]);
}

#[test]
fn s3g_c2_an_earlier_arrival_wins_a_tie_at_the_boundary() {
    let mut t = TopN::new(2);
    for (k, p) in [(3, 10), (3, 11), (3, 12)] {
        t.push(k, p);
    }
    assert_eq!(t.finish(), vec![(3, 10), (3, 11)]);
}

#[test]
fn s3g_c2_n_zero_holds_nothing() {
    let mut t = TopN::new(0);
    t.push(1, 1);
    assert_eq!((t.len(), t.is_empty()), (0, true));
    assert_eq!(t.finish(), vec![]);
}

#[test]
fn s3g_c2_fewer_rows_than_n_and_bounded_memory() {
    let mut t = TopN::new(3);
    t.push(9, 0);
    assert_eq!(t.len(), 1);
    for i in 0..1000 {
        t.push(1000 - i, i as u32);
        assert!(t.len() <= 3);
    }
    let r = t.finish();
    assert_eq!(r.iter().map(|x| x.0).collect::<Vec<_>>(), vec![1, 2, 3]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a stable sort of everything, cut at `n`.
    #[test]
    fn s3g_c2_property_equals_a_stable_sort_and_take(rows in proptest::collection::vec(-5i64..5, 0..30), n in 0usize..10) {
        let mut t = TopN::new(n);
        for (i, &k) in rows.iter().enumerate() { t.push(k, i as u32); prop_assert!(t.len() <= n); }
        let mut want: Vec<(i64, u32)> = rows.iter().enumerate().map(|(i, &k)| (k, i as u32)).collect();
        want.sort_by_key(|r| r.0);
        want.truncate(n);
        prop_assert_eq!(t.finish(), want);
    }
}
''')))

CH.append(C("3g-c3", M3G, "92-challenge-moving-windows", "build", "Challenge: moving windows", "medium", "stages_3g::s3g_c3",
  ["a sliding window sum in linear time with prefix sums","aggregates that skip NULLs and become NULL on an empty window"],
  ["sql-types-and-three-valued-logic","iterators-and-closures"],
  "`moving_sum` in `src/execution/moving_sum.rs`: `SUM(x) OVER (ORDER BY ... ROWS BETWEEN p PRECEDING AND f FOLLOWING)` for a column of nullable integers already in window order. For each row, the sum of the non-NULL values in the frame of rows `i - p ..= i + f` (clipped to the input), or NULL when the frame has no non-NULL value. Linear time.",
  "A running total, a 7-day moving average and a rolling maximum are all window frames, and the naive implementation recomputes each frame from scratch: `O(n * frame)`. Prefix sums make a sum frame `O(1)` per row. The details (clipping at the ends, NULLs) are the same ones a real window executor must get right.",
  ["The frame of row `i` is rows `max(0, i - p)` to `min(n - 1, i + f)` inclusive.","NULL values contribute nothing; a frame with no non-NULL value gives NULL.","Sums wrap on overflow."],
  ["The output has one entry per input row.","Entry `i` depends only on rows inside its frame."],
  ["`p = 0, f = 0` returns each value itself (NULL stays NULL).","Widening the frame never removes a non-NULL result.","`p = n, f = 0` is the running total."],
  ["[1,2,3,4], p=1, f=0 -> [1,3,5,7]","[1,NULL,3], p=1,f=1 -> [1,4,3]","[NULL, NULL] -> [NULL, NULL]"],
  ["Running totals and centred windows.","NULLs and the ends.","A property against the naive frame sum."],
  src=("src/execution/moving_sum.rs", '''
//! Sliding-window sums.

pub fn moving_sum(values: &[Option<i64>], preceding: usize, following: usize) -> Vec<Option<i64>> {
    // @begin 3g-c3
    let n = values.len();
    // prefix[i] = sum of the non-NULL values of rows 0..i; nonnull[i] = how many there are
    let mut prefix = vec![0i64; n + 1];
    let mut nonnull = vec![0usize; n + 1];
    for (i, v) in values.iter().enumerate() {
        prefix[i + 1] = prefix[i].wrapping_add(v.unwrap_or(0));
        nonnull[i + 1] = nonnull[i] + usize::from(v.is_some());
    }
    (0..n)
        .map(|i| {
            let lo = i.saturating_sub(preceding);
            let hi = (i + following).min(n - 1);
            if nonnull[hi + 1] == nonnull[lo] {
                None
            } else {
                Some(prefix[hi + 1].wrapping_sub(prefix[lo]))
            }
        })
        .collect()
    //~ todo!("3g-c3: prefix sums and a count of non-NULL values; each frame is a difference")
    // @end
}
'''),
  test=("tests/stages_3g.rs", '''
use bustub::execution::moving_sum::moving_sum;

fn s(v: &[i64]) -> Vec<Option<i64>> {
    v.iter().map(|&x| Some(x)).collect()
}

#[test]
fn s3g_c3_a_running_total_and_a_trailing_window() {
    assert_eq!(moving_sum(&s(&[1, 2, 3, 4]), 100, 0), s(&[1, 3, 6, 10]));
    assert_eq!(moving_sum(&s(&[1, 2, 3, 4]), 1, 0), s(&[1, 3, 5, 7]));
}

#[test]
fn s3g_c3_a_centred_window_is_clipped_at_both_ends() {
    assert_eq!(moving_sum(&s(&[1, 2, 3, 4]), 1, 1), s(&[3, 6, 9, 7]));
}

#[test]
fn s3g_c3_nulls_contribute_nothing_and_an_all_null_frame_is_null() {
    let v = [Some(1), None, Some(3)];
    assert_eq!(moving_sum(&v, 1, 1), s(&[1, 4, 3]));
    assert_eq!(moving_sum(&[None, None], 1, 1), vec![None, None]);
    assert_eq!(moving_sum(&[None, Some(5)], 0, 0), vec![None, Some(5)]);
}

#[test]
fn s3g_c3_empty_input_and_a_zero_frame() {
    assert_eq!(moving_sum(&[], 2, 2), vec![]);
    assert_eq!(moving_sum(&s(&[7, 8]), 0, 0), s(&[7, 8]));
}

#[test]
fn s3g_c3_a_long_column_is_linear() {
    let v: Vec<Option<i64>> = (0..200_000).map(|i| Some(i % 7)).collect();
    let t = std::time::Instant::now();
    let r = moving_sum(&v, 50_000, 50_000);
    assert_eq!(r.len(), v.len());
    assert!(t.elapsed() < std::time::Duration::from_secs(3), "took {:?}: recomputing each frame is quadratic", t.elapsed());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals summing each frame directly.
    #[test]
    fn s3g_c3_property_equals_the_naive_frame_sum(v in proptest::collection::vec(proptest::option::of(-20i64..20), 0..15), p in 0usize..5, f in 0usize..5) {
        let got = moving_sum(&v, p, f);
        for i in 0..v.len() {
            let frame = &v[i.saturating_sub(p)..(i + f + 1).min(v.len())];
            let want = if frame.iter().all(|x| x.is_none()) { None } else { Some(frame.iter().flatten().sum::<i64>()) };
            prop_assert_eq!(got[i], want, "row {}", i);
        }
        prop_assert_eq!(got.len(), v.len());
    }
}
''')))

CH.append(C("3g-c4", M3G, "93-challenge-ranks-with-gaps", "debug", "Challenge: ranks with gaps", "easy", "stages_3g::s3g_c4",
  ["telling RANK from DENSE_RANK and ROW_NUMBER"],
  ["sort-keys-and-null-ordering","property-testing-and-fuzzing"],
  "`src/execution/ranks.rs` computes `ROW_NUMBER`, `RANK` and `DENSE_RANK` for a list of keys already sorted. `row_number` and `dense_rank` are right; `rank` is wrong whenever there are ties. Find the bug and fix it.",
  "The three ranking functions differ only in what ties do: `ROW_NUMBER` ignores them (1,2,3,4), `RANK` gives ties the same number and **skips** (1,1,3,4), `DENSE_RANK` gives ties the same number and **does not skip** (1,1,2,3). Confusing the last two is the standard mistake, and it only shows when the data has ties.",
  ["Input keys are non-decreasing. `row_number[i] = i + 1`.","`rank[i]` is `1 +` the number of rows with a strictly smaller key. `dense_rank[i]` is `1 +` the number of distinct smaller keys."],
  ["`rank[i] <= row_number[i]` and `dense_rank[i] <= rank[i]`.","Equal keys have equal rank and equal dense rank."],
  ["Without ties all three are equal.","`rank` jumps by the size of the tie group; `dense_rank` always by one.","The last `dense_rank` is the number of distinct keys."],
  ["keys [10,20,20,30]: row_number [1,2,3,4]; rank [1,2,2,4]; dense_rank [1,2,2,3]"],
  ["The three on data with and without ties.","A property against the definitions."],
  src=("src/execution/ranks.rs", '''
//! ROW_NUMBER, RANK and DENSE_RANK over sorted keys.

pub fn row_number(keys: &[i64]) -> Vec<usize> {
    (1..=keys.len()).collect()
}

pub fn dense_rank(keys: &[i64]) -> Vec<usize> {
    let mut out = Vec::with_capacity(keys.len());
    let mut rank = 0;
    for (i, k) in keys.iter().enumerate() {
        if i == 0 || keys[i - 1] != *k {
            rank += 1;
        }
        out.push(rank);
    }
    out
}

pub fn rank(keys: &[i64]) -> Vec<usize> {
    let mut out = Vec::with_capacity(keys.len());
    // @begin 3g-c4
    let mut current = 0;
    for (i, k) in keys.iter().enumerate() {
        if i == 0 || keys[i - 1] != *k {
            current = i + 1;
        }
        out.push(current);
    }
    //~ let mut current = 0;
    //~ for (i, k) in keys.iter().enumerate() {
    //~     if i == 0 || keys[i - 1] != *k {
    //~         current += 1;
    //~     }
    //~     out.push(current);
    //~ }
    // @end
    out
}
'''),
  test=("tests/stages_3g.rs", '''
use bustub::execution::ranks::{dense_rank, rank, row_number};

#[test]
fn s3g_c4_the_three_functions_on_data_with_a_tie() {
    let k = [10, 20, 20, 30];
    assert_eq!(row_number(&k), vec![1, 2, 3, 4]);
    assert_eq!(rank(&k), vec![1, 2, 2, 4]);
    assert_eq!(dense_rank(&k), vec![1, 2, 2, 3]);
}

#[test]
fn s3g_c4_a_big_tie_group_makes_a_big_gap() {
    let k = [1, 1, 1, 1, 2];
    assert_eq!(rank(&k), vec![1, 1, 1, 1, 5]);
    assert_eq!(dense_rank(&k), vec![1, 1, 1, 1, 2]);
}

#[test]
fn s3g_c4_without_ties_all_three_agree_and_empty_is_empty() {
    let k = [1, 2, 3];
    assert_eq!(rank(&k), row_number(&k));
    assert_eq!(dense_rank(&k), row_number(&k));
    assert_eq!(rank(&[]), Vec::<usize>::new());
}

#[test]
fn s3g_c4_all_keys_equal() {
    let k = [5, 5, 5];
    assert_eq!(rank(&k), vec![1, 1, 1]);
    assert_eq!(dense_rank(&k), vec![1, 1, 1]);
    assert_eq!(row_number(&k), vec![1, 2, 3]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the definitions, counting smaller keys.
    #[test]
    fn s3g_c4_property_rank_counts_smaller_rows(mut keys in proptest::collection::vec(-4i64..4, 0..15)) {
        keys.sort();
        let r = rank(&keys);
        let d = dense_rank(&keys);
        for (i, k) in keys.iter().enumerate() {
            prop_assert_eq!(r[i], 1 + keys.iter().filter(|x| *x < k).count());
            let mut smaller: Vec<_> = keys.iter().filter(|x| *x < k).collect();
            smaller.dedup();
            prop_assert_eq!(d[i], 1 + smaller.len());
        }
    }
}
''')))

CH.append(C("3g-c5", M3G, "94-challenge-radix-sort", "build", "Challenge: radix sort", "easy", "stages_3g::s3g_c5",
  ["sorting integers by digit with counting passes","a stable sort that is not comparison-based"],
  ["external-merge-sort","performance-tests-and-measuring"],
  "`radix_sort` in `src/execution/radix_sort.rs`: sort `u32` keys (each with a `u32` payload) with a least-significant-digit radix sort, 8 bits per pass, **stable**: rows with equal keys keep their input order.",
  "Comparison sorts cannot beat `n log n`; sorting fixed-width integers by digit takes four linear passes for `u32`, and is what high-throughput engines (and GPU sorts) use for integer keys. Stability is what makes it composable: sort by the least significant column first and the result is a multi-column sort.",
  ["`radix_sort(rows)` sorts `(key, payload)` ascending by key, stably, in place or by returning a new vector.","Each pass is a counting sort on one byte of the key, least significant byte first."],
  ["The output is a permutation of the input.","Keys are non-decreasing; payloads of equal keys are in input order."],
  ["The result equals the standard library's stable sort by key.","Sorting twice changes nothing.","Sorting by a second key first and then by the main key (stable) gives a lexicographic order."],
  ["[(3,a),(1,b),(3,c),(2,d)] -> [(1,b),(2,d),(3,a),(3,c)]"],
  ["Small inputs and equal keys.","Keys that differ only in a high byte.","A property against `sort_by_key`."],
  src=("src/execution/radix_sort.rs", '''
//! A stable LSD radix sort on u32 keys.

pub fn radix_sort(rows: &mut Vec<(u32, u32)>) {
    // @begin 3g-c5
    let mut buf = vec![(0u32, 0u32); rows.len()];
    for shift in [0u32, 8, 16, 24] {
        let mut count = [0usize; 257];
        for r in rows.iter() {
            count[((r.0 >> shift) & 0xFF) as usize + 1] += 1;
        }
        for i in 0..256 {
            count[i + 1] += count[i];
        }
        for r in rows.iter() {
            let b = ((r.0 >> shift) & 0xFF) as usize;
            buf[count[b]] = *r;
            count[b] += 1;
        }
        std::mem::swap(rows, &mut buf);
    }
    //~ todo!("3g-c5: four stable counting-sort passes, least significant byte first")
    // @end
}
'''),
  test=("tests/stages_3g.rs", '''
use bustub::execution::radix_sort::radix_sort;

#[test]
fn s3g_c5_sorts_by_key_keeping_the_order_of_equal_keys() {
    let mut v = vec![(3, 1), (1, 2), (3, 3), (2, 4)];
    radix_sort(&mut v);
    assert_eq!(v, vec![(1, 2), (2, 4), (3, 1), (3, 3)]);
}

#[test]
fn s3g_c5_keys_that_differ_only_in_a_high_byte() {
    let mut v = vec![(0x0100_0000, 0), (0x00FF_FFFF, 1), (0xFF00_0000, 2), (0, 3)];
    radix_sort(&mut v);
    assert_eq!(v.iter().map(|r| r.1).collect::<Vec<_>>(), vec![3, 1, 0, 2]);
}

#[test]
fn s3g_c5_empty_single_and_already_sorted() {
    let mut e: Vec<(u32, u32)> = vec![];
    radix_sort(&mut e);
    assert!(e.is_empty());
    let mut one = vec![(5, 5)];
    radix_sort(&mut one);
    assert_eq!(one, vec![(5, 5)]);
    let mut sorted: Vec<(u32, u32)> = (0..100).map(|i| (i, i)).collect();
    let copy = sorted.clone();
    radix_sort(&mut sorted);
    assert_eq!(sorted, copy);
}

#[test]
fn s3g_c5_equal_keys_and_reversed_input() {
    let mut same: Vec<(u32, u32)> = (0..50).map(|i| (7, i)).collect();
    let copy = same.clone();
    radix_sort(&mut same);
    assert_eq!(same, copy, "equal keys keep their input order");
    let mut rev: Vec<(u32, u32)> = (0..50).rev().map(|i| (i, i)).collect();
    radix_sort(&mut rev);
    assert!(rev.windows(2).all(|w| w[0].0 < w[1].0));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals the standard library's stable sort by key.
    #[test]
    fn s3g_c5_property_equals_a_stable_sort(keys in proptest::collection::vec(prop_oneof![0u32..8, any::<u32>()], 0..60)) {
        let mut rows: Vec<(u32, u32)> = keys.iter().enumerate().map(|(i, &k)| (k, i as u32)).collect();
        let mut want = rows.clone();
        want.sort_by_key(|r| r.0);
        radix_sort(&mut rows);
        prop_assert_eq!(rows, want);
    }
}
''')))

CH.append(C("3h-c1", M3H, "90-challenge-constant-folding", "build", "Challenge: constant folding", "medium", "stages_3h::s3h_c1",
  ["evaluating the parts of an expression that do not depend on the row","algebraic identities that are always safe"],
  ["rule-based-query-optimization","expression-trees","property-testing-and-fuzzing"],
  "`fold` in `src/optimizer/const_fold.rs`: simplify an expression tree over integer and boolean constants and column references, **without changing its value on any row**. Evaluate every subtree that has no column in it; apply the identities `x + 0`, `0 + x`, `x * 1`, `1 * x` -> `x`, `x * 0`, `0 * x` -> `0`, `true AND x` -> `x`, `false AND x` -> `false`, `false OR x` -> `x`, `true OR x` -> `true`, `NOT NOT x` -> `x`.",
  "`WHERE price * 1.0 > 10 + 5` should not multiply by one and add five a million times. Folding is the oldest and cheapest optimiser rule, and the one every other rule relies on (a predicate that folds to `false` makes the whole scan empty). Its correctness condition is exact and testable: the folded tree must evaluate to the same value on every row.",
  ["`fold` is applied bottom-up: fold the children, then apply the rules to the node.","The language has `Int`, `Bool`, `Col(i)`, `Add`, `Mul`, `Lt` (integer comparison to a boolean), `And`, `Or`, `Not`; all values are non-NULL here.","A node with only constant children becomes a constant."],
  ["`eval(fold(e), row) == eval(e, row)` for every row where `eval(e, row)` is defined.","`fold(fold(e)) == fold(e)`.","The result contains no subtree without a column that is bigger than a literal."],
  ["Folding never increases the number of nodes.","A tree with no columns folds to a single literal.","Substituting values for columns and then folding gives the same literal as evaluating."],
  ["(1 + 2) * x -> 3 * x","x * (2 - 2... ) -> 0 when a factor folds to 0","true AND (x < 5) -> x < 5","NOT NOT (x < 5) -> x < 5"],
  ["Each rule.","Nested folding.","A property: equal value on random rows; idempotence; no growth."],
  src=("src/optimizer/const_fold.rs", '''
//! Constant folding for a small expression language.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Expr {
    Int(i64),
    Bool(bool),
    Col(usize),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Lt(Box<Expr>, Box<Expr>),
    And(Box<Expr>, Box<Expr>),
    Or(Box<Expr>, Box<Expr>),
    Not(Box<Expr>),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Val {
    Int(i64),
    Bool(bool),
}

/// The value of `e` on `row`; `None` for a type error or an overflow (such trees are not folded away).
pub fn eval(e: &Expr, row: &[i64]) -> Option<Val> {
    use Expr::*;
    Some(match e {
        Int(v) => Val::Int(*v),
        Bool(b) => Val::Bool(*b),
        Col(i) => Val::Int(*row.get(*i)?),
        Add(a, b) => match (eval(a, row)?, eval(b, row)?) {
            (Val::Int(x), Val::Int(y)) => Val::Int(x.checked_add(y)?),
            _ => return None,
        },
        Mul(a, b) => match (eval(a, row)?, eval(b, row)?) {
            (Val::Int(x), Val::Int(y)) => Val::Int(x.checked_mul(y)?),
            _ => return None,
        },
        Lt(a, b) => match (eval(a, row)?, eval(b, row)?) {
            (Val::Int(x), Val::Int(y)) => Val::Bool(x < y),
            _ => return None,
        },
        And(a, b) => match (eval(a, row)?, eval(b, row)?) {
            (Val::Bool(x), Val::Bool(y)) => Val::Bool(x && y),
            _ => return None,
        },
        Or(a, b) => match (eval(a, row)?, eval(b, row)?) {
            (Val::Bool(x), Val::Bool(y)) => Val::Bool(x || y),
            _ => return None,
        },
        Not(a) => match eval(a, row)? {
            Val::Bool(x) => Val::Bool(!x),
            _ => return None,
        },
    })
}

pub fn fold(e: &Expr) -> Expr {
    // @begin 3h-c1
    use Expr::*;
    let lit = |v: Val| match v {
        Val::Int(i) => Int(i),
        Val::Bool(b) => Bool(b),
    };
    let has_col = |e: &Expr| -> bool {
        fn go(e: &Expr) -> bool {
            match e {
                Int(_) | Bool(_) => false,
                Col(_) => true,
                Add(a, b) | Mul(a, b) | Lt(a, b) | And(a, b) | Or(a, b) => go(a) || go(b),
                Not(a) => go(a),
            }
        }
        go(e)
    };
    let out = match e {
        Int(_) | Bool(_) | Col(_) => return e.clone(),
        Add(a, b) => {
            let (a, b) = (fold(a), fold(b));
            match (&a, &b) {
                (Int(0), x) | (x, Int(0)) => x.clone(),
                _ => Add(Box::new(a), Box::new(b)),
            }
        }
        Mul(a, b) => {
            let (a, b) = (fold(a), fold(b));
            match (&a, &b) {
                (Int(1), x) | (x, Int(1)) => x.clone(),
                (Int(0), _) | (_, Int(0)) => Int(0),
                _ => Mul(Box::new(a), Box::new(b)),
            }
        }
        Lt(a, b) => Lt(Box::new(fold(a)), Box::new(fold(b))),
        And(a, b) => {
            let (a, b) = (fold(a), fold(b));
            match (&a, &b) {
                (Bool(true), x) | (x, Bool(true)) => x.clone(),
                (Bool(false), _) | (_, Bool(false)) => Bool(false),
                _ => And(Box::new(a), Box::new(b)),
            }
        }
        Or(a, b) => {
            let (a, b) = (fold(a), fold(b));
            match (&a, &b) {
                (Bool(false), x) | (x, Bool(false)) => x.clone(),
                (Bool(true), _) | (_, Bool(true)) => Bool(true),
                _ => Or(Box::new(a), Box::new(b)),
            }
        }
        Not(a) => match fold(a) {
            Not(inner) => *inner,
            Bool(b) => Bool(!b),
            x => Not(Box::new(x)),
        },
    };
    if !has_col(&out) {
        if let Some(v) = eval(&out, &[]) {
            return lit(v);
        }
    }
    out
    //~ todo!("3h-c1: fold the children, evaluate what has no column, then apply the identities")
    // @end
}
'''),
  test=("tests/stages_3h.rs", '''
use bustub::optimizer::const_fold::{eval, fold, Expr, Expr::*};

fn b(e: Expr) -> Box<Expr> {
    Box::new(e)
}

#[test]
fn s3h_c1_subtrees_without_columns_are_evaluated() {
    let e = Mul(b(Add(b(Int(1)), b(Int(2)))), b(Col(0)));
    assert_eq!(fold(&e), Mul(b(Int(3)), b(Col(0))));
    assert_eq!(fold(&Lt(b(Int(1)), b(Int(2)))), Bool(true));
}

#[test]
fn s3h_c1_arithmetic_identities() {
    assert_eq!(fold(&Add(b(Col(0)), b(Int(0)))), Col(0));
    assert_eq!(fold(&Add(b(Add(b(Int(2)), b(Int(-2)))), b(Col(1)))), Col(1));
    assert_eq!(fold(&Mul(b(Int(1)), b(Col(0)))), Col(0));
    assert_eq!(fold(&Mul(b(Col(0)), b(Add(b(Int(1)), b(Int(-1)))))), Int(0));
}

#[test]
fn s3h_c1_boolean_identities() {
    let p = || Lt(b(Col(0)), b(Int(5)));
    assert_eq!(fold(&And(b(Bool(true)), b(p()))), p());
    assert_eq!(fold(&And(b(p()), b(Bool(false)))), Bool(false));
    assert_eq!(fold(&Or(b(Bool(false)), b(p()))), p());
    assert_eq!(fold(&Or(b(p()), b(Bool(true)))), Bool(true));
    assert_eq!(fold(&Not(b(Not(b(p()))))), p());
    assert_eq!(fold(&Not(b(Bool(false)))), Bool(true));
}

#[test]
fn s3h_c1_a_trap_must_not_be_folded_away() {
    // an overflow cannot be evaluated: it is left in the tree, not turned into a made-up value
    let e = Add(b(Int(i64::MAX)), b(Int(1)));
    assert_eq!(fold(&e), e);
}

fn arb_int(depth: u32) -> BoxedStrategy<Expr> {
    let leaf = prop_oneof![(-3i64..4).prop_map(Int), (0usize..2).prop_map(Col)];
    if depth == 0 {
        return leaf.boxed();
    }
    let inner = arb_int(depth - 1);
    prop_oneof![
        leaf,
        (inner.clone(), inner.clone()).prop_map(|(a, c)| Add(Box::new(a), Box::new(c))),
        (inner.clone(), inner).prop_map(|(a, c)| Mul(Box::new(a), Box::new(c))),
    ]
    .boxed()
}

fn arb_bool(depth: u32) -> BoxedStrategy<Expr> {
    let leaf = prop_oneof![any::<bool>().prop_map(Bool), (arb_int(2), arb_int(2)).prop_map(|(a, c)| Lt(Box::new(a), Box::new(c)))];
    if depth == 0 {
        return leaf.boxed();
    }
    let inner = arb_bool(depth - 1);
    prop_oneof![
        leaf,
        (inner.clone(), inner.clone()).prop_map(|(a, c)| And(Box::new(a), Box::new(c))),
        (inner.clone(), inner.clone()).prop_map(|(a, c)| Or(Box::new(a), Box::new(c))),
        inner.prop_map(|a| Not(Box::new(a))),
    ]
    .boxed()
}

fn size(e: &Expr) -> usize {
    match e {
        Int(_) | Bool(_) | Col(_) => 1,
        Add(a, b) | Mul(a, b) | Lt(a, b) | And(a, b) | Or(a, b) => 1 + size(a) + size(b),
        Not(a) => 1 + size(a),
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the folded tree has the same value on every row, is no bigger, and folding again changes nothing.
    #[test]
    fn s3h_c1_property_folding_preserves_the_value(e in arb_bool(3), r0 in -4i64..5, r1 in -4i64..5) {
        let f = fold(&e);
        prop_assert_eq!(eval(&f, &[r0, r1]), eval(&e, &[r0, r1]));
        prop_assert!(size(&f) <= size(&e));
        prop_assert_eq!(fold(&f), f);
    }

    #[test]
    fn s3h_c1_property_integer_trees_too(e in arb_int(3), r0 in -4i64..5, r1 in -4i64..5) {
        let f = fold(&e);
        prop_assert_eq!(eval(&f, &[r0, r1]), eval(&e, &[r0, r1]));
        prop_assert_eq!(fold(&f), f.clone());
    }
}
''')))

CH.append(C("3h-c2", M3H, "91-challenge-where-does-the-predicate-go", "build", "Challenge: where does the predicate go?", "medium", "stages_3h::s3h_c2",
  ["splitting a filter into conjuncts and sorting them by the side of a join they depend on","what may and may not be pushed below a join"],
  ["predicate-pushdown","conjunctive-predicates","rule-based-query-optimization"],
  "`conjuncts` and `split_for_join` in `src/optimizer/pushdown.rs`: `conjuncts(p)` flattens nested `AND`s into a list of predicates; `split_for_join(p, left_cols)` divides them for a join of two inputs whose combined row is `[left columns..., right columns...]`: those that mention only left columns (can be applied below the left input), only right columns (below the right), and the rest (must stay above the join).",
  "`SELECT ... FROM a JOIN b ON ... WHERE a.x = 1 AND b.y > 3 AND a.z < b.w` should filter `a` and `b` *before* joining them, and only the last conjunct needs both sides. Pushdown is among the most valuable rewrites there is, and its safety rule is simple: split only at `AND`, never inside an `OR` or under a `NOT`.",
  ["`Pred` is `Cmp(col, op, constant)`, `ColCmp(col, op, col)`, `And(Vec<Pred>)`, `Or(Vec<Pred>)`, `Not(Box<Pred>)`.","`conjuncts` flattens `And` recursively, keeping order, and returns anything else as one conjunct; an empty `And` has none.","`split_for_join` returns `(left_only, right_only, both)`; columns below `left_cols` are left, the rest right. A conjunct that mentions no column counts as `left_only`."],
  ["Each conjunct goes to exactly one of the three lists, in original order within a list.","`left_only` uses only columns `< left_cols`; `right_only` only columns `>= left_cols`."],
  ["The conjunction of the three lists is equivalent to the input predicate on every row.","An `Or` or `Not` is never split.","Pushing nothing (all three merged back) gives the input's conjuncts."],
  ["a.x=1 AND b.y>3 AND a.z<b.w with left_cols=2 -> left [a.x=1], right [b.y>3], both [a.z<b.w]"],
  ["Flattening nested `AND`s.","The three-way split.","`OR` kept whole.","A property: equivalence on random rows."],
  src=("src/optimizer/pushdown.rs", '''
//! Splitting a filter so that parts can be applied below a join.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CmpOp {
    Lt,
    Eq,
    Gt,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Pred {
    Cmp(usize, CmpOp, i64),
    ColCmp(usize, CmpOp, usize),
    And(Vec<Pred>),
    Or(Vec<Pred>),
    Not(Box<Pred>),
}

fn apply(op: CmpOp, a: i64, b: i64) -> bool {
    match op {
        CmpOp::Lt => a < b,
        CmpOp::Eq => a == b,
        CmpOp::Gt => a > b,
    }
}

/// Does `p` hold on `row`?
pub fn holds(p: &Pred, row: &[i64]) -> bool {
    match p {
        Pred::Cmp(c, op, v) => apply(*op, row[*c], *v),
        Pred::ColCmp(a, op, b) => apply(*op, row[*a], row[*b]),
        Pred::And(ps) => ps.iter().all(|q| holds(q, row)),
        Pred::Or(ps) => ps.iter().any(|q| holds(q, row)),
        Pred::Not(q) => !holds(q, row),
    }
}

/// The columns a predicate mentions.
pub fn columns(p: &Pred) -> Vec<usize> {
    match p {
        Pred::Cmp(c, _, _) => vec![*c],
        Pred::ColCmp(a, _, b) => vec![*a, *b],
        Pred::And(ps) | Pred::Or(ps) => ps.iter().flat_map(columns).collect(),
        Pred::Not(q) => columns(q),
    }
}

pub fn conjuncts(p: &Pred) -> Vec<Pred> {
    // @begin 3h-c2
    match p {
        Pred::And(ps) => ps.iter().flat_map(conjuncts).collect(),
        other => vec![other.clone()],
    }
    //~ todo!("3h-c2: flatten nested ANDs; anything else is one conjunct")
    // @end
}

/// `(left only, right only, both)`.
pub fn split_for_join(p: &Pred, left_cols: usize) -> (Vec<Pred>, Vec<Pred>, Vec<Pred>) {
    // @begin 3h-c2
    let (mut l, mut r, mut b) = (Vec::new(), Vec::new(), Vec::new());
    for c in conjuncts(p) {
        let cols = columns(&c);
        if cols.iter().all(|&i| i < left_cols) {
            l.push(c);
        } else if cols.iter().all(|&i| i >= left_cols) {
            r.push(c);
        } else {
            b.push(c);
        }
    }
    (l, r, b)
    //~ todo!("3h-c2: sort the conjuncts by which side's columns they mention")
    // @end
}
'''),
  test=("tests/stages_3h.rs", '''
use bustub::optimizer::pushdown::{columns, conjuncts, holds, split_for_join, CmpOp::*, Pred, Pred::*};

#[test]
fn s3h_c2_nested_ands_are_flattened_in_order() {
    let p = And(vec![Cmp(0, Eq, 1), And(vec![Cmp(1, Gt, 3), And(vec![])]), Cmp(2, Lt, 9)]);
    assert_eq!(conjuncts(&p), vec![Cmp(0, Eq, 1), Cmp(1, Gt, 3), Cmp(2, Lt, 9)]);
    assert_eq!(conjuncts(&And(vec![])), Vec::<Pred>::new());
    assert_eq!(conjuncts(&Cmp(0, Eq, 1)), vec![Cmp(0, Eq, 1)]);
}

#[test]
fn s3h_c2_the_split_by_side() {
    // left has columns 0 and 1; right has columns 2 and 3
    let p = And(vec![Cmp(0, Eq, 1), Cmp(3, Gt, 3), ColCmp(1, Lt, 2)]);
    let (l, r, b) = split_for_join(&p, 2);
    assert_eq!((l, r, b), (vec![Cmp(0, Eq, 1)], vec![Cmp(3, Gt, 3)], vec![ColCmp(1, Lt, 2)]));
}

#[test]
fn s3h_c2_an_or_is_never_split() {
    let p = And(vec![Or(vec![Cmp(0, Eq, 1), Cmp(3, Eq, 2)]), Cmp(1, Gt, 0)]);
    let (l, r, b) = split_for_join(&p, 2);
    assert_eq!((l.len(), r.len(), b.len()), (1, 0, 1));
    assert_eq!(b[0], Or(vec![Cmp(0, Eq, 1), Cmp(3, Eq, 2)]));
}

#[test]
fn s3h_c2_a_negation_stays_whole_and_goes_by_its_columns() {
    let p = And(vec![Not(Box::new(Cmp(2, Eq, 0))), Not(Box::new(ColCmp(0, Eq, 3)))]);
    let (l, r, b) = split_for_join(&p, 2);
    assert_eq!((l.len(), r.len(), b.len()), (0, 1, 1));
}

fn arb_pred() -> impl Strategy<Value = Pred> {
    let op = prop_oneof![Just(Lt), Just(Eq), Just(Gt)];
    let leaf = prop_oneof![
        (0usize..4, op.clone(), -2i64..3).prop_map(|(c, o, v)| Cmp(c, o, v)),
        (0usize..4, op, 0usize..4).prop_map(|(a, o, b)| ColCmp(a, o, b)),
    ];
    leaf.prop_recursive(3, 12, 3, |inner| {
        prop_oneof![
            proptest::collection::vec(inner.clone(), 0..4).prop_map(And),
            proptest::collection::vec(inner.clone(), 1..3).prop_map(Or),
            inner.prop_map(|p| Not(Box::new(p))),
        ]
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the three lists together are equivalent to the input, and each list obeys its column rule.
    #[test]
    fn s3h_c2_property_the_split_is_equivalent_and_sorted_by_side(p in arb_pred(), left in 0usize..5, row in proptest::collection::vec(-2i64..3, 4)) {
        let (l, r, b) = split_for_join(&p, left);
        for q in &l { prop_assert!(columns(q).iter().all(|&c| c < left)); }
        for q in &r { prop_assert!(columns(q).iter().all(|&c| c >= left)); }
        let all: Vec<Pred> = l.iter().chain(&r).chain(&b).cloned().collect();
        prop_assert_eq!(all.len(), conjuncts(&p).len());
        prop_assert_eq!(all.iter().all(|q| holds(q, &row)), holds(&p, &row));
    }
}
''')))

CH.append(C("3h-c3", M3H, "92-challenge-join-ordering", "build", "Challenge: join ordering", "hard", "stages_3h::s3h_c3",
  ["dynamic programming over subsets of tables","a cost model that sums the sizes of intermediate results"],
  ["rule-based-query-optimization","join-algorithms","model-based-testing"],
  "`best_join_order` in `src/optimizer/join_order.rs`: given the row counts of `n` tables (`n <= 12`) and a symmetric matrix of join selectivities, find the **left-deep** order (`((t1 ⋈ t2) ⋈ t3) ...`) that minimises the **sum of the sizes of the intermediate results**. The size of joining a set `S` of tables is the product of their row counts times the selectivity of every pair inside `S`.",
  "The order of joins is the biggest lever a query optimiser has: the same query can cost a thousand times more in a bad order. The number of orders grows factorially, but the *cost of a set* does not depend on how it was assembled, which is exactly what makes dynamic programming over subsets work. This is the System R algorithm.",
  ["`card[i]` is the row count of table `i`; `sel[i][j] = sel[j][i]` is the selectivity of joining `i` with `j` (1.0 = no predicate, a cross product).","`size(S) = prod(card[i] for i in S) * prod(sel[i][j] for pairs i < j in S)`.","The cost of an order `p0, p1, ...` is `size({p0, p1}) + size({p0, p1, p2}) + ...` (the base tables themselves are not counted). One table has cost 0.","Return `(cost, order)` for a cheapest order; on ties the lexicographically smallest order."],
  ["The returned order is a permutation of `0..n`.","The cost equals the cost of the returned order.","No order is cheaper (checked by brute force for small `n`)."],
  ["Making a selectivity smaller never increases the best cost.","Relabelling the tables relabels the answer: the best cost is unchanged.","With all selectivities 1.0, the best order joins the smallest tables first."],
  ["card [1000, 10, 100], sel(0,1) = 0.001: join 0,1 first (size 10) then 2 (size 1000)"],
  ["Small cases worked by hand.","All selectivities 1.0.","A property against brute force over all permutations for n <= 6."],
  src=("src/optimizer/join_order.rs", '''
//! The cheapest left-deep join order, by dynamic programming over subsets.

/// `(cost, order)`.
pub fn best_join_order(card: &[f64], sel: &[Vec<f64>]) -> (f64, Vec<usize>) {
    // @begin 3h-c3
    let n = card.len();
    if n <= 1 {
        return (0.0, (0..n).collect());
    }
    // size of every subset
    let size = |mask: usize| -> f64 {
        let mut s = 1.0;
        for i in 0..n {
            if mask >> i & 1 == 1 {
                s *= card[i];
                for j in i + 1..n {
                    if mask >> j & 1 == 1 {
                        s *= sel[i][j];
                    }
                }
            }
        }
        s
    };
    let full = (1usize << n) - 1;
    // best[mask] = (cost of joining the tables of mask in the best order, that order)
    let mut best: Vec<Option<(f64, Vec<usize>)>> = vec![None; full + 1];
    for i in 0..n {
        best[1 << i] = Some((0.0, vec![i]));
    }
    for mask in 1..=full {
        if mask.count_ones() < 2 {
            continue;
        }
        let mut cand: Option<(f64, Vec<usize>)> = None;
        for last in 0..n {
            if mask >> last & 1 == 0 {
                continue;
            }
            let rest = mask & !(1 << last);
            let (c, order) = best[rest].clone().unwrap();
            let cost = c + if rest.count_ones() >= 1 && mask.count_ones() >= 2 { size(mask) } else { 0.0 };
            let mut o = order;
            o.push(last);
            let better = match &cand {
                None => true,
                Some((bc, bo)) => cost < *bc - 1e-9 * bc.abs().max(1.0) || ((cost - *bc).abs() <= 1e-9 * bc.abs().max(1.0) && o < *bo),
            };
            if better {
                cand = Some((cost, o));
            }
        }
        best[mask] = cand;
    }
    best[full].clone().unwrap()
    //~ todo!("3h-c3: best[mask] = min over the table added last of best[mask without it] + size(mask)")
    // @end
}
'''),
  test=("tests/stages_3h.rs", '''
use bustub::optimizer::join_order::best_join_order;

fn unit(n: usize) -> Vec<Vec<f64>> {
    vec![vec![1.0; n]; n]
}

fn cost_of(order: &[usize], card: &[f64], sel: &[Vec<f64>]) -> f64 {
    let mut total = 0.0;
    for k in 2..=order.len() {
        let set = &order[..k];
        let mut s = 1.0;
        for (a, &i) in set.iter().enumerate() {
            s *= card[i];
            for &j in &set[a + 1..] {
                s *= sel[i][j];
            }
        }
        total += s;
    }
    total
}

#[test]
fn s3h_c3_a_selective_join_goes_first() {
    let card = [1000.0, 10.0, 100.0];
    let mut sel = unit(3);
    sel[0][1] = 0.001;
    sel[1][0] = 0.001;
    let (cost, order) = best_join_order(&card, &sel);
    assert_eq!(cost_of(&order, &card, &sel), cost);
    assert!(order[..2].contains(&0) && order[..2].contains(&1), "tables 0 and 1 join first: {order:?}");
    assert!((cost - (10.0 + 1000.0)).abs() < 1e-6);
}

#[test]
fn s3h_c3_without_predicates_the_smallest_tables_go_first() {
    let card = [500.0, 5.0, 50.0, 2.0];
    let (_, order) = best_join_order(&card, &unit(4));
    assert_eq!(order[0..2].iter().copied().collect::<std::collections::BTreeSet<_>>(), [1usize, 3].into_iter().collect());
    assert_eq!(*order.last().unwrap(), 0);
}

#[test]
fn s3h_c3_one_table_and_no_tables() {
    assert_eq!(best_join_order(&[7.0], &unit(1)), (0.0, vec![0]));
    assert_eq!(best_join_order(&[], &[]), (0.0, vec![]));
}

fn permutations(n: usize) -> Vec<Vec<usize>> {
    if n == 0 {
        return vec![vec![]];
    }
    let mut out = Vec::new();
    for p in permutations(n - 1) {
        for at in 0..=p.len() {
            let mut q = p.clone();
            q.insert(at, n - 1);
            out.push(q);
        }
    }
    out
}

#[test]
fn s3h_c3_the_returned_order_is_a_permutation_with_the_reported_cost() {
    let card = [30.0, 4.0, 200.0, 9.0, 60.0];
    let mut sel = unit(5);
    sel[1][2] = 0.01;
    sel[2][1] = 0.01;
    sel[3][4] = 0.1;
    sel[4][3] = 0.1;
    let (cost, order) = best_join_order(&card, &sel);
    let mut sorted = order.clone();
    sorted.sort();
    assert_eq!(sorted, vec![0, 1, 2, 3, 4]);
    assert!((cost_of(&order, &card, &sel) - cost).abs() < 1e-6);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the returned cost is that of the returned order, and no permutation is cheaper.
    #[test]
    fn s3h_c3_property_dynamic_programming_equals_brute_force(card in proptest::collection::vec(1.0f64..1000.0, 2..6), sels in proptest::collection::vec(0.001f64..1.0, 15)) {
        let n = card.len();
        let mut sel = unit(n);
        let mut k = 0;
        for i in 0..n { for j in i + 1..n { sel[i][j] = sels[k]; sel[j][i] = sels[k]; k += 1; } }
        let (cost, order) = best_join_order(&card, &sel);
        let mut sorted = order.clone();
        sorted.sort();
        prop_assert_eq!(sorted, (0..n).collect::<Vec<_>>());
        prop_assert!((cost_of(&order, &card, &sel) - cost).abs() <= 1e-6 * cost.max(1.0));
        let best = permutations(n).iter().map(|p| cost_of(p, &card, &sel)).fold(f64::INFINITY, f64::min);
        prop_assert!((best - cost).abs() <= 1e-6 * best.max(1.0), "dp {} vs brute force {}", cost, best);
    }
}
''')))

CH.append(C("3h-c4", M3H, "93-challenge-de-morgan", "debug", "Challenge: De Morgan", "easy", "stages_3h::s3h_c4",
  ["finding a wrong rewrite by checking truth tables"],
  ["rule-based-query-optimization","property-testing-and-fuzzing"],
  "`push_not` in `src/optimizer/push_not.rs` pushes every `NOT` of a boolean expression down to the variables, using De Morgan's laws, so that the result has `Not` only directly on variables. One of the two laws is written wrong. Find the bug and fix it.",
  "A rewrite is correct only if the result means the same thing, and the only convincing evidence is to compare the truth tables. De Morgan is the textbook case: `NOT (a AND b)` is `NOT a OR NOT b`, not `AND`. An optimiser that gets it wrong still runs, returns rows, and returns the wrong ones.",
  ["`push_not(e)` returns an expression with the same truth table as `e` in which `Not` is applied only to variables, and no `Not Not` remains.","The laws: `NOT (a AND b) = NOT a OR NOT b`, `NOT (a OR b) = NOT a AND NOT b`, `NOT NOT a = a`."],
  ["For every assignment of the variables, `eval(push_not(e)) == eval(e)`.","`Not` appears only on `Var` nodes in the result."],
  ["`push_not(push_not(e)) == push_not(e)`.","`push_not(Not(e))` is the negation of `push_not(e)` on every assignment.","The number of variables mentioned is unchanged."],
  ["NOT (a AND b) -> NOT a OR NOT b","NOT (a OR NOT b) -> NOT a AND b"],
  ["Each law.","Nested negations.","A property: equal truth tables on every assignment."],
  src=("src/optimizer/push_not.rs", '''
//! Pushing NOT down to the variables of a boolean expression.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum B {
    Var(usize),
    Not(Box<B>),
    And(Box<B>, Box<B>),
    Or(Box<B>, Box<B>),
}

pub fn eval(e: &B, vars: &[bool]) -> bool {
    match e {
        B::Var(i) => vars[*i],
        B::Not(a) => !eval(a, vars),
        B::And(a, b) => eval(a, vars) && eval(b, vars),
        B::Or(a, b) => eval(a, vars) || eval(b, vars),
    }
}

pub fn push_not(e: &B) -> B {
    go(e, false)
}

/// `negate` says that an odd number of NOTs are being pushed through this subtree.
fn go(e: &B, negate: bool) -> B {
    match e {
        B::Var(i) => {
            if negate {
                B::Not(Box::new(B::Var(*i)))
            } else {
                B::Var(*i)
            }
        }
        B::Not(a) => go(a, !negate),
        B::And(a, b) => {
            let (l, r) = (Box::new(go(a, negate)), Box::new(go(b, negate)));
            // @begin 3h-c4
            if negate {
                B::Or(l, r)
            } else {
                B::And(l, r)
            }
            //~ B::And(l, r)
            // @end
        }
        B::Or(a, b) => {
            let (l, r) = (Box::new(go(a, negate)), Box::new(go(b, negate)));
            if negate {
                B::And(l, r)
            } else {
                B::Or(l, r)
            }
        }
    }
}
'''),
  test=("tests/stages_3h.rs", '''
use bustub::optimizer::push_not::{eval, push_not, B, B::*};

fn b(e: B) -> Box<B> {
    Box::new(e)
}

#[test]
fn s3h_c4_not_over_and_becomes_or_of_nots() {
    let e = Not(b(And(b(Var(0)), b(Var(1)))));
    assert_eq!(push_not(&e), Or(b(Not(b(Var(0)))), b(Not(b(Var(1))))));
}

#[test]
fn s3h_c4_not_over_or_becomes_and_of_nots() {
    let e = Not(b(Or(b(Var(0)), b(Not(b(Var(1)))))));
    assert_eq!(push_not(&e), And(b(Not(b(Var(0)))), b(Var(1))));
}

#[test]
fn s3h_c4_double_negation_disappears() {
    assert_eq!(push_not(&Not(b(Not(b(Var(2)))))), Var(2));
}

fn arb() -> impl Strategy<Value = B> {
    (0usize..3).prop_map(Var).prop_recursive(4, 20, 2, |inner| {
        prop_oneof![
            inner.clone().prop_map(|e| Not(Box::new(e))),
            (inner.clone(), inner.clone()).prop_map(|(a, c)| And(Box::new(a), Box::new(c))),
            (inner.clone(), inner).prop_map(|(a, c)| Or(Box::new(a), Box::new(c))),
        ]
    })
}

fn nots_only_on_vars(e: &B) -> bool {
    match e {
        Var(_) => true,
        Not(a) => matches!(**a, Var(_)),
        And(a, c) | Or(a, c) => nots_only_on_vars(a) && nots_only_on_vars(c),
    }
}

#[test]
fn s3h_c4_triple_negation_leaves_one_and_negated_variables_stay() {
    assert_eq!(push_not(&Not(b(Not(b(Not(b(Var(1)))))))), Not(b(Var(1))));
    assert_eq!(push_not(&Not(b(Var(0)))), Not(b(Var(0))));
    assert_eq!(push_not(&And(b(Var(0)), b(Not(b(Not(b(Var(1)))))))), And(b(Var(0)), b(Var(1))));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: same truth table on every assignment, NOT only on variables, and idempotent.
    #[test]
    fn s3h_c4_property_the_truth_table_is_preserved(e in arb()) {
        let p = push_not(&e);
        for bits in 0..8u32 {
            let vars: Vec<bool> = (0..3).map(|i| bits >> i & 1 == 1).collect();
            prop_assert_eq!(eval(&p, &vars), eval(&e, &vars), "assignment {:03b}", bits);
        }
        prop_assert!(nots_only_on_vars(&p));
        prop_assert_eq!(push_not(&p), p);
    }
}
''')))

CH.append(C("3h-c5", M3H, "94-challenge-a-histogram", "build", "Challenge: a histogram", "medium", "stages_3h::s3h_c5",
  ["estimating how many rows satisfy a range predicate from a summary","error bounds of an equi-width histogram"],
  ["rule-based-query-optimization","property-testing-and-fuzzing"],
  "`Histogram` in `src/optimizer/histogram.rs`: an equi-width histogram of integer values: `build(values, buckets)` divides `[min, max]` into `buckets` equal-width ranges and counts the values in each; `estimate_le(x)` estimates how many values are `<= x`, assuming values are spread evenly **inside** a bucket; `estimate_range(lo, hi)` how many are in `lo..=hi`.",
  "The optimiser cannot count rows to decide how to run a query: it has a few kilobytes of statistics per column. A histogram turns `WHERE age BETWEEN 30 AND 40` into a row estimate, and that estimate decides between an index scan and a table scan. The interesting question is how wrong it can be, and the answer is bounded and testable.",
  ["Buckets cover `[min, max]` in equal widths (the last bucket includes `max`); `n` is the number of values.","`estimate_le(x)` is 0 below `min`, `n` at or above `max`, and between them the counts of the buckets entirely below `x` plus a **linear share** of the bucket containing `x`.","`estimate_range(lo, hi)` is `estimate_le(hi) - estimate_le(lo - 1)` (0 if `hi < lo`)."],
  ["The bucket counts add up to `n`.","`estimate_le` is non-decreasing in `x` and between 0 and `n`."],
  ["At a bucket boundary, the estimate is exact for values that fall on the boundaries.","The estimate of `<= x` is within one bucket's count of the true count.","`estimate_range(a, b) + estimate_le(a - 1) == estimate_le(b)`."],
  ["values 0..100, 10 buckets: estimate_le(49) = 50 (exact), estimate_le(54) is about 55"],
  ["Exact counts at boundaries and the edges.","Monotonicity.","The error bound against true counts."],
  src=("src/optimizer/histogram.rs", '''
//! An equi-width histogram for selectivity estimates.

pub struct Histogram {
    // @begin 3h-c5
    min: i64,
    max: i64,
    counts: Vec<u64>,
    n: u64,
    //~ _hist: (),
    // @end
}

impl Histogram {
    /// `buckets >= 1`. An empty input gives a histogram that estimates 0 everywhere.
    pub fn build(values: &[i64], buckets: usize) -> Histogram {
        // @begin 3h-c5
        let buckets = buckets.max(1);
        let (Some(&min), Some(&max)) = (values.iter().min(), values.iter().max()) else {
            return Histogram { min: 0, max: 0, counts: vec![0; buckets], n: 0 };
        };
        let mut h = Histogram { min, max, counts: vec![0; buckets], n: values.len() as u64 };
        for &v in values {
            let b = h.bucket_of(v);
            h.counts[b] += 1;
        }
        h
        //~ todo!("3h-c5: min, max and a count per equal-width bucket")
        // @end
    }

    // @begin 3h-c5
    fn width(&self) -> f64 {
        (self.max - self.min + 1) as f64 / self.counts.len() as f64
    }

    fn bucket_of(&self, v: i64) -> usize {
        (((v - self.min) as f64 / self.width()) as usize).min(self.counts.len() - 1)
    }
    //~ // TODO(3h-c5): helpers of your own
    // @end

    pub fn count(&self) -> u64 {
        // @begin 3h-c5
        self.n
        //~ todo!("3h-c5: the number of values")
        // @end
    }

    pub fn bucket_counts(&self) -> &[u64] {
        // @begin 3h-c5
        &self.counts
        //~ todo!("3h-c5: the count of each bucket")
        // @end
    }

    /// Estimated number of values `<= x`.
    pub fn estimate_le(&self, x: i64) -> f64 {
        // @begin 3h-c5
        if self.n == 0 || x < self.min {
            return 0.0;
        }
        if x >= self.max {
            return self.n as f64;
        }
        let b = self.bucket_of(x);
        let below: u64 = self.counts[..b].iter().sum();
        let lo = self.min as f64 + b as f64 * self.width();
        let share = ((x as f64 + 1.0 - lo) / self.width()).clamp(0.0, 1.0);
        below as f64 + share * self.counts[b] as f64
        //~ todo!("3h-c5: the buckets below plus a linear share of the bucket x is in")
        // @end
    }

    /// Estimated number of values in `lo..=hi`.
    pub fn estimate_range(&self, lo: i64, hi: i64) -> f64 {
        if hi < lo {
            return 0.0;
        }
        self.estimate_le(hi) - self.estimate_le(lo - 1)
    }
}
'''),
  test=("tests/stages_3h.rs", '''
use bustub::optimizer::histogram::Histogram;

#[test]
fn s3h_c5_counts_add_up_and_the_edges_are_exact() {
    let v: Vec<i64> = (0..100).collect();
    let h = Histogram::build(&v, 10);
    assert_eq!(h.bucket_counts().iter().sum::<u64>(), 100);
    assert_eq!(h.count(), 100);
    assert_eq!(h.estimate_le(-1), 0.0);
    assert_eq!(h.estimate_le(99), 100.0);
    assert_eq!(h.estimate_le(1000), 100.0);
}

#[test]
fn s3h_c5_bucket_boundaries_are_exact_for_evenly_spread_data() {
    let v: Vec<i64> = (0..100).collect();
    let h = Histogram::build(&v, 10);
    assert!((h.estimate_le(49) - 50.0).abs() < 1e-9);
    assert!((h.estimate_le(54) - 55.0).abs() < 1e-9, "half of the sixth bucket, linearly");
    assert!((h.estimate_range(10, 29) - 20.0).abs() < 1e-9);
}

#[test]
fn s3h_c5_skewed_data_is_summarised_by_bucket_not_by_value() {
    let mut v = vec![0i64; 90];
    v.extend(90..100);
    let h = Histogram::build(&v, 10);
    assert_eq!(h.bucket_counts()[0], 90);
    assert!((h.estimate_le(9) - 90.0).abs() < 1e-9);
    assert!(h.estimate_le(4) > 40.0 && h.estimate_le(4) < 50.0, "inside the first bucket the values are assumed even: {}", h.estimate_le(4));
}

#[test]
fn s3h_c5_empty_and_constant_columns() {
    let e = Histogram::build(&[], 4);
    assert_eq!((e.count(), e.estimate_le(10)), (0, 0.0));
    let c = Histogram::build(&[7, 7, 7], 4);
    assert_eq!((c.estimate_le(6), c.estimate_le(7)), (0.0, 3.0));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: monotone, between 0 and n, and within the size of one bucket of the true count.
    #[test]
    fn s3h_c5_property_estimates_are_bounded_and_close(v in proptest::collection::vec(-50i64..50, 1..60), buckets in 1usize..9, x in -60i64..60) {
        let h = Histogram::build(&v, buckets);
        prop_assert_eq!(h.bucket_counts().iter().sum::<u64>(), v.len() as u64);
        let est = h.estimate_le(x);
        prop_assert!(est >= 0.0 && est <= v.len() as f64);
        prop_assert!(h.estimate_le(x + 1) >= est - 1e-9);
        let truth = v.iter().filter(|&&y| y <= x).count() as f64;
        let widest = *h.bucket_counts().iter().max().unwrap() as f64;
        prop_assert!((est - truth).abs() <= widest + 1e-9, "estimate {} truth {} widest bucket {}", est, truth, widest);
        let (a, bnd) = (x.min(x + 7), x.max(x + 7));
        prop_assert!((h.estimate_range(a, bnd) + h.estimate_le(a - 1) - h.estimate_le(bnd)).abs() < 1e-9);
    }
}
''')))
