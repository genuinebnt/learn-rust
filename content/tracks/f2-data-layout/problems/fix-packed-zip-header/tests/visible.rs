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
fn thirty_bytes_align_one() {
    check!(r#"size_of::<LocalHeader>(), align_of::<LocalHeader>()"#, (std::mem::size_of::<LocalHeader>(), std::mem::align_of::<LocalHeader>()), (30, 1));
}

#[test]
fn view_reads_fields() {
    let bytes = local("a.txt", &[], b"hello", 8, 0xCAFE_F00D);
    let h = LocalHeader::view(&bytes).unwrap();
    check!(r#"view(local("a.txt", [], 5 bytes, method 8, crc 0xCAFEF00D))"#, (h.crc32(), h.compressed_size(), h.uncompressed_size(), h.name_len(), h.method()), (0xCAFEF00D, 5, 15, 5, 8));
}

#[test]
fn view_at_odd_offset() {
    let mut bytes = vec![0xEE];
    bytes.extend(local("a.txt", &[], b"hello", 8, 0xCAFE_F00D));
    let h = LocalHeader::view(&bytes[1..]).unwrap();
    check!(r#"the same header behind one byte of junk: view(&bytes[1..])"#, (h.crc32(), h.name_len()), (0xCAFEF00D, 5));
}

#[test]
fn describe_and_is_stored() {
    let bytes = local("x", &[], b"data", 0, 0xABCD);
    let h = LocalHeader::view(&bytes).unwrap();
    check!(r#"describe() and is_stored() of a stored 4-byte entry with crc 0xABCD"#, (h.describe(), h.is_stored()), ("crc 0000abcd, 4 -> 12 bytes".to_string(), true));
}

#[test]
fn walk_entries() {
    let mut archive = local("a.txt", &[], b"hello", 0, 1);
    archive.extend(local("dir/b", &[], b"xyz", 0, 2));
    archive.extend_from_slice(b"PK\x01\x02...");
    check!(r#"entries of ["a.txt": "hello", "dir/b": "xyz"] then a central directory"#, entries(&archive).unwrap().iter().map(|e| (e.name, e.data)).collect::<Vec<_>>(), vec![(&b"a.txt"[..], &b"hello"[..]), (&b"dir/b"[..], &b"xyz"[..])]);
}

#[test]
fn view_rejects() {
    let bytes = local("", &[], b"", 0, 0);
    let zeros = [0u8; 30];
    check!(r#"view of 29 bytes, and of 30 bytes without the signature"#, (LocalHeader::view(&bytes[..29]).is_some(), LocalHeader::view(&zeros).is_some()), (false, false));
}
