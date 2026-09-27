use solution::*;

#[test]
fn one_array() {
    check!(r#"size_of::<Page>()"#, std::mem::size_of::<Page>(), 4096);
}

#[test]
fn empty_header() {
    let page = Page::new();
    check!(r#"Page::new(): header bytes, len, free_space"#, (page.as_bytes()[0..8].to_vec(), page.len(), page.free_space()), (vec![0, 0, 0, 16, 0, 0, 0, 0], 0, 4088));
}

#[test]
fn sorted_lookup() {
    let mut page = Page::new();
    for (k, v) in [("cherry", "red"), ("apple", "green"), ("banana", "yellow")] {
        page.insert(k.as_bytes(), v.as_bytes()).unwrap();
    }
    check!(r#"insert cherry, apple, banana; iter and get"#, (page.iter().map(|(k, _)| k).collect::<Vec<_>>(), page.get(b"banana"), page.get(b"durian")), (vec![&b"apple"[..], &b"banana"[..], &b"cherry"[..]], Some(&b"yellow"[..]), None));
}

#[test]
fn compacted_image() {
    let mut page = Page::new();
    page.insert(b"b", b"2").unwrap();
    page.insert(b"a", b"1").unwrap();
    page.compact();
    let img = page.as_bytes();
    check!(r#"insert b → 2, a → 1, then compact(): header, slots, and the last 8 bytes"#, (img[0..16].to_vec(), img[4088..].to_vec(), img[16..4088].iter().all(|&b| b == 0)), (vec![2, 0, 248, 15, 0, 0, 0, 0, 252, 15, 4, 0, 248, 15, 4, 0], vec![1, 0, b'b', b'2', 1, 0, b'a', b'1'], true));
}

#[test]
fn fills_up() {
    let mut page = Page::new();
    let mut stored = 0;
    while page.insert(format!("k{stored:03}").as_bytes(), &[7; 100]).is_ok() {
        stored += 1;
    }
    check!(r#"insert k000, k001, ... with 100-byte values until PageFull"#, (stored, page.len(), page.free_space(), page.insert(b"x", &[0; 13])), (37, 37, 18, Err(PageFull)));
}

#[test]
fn no_allocation() {
    let (len, n) = anneal_prelude::allocs(|| {
        let mut page = Page::new();
        for i in 0..50u32 {
            page.insert(&i.to_be_bytes(), &[i as u8; 20]).unwrap();
        }
        for i in 0..50u32 {
            assert_eq!(page.get(&i.to_be_bytes()), Some(&[i as u8; 20][..]));
        }
        for i in (0..50u32).step_by(2) {
            page.delete(&i.to_be_bytes());
        }
        page.compact();
        for i in 100..110u32 {
            page.insert(&i.to_be_bytes(), b"v").unwrap();
        }
        page.len()
    });
    check!(r#"new, 50 inserts, gets, 25 deletes, compact, 10 inserts: allocations"#, (n.count, len), (0, 35));
}
