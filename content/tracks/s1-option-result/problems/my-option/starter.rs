#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum MyOption<T> {
    Some(T),
    None,
}

impl<T> MyOption<T> {
    pub fn is_some(&self) -> bool { todo!() }
    pub fn is_none(&self) -> bool { todo!() }
    pub fn unwrap_or(self, default: T) -> T { todo!() }
    pub fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T { todo!() }
    pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyOption<U> { todo!() }
    pub fn and_then<U>(self, f: impl FnOnce(T) -> MyOption<U>) -> MyOption<U> { todo!() }
    pub fn or(self, other: MyOption<T>) -> MyOption<T> { todo!() }
    pub fn ok_or<E>(self, err: E) -> Result<T, E> { todo!() }
    pub fn filter(self, keep: impl FnOnce(&T) -> bool) -> MyOption<T> { todo!() }
    pub fn take(&mut self) -> MyOption<T> { todo!() }
}
