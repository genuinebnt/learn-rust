pub fn dedup_sorted(v: &mut [i32]) -> usize {
    if v.is_empty() {
        return 0;
    }
    let mut write = 1;
    for read in 1..v.len() {
        if v[read] != v[write - 1] {
            v[write] = v[read];
            write += 1;
        }
    }
    write
}
