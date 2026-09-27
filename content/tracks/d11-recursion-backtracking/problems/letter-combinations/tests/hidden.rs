use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn empty() {
    check!(r#"digits = """#, letter_combinations(""), Vec::<String>::new());
}

#[test]
fn nine_has_four_letters() {
    check!(r#"digits = "9""#, sorted(letter_combinations("9")), vec!["w", "x", "y", "z"]);
}

#[test]
fn eight() {
    check!(r#"digits = "8""#, sorted(letter_combinations("8")), vec!["t", "u", "v"]);
}

#[test]
fn three_digits() {
    check!(r#"digits = "234""#, letter_combinations("234").len(), 27);
}

#[test]
fn seven_nine() {
    check!(r#"digits = "79""#, letter_combinations("79").len(), 16);
}

#[test]
fn order_of_digits_kept() {
    check!(r#"digits = "32""#, sorted(letter_combinations("32")), vec!["da", "db", "dc", "ea", "eb", "ec", "fa", "fb", "fc"]);
}

#[test]
fn four_four_letter_keys() {
    check!(r#"digits = "7979""#, letter_combinations("7979").len(), 256);
}

#[test]
fn every_key_once() {
    check!(r#"digits = "23456789""#, letter_combinations("23456789").len(), 11_664);
}

#[test]
fn five_six() {
    check!(r#"digits = "56""#, sorted(letter_combinations("56")), vec!["jm", "jn", "jo", "km", "kn", "ko", "lm", "ln", "lo"]);
}

#[test]
fn random_vs_product() {
    let keys = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];
    let mut rng = anneal_prelude::Rng::new(1113);
    for _ in 0..200 {
        let len = rng.int(1, 5) as usize;
        let digits = rng.string(len, "23456789");
        let mut want = vec![String::new()];
        for d in digits.bytes() {
            want = want.iter().flat_map(|w| keys[(d - b'0') as usize].chars().map(move |c| format!("{w}{c}"))).collect();
        }
        want.sort();
        check!(format!("digits = {digits:?}"), sorted(letter_combinations(&digits)), want);
    }
}

#[test]
fn scale_eight_four_letter_keys() {
    let got = sorted(letter_combinations("79797979"));
    check!("digits = \"79797979\"", (got.len(), got[0].clone(), got[65_535].clone()), (65_536, "pwpwpwpw".to_string(), "szszszsz".to_string()));
}
