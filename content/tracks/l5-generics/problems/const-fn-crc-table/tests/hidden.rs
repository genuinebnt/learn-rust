use solution::*;

#[test]
fn single_byte_is_table_entry() {
    check!(r#"checksum(b"a") == TABLE[b'a']"#, (Crc8::<0x07>::checksum(b"a"), Crc8::<0x07>::TABLE[b'a' as usize]), (0x20, 0x20));
}

#[test]
fn zero_byte() {
    check!(r#"checksum(&[0])"#, Crc8::<0x07>::checksum(&[0]), 0);
}

#[test]
fn table_zero_entry() {
    check!(r#"TABLE[0] for two polynomials"#, (Crc8::<0x07>::TABLE[0], Crc8::<0x31>::TABLE[0]), (0, 0));
}

#[test]
fn table_last_entry() {
    check!(r#"TABLE[0xFF] for 0x07 and 0x31"#, (Crc8::<0x07>::TABLE[0xFF], Crc8::<0x31>::TABLE[0xFF]), (0xF3, 0xAC));
}

#[test]
fn make_table_directly() {
    const M: [u8; 256] = make_table(0x31);
    check!(r#"const M: [u8; 256] = make_table(0x31)"#, (M[1], M[0x80]), (0x31, 0x7A));
}

#[test]
fn poly_0x1d() {
    check!(r#"Crc8::<0x1D>::checksum(b"123456789")"#, Crc8::<0x1D>::checksum(b"123456789"), 0x37);
}

#[test]
fn poly_0x9b_in_const() {
    const X: u8 = Crc8::<0x9B>::checksum(b"123456789");
    check!(r#"const X: u8 = Crc8::<0x9B>::checksum(b"123456789")"#, X, 0xEA);
}

#[test]
fn all_bytes() {
    let bytes: Vec<u8> = (0..=255).collect();
    check!(r#"checksum of 0..=255"#, Crc8::<0x07>::checksum(&bytes), 0x14);
}

#[test]
fn appending_the_crc_gives_zero() {
    let mut data = b"anneal".to_vec();
    data.push(Crc8::<0x07>::checksum(&data));
    check!(r#"data followed by its own CRC checks to 0"#, Crc8::<0x07>::checksum(&data), 0);
}

fn bitwise(data: &[u8], poly: u8) -> u8 {
    let mut crc = 0u8;
    for &b in data {
        crc ^= b;
        for _ in 0..8 {
            crc = if crc & 0x80 != 0 { (crc << 1) ^ poly } else { crc << 1 };
        }
    }
    crc
}

#[test]
fn random_vs_bitwise() {
    let mut rng = anneal_prelude::Rng::new(4512);
    for _ in 0..300 {
        let n = rng.below(20);
        let data: Vec<u8> = rng.vec(n, 0, 255);
        check!(format!("data = {data:?}"), (Crc8::<0x07>::checksum(&data), Crc8::<0x31>::checksum(&data), Crc8::<0xD5>::checksum(&data)),
               (bitwise(&data, 0x07), bitwise(&data, 0x31), bitwise(&data, 0xD5)));
    }
}

#[test]
fn tables_vs_bitwise() {
    const T7: [u8; 256] = Crc8::<0x07>::TABLE;
    for b in 0..=255u8 {
        check!(format!("TABLE[{b}] for 0x07"), T7[b as usize], bitwise(&[b], 0x07));
    }
}
