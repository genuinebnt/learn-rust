use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"[["John","johnsmith@mail.com","john_newyork@mail.com"], ["John","johnsmith@mail.com","john00@mail.com"], ["Mary","mary@mail.com"], ["John","johnnybravo@mail.com"]]"#, accounts_merge(&[vec!["John", "johnsmith@mail.com", "john_newyork@mail.com"], vec!["John", "johnsmith@mail.com", "john00@mail.com"], vec!["Mary", "mary@mail.com"], vec!["John", "johnnybravo@mail.com"]]), vec![vec!["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"], vec!["John", "johnnybravo@mail.com"], vec!["Mary", "mary@mail.com"]]);
}

#[test]
fn nothing_to_merge() {
    check!(r#"[["Gabe","Gabe0@m.co","Gabe3@m.co","Gabe1@m.co"], ["Kevin","Kevin3@m.co","Kevin5@m.co","Kevin0@m.co"], ["Ethan","Ethan5@m.co","Ethan4@m.co","Ethan0@m.co"]]"#, accounts_merge(&[vec!["Gabe", "Gabe0@m.co", "Gabe3@m.co", "Gabe1@m.co"], vec!["Kevin", "Kevin3@m.co", "Kevin5@m.co", "Kevin0@m.co"], vec!["Ethan", "Ethan5@m.co", "Ethan4@m.co", "Ethan0@m.co"]]), vec![vec!["Ethan", "Ethan0@m.co", "Ethan4@m.co", "Ethan5@m.co"], vec!["Gabe", "Gabe0@m.co", "Gabe1@m.co", "Gabe3@m.co"], vec!["Kevin", "Kevin0@m.co", "Kevin3@m.co", "Kevin5@m.co"]]);
}

#[test]
fn one_account() {
    check!(r#"[["Ann","a@x"]]"#, accounts_merge(&[vec!["Ann", "a@x"]]), vec![vec!["Ann", "a@x"]]);
}

#[test]
fn same_name_is_not_enough() {
    check!(r#"[["Ann","a@x"], ["Ann","b@x"]]"#, accounts_merge(&[vec!["Ann", "a@x"], vec!["Ann", "b@x"]]), vec![vec!["Ann", "a@x"], vec!["Ann", "b@x"]]);
}

#[test]
fn linked_through_a_third_account() {
    check!(r#"[["Ann","a@x","b@x"], ["Ann","c@x","d@x"], ["Ann","b@x","c@x"]]"#, accounts_merge(&[vec!["Ann", "a@x", "b@x"], vec!["Ann", "c@x", "d@x"], vec!["Ann", "b@x", "c@x"]]), vec![vec!["Ann", "a@x", "b@x", "c@x", "d@x"]]);
}
