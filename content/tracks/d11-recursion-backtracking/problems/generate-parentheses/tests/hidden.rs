use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

fn balanced(s: &str) -> bool {
    let mut depth = 0i32;
    for ch in s.chars() {
        depth += if ch == '(' { 1 } else if ch == ')' { -1 } else { return false };
        if depth < 0 {
            return false;
        }
    }
    depth == 0
}

#[test]
fn four() {
    check!(r#"n = 4"#, sorted(generate_parenthesis(4)), vec!["(((())))", "((()()))", "((())())", "((()))()", "(()(()))", "(()()())", "(()())()", "(())(())", "(())()()", "()((()))", "()(()())", "()(())()", "()()(())", "()()()()"]);
}

#[test]
fn six() {
    check!(r#"n = 6"#, generate_parenthesis(6).len(), 132);
}

#[test]
fn seven_no_duplicates() {
    check!(r#"n = 7, duplicates removed"#, { let mut v = sorted(generate_parenthesis(7)); v.dedup(); v.len() }, 429);
}

#[test]
fn eight() {
    check!(r#"n = 8"#, generate_parenthesis(8).len(), 1430);
}

#[test]
fn nine_all_balanced() {
    check!(r#"n = 9, every string well formed"#, generate_parenthesis(9).iter().all(|s| balanced(s)), true);
}

#[test]
fn ten_all_length_twenty() {
    check!(r#"n = 10, every string has 20 characters"#, generate_parenthesis(10).iter().all(|s| s.len() == 20), true);
}

#[test]
fn eleven_first_and_last() {
    check!(r#"n = 11, smallest and largest"#, { let v = sorted(generate_parenthesis(11)); (v.len(), v[0].clone(), v[v.len() - 1].clone()) }, (58786, "((((((((((()))))))))))".to_string(), "()()()()()()()()()()()".to_string()));
}

#[test]
fn zero_again() {
    check!(r#"n = 0"#, generate_parenthesis(0).len(), 1);
}

#[test]
fn random_strings_vs_balance_check() {
    let answers: Vec<std::collections::HashSet<String>> = (0..=8).map(|n| generate_parenthesis(n).into_iter().collect()).collect();
    for n in 0..=8usize {
        // Every string of n pairs, filtered by a direct balance check.
        let brute = (0u32..1 << (2 * n)).filter(|m| {
            let s: String = (0..2 * n).map(|i| if m >> i & 1 == 1 { '(' } else { ')' }).collect();
            balanced(&s)
        }).count();
        check!(format!("n = {n}: count vs brute force"), answers[n].len(), brute);
    }
    let mut rng = anneal_prelude::Rng::new(1127);
    for _ in 0..400 {
        let n = rng.int(0, 8) as usize;
        let len = 2 * n;
        let s = rng.string(len, "()");
        check!(format!("n = {n}: is {s:?} an answer?"), answers[n].contains(&s), balanced(&s));
    }
}

#[test]
fn scale_thirteen_pairs() {
    let v = sorted(generate_parenthesis(13));
    let distinct = v.windows(2).all(|w| w[0] < w[1]);
    let valid = v.iter().all(|s| s.len() == 26 && balanced(s));
    check!("n = 13", (v.len(), distinct, valid, v[371_450].clone()), (742_900, true, true, "(()((()))((())))(())()()()".to_string()));
}
