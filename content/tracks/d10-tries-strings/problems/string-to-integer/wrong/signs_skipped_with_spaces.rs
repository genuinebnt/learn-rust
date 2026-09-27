pub fn my_atoi(s: &str) -> i32 {
    let negative = s.trim_start_matches(' ').starts_with('-');
    let digits = s.trim_start_matches([' ', '+', '-']);
    let mut n: i32 = 0;
    for b in digits.bytes().take_while(u8::is_ascii_digit) {
        let d = i32::from(b - b'0');
        let next = n.checked_mul(10).and_then(|n| if negative { n.checked_sub(d) } else { n.checked_add(d) });
        match next {
            Some(v) => n = v,
            None => return if negative { i32::MIN } else { i32::MAX },
        }
    }
    n
}
