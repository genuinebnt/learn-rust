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
fn vec() {
    check!(r#"Report::new("Nums", vec![1, 2])"#, Report::new("Nums", vec![1, 2]).to_string(), "Nums\n- 1\n- 2");
}

#[test]
fn empty_is_just_the_title() {
    check!(r#"Report::new("None", Vec::<i32>::new())"#, Report::new("None", Vec::<i32>::new()).to_string(), "None");
}

#[test]
fn btreeset_in_order() {
    check!(r#"Report::new("Fruit", BTreeSet::from(["pear", "apple"]))"#, Report::new("Fruit", std::collections::BTreeSet::from(["pear", "apple"])).to_string(), "Fruit\n- apple\n- pear");
}

#[test]
fn rows_still_there() {
    let r = Report::new("Q", std::collections::VecDeque::from(vec!['a', 'b']));
    let text = r.to_string();
    check!(r#"print a VecDeque report, then rows().len()"#, (text, r.rows().len()), ("Q\n- a\n- b".to_string(), 2));
}

#[test]
fn own_collection() {
    check!(r#"Report::new("Evens", Evens(3)): items are owned u32s"#, Report::new("Evens", Evens(3)).to_string(), "Evens\n- 0\n- 2\n- 4");
}
