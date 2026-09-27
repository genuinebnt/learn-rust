use solution::*;

#[test]
fn qualify_example() {
    check!(r#"qualify(["net", "tcp", "net::udp", "network"])"#, { let src: [&str; 4] = ["net", "tcp", "net::udp", "network"]; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, vec!["net", "net::tcp", "net::udp", "net::network"]);
}

#[test]
fn qualify_empty_slice() {
    check!(r#"qualify([])"#, { let src: [&str; 0] = []; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }, Vec::<String>::new());
}

#[test]
fn seal_two_frames() {
    check!(r#"seal_frames([3, 1, 2, 0, 5, 5, 5, 0], size 4)"#, { let mut b: Vec<u8> = vec![3, 1, 2, 0, 5, 5, 5, 0]; let n = seal_frames(&mut b, 4); (n, b) }, (2, vec![3, 2, 1, 3, 5, 0, 0, 0]));
}

#[test]
fn partial_frame_untouched() {
    check!(r#"seal_frames([1, 1, 1, 9, 9], size 3)"#, { let mut b: Vec<u8> = vec![1, 1, 1, 9, 9]; let n = seal_frames(&mut b, 3); (n, b) }, (1, vec![1, 0, 0, 9, 9]));
}

#[test]
fn swap_halves_odd() {
    check!(r#"swap_halves([1, 2, 3, 4, 5])"#, { let mut v = [1, 2, 3, 4, 5]; swap_halves(&mut v); v }, [4, 5, 3, 1, 2]);
}

#[test]
fn swap_halves_strings() {
    check!(r#"swap_halves(["a", "b", "c", "d"])"#, { let mut v = ["a", "b", "c", "d"].map(String::from); swap_halves(&mut v); v }, ["c", "d", "a", "b"].map(String::from));
}
