use solution::*;

/// `Probe::<T>::DEFAULT` is true only if T: Default (inherent consts win over trait consts when their bounds hold).
#[allow(dead_code)]
struct Probe<T: ?Sized>(std::marker::PhantomData<T>);

#[allow(dead_code)]
trait Fallback {
    const DEFAULT: bool = false;
    const FROM_STR_REF: bool = false;
}

#[allow(dead_code)]
impl<T: ?Sized> Fallback for Probe<T> {}

#[allow(dead_code)]
impl<T: Default> Probe<T> {
    const DEFAULT: bool = true;
}

#[allow(dead_code)]
impl<T: for<'a> From<&'a str>> Probe<T> {
    const FROM_STR_REF: bool = true;
}

fn ne(v: Vec<i32>) -> NonEmpty<i32> {
    NonEmpty::try_from(v).unwrap()
}

#[test]
fn first_last_max_are_not_options() {
    check!(r#"[3, 9, 2]: first, last, max"#, { let v = ne(vec![3, 9, 2]); let (a, b, c): (&i32, &i32, &i32) = (v.first(), v.last(), v.max()); (*a, *b, *c) }, (3, 2, 9));
}

#[test]
fn pop_never_empties() {
    check!(r#"[1, 2]: pop three times"#, { let mut v = ne(vec![1, 2]); (v.pop(), v.pop(), v.pop(), v.len(), *v.first()) }, (Some(2), None, None, 1, 1));
}

#[test]
fn try_from_empty() {
    check!(r#"an empty Vec"#, NonEmpty::<i32>::try_from(Vec::new()), Err(Empty));
}

#[test]
fn round_trip() {
    check!(r#"vec [4, 5, 6] -> NonEmpty -> map(x * 10) -> into_vec"#, ne(vec![4, 5, 6]).map(|x| x * 10).into_vec(), vec![40, 50, 60]);
}

#[test]
fn no_default() {
    check!(r#"is NonEmpty<i32> Default?"#, Probe::<NonEmpty<i32>>::DEFAULT, false);
}
