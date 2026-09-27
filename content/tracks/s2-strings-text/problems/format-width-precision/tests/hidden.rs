use solution::*;

#[test]
fn table_unicode_names() {
    check!(r#"[("crème", 1.0), ("tea", 2.0)], prec 1: width in chars"#, table(&[("crème", 1.0), ("tea", 2.0)], 1), "crème | 1.0\ntea   | 2.0\n".to_string());
}

#[test]
fn table_negative_value() {
    check!(r#"[("in", 10.0), ("out", -3.75)], prec 2"#, table(&[("in", 10.0), ("out", -3.75)], 2), "in  | 10.00\nout | -3.75\n".to_string());
}

#[test]
fn table_prec_zero() {
    check!(r#"[("a", 3.25), ("bb", 100.0)], prec 0"#, table(&[("a", 3.25), ("bb", 100.0)], 0), "a  |   3\nbb | 100\n".to_string());
}

#[test]
fn table_prec_four() {
    check!(r#"[("pi", 3.14159265)], prec 4"#, table(&[("pi", 3.14159265)], 4), "pi | 3.1416\n".to_string());
}

#[test]
fn table_empty_name() {
    check!(r#"[("", 1.0), ("x", 22.5)], prec 1"#, table(&[("", 1.0), ("x", 22.5)], 1), "  |  1.0\nx | 22.5\n".to_string());
}

#[test]
fn table_cjk_name() {
    check!(r#"[("日本", 1.0), ("abc", 1.0)], prec 0"#, table(&[("日本", 1.0), ("abc", 1.0)], 0), "日本  | 1\nabc | 1\n".to_string());
}

#[test]
fn register_zero_and_max() {
    check!(r#"0 and u32::MAX"#, (register(0), register(u32::MAX)), ("0x00000000 = 00000000_00000000_00000000_00000000".to_string(), "0xffffffff = 11111111_11111111_11111111_11111111".to_string()));
}

#[test]
fn register_byte_order() {
    check!(r#"0x01020304"#, register(0x0102_0304), "0x01020304 = 00000001_00000010_00000011_00000100".to_string());
}

#[test]
fn register_high_bit() {
    check!(r#"0x80000001"#, register(0x8000_0001), "0x80000001 = 10000000_00000000_00000000_00000001".to_string());
}

#[test]
fn hexdump_empty() {
    check!(r#"offset 0x20, bytes b''"#, hexdump_line(0x20, b""), "00000020                                                    ||".to_string());
}

#[test]
fn hexdump_eight_bytes() {
    check!(r#"offset 0x8, bytes b'ABCDEFGH'"#, hexdump_line(0x8, b"\x41\x42\x43\x44\x45\x46\x47\x48"), "00000008  41 42 43 44 45 46 47 48                           |ABCDEFGH|".to_string());
}

#[test]
fn hexdump_nine_bytes() {
    check!(r#"offset 0x8, bytes b'ABCDEFGHI'"#, hexdump_line(0x8, b"\x41\x42\x43\x44\x45\x46\x47\x48\x49"), "00000008  41 42 43 44 45 46 47 48  49                       |ABCDEFGHI|".to_string());
}

#[test]
fn hexdump_control_and_high_bytes() {
    check!(r#"offset 0xff, bytes b'\x00\t\x1f\x7f\x80\xc3\xa9\xff ~'"#, hexdump_line(0xff, b"\x00\x09\x1f\x7f\x80\xc3\xa9\xff\x20\x7e"), "000000ff  00 09 1f 7f 80 c3 a9 ff  20 7e                    |........ ~|".to_string());
}

#[test]
fn hexdump_large_offset() {
    check!(r#"offset 0x12345678, bytes b'z'"#, hexdump_line(0x12345678, b"\x7a"), "12345678  7a                                                |z|".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7205);
    for _ in 0..300 {
        let n = rng.below(5);
        let mut names = Vec::new();
        let mut values = Vec::new();
        for _ in 0..n {
            let len = rng.below(6);
            names.push(rng.string(len, "abé日"));
            values.push(rng.int(-100_000, 1_000_000) as f64 / 64.0);
        }
        let prec = rng.below(4);
        let rows: Vec<(&str, f64)> = names.iter().map(|s| s.as_str()).zip(values.iter().copied()).collect();
        let shown: Vec<String> = values.iter().map(|v| format!("{v:.prec$}")).collect();
        let nw = names.iter().map(|s| s.chars().count()).max().unwrap_or(0);
        let vw = shown.iter().map(|s| s.len()).max().unwrap_or(0);
        let mut want = String::new();
        for (name, v) in names.iter().zip(&shown) {
            want += name;
            want += &" ".repeat(nw - name.chars().count());
            want += " | ";
            want += &" ".repeat(vw - v.len());
            want += v;
            want.push('\n');
        }
        let value = rng.next_u64() as u32;
        let mut reg = String::from("0x");
        for shift in (0..8).rev() {
            reg.push(char::from_digit((value >> (shift * 4)) & 0xf, 16).unwrap());
        }
        reg += " = ";
        for bit in (0..32).rev() {
            reg.push(if value >> bit & 1 == 1 { '1' } else { '0' });
            if bit % 8 == 0 && bit > 0 {
                reg.push('_');
            }
        }
        let len = rng.below(17);
        let bytes: Vec<u8> = rng.vec(len, 0, 255);
        let offset = rng.below(1 << 20);
        let mut line = String::new();
        for shift in (0..8).rev() {
            line.push(char::from_digit(((offset >> (shift * 4)) & 0xf) as u32, 16).unwrap());
        }
        line += "  ";
        let mut hex = String::new();
        for (i, b) in bytes.iter().enumerate() {
            hex.push(char::from_digit((b >> 4) as u32, 16).unwrap());
            hex.push(char::from_digit((b & 0xf) as u32, 16).unwrap());
            hex.push(' ');
            if i == 7 {
                hex.push(' ');
            }
        }
        while hex.len() < 49 {
            hex.push(' ');
        }
        line += &hex;
        line += " |";
        for &b in &bytes {
            line.push(if (0x20..0x7f).contains(&b) { b as char } else { '.' });
        }
        line.push('|');
        check!(format!("rows = {rows:?}, prec = {prec}, value = {value}, offset = {offset}, bytes = {bytes:?}"),
               (table(&rows, prec), register(value), hexdump_line(offset, &bytes)), (want, reg, line));
    }
}
