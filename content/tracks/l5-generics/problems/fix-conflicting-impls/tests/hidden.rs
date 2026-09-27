use solution::*;

/// A type from "another crate" whose Describe differs from its Display.
struct Celsius(f64);

impl std::fmt::Display for Celsius {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl Describe for Celsius {
    fn describe(&self) -> String {
        format!("{}°C", self.0)
    }
}

#[test]
fn empty_vec() {
    check!(r#"Vec::<u8>::new()"#, Vec::<u8>::new().describe(), "[]");
}

#[test]
fn nested_vecs() {
    check!(r#"vec![vec![1], vec![], vec![2, 3]]"#, vec![vec![1], vec![], vec![2, 3]].describe(), "[[1], [], [2, 3]]");
}

#[test]
fn option_of_vec() {
    check!(r#"Some(vec![None, Some(1)])"#, Some(vec![None, Some(1u64)]).describe(), "[-, 1]");
}

#[test]
fn every_integer_width() {
    check!(r#"i8, i16, i64, i128, isize, u8, u16, u32, u128, usize"#, vec![(-1i8).describe(), 2i16.describe(), (-3i64).describe(), 4i128.describe(), 5isize.describe(), 6u8.describe(), 7u16.describe(), 8u32.describe(), 9u128.describe(), 10usize.describe()].join(" "), "-1 2 -3 4 5 6 7 8 9 10");
}

#[test]
fn f32() {
    check!(r#"0.5f32"#, 0.5f32.describe(), "0.5");
}

#[test]
fn double_reference() {
    check!(r#"&&"x""#, (&&"x").describe(), "x");
}

#[test]
fn vec_of_names() {
    check!(r#"vec![Name("Bo"), Name("CY")]"#, vec![Name("Bo".into()), Name("CY".into())].describe(), "[bo, cy]");
}

#[test]
fn option_of_celsius() {
    check!(r#"Some(Celsius(-4.0)), None"#, (Some(Celsius(-4.0)).describe(), None::<Celsius>.describe()), ("-4°C".to_string(), "-".to_string()));
}

#[test]
fn vec_of_strs_unicode() {
    check!(r#"vec!["é", "ß"]"#, vec!["é", "ß"].describe(), "[é, ß]");
}

#[test]
fn through_generic_fn() {
    fn show<T: Describe + ?Sized>(x: &T) -> String {
        format!("<{}>", x.describe())
    }
    check!(r#"a generic fn that takes T: Describe + ?Sized"#, show("str slice"), "<str slice>");
}

#[test]
fn random_vs_format() {
    let mut rng = anneal_prelude::Rng::new(4506);
    for _ in 0..300 {
        let n = rng.below(5);
        let v: Vec<Option<i64>> = (0..n).map(|_| if rng.bool() { Some(rng.int(-99, 99)) } else { None }).collect();
        let want = format!("[{}]", v.iter().map(|x| x.map_or("-".to_string(), |y| y.to_string())).collect::<Vec<_>>().join(", "));
        check!(format!("{v:?}"), v.describe(), want);
    }
}
