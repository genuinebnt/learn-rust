use solution::*;

use std::collections::HashMap;

/// Every way `sched` breaks the rules for `tasks` with cooldown `n` (empty when it is valid).
fn problems(tasks: &[char], n: usize, sched: &[Option<char>]) -> Vec<String> {
    let mut out = Vec::new();
    let mut want: HashMap<char, usize> = HashMap::new();
    for &c in tasks {
        *want.entry(c).or_default() += 1;
    }
    let mut got: HashMap<char, usize> = HashMap::new();
    for &c in sched.iter().flatten() {
        *got.entry(c).or_default() += 1;
    }
    if want != got {
        out.push("doesn't run each task exactly as often as it appears".to_string());
    }
    if sched.last() == Some(&None) {
        out.push("ends with an idle slot".to_string());
    }
    let mut last: HashMap<char, usize> = HashMap::new();
    for (t, slot) in sched.iter().enumerate() {
        if let Some(c) = *slot {
            if let Some(&p) = last.get(&c) {
                if t - p <= n {
                    out.push(format!("{c:?} runs at {p} and again at {t}"));
                }
            }
            last.insert(c, t);
        }
    }
    out
}

#[test]
fn leetcode_two_tied() {
    check!(r#"tasks = "AAABBB", n = 2"#, least_interval(&"AAABBB".chars().collect::<Vec<char>>(), 2), 8);
}

#[test]
fn leetcode_no_cooldown() {
    check!(r#"tasks = "AAABBB", n = 0"#, least_interval(&"AAABBB".chars().collect::<Vec<char>>(), 0), 6);
}

#[test]
fn leetcode_one_dominant() {
    check!(r#"tasks = "AAAAAABCDEFG", n = 2"#, least_interval(&"AAAAAABCDEFG".chars().collect::<Vec<char>>(), 2), 16);
}

#[test]
fn leetcode_no_idle_needed() {
    check!(r#"tasks = "ACABDB", n = 1"#, least_interval(&"ACABDB".chars().collect::<Vec<char>>(), 1), 6);
}

#[test]
fn only_one_kind() {
    check!(r#"tasks = "AAAA", n = 2 (A _ _ A _ _ A _ _ A)"#, least_interval(&"AAAA".chars().collect::<Vec<char>>(), 2), 10);
}

#[test]
fn schedule_aaabbb() {
    let tasks = "AAABBB".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 2);
    check!(r#"tasks = "AAABBB", n = 2; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 2, &s)), (8, Vec::<String>::new()));
}

#[test]
fn empty() {
    check!(r#"tasks = [], n = 3"#, (least_interval(&[], 3), schedule(&[], 3)), (0, Vec::<Option<char>>::new()));
}
