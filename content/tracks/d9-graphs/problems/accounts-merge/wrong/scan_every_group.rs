use std::collections::HashSet;

pub fn accounts_merge(accounts: &[Vec<&str>]) -> Vec<Vec<String>> {
    let mut groups: Vec<(String, HashSet<String>)> = Vec::new();
    for account in accounts {
        let mut merged: HashSet<String> = account[1..].iter().map(|e| e.to_string()).collect();
        let mut kept = Vec::new();
        for (name, emails) in groups {
            if account[1..].iter().any(|e| emails.contains(*e)) {
                merged.extend(emails);
            } else {
                kept.push((name, emails));
            }
        }
        kept.push((account[0].to_string(), merged));
        groups = kept;
    }
    let mut out: Vec<Vec<String>> = groups
        .into_iter()
        .map(|(name, emails)| {
            let mut emails: Vec<String> = emails.into_iter().collect();
            emails.sort_unstable();
            std::iter::once(name).chain(emails).collect()
        })
        .collect();
    out.sort_unstable();
    out
}
