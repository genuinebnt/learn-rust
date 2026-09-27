use solution::*;

#[test]
fn unknown_variable_over_itself() {
    check!(r#"equations = [("a","b")], values = [2.0], queries = [("z","z")]"#, calc_equation(&[("a", "b")], &[2.0], &[("z", "z")]), vec![None]);
}

#[test]
fn known_variable_over_itself() {
    check!(r#"equations = [("a","b")], values = [2.0], queries = [("b","b")]"#, calc_equation(&[("a", "b")], &[2.0], &[("b", "b")]), vec![Some(1.0)]);
}

#[test]
fn joined_later() {
    check!(r#"equations = [("a","b"), ("c","d"), ("b","c")], values = [2.0, 4.0, 0.5], queries = [("a","d"), ("d","a")]"#, calc_equation(&[("a", "b"), ("c", "d"), ("b", "c")], &[2.0, 4.0, 0.5], &[("a", "d"), ("d", "a")]), vec![Some(4.0), Some(0.25)]);
}

#[test]
fn redundant_equation() {
    check!(r#"equations = [("a","b"), ("b","c"), ("a","c")], values = [2.0, 2.0, 4.0], queries = [("c","a")]"#, calc_equation(&[("a", "b"), ("b", "c"), ("a", "c")], &[2.0, 2.0, 4.0], &[("c", "a")]), vec![Some(0.25)]);
}

#[test]
fn star_through_the_middle() {
    check!(r#"equations = [("x","m"), ("y","m"), ("z","m")], values = [2.0, 4.0, 8.0], queries = [("x","z"), ("z","y")]"#, calc_equation(&[("x", "m"), ("y", "m"), ("z", "m")], &[2.0, 4.0, 8.0], &[("x", "z"), ("z", "y")]), vec![Some(0.25), Some(2.0)]);
}

#[test]
fn unicode_names() {
    check!(r#"equations = [("α","β")], values = [4.0], queries = [("β","α")]"#, calc_equation(&[("α", "β")], &[4.0], &[("β", "α")]), vec![Some(0.25)]);
}

#[test]
fn random_vs_brute_force() {
    let names = ["a", "b", "c", "d", "e", "f"];
    let vals = [0.25, 0.5, 1.0, 2.0, 4.0];
    let mut rng = anneal_prelude::Rng::new(945);
    for _ in 0..300 {
        // A random forest of equations, so they never contradict each other.
        let n = 1 + rng.below(6);
        let mut eqs: Vec<(&str, &str)> = Vec::new();
        let mut values = Vec::new();
        for i in 1..n {
            if rng.below(4) > 0 {
                let j = rng.below(i);
                eqs.push(if rng.bool() { (names[i], names[j]) } else { (names[j], names[i]) });
                values.push(*rng.pick(&vals));
            }
        }
        let queries: Vec<(&str, &str)> = (0..5).map(|_| (*rng.pick(&names), *rng.pick(&names))).collect();
        // Brute force: fill a ratio table by repeated composition.
        let idx = |s: &str| names.iter().position(|&x| x == s).unwrap();
        let mut r: Vec<Vec<Option<f64>>> = vec![vec![None; 6]; 6];
        for (&(a, b), &v) in eqs.iter().zip(&values) {
            let (i, j) = (idx(a), idx(b));
            r[i][j] = Some(v);
            r[j][i] = Some(1.0 / v);
            r[i][i] = Some(1.0);
            r[j][j] = Some(1.0);
        }
        for k in 0..6 {
            for i in 0..6 {
                for j in 0..6 {
                    if let (Some(x), Some(y), None) = (r[i][k], r[k][j], r[i][j]) {
                        r[i][j] = Some(x * y);
                    }
                }
            }
        }
        let want: Vec<Option<f64>> = queries.iter().map(|&(c, d)| r[idx(c)][idx(d)]).collect();
        check!(format!("equations = {eqs:?}, values = {values:?}, queries = {queries:?}"), calc_equation(&eqs, &values, &queries), want);
    }
}

#[test]
fn scale_long_chain() {
    // v0 / v1 = 2, v1 / v2 = 0.5, v2 / v3 = 2, …: v0 / vk is 2 when k is odd and 1 when k is even.
    let n = 20_000;
    let names: Vec<String> = (0..n).map(|i| format!("v{i}")).collect();
    let eqs: Vec<(&str, &str)> = (0..n - 1).map(|i| (names[i].as_str(), names[i + 1].as_str())).collect();
    let values: Vec<f64> = (0..n - 1).map(|i| if i % 2 == 0 { 2.0 } else { 0.5 }).collect();
    let queries: Vec<(&str, &str)> = (0..n).map(|k| (names[0].as_str(), names[(k * 7919) % n].as_str())).collect();
    let got = calc_equation(&eqs, &values, &queries);
    let bad = (0..n).filter(|&k| got[k] != Some(if (k * 7919) % n % 2 == 1 { 2.0 } else { 1.0 })).count();
    check!("a chain of 20000 variables, 20000 queries from the first: how many answers are wrong", bad, 0);
}
