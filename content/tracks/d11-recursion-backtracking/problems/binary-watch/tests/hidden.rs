use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn ten_leds() {
    check!(r#"turned_on = 10"#, read_binary_watch(10), Vec::<String>::new());
}

#[test]
fn three_leds() {
    check!(r#"turned_on = 3"#, read_binary_watch(3).len(), 112);
}

#[test]
fn four_leds() {
    check!(r#"turned_on = 4"#, read_binary_watch(4).len(), 181);
}

#[test]
fn five_leds() {
    check!(r#"turned_on = 5"#, read_binary_watch(5).len(), 190);
}

#[test]
fn six_leds() {
    check!(r#"turned_on = 6"#, read_binary_watch(6).len(), 126);
}

#[test]
fn seven_leds() {
    check!(r#"turned_on = 7"#, read_binary_watch(7).len(), 48);
}

#[test]
fn minutes_padded() {
    check!(r#"turned_on = 1: "0:01" is there"#, read_binary_watch(1).contains(&"0:01".to_string()), true);
}

#[test]
fn no_hour_twelve() {
    check!(r#"turned_on = 2: "12:00" is not a time"#, read_binary_watch(2).contains(&"12:00".to_string()), false);
}

#[test]
fn no_minute_sixty() {
    check!(r#"turned_on = 4: "0:60" is not a time"#, read_binary_watch(4).contains(&"0:60".to_string()), false);
}

#[test]
fn every_count_vs_clock_scan() {
    for on in 0..=10u32 {
        let mut want = Vec::new();
        for h in 0..12u32 {
            for m in 0..60u32 {
                if h.count_ones() + m.count_ones() == on {
                    want.push(format!("{h}:{m:02}"));
                }
            }
        }
        want.sort();
        check!(format!("turned_on = {on}"), sorted(read_binary_watch(on)), want);
    }
}
