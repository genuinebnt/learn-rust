use solution::*;

#[test]
fn pin_float() {
    check!(r#"pin 1.5"#, { let mut b = Board::new(); b.pin(1.5); b.render() }, "<1.5>");
}

#[test]
fn pin_char_and_bool() {
    check!(r#"pin 'c', true"#, { let mut b = Board::new(); b.pin('c'); b.pin(true); b.render() }, "<c> <true>");
}

#[test]
fn pin_all_empty() {
    check!(r#"pin_all([])"#, { let items: Vec<u8> = vec![]; let mut b = Board::new(); pin_all(&mut b, &items); b.render() }, "");
}

#[test]
fn mixed_board() {
    let items = vec![String::from("p"), String::from("q")];
    let mut b = Board::new();
    b.pin(0);
    pin_all(&mut b, &items);
    check!(r#"pin 0, then pin_all of Strings"#, b.render(), "<0> <p> <q>");
}

#[test]
fn boxed_owned() {
    check!(r#"boxed(42)"#, boxed(42).describe(), "<42>");
}

#[test]
fn describe_each_empty() {
    check!(r#"describe_each of an empty slice"#, describe_each::<u8>(&[]).count(), 0);
}

#[test]
fn boxed_forever_literal() {
    check!(r#"boxed_forever("lit")"#, boxed_forever("lit").describe(), "<lit>");
}

#[test]
fn unicode() {
    check!(r#"pin "日本""#, { let mut b = Board::new(); b.pin("日本"); b.render() }, "<日本>");
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6313);
    for _ in 0..200 {
        let n = rng.below(6);
        let owned: Vec<String> = (0..n).map(|i| format!("w{i}")).collect();
        let nums: Vec<i64> = rng.vec(n, -9, 9);
        let mut b = Board::new();
        let mut want = Vec::new();
        for i in 0..n {
            if rng.bool() {
                b.pin(owned[i].as_str());
                want.push(format!("<{}>", owned[i]));
            } else {
                b.pin(nums[i]);
                want.push(format!("<{}>", nums[i]));
            }
        }
        check!(format!("pins over {owned:?} / {nums:?}"), b.render(), want.join(" "));
    }
}
