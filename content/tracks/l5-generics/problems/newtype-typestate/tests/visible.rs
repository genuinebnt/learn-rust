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

fn user(name: &str, pw: &str) -> User<LoggedOut> {
    User::new(Username::parse(name).unwrap(), pw)
}

/// Which variant, and the failure count it carries.
fn outcome(r: Result<User<LoggedIn>, LoginError>) -> (&'static str, u32) {
    match r {
        Ok(u) => ("in", u.failures()),
        Err(LoginError::WrongPassword(u)) => ("wrong", u.failures()),
        Err(LoginError::Locked(u)) => ("locked", u.failures()),
    }
}

fn wrong(r: Result<User<LoggedIn>, LoginError>) -> User<LoggedOut> {
    match r {
        Err(LoginError::WrongPassword(u)) => u,
        _ => panic!("expected WrongPassword"),
    }
}

#[test]
fn login_and_dashboard() {
    check!(r#"user "ada" / "pw", login with "pw""#, user("ada", "pw").login("pw").ok().map(|u| u.dashboard()), Some("dashboard:ada".to_string()));
}

#[test]
fn third_failure_locks() {
    check!(r#"three wrong passwords"#, outcome(wrong(wrong(user("ada", "pw").login("x")).login("y")).login("z")), ("locked", 3));
}

#[test]
fn success_resets_failures() {
    check!(r#"wrong, then right, then logout"#, wrong(user("ada", "pw").login("x")).login("pw").ok().map(|u| u.logout().failures()), Some(0));
}

#[test]
fn username_rules() {
    check!(r#""ada_1", "Ada", "adA", "ab", "1ab", "a-b""#, ["ada_1", "Ada", "adA", "ab", "1ab", "a-b"].map(|s| Username::parse(s).is_some()), [true, false, false, false, false, false]);
}

#[test]
fn no_shortcuts_to_a_username() {
    check!(r#"is Username Default? From<&str>?"#, (Probe::<Username>::DEFAULT, Probe::<Username>::FROM_STR_REF), (false, false));
}
