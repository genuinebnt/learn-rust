use solution::*;

#[test]
fn check_value_smbus() {
    const C: u8 = Crc8::<0x07>::checksum(b"123456789");
    check!(r#"const C: u8 = Crc8::<0x07>::checksum(b"123456789")"#, C, 0xF4);
}

#[test]
fn table_entries() {
    const T: [u8; 256] = Crc8::<0x07>::TABLE;
    check!(r#"Crc8::<0x07>::TABLE[1], [2], [0x80]"#, (T[1], T[2], T[0x80]), (0x07, 0x0E, 0x89));
}

#[test]
fn empty_input() {
    check!(r#"checksum(b"")"#, Crc8::<0x07>::checksum(b""), 0);
}

#[test]
fn another_polynomial() {
    check!(r#"Crc8::<0x31>::checksum(b"123456789")"#, Crc8::<0x31>::checksum(b"123456789"), 0xA2);
}

#[test]
fn runtime_data() {
    let s = String::from("héllo");
    check!(r#"checksum of a String's bytes at run time"#, Crc8::<0x07>::checksum(s.as_bytes()), 0x9E);
}
