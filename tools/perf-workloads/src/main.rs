use std::time::Instant;

use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::concurrency::transaction::IsolationLevel;
use bustub::concurrency::watermark::Watermark;
use bustub::primer::robin_hood_hash_set::RobinHoodHashSet;
use bustub::primer::skiplist::SkipList;
use bustub::primer::trie::Trie;

fn time<R>(what: &str, f: impl FnOnce() -> R) -> R {
    let t = Instant::now();
    let r = f();
    println!("{what:<62} {:>9.1} ms", t.elapsed().as_secs_f64() * 1000.0);
    r
}

fn sql(db: &BusTubInstance, txn: &std::sync::Arc<bustub::concurrency::transaction::Transaction>, q: &str) -> usize {
    let mut out = String::new();
    db.execute_sql_txn(q, &mut SimpleStreamWriter::new(&mut out, true, " "), txn).unwrap();
    out.lines().count()
}

fn main() {
    let which = std::env::args().nth(1).unwrap_or_default();
    let all = which.is_empty();
    if all || which == "watermark" {
        time("watermark: add 1M readers, remove them (BTreeMap)", || {
            let mut w = Watermark::new(0);
            for i in 0..1_000_000 {
                w.add_txn(i).unwrap();
            }
            for i in 0..1_000_000 {
                w.update_commit_ts(i + 1);
                w.remove_txn(i);
                std::hint::black_box(w.get_watermark());
            }
        });
    }
    if all || which == "skiplist" {
        let l: SkipList<i32> = SkipList::new();
        time("skip list: 200k inserts", || (0..200_000).for_each(|i| drop(l.insert(&i))));
        time("skip list: 200k contains", || (0..200_000).for_each(|i| drop(std::hint::black_box(l.contains(&i)))));
    }
    if all || which == "robin" {
        let s: RobinHoodHashSet<i32> = RobinHoodHashSet::new(262_144).unwrap();
        time("robin hood: 200k inserts (load 0.76)", || (0..200_000).for_each(|i| drop(s.insert(&i))));
        println!("  max probe distance {}", s.max_probe_distance());
        time("robin hood: 200k contains", || (0..200_000).for_each(|i| drop(std::hint::black_box(s.contains(&i)))));
        time("robin hood: 200k absent lookups", || (200_000..400_000).for_each(|i| drop(std::hint::black_box(s.contains(&i)))));
    }
    if all || which == "robin_random" {
        let s: RobinHoodHashSet<i64> = RobinHoodHashSet::new(262_144).unwrap();
        let mut x = 88172645463325252u64;
        let keys: Vec<i64> = (0..200_000).map(|_| { x ^= x << 13; x ^= x >> 7; x ^= x << 17; (x >> 3) as i64 }).collect();
        time("robin hood: 200k RANDOM inserts (load 0.76)", || keys.iter().for_each(|k| drop(s.insert(k))));
        println!("  max probe distance {}", s.max_probe_distance());
        time("robin hood: 200k random lookups (present)", || keys.iter().for_each(|k| drop(std::hint::black_box(s.contains(k)))));
        time("robin hood: 200k random lookups (absent)", || keys.iter().for_each(|k| drop(std::hint::black_box(s.contains(&(k ^ 0x5555))))));
    }
    if which == "flame_mvcc" {
        let db = BusTubInstance::new(256);
        let mut sink = String::new();
        db.execute_sql("CREATE TABLE t(a int, b int)", &mut SimpleStreamWriter::new(&mut sink, true, " "), None).unwrap();
        let t0 = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
        let values: Vec<String> = (0..20_000).map(|i| format!("({i}, 0)")).collect();
        sql(&db, &t0, &format!("INSERT INTO t VALUES {}", values.join(",")));
        db.txn_manager.commit(&t0).unwrap();
        let old = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
        for _ in 0..10 {
            let t = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
            sql(&db, &t, "UPDATE t SET b = b + 1");
            db.txn_manager.commit(&t).unwrap();
        }
        for _ in 0..400 {
            std::hint::black_box(sql(&db, &old, "SELECT * FROM t"));
        }
    }
    if all || which == "trie" {
        time("trie: 23333 puts keeping every version", || {
            let mut t = Trie::new();
            let mut keep = Vec::new();
            for i in 0..23_333u32 {
                t = t.put(&format!("{i:05}"), i);
                keep.push(t.clone());
            }
            std::hint::black_box(keep.len())
        });
    }
    if all || which == "mvcc" {
        let db = BusTubInstance::new(256);
        let mut sink = String::new();
        db.execute_sql("CREATE TABLE t(a int, b int)", &mut SimpleStreamWriter::new(&mut sink, true, " "), None).unwrap();
        let t0 = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
        let values: Vec<String> = (0..20_000).map(|i| format!("({i}, 0)")).collect();
        time("mvcc: insert 20k rows in one transaction", || sql(&db, &t0, &format!("INSERT INTO t VALUES {}", values.join(","))));
        time("mvcc: commit it", || db.txn_manager.commit(&t0).unwrap());
        let old = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
        for round in 0..10 {
            let t = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
            time(&format!("mvcc: update all 20k rows (round {round})"), || sql(&db, &t, "UPDATE t SET b = b + 1"));
            db.txn_manager.commit(&t).unwrap();
        }
        let new = db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap();
        time("mvcc: scan 20k rows as a NEW reader (no logs to apply)", || sql(&db, &new, "SELECT * FROM t"));
        time("mvcc: scan 20k rows as an OLD reader (10-log chains)", || sql(&db, &old, "SELECT * FROM t"));
        db.txn_manager.commit(&old).unwrap();
        db.txn_manager.commit(&new).unwrap();
        time("mvcc: garbage collection over 20k chains", || db.txn_manager.garbage_collection());
    }
}
