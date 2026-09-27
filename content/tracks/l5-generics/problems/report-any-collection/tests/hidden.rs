use solution::*;

/// A collection that isn't Clone and whose by-reference items are owned u32s.
struct Evens(u32);

impl<'a> IntoIterator for &'a Evens {
    type Item = u32;
    type IntoIter = std::iter::StepBy<std::ops::Range<u32>>;
    fn into_iter(self) -> Self::IntoIter {
        (0..2 * self.0).step_by(2)
    }
}

#[test]
fn array() {
    check!(r#"Report::new("A", ["x", "y", "z"])"#, Report::new("A", ["x", "y", "z"]).to_string(), "A\n- x\n- y\n- z");
}

#[test]
fn option_some() {
    check!(r#"Report::new("Maybe", Some(5))"#, Report::new("Maybe", Some(5)).to_string(), "Maybe\n- 5");
}

#[test]
fn option_none() {
    check!(r#"Report::new("Maybe", None::<i32>)"#, Report::new("Maybe", None::<i32>).to_string(), "Maybe");
}

#[test]
fn strings() {
    check!(r#"Report::new("S", vec!["héllo".to_string()])"#, Report::new("S", vec!["héllo".to_string()]).to_string(), "S\n- héllo");
}

#[test]
fn nested_reports() {
    check!(r#"a Report of Reports"#, Report::new("outer", vec![Report::new("a", vec![1]), Report::new("b", vec![])]).to_string(), "outer\n- a\n- 1\n- b");
}

#[test]
fn empty_evens() {
    check!(r#"Report::new("E", Evens(0))"#, Report::new("E", Evens(0)).to_string(), "E");
}

#[test]
fn printed_twice() {
    let r = Report::new("T", Evens(1));
    check!(r#"print the same report twice"#, (r.to_string(), r.to_string()), ("T\n- 0".to_string(), "T\n- 0".to_string()));
}

#[test]
fn rows_returns_the_collection() {
    let r = Report::new("B", std::collections::BTreeSet::from([3, 1, 2]));
    let _ = r.to_string();
    check!(r#"rows() of a BTreeSet report"#, r.rows().iter().next().copied(), Some(1));
}

#[test]
fn empty_title() {
    check!(r#"Report::new("", vec![0])"#, Report::new("", vec![0]).to_string(), "\n- 0");
}

#[test]
fn random_vs_format() {
    let mut rng = anneal_prelude::Rng::new(4505);
    for _ in 0..300 {
        let n = rng.below(5);
        let v: Vec<i32> = rng.vec(n, -99, 99);
        let mut want = String::from("R");
        for x in &v {
            want.push_str(&format!("\n- {x}"));
        }
        let r = Report::new("R", v.clone());
        check!(format!("rows = {v:?}"), (r.to_string(), r.rows().len()), (want, n));
    }
}
