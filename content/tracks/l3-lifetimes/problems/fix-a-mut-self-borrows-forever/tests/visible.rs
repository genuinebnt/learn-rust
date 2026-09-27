use solution::*;

#[test]
fn take_twice() {
    let data = [1u8, 2, 3, 4];
    let mut r = Reader::new(&data);
    check!(r#"data [1, 2, 3, 4]: take 1, take 2, remaining"#, (r.take(1), r.take(2), r.remaining()), (Some(&[1u8][..]), Some(&[2u8, 3][..]), 1));
}

#[test]
fn peek_then_take() {
    let data = [7u8, 8];
    let mut r = Reader::new(&data);
    check!(r#"data [7, 8]: peek, take 1, peek"#, (r.peek(), r.take(1).map(|b| b[0]), r.peek()), (Some(7), Some(7), Some(8)));
}

#[test]
fn u16_big_endian() {
    let data = [1u8, 2, 0xff];
    let mut r = Reader::new(&data);
    check!(r#"data [1, 2, 0xff]: u16, then u16"#, (r.u16(), r.u16(), r.remaining()), (Some(258), None, 1));
}

#[test]
fn records_then_keep_reading() {
    let data = [0u8, 2, b'h', b'i', 0, 0];
    let mut r = Reader::new(&data);
    let recs = records(&mut r);
    check!(r#"records of [0, 2, 'h', 'i', 0, 0]; then remaining"#, (recs, r.remaining()), (Some(vec![&b"hi"[..], &b""[..]]), 0));
}

#[test]
fn chunks_outlive_the_reader() {
    let data = [9u8, 9, 9];
    let chunk = Reader::new(&data).take(2);
    check!(r#"take 2 from a reader that's then dropped"#, chunk, Some(&[9u8, 9][..]));
}
