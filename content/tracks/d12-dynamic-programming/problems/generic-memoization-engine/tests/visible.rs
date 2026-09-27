use solution::*;
use std::cell::Cell;

#[test]
fn fibonacci_90() {
    let mut fib = Memo::<u64, u128>::new(|m, n| if n < 2 { n as u128 } else { m.get(n - 1) + m.get(n - 2) });
    check!(r#"fib via Memo<u64, u128>, n = 90"#, fib.get(90), 2_880_067_194_370_816_120);
}

#[test]
fn computes_each_key_once() {
    let calls = Cell::new(0);
    let mut square = Memo::<u32, u32>::new(|_, n| {
        calls.set(calls.get() + 1);
        n * n
    });
    check!(r#"square(7) asked twice; (first, second, calls to f)"#, (square.get(7), square.get(7), calls.get()), (49, 49, 1));
}

#[test]
fn len_counts_cached_keys() {
    let mut fib = Memo::<u64, u64>::new(|m, n| if n < 2 { n } else { m.get(n - 1) + m.get(n - 2) });
    fib.get(10);
    check!(r#"fib.get(10), then fib.len()"#, fib.len(), 11);
}

#[test]
fn starts_empty() {
    let m = Memo::<u8, u8>::new(|_, x| x);
    check!(r#"a new memo: (len, is_empty)"#, (m.len(), m.is_empty()), (0, true));
}

#[test]
fn tuple_keys() {
    let mut paths = Memo::<(u32, u32), u64>::new(|m, (r, c)| if r == 0 || c == 0 { 1 } else { m.get((r - 1, c)) + m.get((r, c - 1)) });
    check!(r#"grid paths to (16, 16), key (row, col)"#, paths.get((16, 16)), 601_080_390);
}
