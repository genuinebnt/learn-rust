use std::collections::HashMap;

pub fn accounts_merge(accounts: &[Vec<&str>]) -> Vec<Vec<String>> {
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }

    // Every distinct email gets an index; `owner[e]` is the first account that listed it.
    let mut id: HashMap<&str, usize> = HashMap::new();
    let mut parent: Vec<usize> = Vec::new();
    let mut owner: Vec<usize> = Vec::new();
    for (a, account) in accounts.iter().enumerate() {
        let mut first = None;
        for &email in &account[1..] {
            let e = *id.entry(email).or_insert_with(|| {
                parent.push(parent.len());
                owner.push(a);
                parent.len() - 1
            });
            match first {
                None => first = Some(e),
                Some(f) => {
                    let (rf, re) = (root(&mut parent, f), root(&mut parent, e));
                    parent[re] = rf;
                }
            }
        }
    }

    let mut groups: HashMap<usize, Vec<&str>> = HashMap::new();
    for (&email, &e) in &id {
        let r = root(&mut parent, e);
        groups.entry(r).or_default().push(email);
    }
    let mut out: Vec<Vec<String>> = groups
        .into_iter()
        .map(|(r, mut emails)| {
            emails.sort_unstable();
            let mut merged = vec![accounts[owner[r]][0].to_string()];
            merged.extend(emails.into_iter().map(String::from));
            merged
        })
        .collect();
    out.sort_unstable();
    out
}
