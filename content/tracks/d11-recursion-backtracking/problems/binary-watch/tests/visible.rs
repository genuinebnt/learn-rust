use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_one_led() {
    check!(r#"turned_on = 1"#, sorted(read_binary_watch(1)), vec!["0:01", "0:02", "0:04", "0:08", "0:16", "0:32", "1:00", "2:00", "4:00", "8:00"]);
}

#[test]
fn leetcode_nine_leds() {
    check!(r#"turned_on = 9"#, read_binary_watch(9), Vec::<String>::new());
}

#[test]
fn zero_leds() {
    check!(r#"turned_on = 0"#, read_binary_watch(0), vec!["0:00"]);
}

#[test]
fn eight_leds() {
    check!(r#"turned_on = 8"#, sorted(read_binary_watch(8)), vec!["11:31", "11:47", "11:55", "11:59", "7:31", "7:47", "7:55", "7:59"]);
}

#[test]
fn two_leds_count() {
    check!(r#"turned_on = 2"#, read_binary_watch(2).len(), 44);
}
