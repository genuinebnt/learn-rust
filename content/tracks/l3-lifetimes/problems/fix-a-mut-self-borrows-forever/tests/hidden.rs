use solution::*;

#[test]
fn take_too_many() {
    let data = [1u8];
    let mut r = Reader::new(&data);
    check!(r#"data [1]: take 2, then take 1"#, (r.take(2), r.take(1)), (None, Some(&[1u8][..])));
}

#[test]
fn take_zero() {
    let data: [u8; 0] = [];
    let mut r = Reader::new(&data);
    check!(r#"data []: take 0"#, r.take(0), Some(&[][..]));
}

#[test]
fn peek_empty() {
    check!(r#"data []: peek"#, Reader::new(&[]).peek(), None);
}

#[test]
fn records_cut_short() {
    let data = [0u8, 1, b'a', 0, 5, b'b'];
    let mut r = Reader::new(&data);
    let recs = records(&mut r);
    check!(r#"records of [0, 1, 'a', 0, 5, 'b']"#, (recs, r.remaining(), r.peek()), (None, 3, Some(0)));
}

#[test]
fn records_half_length() {
    let data = [0u8, 1, b'a', 7];
    let mut r = Reader::new(&data);
    let recs = records(&mut r);
    check!(r#"records of [0, 1, 'a', 7]"#, (recs, r.remaining()), (None, 1));
}

#[test]
fn records_empty() {
    check!(r#"records of []"#, records(&mut Reader::new(&[])), Some(vec![]));
}

#[test]
fn u16_max() {
    check!(r#"data [0xff, 0xff]"#, Reader::new(&[0xff, 0xff]).u16(), Some(u16::MAX));
}

#[test]
fn results_point_into_data() {
    let data = [5u8];
    check!(r#"take returns a slice of the data"#, Reader::new(&data).take(1).unwrap().as_ptr() == data.as_ptr(), true);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6309);
    for _ in 0..300 {
        let n = rng.below(10);
        let data: Vec<u8> = rng.vec(n, 0, 3);
        let mut r = Reader::new(&data);
        let mut pos = 0;
        let mut ops = Vec::new();
        for _ in 0..5 {
            match rng.below(3) {
                0 => {
                    let k = rng.below(4);
                    let want = data.get(pos..pos + k);
                    if want.is_some() {
                        pos += k;
                    }
                    ops.push(format!("take {k}"));
                    check!(format!("{data:?}: {}", ops.join(", ")), r.take(k), want);
                }
                1 => {
                    ops.push("peek".to_string());
                    check!(format!("{data:?}: {}", ops.join(", ")), r.peek(), data.get(pos).copied());
                }
                _ => {
                    let want = data.get(pos..pos + 2).map(|b| u16::from_be_bytes([b[0], b[1]]));
                    if want.is_some() {
                        pos += 2;
                    }
                    ops.push("u16".to_string());
                    check!(format!("{data:?}: {}", ops.join(", ")), r.u16(), want);
                }
            }
        }
        check!(format!("{data:?}: {}; remaining", ops.join(", ")), r.remaining(), data.len() - pos);
    }
}

#[test]
fn many_records() {
    let mut data = Vec::new();
    for i in 0..50_000u32 {
        data.extend_from_slice(&[0, 2, (i % 256) as u8, 1]);
    }
    let mut r = Reader::new(&data);
    let recs = records(&mut r).unwrap();
    check!("50000 two-byte records", (recs.len(), recs[49_999], r.remaining()), (50_000, &[(49_999 % 256) as u8, 1][..], 0));
}
