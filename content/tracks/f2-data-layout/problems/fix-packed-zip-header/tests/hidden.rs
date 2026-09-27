use solution::*;

/// One local header, name, extra field and data, as a ZIP writer lays them out (little-endian).
fn local(name: &str, extra: &[u8], data: &[u8], method: u16, crc: u32) -> Vec<u8> {
    let mut v = Vec::new();
    v.extend_from_slice(&0x0403_4b50u32.to_le_bytes());
    v.extend_from_slice(&20u16.to_le_bytes()); // version needed
    v.extend_from_slice(&0u16.to_le_bytes()); // flags
    v.extend_from_slice(&method.to_le_bytes());
    v.extend_from_slice(&0x6000u16.to_le_bytes()); // time
    v.extend_from_slice(&0x5a21u16.to_le_bytes()); // date
    v.extend_from_slice(&crc.to_le_bytes());
    v.extend_from_slice(&(data.len() as u32).to_le_bytes());
    v.extend_from_slice(&(data.len() as u32 * 3).to_le_bytes()); // uncompressed size
    v.extend_from_slice(&(name.len() as u16).to_le_bytes());
    v.extend_from_slice(&(extra.len() as u16).to_le_bytes());
    v.extend_from_slice(name.as_bytes());
    v.extend_from_slice(extra);
    v.extend_from_slice(data);
    v
}

#[test]
fn extra_field_skipped() {
    let archive = local("n", &[1, 2, 3, 4, 5, 6, 7], b"payload", 8, 7);
    check!(r#"entries of one file with a 7-byte extra field"#, entries(&archive).unwrap().iter().map(|e| (e.name, e.crc32, e.data)).collect::<Vec<_>>(), vec![(&b"n"[..], 7, &b"payload"[..])]);
}

#[test]
fn every_offset() {
    let mut crcs = Vec::new();
    for off in 0..8 {
        let mut bytes = vec![0; off];
        bytes.extend(local("f", &[], b"z", 0, 0x0102_0304));
        crcs.push(LocalHeader::view(&bytes[off..]).unwrap().crc32());
    }
    check!(r#"the same header at offsets 0 to 7"#, crcs, vec![0x0102_0304; 8]);
}

#[test]
fn header_is_eq_hash_debug() {
    let (x, y) = (local("f", &[], b"z", 0, 9), local("f", &[], b"z", 0, 9));
    let (a, b) = (LocalHeader::view(&x).unwrap(), LocalHeader::view(&y).unwrap());
    let set: std::collections::HashSet<&LocalHeader> = [a, b].into_iter().collect();
    check!(r#"two views of equal headers: ==, a HashSet of both, Debug"#, (a == b, set.len(), format!("{:?}", a).starts_with("LocalHeader")), (true, 1, true));
}

#[test]
fn empty_archive() {
    check!(r#"entries of [] and of a lone central directory"#, (entries(&[]), entries(b"PK\x01\x02xx")), (Some(vec![]), Some(vec![])));
}

#[test]
fn truncated_data() {
    let archive = local("a", &[], b"hello", 0, 1);
    check!(r#"a header promising 5 bytes of data followed by 4"#, entries(&archive[..archive.len() - 1]), None);
}

#[test]
fn large_values() {
    let bytes = local("big", &[], &vec![7; 60000], 8, u32::MAX);
    let h = LocalHeader::view(&bytes).unwrap();
    check!(r#"crc 0xFFFFFFFF and a 60000-byte entry"#, (h.crc32(), h.compressed_size(), h.describe()), (u32::MAX, 60000, "crc ffffffff, 60000 -> 180000 bytes".to_string()));
}

#[test]
fn arrays_and_options() {
    check!(r#"size_of::<[LocalHeader; 2]>(), size_of::<Option<&LocalHeader>>()"#, (std::mem::size_of::<[LocalHeader; 2]>(), std::mem::size_of::<Option<&LocalHeader>>()), (60, 8));
}

#[test]
fn deflated_not_stored() {
    check!(r#"is_stored() for method 8"#, LocalHeader::view(&local("a", &[], b"x", 8, 0)).unwrap().is_stored(), false);
}

#[test]
fn random_archives() {
    let mut rng = anneal_prelude::Rng::new(8208);
    for _ in 0..200 {
        let junk = rng.below(2);
        let mut archive: Vec<u8> = rng.vec(junk, 0, 255);
        let skip = archive.len();
        let mut want = Vec::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(5) {
            let name_len = rng.below(12);
            let name = rng.string(name_len, "abcdefghij/._");
            let extra_len = if rng.bool() { 0 } else { rng.below(9) };
            let extra: Vec<u8> = rng.vec(extra_len, 0, 255);
            let data_len = rng.below(40);
            let data: Vec<u8> = rng.vec(data_len, 0, 255);
            let (method, crc) = (if rng.bool() { 0 } else { 8 }, rng.next_u64() as u32);
            log.push(format!("{name:?} (extra {}, data {}, method {method}, crc {crc:#x})", extra.len(), data.len()));
            archive.extend(local(&name, &extra, &data, method, crc));
            want.push((name.into_bytes(), method, crc, data));
        }
        archive.extend_from_slice(b"PK\x01\x02 central directory");
        let got = entries(&archive[skip..]).map(|es| es.into_iter().map(|e| (e.name.to_vec(), e.method, e.crc32, e.data.to_vec())).collect::<Vec<_>>());
        check!(format!("archive at offset {skip}: [{}]", log.join(", ")), got, Some(want));
    }
}
