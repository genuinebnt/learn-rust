use solution::*;

#[test]
fn reverse_is_not_the_answer() {
    check!(r#"s = "abacdfgdcaba" ("abacd" appears reversed too, but isn't a palindrome)"#, longest_palindrome("abacdfgdcaba"), "aba");
}

#[test]
fn all_same() {
    check!(r#"s = "aaaa""#, longest_palindrome("aaaa"), "aaaa");
}

#[test]
fn even_at_the_end() {
    check!(r#"s = "abb""#, longest_palindrome("abb"), "bb");
}

#[test]
fn long_even() {
    check!(r#"s = "forgeeksskeegfor""#, longest_palindrome("forgeeksskeegfor"), "geeksskeeg");
}

#[test]
fn lone_multibyte() {
    check!(r#"s = "é""#, longest_palindrome("é"), "é");
}

#[test]
fn emoji() {
    check!(r#"s = "🦀a🦀""#, longest_palindrome("🦀a🦀"), "🦀a🦀");
}

#[test]
fn distinct_letters() {
    check!(r#"s = "abcde""#, longest_palindrome("abcde"), "a");
}

#[test]
fn spaces_count() {
    check!(r#"s = "ab ba""#, longest_palindrome("ab ba"), "ab ba");
}

#[test]
fn case_sensitive() {
    check!(r#"s = "Aa""#, longest_palindrome("Aa"), "A");
}

#[test]
fn at_the_start() {
    check!(r#"s = "xabax yz""#, longest_palindrome("xabax yz"), "xabax");
}

#[test]
fn slice_of_the_input() {
    let s = String::from("xracecary");
    let got = longest_palindrome(&s);
    check!(r#"the answer points into s"#, std::ptr::eq(got.as_ptr(), s[1..].as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1014);
    for _ in 0..400 {
        let len = rng.below(12);
        let s = rng.string(len, "abé");
        let cs: Vec<char> = s.chars().collect();
        let mut want: Vec<char> = Vec::new();
        for i in 0..cs.len() {
            for j in i + 1..=cs.len() {
                let w = &cs[i..j];
                if w.iter().eq(w.iter().rev()) && w.len() > want.len() {
                    want = w.to_vec();
                }
            }
        }
        check!(format!("s = {s:?}"), longest_palindrome(&s).to_string(), want.iter().collect::<String>());
    }
}

#[test]
fn scale_5000_same_letter() {
    let s = "a".repeat(5000);
    check!("s = 'a' × 5000", longest_palindrome(&s).len(), 5000);
}

#[test]
fn scale_5000_two_blocks() {
    // The answer is the block of b's at the end.
    let s = format!("{}{}", "abc".repeat(1000), "b".repeat(2000));
    let got = longest_palindrome(&s);
    check!("s = \"abc\" × 1000 + 'b' × 2000", (got.len(), std::ptr::eq(got.as_ptr(), s[3000..].as_ptr())), (2000, true));
}
