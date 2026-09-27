use solution::*;

#[test]
fn repeated_email_in_one_account() {
    check!(r#"[["Ann","a@x","a@x"]]"#, accounts_merge(&[vec!["Ann", "a@x", "a@x"]]), vec![vec!["Ann", "a@x"]]);
}

#[test]
fn identical_accounts() {
    check!(r#"[["Bob","b@x"], ["Bob","b@x"]]"#, accounts_merge(&[vec!["Bob", "b@x"], vec!["Bob", "b@x"]]), vec![vec!["Bob", "b@x"]]);
}

#[test]
fn empty() {
    check!(r#"accounts = []"#, accounts_merge(&[]), Vec::<Vec<String>>::new());
}

#[test]
fn long_chain_listed_backwards() {
    check!(r#"[["C","e@x","f@x"], ["C","d@x","e@x"], ["C","c@x","d@x"], ["C","b@x","c@x"], ["C","a@x","b@x"]]"#, accounts_merge(&[vec!["C", "e@x", "f@x"], vec!["C", "d@x", "e@x"], vec!["C", "c@x", "d@x"], vec!["C", "b@x", "c@x"], vec!["C", "a@x", "b@x"]]), vec![vec!["C", "a@x", "b@x", "c@x", "d@x", "e@x", "f@x"]]);
}

#[test]
fn two_groups_joined_late() {
    check!(r#"[["D","a@x"], ["D","b@x"], ["D","c@x","a@x"], ["D","c@x","b@x"]]"#, accounts_merge(&[vec!["D", "a@x"], vec!["D", "b@x"], vec!["D", "c@x", "a@x"], vec!["D", "c@x", "b@x"]]), vec![vec!["D", "a@x", "b@x", "c@x"]]);
}

#[test]
fn sorted_by_name_then_email() {
    check!(r#"[["Zed","z@x"], ["Amy","y@x"], ["Amy","b@x"]]"#, accounts_merge(&[vec!["Zed", "z@x"], vec!["Amy", "y@x"], vec!["Amy", "b@x"]]), vec![vec!["Amy", "b@x"], vec!["Amy", "y@x"], vec!["Zed", "z@x"]]);
}

#[test]
fn unicode() {
    check!(r#"[["Zoë","ü@x","a@x"], ["Zoë","a@x"]]"#, accounts_merge(&[vec!["Zoë", "ü@x", "a@x"], vec!["Zoë", "a@x"]]), vec![vec!["Zoë", "a@x", "ü@x"]]);
}

#[test]
fn random_vs_brute_force() {
    use std::collections::BTreeSet;
    let mut rng = anneal_prelude::Rng::new(951);
    let names = ["Ann", "Bob"];
    for _ in 0..300 {
        let people = 1 + rng.below(4);
        let name_of: Vec<&str> = (0..people).map(|_| *rng.pick(&names)).collect();
        let count = 1 + rng.below(6);
        let mut owned: Vec<Vec<String>> = Vec::new();
        for _ in 0..count {
            let p = rng.below(people);
            let k = 1 + rng.below(3);
            let mut account = vec![name_of[p].to_string()];
            for _ in 0..k {
                let j = rng.below(3);
                account.push(format!("p{p}_{j}@m"));
            }
            owned.push(account);
        }
        let accounts: Vec<Vec<&str>> = owned.iter().map(|a| a.iter().map(|s| s.as_str()).collect()).collect();
        // Brute force: merge any two groups that share an email until nothing changes.
        let mut groups: Vec<(String, BTreeSet<String>)> = owned.iter().map(|a| (a[0].clone(), a[1..].iter().cloned().collect())).collect();
        'outer: loop {
            for i in 0..groups.len() {
                for j in i + 1..groups.len() {
                    if !groups[i].1.is_disjoint(&groups[j].1) {
                        let (_, moved) = groups.remove(j);
                        groups[i].1.extend(moved);
                        continue 'outer;
                    }
                }
            }
            break;
        }
        let mut want: Vec<Vec<String>> = groups.into_iter().map(|(n, e)| std::iter::once(n).chain(e).collect()).collect();
        want.sort();
        check!(format!("accounts = {accounts:?}"), accounts_merge(&accounts), want);
    }
}

#[test]
fn scale_all_separate_50k() {
    let n = 50_000;
    let owned: Vec<[String; 2]> = (0..n).map(|i| [format!("P{i:06}"), format!("e{i:06}@x")]).collect();
    let accounts: Vec<Vec<&str>> = owned.iter().rev().map(|[a, b]| vec![a.as_str(), b.as_str()]).collect();
    let out = accounts_merge(&accounts);
    check!("50000 accounts, no shared emails, listed in reverse", (out.len(), out[0].clone(), out[n - 1].clone()),
           (n, vec!["P000000".to_string(), "e000000@x".to_string()], vec!["P049999".to_string(), "e049999@x".to_string()]));
}

#[test]
fn scale_scrambled_chain_50k() {
    // Account i holds e_i and e_(i+1); listed in a scrambled order, they all merge into one.
    let n = 50_000;
    let emails: Vec<String> = (0..=n).map(|i| format!("e{i:06}@x")).collect();
    let accounts: Vec<Vec<&str>> = (0..n).map(|k| k * 7919 % n).map(|i| vec!["Ann", emails[i].as_str(), emails[i + 1].as_str()]).collect();
    let out = accounts_merge(&accounts);
    check!("50000 accounts chained by shared emails, scrambled", (out.len(), out[0].len(), out[0][1].clone(), out[0][n + 1].clone()),
           (1, n + 2, "e000000@x".to_string(), "e050000@x".to_string()));
}
