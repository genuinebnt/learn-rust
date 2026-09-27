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

#[test]
fn map_leaves_err_alone() {
    check!(r#"Err("x")"#, MyResult::<i32, &str>::Err("x").map(|v| -> i32 { panic!("should not run: {v}") }), MyResult::Err("x"));
}

#[test]
fn map_err_skips_f_on_ok() {
    check!(r#"Ok(1)"#, MyResult::<i32, i32>::Ok(1).map_err(|e| -> i32 { panic!("should not run: {e}") }), MyResult::Ok(1));
}

#[test]
fn and_then_ok_to_err() {
    check!(r#"Ok(1)"#, MyResult::<i32, &str>::Ok(1).and_then(|_| MyResult::<i32, &str>::Err("late")), MyResult::Err("late"));
}

#[test]
fn map_changes_type() {
    check!(r#"Ok("abc")"#, MyResult::<&str, ()>::Ok("abc").map(str::len), MyResult::Ok(3));
}

fn sum3(a: MyResult<i32, String>, b: MyResult<i32, String>, c: MyResult<i32, String>, steps: &mut u32) -> MyResult<i32, String> {
    let x = try_my!(a);
    *steps += 1;
    let y = try_my!(b);
    *steps += 1;
    let z = try_my!(c);
    *steps += 1;
    MyResult::Ok(x + y + z)
}

fn once(r: MyResult<i32, String>, calls: &mut u32) -> MyResult<i32, String> {
    *calls += 1;
    r
}

fn inline(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
    MyResult::Ok(try_my!(a) * 10 + try_my!(b))
}

#[test]
fn try_first_error_wins() {
    let mut steps = 0;
    let got = sum3(MyResult::Ok(1), MyResult::Err("b".into()), MyResult::Err("c".into()), &mut steps);
    check!("Ok(1), Err(\"b\"), Err(\"c\")", (got, steps), (MyResult::Err("b".to_string()), 1));
}

#[test]
fn try_stops_at_the_first_error() {
    let mut steps = 0;
    let got = sum3(MyResult::Err("a".into()), MyResult::Ok(2), MyResult::Ok(3), &mut steps);
    check!("Err(\"a\"), Ok(2), Ok(3)", (got, steps), (MyResult::Err("a".to_string()), 0));
}

#[test]
fn try_evaluates_its_argument_once() {
    fn run(calls: &mut u32) -> MyResult<i32, String> {
        let v = try_my!(once(MyResult::Ok(4), calls));
        MyResult::Ok(v)
    }
    let mut calls = 0;
    let got = run(&mut calls);
    check!("try_my!(once(Ok(4)))", (got, calls), (MyResult::Ok(4), 1));
}

#[test]
fn try_inside_an_expression() {
    check!("Ok(Ok(4) * 10 + Ok(2))", inline(MyResult::Ok(4), MyResult::Ok(2)), MyResult::Ok(42));
    check!("Ok(Ok(4) * 10 + Err(\"b\"))", inline(MyResult::Ok(4), MyResult::Err("b".into())), MyResult::Err("b".to_string()));
}

fn add_mine(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
    MyResult::Ok(try_my!(a) + try_my!(b))
}

fn add_std(a: Result<i32, String>, b: Result<i32, String>) -> Result<i32, String> {
    Ok(a? + b?)
}

fn mine(r: Result<i32, String>) -> MyResult<i32, String> {
    match r {
        Ok(v) => MyResult::Ok(v),
        Err(e) => MyResult::Err(e),
    }
}

#[test]
fn random_vs_std_result() {
    let mut rng = anneal_prelude::Rng::new(1310);
    for _ in 0..300 {
        let a: Result<i32, String> = if rng.below(3) > 0 { Ok(rng.int(-9, 9) as i32) } else { Err(rng.string(1, "xyz")) };
        let b: Result<i32, String> = if rng.below(3) > 0 { Ok(rng.int(-9, 9) as i32) } else { Err(rng.string(1, "xyz")) };
        let desc = format!("a = {a:?}, b = {b:?}");
        check!(format!("map(x * 2), {desc}"), mine(a.clone()).map(|x| x * 2), mine(a.clone().map(|x| x * 2)));
        check!(format!("map_err(push '!'), {desc}"), mine(a.clone()).map_err(|e| e + "!"), mine(a.clone().map_err(|e| e + "!")));
        check!(format!("and_then(positive), {desc}"), mine(a.clone()).and_then(|x| if x > 0 { MyResult::Ok(x) } else { MyResult::Err("neg".to_string()) }), mine(a.clone().and_then(|x| if x > 0 { Ok(x) } else { Err("neg".to_string()) })));
        check!(format!("try_my!(a) + try_my!(b), {desc}"), add_mine(mine(a.clone()), mine(b.clone())), mine(add_std(a, b)));
    }
}
