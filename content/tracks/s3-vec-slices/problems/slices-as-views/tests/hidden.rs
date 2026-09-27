use solution::*;

#[test]
fn parse_tag_without_length() {
    check!(r#"b"\x01\x01a\x09""#, parse_tlv(b"\x01\x01a\x09"), None);
}

#[test]
fn parse_magic_only_at_start() {
    check!(r#"b"\x01\x03TLV""#, parse_tlv(b"\x01\x03TLV"), Some(vec![(1, &b"TLV"[..])]));
}

#[test]
fn parse_partial_magic_is_data() {
    check!(r#"b"T\x00""#, parse_tlv(b"T\x00"), Some(vec![(b'T', &b""[..])]));
}

#[test]
fn parse_max_length() {
    let mut data = vec![9u8, 255];
    data.extend(std::iter::repeat(7u8).take(255));
    check!(r#"a record with len 255"#, parse_tlv(&data).map(|r| (r.len(), r[0].0, r[0].1.len())), Some((1, 9, 255)));
}

#[test]
fn parse_len_one_short() {
    let mut data = vec![9u8, 255];
    data.extend(std::iter::repeat(7u8).take(254));
    check!(r#"a record with len 255 and 254 bytes"#, parse_tlv(&data), None);
}

#[test]
fn values_borrow_input() {
    let data = b"\x01\x02ab\x02\x01c".to_vec();
    let r = parse_tlv(&data).unwrap();
    check!(r#"values point into data"#, r[0].1.as_ptr() == data[2..].as_ptr() && r[1].1.as_ptr() == data[6..].as_ptr(), true);
}

#[test]
fn encode_too_long() {
    let big = vec![0u8; 256];
    check!(r#"a 256-byte value"#, encode_tlv(&[(1, &big)]), None);
}

#[test]
fn encode_255_is_fine() {
    let big = vec![0u8; 255];
    check!(r#"a 255-byte value"#, encode_tlv(&[(1, &big)]).map(|e| (e.len(), e[1])), Some((257, 255)));
}

#[test]
fn encode_one_exact_allocation() {
    let (out, n) = anneal_prelude::allocs(|| encode_tlv(&[(1, b"abc"), (2, b""), (3, b"z")]));
    check!(r#"three records"#, (out.as_ref().map(|v| v.len() == v.capacity()), n.count), (Some(true), 1));
}

#[test]
fn encode_nothing_allocates_nothing() {
    let (out, n) = anneal_prelude::allocs(|| encode_tlv(&[]));
    check!(r#"no records"#, (out, n.count), (Some(vec![]), 0));
}

#[test]
fn join_edges() {
    check!(r#"no records, one record"#, (join_values(&[], b','), join_values(&[(1, b"x")], b',')), (vec![], b"x".to_vec()));
}

#[test]
fn join_all_empty() {
    check!(r#"three empty values"#, join_values(&[(1, b""), (2, b""), (3, b"")], b','), b",,".to_vec());
}

#[test]
fn random_round_trip() {
    let mut rng = anneal_prelude::Rng::new(7304);
    for _ in 0..300 {
        let n = rng.below(5);
        let values: Vec<Vec<u8>> = (0..n).map(|_| {
            let len = rng.below(5);
            rng.vec(len, 0, 255)
        }).collect();
        let recs: Vec<(u8, &[u8])> = values.iter().enumerate().map(|(i, v)| (i as u8, v.as_slice())).collect();
        let mut want_bytes = Vec::new();
        for (t, v) in &recs {
            want_bytes.push(*t);
            want_bytes.push(v.len() as u8);
            want_bytes.extend(v.iter());
        }
        let enc = encode_tlv(&recs);
        let cut = rng.below(want_bytes.len() + 1);
        let prefix = &want_bytes[..cut];
        let mut boundaries = vec![0];
        for (_, v) in &recs {
            boundaries.push(boundaries.last().unwrap() + 2 + v.len());
        }
        let want_prefix = boundaries.iter().position(|&b| b == cut).map(|k| recs[..k].to_vec());
        let mut sep_join = Vec::new();
        for (i, v) in values.iter().enumerate() {
            if i > 0 {
                sep_join.push(b'|');
            }
            sep_join.extend(v.iter());
        }
        check!(format!("records = {recs:?}, cut at {cut}"),
               (enc.clone(), parse_tlv(&want_bytes), parse_tlv(prefix), join_values(&recs, b'|')),
               (Some(want_bytes.clone()), Some(recs.clone()), want_prefix, sep_join));
    }
}

#[test]
fn scale_100k_records() {
    let data: Vec<u8> = (0..100_000u32).flat_map(|i| [(i % 256) as u8, 3, 1, 2, 3]).collect();
    let recs = parse_tlv(&data).unwrap();
    let enc = encode_tlv(&recs).unwrap();
    check!("100000 records of 3 bytes", (recs.len(), enc == data, join_values(&recs, 0).len()), (100_000, true, 399_999));
}
