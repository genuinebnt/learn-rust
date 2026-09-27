use solution::*;

#[test]
fn chain_and_unknowns() {
    check!(r#"equations = [("a","b"), ("b","c")], values = [2.0, 3.0], queries = [("a","c"), ("b","a"), ("a","e"), ("a","a"), ("x","x")]"#, calc_equation(&[("a", "b"), ("b", "c")], &[2.0, 3.0], &[("a", "c"), ("b", "a"), ("a", "e"), ("a", "a"), ("x", "x")]), vec![Some(6.0), Some(0.5), None, Some(1.0), None]);
}

#[test]
fn longer_names() {
    check!(r#"equations = [("a","b"), ("b","c"), ("bc","cd")], values = [1.5, 2.5, 5.0], queries = [("a","c"), ("c","b"), ("bc","cd"), ("cd","bc")]"#, calc_equation(&[("a", "b"), ("b", "c"), ("bc", "cd")], &[1.5, 2.5, 5.0], &[("a", "c"), ("c", "b"), ("bc", "cd"), ("cd", "bc")]), vec![Some(3.75), Some(0.4), Some(5.0), Some(0.2)]);
}

#[test]
fn one_equation() {
    check!(r#"equations = [("a","b")], values = [0.5], queries = [("a","b"), ("b","a"), ("a","c"), ("x","y")]"#, calc_equation(&[("a", "b")], &[0.5], &[("a", "b"), ("b", "a"), ("a", "c"), ("x", "y")]), vec![Some(0.5), Some(2.0), None, None]);
}

#[test]
fn separate_groups() {
    check!(r#"equations = [("a","b"), ("c","d")], values = [2.0, 4.0], queries = [("a","d")]"#, calc_equation(&[("a", "b"), ("c", "d")], &[2.0, 4.0], &[("a", "d")]), vec![None]);
}

#[test]
fn no_queries() {
    check!(r#"equations = [("a","b")], values = [2.0], queries = []"#, calc_equation(&[("a", "b")], &[2.0], &[]), Vec::<Option<f64>>::new());
}
