use solution::*;

fn add(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
    let x = try_my!(a);
    let y = try_my!(b);
    MyResult::Ok(x + y)
}

#[test]
fn try_passes_values_through() {
    check!("Ok(2) + Ok(3)", add(MyResult::Ok(2), MyResult::Ok(3)), MyResult::Ok(5));
}

#[test]
fn try_returns_early() {
    check!("Ok(2) + Err(\"no\")", add(MyResult::Ok(2), MyResult::Err("no".into())), MyResult::Err("no".to_string()));
}

#[test]
fn map() {
    check!(r#"Ok(2)"#, MyResult::<i32, ()>::Ok(2).map(|x| x * 3), MyResult::Ok(6));
}
