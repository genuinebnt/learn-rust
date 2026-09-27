use solution::*;

/// The page image that `compact` must produce for these cells: header, sorted slots, cells packed from the
/// end in slot order, zeros between.
fn packed_image(cells: &std::collections::BTreeMap<Vec<u8>, Vec<u8>>) -> Vec<u8> {
    let mut img = vec![0u8; 4096];
    let mut end = 4096;
    for (i, (k, v)) in cells.iter().enumerate() {
        let len = 2 + k.len() + v.len();
        let at = end - len;
        img[at..at + 2].copy_from_slice(&(k.len() as u16).to_le_bytes());
        img[at + 2..at + 2 + k.len()].copy_from_slice(k);
        img[at + 2 + k.len()..end].copy_from_slice(v);
        img[8 + 4 * i..8 + 4 * i + 2].copy_from_slice(&(at as u16).to_le_bytes());
        img[8 + 4 * i + 2..8 + 4 * i + 4].copy_from_slice(&(len as u16).to_le_bytes());
        end = at;
    }
    img[0..2].copy_from_slice(&(cells.len() as u16).to_le_bytes());
    img[2..4].copy_from_slice(&(end as u16).to_le_bytes());
    img
}

fn used(cells: &std::collections::BTreeMap<Vec<u8>, Vec<u8>>) -> usize {
    8 + cells.iter().map(|(k, v)| 4 + 2 + k.len() + v.len()).sum::<usize>()
}

