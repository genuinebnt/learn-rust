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
fn locked_then_unlocked() {
    let locked = match wrong(wrong(user("bob", "pw").login("1")).login("2")).login("3") {
        Err(LoginError::Locked(u)) => u,
        _ => panic!("expected Locked"),
    };
    check!(r#"three failures, then unlock"#, (locked.failures(), locked.unlock().failures()), (3, 0));
}

#[test]
fn unlocked_user_can_log_in() {
    let locked = match wrong(wrong(user("bob", "pw").login("1")).login("2")).login("3") {
        Err(LoginError::Locked(u)) => u,
        _ => panic!("expected Locked"),
    };
    let u = locked.unlock();
    check!(r#"lock, unlock, log in with the right password"#, u.login("pw").ok().map(|u| (u.dashboard(), u.failures())), Some(("dashboard:bob".to_string(), 0)));
}

#[test]
fn change_password() {
    let mut u = user("cyd", "pw").login("pw").ok().unwrap();
    u.change_password("new");
    let u = u.logout();
    check!(r#"log in, change to "new", log out, log in with old then new"#, outcome(wrong(u.login("pw")).login("new")), ("in", 0));
}

#[test]
fn failures_count_up() {
    check!(r#"two wrong passwords"#, wrong(wrong(user("ada", "pw").login("a")).login("b")).failures(), 2);
}

#[test]
fn password_is_case_sensitive() {
    check!(r#"password "PW", login "pw""#, outcome(user("ada", "PW").login("pw")), ("wrong", 1));
}

#[test]
fn name_in_every_state() {
    let u = user("dora", "p");
    check!(r#"name() while logged out and in"#, (u.name().as_str().to_string(), u.login("p").ok().map(|u| u.name().clone())), ("dora".to_string(), Username::parse("dora")));
}

#[test]
fn length_limits() {
    check!(r#"3, 16 and 17 characters"#, ["abc", "a234567890123456", "a2345678901234567"].map(|s| Username::parse(s).is_some()), [true, true, false]);
}

#[test]
fn non_ascii_rejected() {
    check!(r#""josé", "ünï", "abc ""#, ["josé", "ünï", "abc "].map(|s| Username::parse(s).is_some()), [false, false, false]);
}

#[test]
fn empty_and_underscore_start() {
    check!(r#""", "_ab", "a__""#, ["", "_ab", "a__"].map(|s| Username::parse(s).is_some()), [false, false, true]);
}

#[test]
fn zero_cost_states() {
    check!(r#"size_of User<LoggedOut>, User<LoggedIn>, User<Locked>"#, (std::mem::size_of::<User<LoggedIn>>(), std::mem::size_of::<User<Locked>>(), std::mem::size_of::<LoggedIn>()), (std::mem::size_of::<User<LoggedOut>>(), std::mem::size_of::<User<LoggedOut>>(), 0));
}

enum Any {
    Out(User<LoggedOut>),
    In(User<LoggedIn>),
    Lock(User<Locked>),
}

#[test]
fn random_vs_state_model() {
    let mut rng = anneal_prelude::Rng::new(4515);
    for _ in 0..300 {
        let mut acct = Any::Out(user("eve", "a"));
        // model: 0 = out, 1 = in, 2 = locked
        let (mut state, mut failures, mut pw) = (0, 0u32, "a".to_string());
        let mut log = Vec::new();
        for _ in 0..rng.below(12) {
            let guess = rng.string(1, "ab");
            let fresh = rng.string(1, "ab");
            acct = match acct {
                Any::Out(u) => {
                    log.push(format!("login({guess})"));
                    if guess == pw {
                        state = 1;
                        failures = 0;
                    } else {
                        failures += 1;
                        state = if failures >= 3 { 2 } else { 0 };
                    }
                    match u.login(&guess) {
                        Ok(u) => Any::In(u),
                        Err(LoginError::WrongPassword(u)) => Any::Out(u),
                        Err(LoginError::Locked(u)) => Any::Lock(u),
                    }
                }
                Any::In(mut u) => {
                    if rng.bool() {
                        log.push(format!("change_password({fresh})"));
                        u.change_password(&fresh);
                        pw = fresh;
                        Any::In(u)
                    } else {
                        log.push("logout".to_string());
                        state = 0;
                        Any::Out(u.logout())
                    }
                }
                Any::Lock(u) => {
                    log.push("unlock".to_string());
                    state = 0;
                    failures = 0;
                    Any::Out(u.unlock())
                }
            };
            let got = match &acct {
                Any::Out(u) => (0, u.failures()),
                Any::In(u) => (1, u.failures()),
                Any::Lock(u) => (2, u.failures()),
            };
            check!(log.join(", "), got, (state, failures));
        }
    }
}

#[test]
fn random_usernames_vs_rules() {
    let mut rng = anneal_prelude::Rng::new(4516);
    for _ in 0..400 {
        let n = rng.below(19);
        let s = rng.string(n, "az_09Aé-");
        let b = s.as_bytes();
        let want = (3..=16).contains(&b.len())
            && b[0].is_ascii_lowercase()
            && b.iter().all(|&c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == b'_');
        check!(format!("{s:?}"), Username::parse(&s).map(|u| u.as_str().to_string()), want.then(|| s.clone()));
    }
}
