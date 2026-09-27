use solution::*;

fn queue(xs: &[(&str, u64)]) -> Queue {
    Queue { jobs: xs.iter().map(|&(n, d)| Job { name: n.to_string(), deadline: d }).collect() }
}

fn sv(xs: &[&str]) -> Vec<String> {
    xs.iter().map(|s| s.to_string()).collect()
}

fn names(jobs: &[Job]) -> Vec<String> {
    jobs.iter().map(|j| j.name.to_string()).collect()
}

#[test]
fn take_expired() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 10, limit 5)"#, (names(&q.take_expired(10, 5)), names(&q.jobs)), (sv(&["a", "c", "d"]), sv(&["b", "e"])));
}

#[test]
fn limit_leaves_the_rest() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 10, limit 2)"#, (names(&q.take_expired(10, 2)), names(&q.jobs)), (sv(&["a", "c"]), sv(&["b", "d", "e"])));
}

#[test]
fn next_batch() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; next_batch(2), then next_batch(9)"#, { let first = q.next_batch(2); let rest = q.next_batch(9); (names(&first), names(&rest), q.jobs.len()) }, (sv(&["a", "b"]), sv(&["c", "d", "e"]), 0));
}

#[test]
fn defer() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; defer("b"), defer("z")"#, (q.defer("b"), q.defer("z"), names(&q.jobs)), (true, false, sv(&["a", "c", "d", "e", "b"])));
}

#[test]
fn deadline_is_strict() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 5, limit 9)"#, names(&q.take_expired(5, 9)), sv(&["d"]));
}

#[test]
fn limit_zero() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 100, limit 0)"#, (q.take_expired(100, 0).len(), q.jobs.len()), (0, 5));
}
