use solution::*;

#[test]
fn zero() {
    check!(r#"take 0 from empty"#, Reader::new(&[]).take(0), Some(&[][..]));
}

#[test]
fn empty_take_one() {
    check!(r#"take 1 from empty"#, Reader::new(&[]).take(1), None);
}

#[test]
fn remaining_at_start() {
    check!(r#"data [1, 2, 3]"#, Reader::new(&[1, 2, 3]).remaining(), 3);
}

#[test]
fn zero_does_not_move() {
    let data = [5u8];
    let mut r = Reader::new(&data);
    let a = r.take(0);
    let b = r.take(0);
    let c = r.take(1);
    check!(r#"data [5]; take 0, take 0, take 1"#, (a, b, c), (Some(&[][..]), Some(&[][..]), Some(&[5u8][..])));
}

#[test]
fn chunks_outlive_reader() {
    let data = vec![1u8, 2, 3];
    let (a, b);
    {
        let mut r = Reader::new(&data);
        a = r.take(1);
        b = r.take(2);
    }
    check!(r#"take twice, drop the reader, use both chunks"#, (a, b), (Some(&[1u8][..]), Some(&[2u8, 3][..])));
}

#[test]
fn zero_copy() {
    let data = [0u8, 1, 2, 3];
    let mut r = Reader::new(&data);
    r.take(2);
    let chunk = r.take(2).unwrap();
    check!(r#"chunk points into data"#, std::ptr::eq(chunk.as_ptr(), data[2..].as_ptr()), true);
}

#[test]
fn many_small_takes() {
    let data = vec![7u8; 10_000];
    let mut r = Reader::new(&data);
    let mut sum = 0u32;
    while let Some(c) = r.take(1) {
        sum += c[0] as u32;
    }
    check!(r#"10000 bytes, 10000 takes of 1"#, (sum, r.remaining()), (10_000 * 7, 0));
}

#[test]
fn fails_then_exact() {
    let data = [1u8, 2];
    let mut r = Reader::new(&data);
    let a = r.take(3);
    let b = r.take(2);
    check!(r#"data [1, 2]; take 3, then take 2"#, (a, b), (None, Some(&[1u8, 2][..])));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(312);
    for _ in 0..300 {
        let len = rng.below(10);
        let data: Vec<u8> = rng.vec(len, 0, 9);
        let mut r = Reader::new(&data);
        let mut pos = 0;
        for _ in 0..6 {
            let n = rng.below(5);
            let want = if pos + n <= data.len() { pos += n; Some(&data[pos - n..pos]) } else { None };
            check!(format!("data = {data:?}, take({n}) at {pos}"), r.take(n), want);
            check!(format!("data = {data:?}: remaining"), r.remaining(), data.len() - pos);
        }
    }
}
