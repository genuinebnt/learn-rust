use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, longest_valid_parentheses(""), 0);
}

#[test]
fn single_open() {
    check!(r#"s = "(""#, longest_valid_parentheses("("), 0);
}

#[test]
fn single_close() {
    check!(r#"s = ")""#, longest_valid_parentheses(")"), 0);
}

#[test]
fn backwards_pair() {
    check!(r#"s = ")(""#, longest_valid_parentheses(")("), 0);
}

#[test]
fn all_open() {
    check!(r#"s = "((((""#, longest_valid_parentheses("(((("), 0);
}

#[test]
fn nested_inside() {
    check!(r#"s = "(()())""#, longest_valid_parentheses("(()())"), 6);
}

#[test]
fn extra_close_in_middle() {
    check!(r#"s = "(()))())(""#, longest_valid_parentheses("(()))())("), 4);
}

#[test]
fn closes_at_the_start() {
    check!(r#"s = ")))((()""#, longest_valid_parentheses(")))((()"), 2);
}

#[test]
fn deep_in_the_middle() {
    check!(r#"s = ")()(((())))(""#, longest_valid_parentheses(")()(((())))("), 10);
}

#[test]
fn opens_left_unclosed() {
    check!(r#"s = "(()(((()""#, longest_valid_parentheses("(()(((()"), 2);
}

#[test]
fn random_vs_brute_force() {
    let valid = |t: &[u8]| {
        let mut depth = 0i32;
        for &c in t {
            depth += if c == b'(' { 1 } else { -1 };
            if depth < 0 {
                return false;
            }
        }
        depth == 0
    };
    let mut rng = anneal_prelude::Rng::new(1251);
    for _ in 0..300 {
        let n = rng.below(15);
        let s = rng.string(n, "()");
        let b = s.as_bytes();
        let mut want = 0;
        for i in 0..b.len() {
            for j in i..=b.len() {
                if valid(&b[i..j]) {
                    want = want.max(j - i);
                }
            }
        }
        check!(format!("s = {s:?}"), longest_valid_parentheses(&s), want);
    }
}

#[test]
fn scale_nested_200000() {
    let s = "(".repeat(100_000) + &")".repeat(100_000);
    check!("s = 100000 × '(' then 100000 × ')'", longest_valid_parentheses(&s), 200_000);
}

#[test]
fn scale_unclosed_200000() {
    let s = "(".repeat(100_001) + &"()".repeat(49_999);
    check!("s = 100001 × '(' then 49999 × \"()\"", longest_valid_parentheses(&s), 99_998);
}
