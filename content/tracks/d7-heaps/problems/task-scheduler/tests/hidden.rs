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
fn enough_kinds_to_fill_gaps() {
    check!(r#"tasks = "AAABBBCCCDDE", n = 2"#, least_interval(&"AAABBBCCCDDE".chars().collect::<Vec<char>>(), 2), 12);
}

#[test]
fn unicode_ids() {
    check!(r#"tasks = "ééé🦀🦀", n = 1"#, least_interval(&"ééé🦀🦀".chars().collect::<Vec<char>>(), 1), 5);
}

#[test]
fn lowercase_and_uppercase_differ() {
    check!(r#"tasks = "aaZ", n = 3"#, least_interval(&"aaZ".chars().collect::<Vec<char>>(), 3), 5);
}

#[test]
fn single_task_long_cooldown() {
    check!(r#"tasks = "A", n = 100"#, least_interval(&"A".chars().collect::<Vec<char>>(), 100), 1);
}

#[test]
fn twice_long_cooldown() {
    check!(r#"tasks = "AA", n = 100"#, least_interval(&"AA".chars().collect::<Vec<char>>(), 100), 102);
}

#[test]
fn schedule_unicode() {
    let tasks = "ééé🦀🦀".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 1);
    check!(r#"tasks = "ééé🦀🦀", n = 1; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 1, &s)), (5, Vec::<String>::new()));
}

#[test]
fn schedule_one_dominant() {
    let tasks = "AAAAAABCDEFG".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 2);
    check!(r#"tasks = "AAAAAABCDEFG", n = 2; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 2, &s)), (16, Vec::<String>::new()));
}

#[test]
fn schedule_no_cooldown() {
    let tasks = "ABBA".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 0);
    check!(r#"tasks = "ABBA", n = 0; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 0, &s)), (4, Vec::<String>::new()));
}

#[test]
fn schedule_single_kind() {
    let tasks = "ZZZ".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 3);
    check!(r#"tasks = "ZZZ", n = 3; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 3, &s)), (9, Vec::<String>::new()));
}

#[test]
fn schedule_many_tied() {
    let tasks = "AAABBBCCCDDE".chars().collect::<Vec<char>>();
    let s = schedule(&tasks, 2);
    check!(r#"tasks = "AAABBBCCCDDE", n = 2; schedule(tasks, n): (length, rule breaks)"#, (s.len(), problems(&tasks, 2, &s)), (12, Vec::<String>::new()));
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(709);
            for _ in 0..300 {
                let len = rng.below(8);
                let tasks: Vec<char> = rng.string(len, "abc").chars().collect();
                let n = rng.below(4);
                let want = brute_least(&tasks, n);
                let s = schedule(&tasks, n);
                check!(format!("tasks = {tasks:?}, n = {n}"), (least_interval(&tasks, n), s.len(), problems(&tasks, n, &s)), (want, want, Vec::<String>::new()));
            }
        }

        #[test]
        fn scale_50k_kinds() {
            // 50000 different ids (from U+10000 up), each twice.
            let ids: Vec<char> = (0..50_000).map(|i| char::from_u32(0x1_0000 + i).unwrap()).collect();
            let tasks: Vec<char> = ids.iter().chain(ids.iter()).copied().collect();
            let s = schedule(&tasks, 3);
            check!("tasks = 50000 different ids, each twice, n = 3", (least_interval(&tasks, 3), s.len(), problems(&tasks, 3, &s)), (100_000, 100_000, Vec::<String>::new()));
        }

        #[test]
        fn scale_one_kind_many_times() {
            let tasks = vec!['x'; 1000];
            let s = schedule(&tasks, 100);
            check!("tasks = 'x' × 1000, n = 100", (least_interval(&tasks, 100), s.len(), problems(&tasks, 100, &s)), (100_900, 100_900, Vec::<String>::new()));
        }

/// Breadth-first search over (tasks left, cooldown left) states: the true minimum for tiny inputs.
fn brute_least(tasks: &[char], n: usize) -> usize {
    let mut ids = tasks.to_vec();
    ids.sort_unstable();
    ids.dedup();
    let left: Vec<usize> = ids.iter().map(|c| tasks.iter().filter(|&t| t == c).count()).collect();
    let start = (left, vec![0usize; ids.len()]);
    let mut seen = std::collections::HashSet::new();
    seen.insert(start.clone());
    let mut queue = std::collections::VecDeque::from([(start, 0)]);
    while let Some(((left, wait), steps)) = queue.pop_front() {
        if left.iter().all(|&x| x == 0) {
            return steps;
        }
        // Run task `pick`, or stay idle when pick == ids.len().
        for pick in 0..=ids.len() {
            if pick < ids.len() && (left[pick] == 0 || wait[pick] > 0) {
                continue;
            }
            let mut l = left.clone();
            let mut w: Vec<usize> = wait.iter().map(|&x| x.saturating_sub(1)).collect();
            if pick < ids.len() {
                l[pick] -= 1;
                w[pick] = n;
            }
            if seen.insert((l.clone(), w.clone())) {
                queue.push_back(((l, w), steps + 1));
            }
        }
    }
    unreachable!()
}
