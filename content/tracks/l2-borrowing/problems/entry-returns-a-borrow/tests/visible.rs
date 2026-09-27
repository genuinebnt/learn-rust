use solution::*;

#[test]
fn docs_example() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow""#, (ix.docs("rust"), ix.docs("borrow"), ix.docs("check")), (&[1u32, 2][..], &[1u32, 5][..], &[1u32][..]));
}

#[test]
fn unknown_word_is_empty() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; docs("go")"#, (ix.docs("go"), ix.words()), (&[][..], 4));
}

#[test]
fn docs_mut_creates_and_edits() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    ix.docs_mut("go").push(9);
    ix.docs_mut("rust").retain(|&d| d != 1);
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; docs_mut("go").push(9); docs_mut("rust").retain(|&d| d != 1)"#, (ix.docs("go"), ix.docs("rust")), (&[9u32][..], &[2u32][..]));
}

#[test]
fn hit_counts() {
    let mut ix = Index::new();
    check!(r#"hit rust, rust, go, rust"#, (ix.hit("rust"), ix.hit("rust"), ix.hit("go"), ix.hit("rust")), (1, 2, 1, 3));
}

#[test]
fn remove_doc() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; remove_doc(1)"#, (ix.remove_doc(1), ix.docs("rust"), ix.docs("check"), ix.words()), (3, &[2u32][..], &[][..], 3));
}

#[test]
fn repeated_word_listed_once() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; docs("rust") after doc 2 said it twice"#, ix.docs("rust"), &[1u32, 2][..]);
}
