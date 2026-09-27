use solution::*;

#[test]
fn twice() {
    let data = [1u8, 2, 3, 4, 5];
    let mut r = Reader::new(&data);
    let a = r.take(2);
    let b = r.take(3);
    check!(r#"data [1, 2, 3, 4, 5]; take 2, take 3, remaining"#, (a, b, r.remaining()), (Some(&[1u8, 2][..]), Some(&[3u8, 4, 5][..]), 0));
}

#[test]
fn too_many() {
    let data = [1u8];
    let mut r = Reader::new(&data);
    let x = r.take(9);
    let y = r.take(1);
    check!(r#"data [1]; take 9, then take 1"#, (x, y), (None, Some(&[1u8][..])));
}

#[test]
fn zero() {
    check!(r#"take 0 from empty"#, Reader::new(&[]).take(0), Some(&[][..]));
}

#[test]
fn everything_then_nothing() {
    let data = [7u8, 8];
    let mut r = Reader::new(&data);
    let a = r.take(2);
    let b = r.take(1);
    check!(r#"data [7, 8]; take 2, take 1"#, (a, b, r.remaining()), (Some(&[7u8, 8][..]), None, 0));
}

#[test]
fn failed_take_keeps_position() {
    let data = [1u8, 2, 3];
    let mut r = Reader::new(&data);
    let a = r.take(1);
    let b = r.take(5);
    check!(r#"data [1, 2, 3]; take 1, take 5, remaining"#, (a, b, r.remaining()), (Some(&[1u8][..]), None, 2));
}
