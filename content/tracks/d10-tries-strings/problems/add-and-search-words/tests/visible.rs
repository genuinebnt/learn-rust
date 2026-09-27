use solution::*;

#[test]
fn leetcode_bad_dad_mad() {
    let mut d = WordDictionary::new();
    for w in ["bad", "dad", "mad"] {
        d.add_word(w);
    }
    check!(r#"add "bad", "dad", "mad"; search "pad", "bad", ".ad", "b..""#, (d.search("pad"), d.search("bad"), d.search(".ad"), d.search("b..")), (false, true, true, true));
}

#[test]
fn empty_dictionary() {
    let d = WordDictionary::new();
    check!(r#"new dictionary; search "a", ".""#, (d.search("a"), d.search(".")), (false, false));
}

#[test]
fn dot_matches_one_letter() {
    let mut d = WordDictionary::new();
    d.add_word("ab");
    check!(r#"add "ab"; search ".", "..", "...""#, (d.search("."), d.search(".."), d.search("...")), (false, true, false));
}

#[test]
fn prefix_is_not_a_match() {
    let mut d = WordDictionary::new();
    d.add_word("bad");
    check!(r#"add "bad"; search "ba", "b.""#, (d.search("ba"), d.search("b.")), (false, false));
}

#[test]
fn dot_must_try_every_branch() {
    let mut d = WordDictionary::new();
    d.add_word("ab");
    d.add_word("cd");
    check!(r#"add "ab", "cd"; search ".d""#, d.search(".d"), true);
}
