#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum MyOption<T> {
    Some(T),
    None,
}

impl<T> MyOption<T> {
    pub fn is_some_and(self, f: impl FnOnce(T) -> bool) -> bool {
        match self {
            MyOption::Some(v) => f(v),
            MyOption::None => false,
        }
    }
    pub fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T {
        match self {
            MyOption::Some(v) => v,
            MyOption::None => f(),
        }
    }
    pub fn unwrap_or_default(self) -> T
    where
        T: Default,
    {
        match self {
            MyOption::Some(v) => v,
            MyOption::None => T::default(),
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
    pub fn and<U>(self, other: MyOption<U>) -> MyOption<U> {
        match self {
            MyOption::Some(_) => other,
            MyOption::None => MyOption::None,
        }
    }
    pub fn or_else(self, f: impl FnOnce() -> MyOption<T>) -> MyOption<T> {
        let other = f();
        match self {
            MyOption::Some(v) => MyOption::Some(v),
            MyOption::None => other,
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
    pub fn iter(&self) -> Iter<'_, T> {
        Iter {
            inner: match self {
                MyOption::Some(v) => MyOption::Some(v),
                MyOption::None => MyOption::None,
            },
        }
    }
}

/// Yields a reference to the value, at most once.
pub struct Iter<'a, T> {
    inner: MyOption<&'a T>,
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<&'a T> {
        match self.inner.take() {
            MyOption::Some(v) => Some(v),
            MyOption::None => None,
        }
    }
}