#[test]
fn fragments_are_reused() {
    let mut page = Page::new();
    let mut stored = 0;
    while page.insert(format!("k{stored:03}").as_bytes(), &[7; 100]).is_ok() {
        stored += 1;
    }
    for i in (0..37).step_by(2) {
        page.delete(format!("k{i:03}").as_bytes());
    }
    check!(r#"fill with 37 cells, delete every other one, insert a 700-byte value"#, (page.insert(b"big", &[1; 700]), page.get(b"big").map(|v| v.len()), page.len()), (Ok(()), Some(700), 19));
}

#[test]
fn replace_too_big_changes_nothing() {
    let mut page = Page::new();
    let mut stored = 0;
    while page.insert(format!("k{stored:03}").as_bytes(), &[7; 100]).is_ok() {
        stored += 1;
    }
    let before = *page.as_bytes();
    check!(r#"full page; replace k005's 100 bytes with 200"#, (page.insert(b"k005", &[9; 200]), page.as_bytes() == &before, page.get(b"k005").map(|v| v[0])), (Err(PageFull), true, Some(7)));
}

#[test]
fn replace_grows_into_its_own_space() {
    let mut page = Page::new();
    let mut stored = 0;
    while page.insert(format!("k{stored:03}").as_bytes(), &[7; 100]).is_ok() {
        stored += 1;
    }
    check!(r#"full page; replace k005 with 118 bytes (its old 106-byte cell plus the 18 free)"#, (page.insert(b"k005", &[9; 118]), page.free_space(), page.len()), (Ok(()), 0, 37));
}

#[test]
fn replace_smaller() {
    let mut page = Page::new();
    page.insert(b"a", &[0; 10]).unwrap();
    page.insert(b"a", b"hi").unwrap();
    check!(r#"a → 10 bytes, then a → 2 bytes"#, (page.get(b"a"), page.len(), page.free_space()), (Some(&b"hi"[..]), 1, 4096 - 8 - 4 - 2 - 1 - 2));
}

#[test]
fn empty_key_and_value() {
    let mut page = Page::new();
    page.insert(b"", b"").unwrap();
    page.insert(b"x", b"").unwrap();
    check!(r#"insert ("", "") and ("x", "")"#, (page.get(b""), page.get(b"x"), page.iter().count()), (Some(&b""[..]), Some(&b""[..]), 2));
}

#[test]
fn largest_cell() {
    check!(r#"one key byte and 4081 value bytes fits exactly; 4082 doesn't"#, (Page::new().insert(b"k", &[1; 4081]), Page::new().insert(b"k", &[1; 4082])), (Ok(()), Err(PageFull)));
}

#[test]
fn delete_all() {
    let mut page = Page::new();
    for i in 0..10u8 {
        page.insert(&[i], &[i; 30]).unwrap();
    }
    for i in 0..10u8 {
        page.delete(&[i]);
    }
    let again = page.delete(&[3]);
    check!(r#"insert 10, delete them all, delete one again"#, (page.len(), page.free_space(), again, page.iter().count()), (0, 4088, false, 0));
}

#[test]
fn from_disk() {
    let mut cells = std::collections::BTreeMap::new();
    cells.insert(b"a".to_vec(), b"1".to_vec());
    cells.insert(b"b".to_vec(), b"2".to_vec());
    let img: [u8; 4096] = packed_image(&cells).try_into().unwrap();
    let page = Page::from_bytes(&img);
    check!(r#"a page image written by another process: from_bytes, get"#, (page.get(b"a"), page.get(b"b"), page.len()), (Some(&b"1"[..]), Some(&b"2"[..]), 2));
}

#[test]
fn fragmented_header() {
    let mut page = Page::new();
    page.insert(b"a", &[0; 10]).unwrap();
    page.insert(b"b", &[0; 20]).unwrap();
    page.delete(b"a");
    check!(r#"insert a (10 bytes), b (20 bytes), delete a: header bytes 0..6"#, page.as_bytes()[0..6].to_vec(), vec![1, 0, 0xDC, 0x0F, 13, 0]);
}

#[test]
fn random_vs_btreemap() {
    let mut rng = anneal_prelude::Rng::new(8216);
    for _ in 0..120 {
        let mut page = Page::new();
        let mut model = std::collections::BTreeMap::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(150) {
            let key_len = rng.below(6);
            let key = rng.string(key_len, "abcd").into_bytes();
            if rng.below(3) < 2 {
                let value_len = if rng.below(10) == 0 { rng.below(1500) } else { rng.below(60) };
                let value: Vec<u8> = rng.vec(value_len, 0, 255);
                let mut next = model.clone();
                next.insert(key.clone(), value.clone());
                let fits = used(&next) <= 4096;
                log.push(format!("insert({:?}, {} bytes)", String::from_utf8_lossy(&key), value.len()));
                let before = *page.as_bytes();
                let got = page.insert(&key, &value);
                check!(format!("{}", log.join(", ")), got, if fits { Ok(()) } else { Err(PageFull) });
                if fits {
                    model = next;
                } else {
                    check!(format!("{}: page unchanged after PageFull", log.join(", ")), page.as_bytes() == &before, true);
                }
            } else {
                log.push(format!("delete({:?})", String::from_utf8_lossy(&key)));
                check!(log.join(", "), page.delete(&key), model.remove(&key).is_some());
            }
            if rng.below(8) == 0 {
                log.push("compact()".to_string());
                page.compact();
                check!(format!("{}: the compacted image", log.join(", ")), page.as_bytes().to_vec() == packed_image(&model), true);
            }
        }
        let ctx = log.join(", ");
        let want: Vec<(&[u8], &[u8])> = model.iter().map(|(k, v)| (&k[..], &v[..])).collect();
        check!(format!("{ctx}: iter()"), page.iter().collect::<Vec<_>>(), want);
        check!(format!("{ctx}: len, free_space"), (page.len(), page.free_space()), (model.len(), 4096 - used(&model)));
        let probe = rng.string(3, "abcd").into_bytes();
        check!(format!("{ctx}: get({:?})", String::from_utf8_lossy(&probe)), page.get(&probe), model.get(&probe).map(|v| &v[..]));
        let copy = Page::from_bytes(page.as_bytes());
        check!(format!("{ctx}: from_bytes(as_bytes()) iterates the same"), copy.iter().collect::<Vec<_>>(), page.iter().collect::<Vec<_>>());
    }
}
