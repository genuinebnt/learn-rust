use solution::*;

#[test]
fn table_two_rows() {
    check!(r#"[("coffee", 3.5), ("tea", 12.25)], prec 2"#, table(&[("coffee", 3.5), ("tea", 12.25)], 2), "coffee |  3.50\ntea    | 12.25\n".to_string());
}

#[test]
fn table_empty() {
    check!(r#"[], prec 2"#, table(&[], 2), "".to_string());
}

#[test]
fn register_small() {
    check!(r#"0xdead"#, register(0xdead), "0x0000dead = 00000000_00000000_11011110_10101101".to_string());
}

#[test]
fn hexdump_short_line() {
    check!(r#"offset 0x10, bytes b'Hi!\n'"#, hexdump_line(0x10, b"\x48\x69\x21\x0a"), "00000010  48 69 21 0a                                       |Hi!.|".to_string());
}

#[test]
fn hexdump_full_line() {
    check!(r#"offset 0x0, bytes b'0123456789abcdef'"#, hexdump_line(0x0, b"\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x61\x62\x63\x64\x65\x66"), "00000000  30 31 32 33 34 35 36 37  38 39 61 62 63 64 65 66  |0123456789abcdef|".to_string());
}
