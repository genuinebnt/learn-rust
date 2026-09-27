use solution::*;

#[test]
fn parallel_sum_example() {
    check!(r#"1..=100 on 4 threads"#, parallel_sum(&(1..=100).collect::<Vec<u64>>(), 4), 5050);
}

#[test]
fn count_after_dropping_docs() {
    check!(r#"count_later(["a b", "c"]), docs dropped, then join"#, { let h = { let docs = vec!["a b".to_string(), "c".to_string()]; count_later(&docs) }; h.join().unwrap() }, 3);
}

#[test]
fn spawn_named_sets_the_name() {
    check!(r#"spawn_named("worker-1", read own name)"#, spawn_named("worker-1", || std::thread::current().name().map(String::from)).join().unwrap(), Some("worker-1".to_string()));
}

#[test]
fn parallel_sum_empty() {
    check!(r#"[] on 3 threads"#, parallel_sum(&[], 3), 0);
}

#[test]
fn spawn_named_moves_data() {
    let v = vec![1, 2, 3];
    check!(r#"spawn_named with an owned Vec"#, spawn_named("sum", move || v.iter().sum::<i32>()).join().unwrap(), 6);
}
