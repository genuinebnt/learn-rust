use solution::*;

#[test]
fn too_small() {
    check!(r#"greed = [2], cookies = [1]"#, find_content_children(&[2], &[1]), 0);
}

#[test]
fn both_empty() {
    check!(r#"greed = [], cookies = []"#, find_content_children(&[], &[]), 0);
}

#[test]
fn duplicates() {
    check!(r#"greed = [2, 2, 2], cookies = [2, 2]"#, find_content_children(&[2, 2, 2], &[2, 2]), 2);
}

#[test]
fn max_values() {
    check!(r#"greed = [4294967295, 1], cookies = [4294967295]"#, find_content_children(&[u32::MAX, 1], &[u32::MAX]), 1);
}

#[test]
fn big_cookie_not_wasted() {
    check!(r#"greed = [1, 3], cookies = [3, 1]"#, find_content_children(&[1, 3], &[3, 1]), 2);
}

#[test]
fn all_cookies_too_small() {
    check!(r#"greed = [10, 20], cookies = [1, 2, 3]"#, find_content_children(&[10, 20], &[1, 2, 3]), 0);
}

#[test]
fn more_cookies_than_children() {
    check!(r#"greed = [2, 1], cookies = [1, 1, 2, 2, 3]"#, find_content_children(&[2, 1], &[1, 1, 2, 2, 3]), 2);
}

#[test]
fn greedy_child_skipped() {
    check!(r#"greed = [1, 2, 100], cookies = [1, 2, 3]"#, find_content_children(&[1, 2, 100], &[1, 2, 3]), 2);
}

#[test]
fn random_vs_brute_force() {
    fn best(greed: &[u32], cookies: &[u32], used: &mut Vec<bool>) -> usize {
        let Some((&g, rest)) = greed.split_first() else { return 0 };
        let mut out = best(rest, cookies, used);
        for j in 0..cookies.len() {
            if !used[j] && cookies[j] >= g {
                used[j] = true;
                out = out.max(1 + best(rest, cookies, used));
                used[j] = false;
            }
        }
        out
    }
    let mut rng = anneal_prelude::Rng::new(801);
    for _ in 0..300 {
        let n = rng.below(6);
        let m = rng.below(6);
        let greed: Vec<u32> = rng.vec(n, 1, 8);
        let cookies: Vec<u32> = rng.vec(m, 1, 8);
        let want = best(&greed, &cookies, &mut vec![false; m]);
        check!(format!("greed = {greed:?}, cookies = {cookies:?}"), find_content_children(&greed, &cookies), want);
    }
}

#[test]
fn scale_200k() {
    let greed: Vec<u32> = (1..=200_000).collect();
    let cookies: Vec<u32> = (1..=200_000).rev().collect();
    check!("greed = 1..=200000, cookies = 200000 down to 1", find_content_children(&greed, &cookies), 200_000);
}
