#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum MyOption<T> {
    Some(T),
    None,
}

impl<T> MyOption<T> {
    pub fn is_some(&self) -> bool {
        matches!(self, MyOption::Some(_))
    }
    pub fn is_none(&self) -> bool {
        !self.is_some()
    }
    pub fn unwrap_or(self, default: T) -> T {
        match self {
            MyOption::Some(v) => v,
            MyOption::None => default,
        }
    }
    pub fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T {
        let d = f();
        match self {
            MyOption::Some(v) => v,
            MyOption::None => d,
        }
    }
    pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyOption<U> {
        match self {
            MyOption::Some(v) => MyOption::Some(f(v)),
            MyOption::None => MyOption::None,
        }
    }
    pub fn and_then<U>(self, f: impl FnOnce(T) -> MyOption<U>) -> MyOption<U> {
        match self {
            MyOption::Some(v) => f(v),
            MyOption::None => MyOption::None,
        }
    }
    pub fn or(self, other: MyOption<T>) -> MyOption<T> {
        match self {
            MyOption::Some(_) => self,
            MyOption::None => other,
        }
    }
    pub fn ok_or<E>(self, err: E) -> Result<T, E> {
        match self {
            MyOption::Some(v) => Ok(v),
            MyOption::None => Err(err),
        }
    }
    pub fn filter(self, keep: impl FnOnce(&T) -> bool) -> MyOption<T> {
        match self {
            MyOption::Some(v) if keep(&v) => MyOption::Some(v),
            _ => MyOption::None,
        }
    }
    pub fn take(&mut self) -> MyOption<T> {
        std::mem::replace(self, MyOption::None)
    }
}
