use std::marker::PhantomData;

/// 3 to 16 characters: a lowercase ASCII letter, then lowercase letters, digits or `_`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Username(String);

pub struct LoggedOut;
pub struct LoggedIn;
pub struct Locked;

pub struct User<S> {
    name: Username,
    password: String,
    failures: u32,
    state: PhantomData<S>,
}

/// A failed login hands the user back, in whichever state it ended up.
pub enum LoginError {
    WrongPassword(User<LoggedOut>),
    Locked(User<Locked>),
}

impl Username {
    pub fn parse(s: &str) -> Option<Username> {
        todo!()
    }

    pub fn as_str(&self) -> &str {
        todo!()
    }
}

impl<S> User<S> {
    pub fn name(&self) -> &Username {
        todo!()
    }

    pub fn failures(&self) -> u32 {
        todo!()
    }
}

impl User<LoggedOut> {
    pub fn new(name: Username, password: &str) -> Self {
        todo!()
    }

    /// Right password: logged in, failures reset. Wrong: one more failure; the third in a row locks the account.
    pub fn login(self, password: &str) -> Result<User<LoggedIn>, LoginError> {
        todo!()
    }
}

impl User<LoggedIn> {
    pub fn dashboard(&self) -> String {
        todo!()
    }

    pub fn change_password(&mut self, new: &str) {
        todo!()
    }

    pub fn logout(self) -> User<LoggedOut> {
        todo!()
    }
}

impl User<Locked> {
    /// An admin unlock: back to logged out with no failures.
    pub fn unlock(self) -> User<LoggedOut> {
        todo!()
    }
}
