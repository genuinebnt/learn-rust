use solution::*;

#[derive(Debug, PartialEq)]
struct AppError(String);

impl From<&'static str> for AppError {
    fn from(s: &'static str) -> Self {
        AppError(s.to_string())
    }
}

fn converts(r: MyResult<u8, &'static str>) -> MyResult<u8, AppError> {
    let v = try_my!(r);
    MyResult::Ok(v)
}

#[test]
fn try_converts_the_error_with_from() {
    check!("Err(\"bad\")", converts(MyResult::Err("bad")), MyResult::Err(AppError("bad".into())));
}

#[test]
fn map_err() {
    check!(r#"Err(4)"#, MyResult::<(), i32>::Err(4).map_err(|e| e + 1), MyResult::Err(5));
}

#[test]
fn and_then_short_circuits() {
    check!(r#"Err("x")"#, MyResult::<i32, &str>::Err("x").and_then(|v| MyResult::Ok(v + 1)), MyResult::Err("x"));
}
