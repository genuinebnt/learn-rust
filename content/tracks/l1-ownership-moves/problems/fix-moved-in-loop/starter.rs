/// Groups consecutive records with the same key, and counts the records:
/// [("a", 1), ("a", 2), ("b", 3), ("a", 4)] → ([("a", [1, 2]), ("b", [3]), ("a", [4])], 4).
pub fn group_runs(records: Vec<(String, u32)>) -> (Vec<(String, Vec<u32>)>, usize) {
    let mut groups = Vec::new();
    let mut key = String::new();
    let mut run = Vec::new();
    for (k, v) in records {
        if k != key && !run.is_empty() {
            groups.push((key, run));
            run.clear();
        }
        key = k;
        run.push(v);
    }
    if !run.is_empty() {
        groups.push((key, run));
    }
    (groups, records.len())
}
