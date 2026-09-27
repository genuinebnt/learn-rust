use solution::*;

#[test]
fn zero() {
    check!(r#""0[x]y""#, decode_string("0[x]y"), "y".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, decode_string(""), String::new());
}

#[test]
fn one() {
    check!(r#""1[a]""#, decode_string("1[a]"), "a".to_string());
}

#[test]
fn deep() {
    check!(r#""2[2[2[a]]]""#, decode_string("2[2[2[a]]]"), "a".repeat(8));
}

#[test]
fn letters_around() {
    check!(r#""a2[b]c""#, decode_string("a2[b]c"), "abbc".to_string());
}

#[test]
fn hundred() {
    check!(r#""100[ab]""#, decode_string("100[ab]"), "ab".repeat(100));
}

#[test]
fn adjacent_groups() {
    check!(r#""2[a]2[a]""#, decode_string("2[a]2[a]"), "aaaa".to_string());
}

#[test]
fn mixed_nesting() {
    check!(r#""3[z]2[2[y]pq4[2[jk]e1[f]]]ef""#, decode_string("3[z]2[2[y]pq4[2[jk]e1[f]]]ef"), "zzzyypqjkjkefjkjkefjkjkefjkjkefyypqjkjkefjkjkefjkjkefjkjkefef".to_string());
}

#[test]
fn counts_after_letters() {
    check!(r#""ab12[c]""#, decode_string("ab12[c]"), format!("ab{}", "c".repeat(12)));
}

#[test]
fn random_vs_generator() {
    // Builds a random encoded string alongside what it decodes to.
    fn gen(rng: &mut anneal_prelude::Rng, depth: u32) -> (String, String) {
        let (mut enc, mut dec) = (String::new(), String::new());
        let parts = 1 + rng.below(3);
        for _ in 0..parts {
            if depth > 0 && rng.bool() {
                let k = rng.below(12);
                let (e, d) = gen(rng, depth - 1);
                enc.push_str(&format!("{k}[{e}]"));
                dec.push_str(&d.repeat(k));
            } else {
                let l = 1 + rng.below(2);
                let w = rng.string(l, "ab");
                enc.push_str(&w);
                dec.push_str(&w);
            }
        }
        (enc, dec)
    }
    let mut rng = anneal_prelude::Rng::new(3009);
    for _ in 0..300 {
        let (enc, dec) = gen(&mut rng, 3);
        check!(format!("s = {enc:?}"), decode_string(&enc), dec);
    }
}

#[test]
fn scale_1m_groups() {
    let s = "1[ab]".repeat(1_000_000);
    let out = decode_string(&s);
    check!("\"1[ab]\" × 1000000", (out.len(), &out[..4]), (2_000_000, "abab"));
}
