use solution::*;

#[test]
fn qualify_only_namespace() {
    check!(r#"qualify(["ns"])"#, { let src: [&str; 1] = ["ns"]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["ns"]);
}

#[test]
fn qualify_prefix_without_colons() {
    check!(r#"qualify(["a", "ab", "a:b", "a::"])"#, { let src: [&str; 4] = ["a", "ab", "a:b", "a::"]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["a", "a::ab", "a::a:b", "a::"]);
}

#[test]
fn qualify_empty_namespace() {
    check!(r#"qualify(["", "x", "::y"])"#, { let src: [&str; 3] = ["", "x", "::y"]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["", "::x", "::y"]);
}

#[test]
fn qualify_empty_name() {
    check!(r#"qualify(["n", ""])"#, { let src: [&str; 2] = ["n", ""]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["n", "n::"]);
}

#[test]
fn qualify_unicode() {
    check!(r#"qualify(["日本", "東京", "日本::大阪"])"#, { let src: [&str; 3] = ["日本", "東京", "日本::大阪"]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["日本", "日本::東京", "日本::大阪"]);
}

#[test]
fn seal_size_two() {
    check!(r#"seal_frames([7, 7, 1, 2], size 2)"#, { let mut b: Vec<u8> = vec![7, 7, 1, 2]; let n = seal_frames(&mut b, 2); (n, b) }, (2, vec![7, 0, 1, 0]));
}

#[test]
fn seal_wraps() {
    check!(r#"seal_frames([0, 200, 100, 0], size 4)"#, { let mut b: Vec<u8> = vec![0, 200, 100, 0]; let n = seal_frames(&mut b, 4); (n, b) }, (1, vec![0, 200, 100, 44]));
}

#[test]
fn seal_buffer_shorter_than_frame() {
    check!(r#"seal_frames([1, 2], size 3)"#, { let mut b: Vec<u8> = vec![1, 2]; let n = seal_frames(&mut b, 3); (n, b) }, (0, vec![1, 2]));
}

#[test]
fn seal_empty() {
    check!(r#"seal_frames([], size 3)"#, { let mut b: Vec<u8> = vec![]; let n = seal_frames(&mut b, 3); (n, b) }, (0, vec![]));
}

#[test]
fn swap_halves_short() {
    check!(r#"swap_halves on [], [1], [1, 2]"#, { let (mut a, mut b, mut c): ([i32; 0], [i32; 1], [i32; 2]) = ([], [1], [1, 2]); swap_halves(&mut a); swap_halves(&mut b); swap_halves(&mut c); (b, c) }, ([1], [2, 1]));
}

#[test]
fn qualify_extends_in_place() {
    let mut v = vec!["ns".to_string(), String::with_capacity(64)];
    v[1].push_str("x");
    let before = v[1].as_ptr();
    qualify(&mut v);
    check!("qualify([\"ns\", \"x\" with spare capacity]): the String grows in place", (v[1].as_str(), v[1].as_ptr() == before), ("ns::x", true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6206);
    for _ in 0..300 {
        let size = 2 + rng.below(4);
        let len = rng.below(14);
        let buf: Vec<u8> = rng.vec(len, 0, 255);
        let mut want = buf.clone();
        let mut n = 0;
        let total = want.len();
        for s in (0..).step_by(size).take_while(|s| s + size <= total) {
            let k = want[s];
            let mut tot = 0u8;
            for j in s + 1..s + size - 1 {
                want[j] ^= k;
                tot = tot.wrapping_add(want[j]);
            }
            want[s + size - 1] = tot;
            n += 1;
        }
        let mut got = buf.clone();
        let sealed = seal_frames(&mut got, size);
        check!(format!("seal_frames({buf:?}, size {size})"), (sealed, got), (n, want));

        let v: Vec<u32> = rng.vec(len, 0, 9);
        let h = len / 2;
        let mut want = v[len - h..].to_vec();
        want.extend_from_slice(&v[h..len - h]);
        want.extend_from_slice(&v[..h]);
        let mut got = v.clone();
        swap_halves(&mut got);
        check!(format!("swap_halves({v:?})"), got, want);
    }
}

#[test]
fn big_buffer() {
    let mut buf = vec![1u8; 300_001];
    let n = seal_frames(&mut buf, 3);
    check!("300001 bytes of 1, size 3", (n, buf[0], buf[1], buf[2], buf[300_000]), (100_000, 1, 0, 0, 1));
    let mut v: Vec<u32> = (0..200_001).collect();
    swap_halves(&mut v);
    check!("swap_halves(0..200001)", (v[0], v[99_999], v[100_000], v[100_001], v[200_000]), (100_001, 200_000, 100_000, 0, 99_999));
}
