use solution::*;
use std::cmp::Ordering;

#[test]
fn identical() {
    check!(r#""abc10" vs "abc10""#, (natural_cmp("abc10", "abc10"), natural_cmp("abc10", "abc10")), (Ordering::Equal, Ordering::Equal));
}

#[test]
fn both_empty() {
    check!(r#""" vs """#, (natural_cmp("", ""), natural_cmp("", "")), (Ordering::Equal, Ordering::Equal));
}

#[test]
fn prefix_is_smaller() {
    check!(r#""a" vs "a1""#, (natural_cmp("a", "a1"), natural_cmp("a1", "a")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn plain_text() {
    check!(r#""abc" vs "abd""#, (natural_cmp("abc", "abd"), natural_cmp("abd", "abc")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn huge_numbers() {
    check!(r#""v99999999999999999999999" vs "v100000000000000000000000""#, (natural_cmp("v99999999999999999999999", "v100000000000000000000000"), natural_cmp("v100000000000000000000000", "v99999999999999999999999")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn zeros_do_not_count_as_digits() {
    check!(r#""007" vs "10""#, (natural_cmp("007", "10"), natural_cmp("10", "007")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn equal_value_then_rest_decides() {
    check!(r#""a1b" vs "a01a""#, (natural_cmp("a1b", "a01a"), natural_cmp("a01a", "a1b")), (Ordering::Greater, Ordering::Less));
}

#[test]
fn digit_vs_letter_by_code_point() {
    check!(r#""a1" vs "a-""#, (natural_cmp("a1", "a-"), natural_cmp("a-", "a1")), (Ordering::Greater, Ordering::Less));
}

#[test]
fn zeros_tie_break_comes_last() {
    check!(r#""x01b" vs "x1a""#, (natural_cmp("x01b", "x1a"), natural_cmp("x1a", "x01b")), (Ordering::Greater, Ordering::Less));
}

#[test]
fn case_sensitive() {
    check!(r#""IMG2" vs "img1""#, (natural_cmp("IMG2", "img1"), natural_cmp("img1", "IMG2")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn unicode_text() {
    check!(r#""é2" vs "é10""#, (natural_cmp("é2", "é10"), natural_cmp("é10", "é2")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn arabic_indic_digit_is_not_ascii() {
    check!(r#""a٣" vs "a2""#, (natural_cmp("a٣", "a2"), natural_cmp("a2", "a٣")), (Ordering::Greater, Ordering::Less));
}

#[test]
fn all_zeros() {
    check!(r#""0" vs "000""#, (natural_cmp("0", "000"), natural_cmp("000", "0")), (Ordering::Less, Ordering::Greater));
}

#[test]
fn versions() {
    check!(r#""v1.10.0" vs "v1.9.2""#, (natural_cmp("v1.10.0", "v1.9.2"), natural_cmp("v1.9.2", "v1.10.0")), (Ordering::Greater, Ordering::Less));
}

#[test]
fn luhn_small_valid() {
    check!(r#""059", "59", "091", "0 0""#, [luhn_valid("059"), luhn_valid("59"), luhn_valid("091"), luhn_valid("0 0")], [true; 4]);
}

#[test]
fn luhn_too_short() {
    check!(r#""0", " 0", "", "   ""#, [luhn_valid("0"), luhn_valid(" 0"), luhn_valid(""), luhn_valid("   ")], [false; 4]);
}

#[test]
fn luhn_bad_checksum() {
    check!(r#""8273 1232 7352 0569", "1234", "055 444 286""#, [luhn_valid("8273 1232 7352 0569"), luhn_valid("1234"), luhn_valid("055 444 286")], [false; 3]);
}

#[test]
fn luhn_good_grouped() {
    check!(r#""055 444 285", "4111 1111 1111 1111""#, [luhn_valid("055 444 285"), luhn_valid("4111 1111 1111 1111")], [true; 2]);
}

#[test]
fn luhn_other_characters() {
    check!(r#""055-444-285", "055a 444 285", "059\t""#, [luhn_valid("055-444-285"), luhn_valid("055a 444 285"), luhn_valid("059\t")], [false; 3]);
}

#[test]
fn luhn_non_ascii_digits() {
    check!(r#""٣٣", "①8", "0½", "6٣""#, [luhn_valid("٣٣"), luhn_valid("①8"), luhn_valid("0½"), luhn_valid("6٣")], [false; 4]);
}

#[test]
fn luhn_long_zeros() {
    check!(r#""0" × 100"#, luhn_valid(&"0".repeat(100)), true);
}

#[test]
fn random_vs_brute_force() {
    #[derive(PartialEq, Eq, PartialOrd, Ord, Debug)]
    enum Tok {
        // Numbers sort between the characters below '0' and those above '9'.
        Low(char),
        Num(u128),
        High(char),
    }
    fn toks(s: &str) -> Vec<Tok> {
        let cs: Vec<char> = s.chars().collect();
        let mut out = Vec::new();
        let mut i = 0;
        while i < cs.len() {
            if cs[i].is_ascii_digit() {
                let mut v = 0u128;
                while i < cs.len() && cs[i].is_ascii_digit() {
                    v = v * 10 + cs[i] as u128 - '0' as u128;
                    i += 1;
                }
                out.push(Tok::Num(v));
            } else {
                out.push(if cs[i] < '0' { Tok::Low(cs[i]) } else { Tok::High(cs[i]) });
                i += 1;
            }
        }
        out
    }
    let mut rng = anneal_prelude::Rng::new(7213);
    let pieces = ["a", "b", "0", "1", "9", "10", "007", "é", "-"];
    let sample = |rng: &mut anneal_prelude::Rng| {
        let mut s = String::new();
        for _ in 0..rng.below(6) {
            s += *rng.pick(&pieces);
        }
        s
    };
    for _ in 0..400 {
        let (a, b) = (sample(&mut rng), sample(&mut rng));
        let want = toks(&a).cmp(&toks(&b)).then_with(|| a.cmp(&b));
        let digits: String = (0..rng.below(20)).map(|_| char::from(b'0' + rng.below(10) as u8)).collect();
        let spaced: String = digits.chars().flat_map(|c| [c, ' ']).collect();
        let mut sum = 0;
        for (i, c) in digits.chars().rev().enumerate() {
            let d = c as u32 - '0' as u32;
            sum += if i % 2 == 1 { (d * 2) / 10 + (d * 2) % 10 } else { d };
        }
        let want_luhn = digits.len() >= 2 && sum % 10 == 0;
        check!(format!("a = {a:?}, b = {b:?}, card = {spaced:?}"), (natural_cmp(&a, &b), luhn_valid(&spaced)), (want, want_luhn));
    }
}

#[test]
fn scale_sort_100k_names() {
    let mut names: Vec<String> = (0..100_000).map(|i| format!("log{i}.txt")).collect();
    let mut rng = anneal_prelude::Rng::new(7214);
    rng.shuffle(&mut names);
    names.sort_by(|a, b| natural_cmp(a, b));
    let ok = names.iter().enumerate().all(|(i, n)| *n == format!("log{i}.txt"));
    check!("100000 shuffled names log0.txt … log99999.txt", ok, true);
    let (a, b) = ("1".repeat(1_000_000) + "a", "1".repeat(1_000_000) + "b");
    check!("two 1000001-char strings that differ at the end", natural_cmp(&a, &b), Ordering::Less);
}
