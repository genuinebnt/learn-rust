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
fn single() {
    check!(r#"NonEmpty::new(7)"#, { let v = NonEmpty::new(7); (*v.first(), *v.last(), *v.max(), v.len()) }, (7, 7, 7, 1));
}

#[test]
fn get() {
    check!(r#"[1, 2, 3]: get 0, 2, 3"#, { let v = ne(vec![1, 2, 3]); (v.get(0).copied(), v.get(2).copied(), v.get(3).copied()) }, (Some(1), Some(3), None));
}

#[test]
fn max_first_of_ties() {
    check!(r#"[5, 5, 4]: which 5 is the max?"#, { let v = ne(vec![5, 5, 4]); std::ptr::eq(v.max(), v.first()) }, true);
}

#[test]
fn sort_moves_a_smaller_item_to_the_front() {
    check!(r#"[5, 3, 9, 1] sorted"#, { let mut v = ne(vec![5, 3, 9, 1]); v.sort(); v.into_vec() }, vec![1, 3, 5, 9]);
}

#[test]
fn sort_keeps_the_front_when_smallest() {
    check!(r#"[1, 3, 2] sorted"#, { let mut v = ne(vec![1, 3, 2]); v.sort(); v.into_vec() }, vec![1, 2, 3]);
}

#[test]
fn sort_single() {
    check!(r#"[7] sorted"#, { let mut v = NonEmpty::new(7); v.sort(); v.into_vec() }, vec![7]);
}

#[test]
fn into_iter_order() {
    check!(r#"strings [a, b, c] by value"#, NonEmpty::try_from(vec!["a".to_string(), "b".to_string(), "c".to_string()]).unwrap().into_iter().collect::<Vec<_>>().join(""), "abc");
}

#[test]
fn iter_and_split_first() {
    check!(r#"[1, 2, 3]: iter, split_first"#, { let v = ne(vec![1, 2, 3]); (v.iter().copied().collect::<Vec<_>>(), v.split_first().0.clone(), v.split_first().1.to_vec()) }, (vec![1, 2, 3], 1, vec![2, 3]));
}

#[test]
fn map_changes_type() {
    check!(r#"[1, 22] map to_string"#, ne(vec![1, 22]).map(|x| x.to_string()).into_vec(), vec!["1".to_string(), "22".to_string()]);
}

#[test]
fn push_after_pops() {
    check!(r#"[1]: pop, push 2, last"#, { let mut v = NonEmpty::new(1); let p = v.pop(); v.push(2); (p, *v.last(), v.len()) }, (None, 2, 2));
}

#[test]
fn try_from_non_empty_is_ok() {
    check!(r#"vec [0]"#, NonEmpty::try_from(vec![0]).map(|v| v.len()), Ok(1));
}

#[test]
fn random_vs_vec_model() {
    let mut rng = anneal_prelude::Rng::new(4519);
    for _ in 0..300 {
        let first = rng.int(-9, 9);
        let mut v = NonEmpty::new(first);
        let mut model = vec![first];
        let mut log = vec![format!("new({first})")];
        for _ in 0..rng.below(15) {
            match rng.below(4) {
                0 | 1 => {
                    let x = rng.int(-9, 9);
                    log.push(format!("push({x})"));
                    v.push(x);
                    model.push(x);
                }
                2 => {
                    log.push("pop".to_string());
                    let want = if model.len() > 1 { model.pop() } else { None };
                    check!(log.join(", "), v.pop(), want);
                }
                _ => {
                    log.push("sort".to_string());
                    v.sort();
                    model.sort();
                }
            }
            let mut max_at = 0;
            for i in 1..model.len() {
                if model[i] > model[max_at] {
                    max_at = i;
                }
            }
            let i = rng.below(model.len() + 1);
            check!(log.join(", "), (v.len(), *v.first(), *v.last(), *v.max(), v.get(i).copied(), v.iter().copied().collect::<Vec<_>>()),
                   (model.len(), model[0], model[model.len() - 1], model[max_at], model.get(i).copied(), model.clone()));
        }
        check!(log.join(", "), v.into_vec(), model);
    }
}
