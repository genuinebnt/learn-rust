Model an account so misuse doesn't compile. A `Username` can only come from `Username::parse` (3 to 16
characters: a lowercase ASCII letter, then lowercase letters, digits or `_`). A `User<S>` is in one of
three states, and each state has only the methods that make sense in it:

- `User<LoggedOut>`: `new`, and `login(pw)`. The right password returns a `User<LoggedIn>` and resets the
  failure count. A wrong one adds a failure and hands the user back in `LoginError::WrongPassword`; the
  **third failure in a row** hands it back as a `User<Locked>` in `LoginError::Locked`.
- `User<LoggedIn>`: `dashboard()` (`"dashboard:<name>"`), `change_password`, `logout`.
- `User<Locked>`: `unlock()`, back to logged out with no failures.
- Every state: `name()` and `failures()`.

There must be no other way to make a `Username`: no `Default`, no `From<&str>`.
