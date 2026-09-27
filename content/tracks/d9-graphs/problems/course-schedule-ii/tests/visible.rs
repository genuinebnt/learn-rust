use solution::*;

/// "valid order", "no order", or what's wrong with the answer.
fn verdict(n: usize, prereqs: &[(usize, usize)], got: Option<Vec<usize>>) -> String {
    let Some(order) = got else {
        return "no order".to_string();
    };
    let mut pos = vec![usize::MAX; n];
    for (i, &c) in order.iter().enumerate() {
        if c >= n || pos[c] != usize::MAX {
            return format!("not a permutation of 0..{n}: {order:?}");
        }
        pos[c] = i;
    }
    if order.len() != n {
        return format!("only {} of {n} courses: {order:?}", order.len());
    }
    match prereqs.iter().find(|&&(a, b)| pos[a] > pos[b]) {
        Some(&(a, b)) => format!("{b} comes before its prerequisite {a}: {order:?}"),
        None => "valid order".to_string(),
    }
}

#[test]
fn two_courses() {
    check!(r#"n = 2, prereqs = [(0, 1)]"#, verdict(2, &[(0, 1)], find_order(2, &[(0, 1)])), "valid order");
}

#[test]
fn diamond() {
    let p = [(0, 1), (0, 2), (1, 3), (2, 3)];
    check!(r#"n = 4, prereqs = [(0, 1), (0, 2), (1, 3), (2, 3)]"#, verdict(4, &p, find_order(4, &p)), "valid order");
}

#[test]
fn one_course() {
    check!(r#"n = 1, prereqs = []"#, find_order(1, &[]), Some(vec![0]));
}

#[test]
fn cycle() {
    check!(r#"n = 2, prereqs = [(0, 1), (1, 0)]"#, find_order(2, &[(0, 1), (1, 0)]), None);
}

#[test]
fn every_course_listed() {
    check!(r#"n = 3, prereqs = [(2, 0)]"#, verdict(3, &[(2, 0)], find_order(3, &[(2, 0)])), "valid order");
}
