#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum MyOption<T> {
    Some(T),
    None,
}

impl<T> MyOption<T> {
    pub fn as_ref(&self) -> MyOption<&T> {
        match self {
            MyOption::Some(v) => MyOption::Some(v),
            MyOption::None => MyOption::None,
        }
    }
    pub fn as_mut(&mut self) -> MyOption<&mut T> {
        match self {
            MyOption::Some(v) => MyOption::Some(v),
            MyOption::None => MyOption::None,
        }
    }
    pub fn insert(&mut self, value: T) -> &mut T {
        *self = MyOption::Some(value);
        match self {
            MyOption::Some(v) => v,
            MyOption::None => unreachable!(),
        }
    }
    pub fn replace(&mut self, value: T) -> MyOption<T> {
        std::mem::replace(self, MyOption::Some(value))
    }
    pub fn get_or_insert_with(&mut self, f: impl FnOnce() -> T) -> &mut T {
        if let MyOption::None = self {
            *self = MyOption::Some(f());
        }
        match self {
            MyOption::Some(v) => v,
            MyOption::None => unreachable!(),
        }
    }
    pub fn zip<U>(self, other: MyOption<U>) -> MyOption<(T, U)> {
        match (self, other) {
            (MyOption::Some(a), MyOption::Some(b)) => MyOption::Some((a, b)),
            _ => MyOption::None,
        }
    }
    pub fn inspect(self, f: impl FnOnce(&T)) -> MyOption<T> {
        if let MyOption::Some(v) = &self {
            f(v);
        }
        self
    }
    pub fn map_or_else<U>(self, default: impl FnOnce() -> U, f: impl FnOnce(T) -> U) -> U {
        match self {
            MyOption::Some(v) => f(v),
            MyOption::None => default(),
        }
    }
}

impl<T> MyOption<MyOption<T>> {
    pub fn flatten(self) -> MyOption<T> {
        match self {
            MyOption::Some(inner) => inner,
            MyOption::None => MyOption::None,
        }
    }
}

impl<T: Copy> MyOption<&T> {
    pub fn copied(self) -> MyOption<T> {
        match self {
            MyOption::Some(&v) => MyOption::Some(v),
            MyOption::None => MyOption::None,
        }
    }
}
