use solution::*;

fn collect_upper(text: &str) -> Vec<String> {
    let mut it = upper_lines(text);
    let mut out = Vec::new();
    while let Some(s) = it.next() {
        out.push(s.to_string());
    }
    out
}

#[test]
fn reuses_one_buffer() {
    let mut it = upper_lines("hello\nhi");
    let p1 = it.next().unwrap().as_ptr() as usize;
    let p2 = it.next().unwrap().as_ptr() as usize;
    check!(r#"addresses of the first and second item of "hello\nhi""#, p1 == p2, true);
}

#[test]
fn whole_slice_window() {
    check!(r#"windows of 3 over [1, 2, 3]"#, count(windows_mut(&mut [1, 2, 3], 3)), 1);
}

#[test]
fn empty_slice() {
    check!(r#"windows of 1 over []"#, count(windows_mut(&mut Vec::<i32>::new(), 1)), 0);
}

#[test]
fn zero_size_panics() {
    check!(r#"windows_mut(&mut [1], 0)"#, std::panic::catch_unwind(|| count(windows_mut(&mut [1], 0))).is_err(), true);
}

#[test]
fn windows_see_earlier_writes() {
    let mut v = vec![1, 0, 0, 0, 0];
    let mut it = windows_mut(&mut v, 3);
    while let Some(w) = it.next() {
        w[2] = w[0] + w[1] + 1;
    }
    check!(r#"windows of 3 over [1, 0, 0, 0, 0]: w[2] = w[0] + w[1] + 1"#, v, vec![1, 0, 2, 3, 6]);
}

#[test]
fn upper_unicode() {
    check!(r#"upper_lines("straße\n  é ")"#, collect_upper("straße\n  é "), vec!["STRASSE", "É"]);
}

#[test]
fn upper_empty_lines() {
    check!(r#"upper_lines("a\n\n b")"#, collect_upper("a\n\n b"), vec!["A", "", "B"]);
}

#[test]
fn upper_no_text() {
    check!(r#"upper_lines("")"#, count(upper_lines("")), 0);
}

#[test]
fn a_new_lending_iterator() {
    // count accepts any implementation, including items that don't borrow at all.
    struct Countdown(u32);
    impl LendingIterator for Countdown {
        type Item<'a> = u32 where Self: 'a;
        fn next(&mut self) -> Option<u32> {
            self.0 = self.0.checked_sub(1)?;
            Some(self.0)
        }
    }
    check!("count(Countdown(4))", count(Countdown(4)), 4);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4422);
    for _ in 0..300 {
        let len = rng.below(8);
        let orig: Vec<i64> = rng.vec(len, -5, 5);
        let size = rng.below(4) + 1;
        let mut v = orig.clone();
        let mut it = windows_mut(&mut v, size);
        while let Some(w) = it.next() {
            w[size - 1] += w[0] * 2;
        }
        let mut want = orig.clone();
        for s in 0..(len + 1).saturating_sub(size) {
            want[s + size - 1] += want[s] * 2;
        }
        check!(format!("{orig:?}, size {size}"), v, want);
    }
}
