use solution::*;

/// Ordered by priority only, so equal-priority jobs are distinguishable.
#[derive(Debug, PartialEq, Eq)]
struct Job(u8, &'static str);

impl PartialOrd for Job {
    fn partial_cmp(&self, o: &Job) -> Option<std::cmp::Ordering> {
        Some(self.cmp(o))
    }
}

impl Ord for Job {
    fn cmp(&self, o: &Job) -> std::cmp::Ordering {
        self.0.cmp(&o.0)
    }
}

/// A test-defined strategy: everything is equal.
#[allow(dead_code)]
struct Unordered;

impl Order for Unordered {
    fn cmp<T: Ord>(_: &T, _: &T) -> std::cmp::Ordering {
        std::cmp::Ordering::Equal
    }
}

fn names<O: Order>(v: &SortedVec<Job, O>) -> Vec<&'static str> {
    v.as_slice().iter().map(|j| j.1).collect()
}

#[test]
fn default_is_ascending() {
    let v: SortedVec<i32> = vec![3, 1, 2].into_iter().collect();
    check!(r#"SortedVec<i32> from [3, 1, 2]"#, v.as_slice(), [1, 2, 3]);
}

#[test]
fn descending() {
    let v: SortedVec<i32, Desc> = vec![3, 1, 2].into_iter().collect();
    check!(r#"SortedVec<i32, Desc> from [3, 1, 2]"#, v.as_slice(), [3, 2, 1]);
}

#[test]
fn equal_items_keep_insertion_order() {
    let v: SortedVec<Job> = vec![Job(1, "a"), Job(0, "b"), Job(1, "c"), Job(0, "d")].into_iter().collect();
    check!(r#"jobs (1, a), (0, b), (1, c), (0, d)"#, names(&v), vec!["b", "d", "a", "c"]);
}

#[test]
fn reorder_is_stable() {
    let v: SortedVec<Job> = vec![Job(1, "a"), Job(0, "b"), Job(1, "c"), Job(0, "d")].into_iter().collect();
    check!(r#"the same jobs, reordered to Desc"#, names(&v.reorder::<Desc>()), vec!["a", "c", "b", "d"]);
}

#[test]
fn zero_cost() {
    check!(r#"size_of SortedVec<u64, Desc> vs Vec<u64>"#, (std::mem::size_of::<SortedVec<u64, Desc>>(), std::mem::size_of::<Asc>()), (std::mem::size_of::<Vec<u64>>(), 0));
}
