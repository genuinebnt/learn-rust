pub struct User {
    pub name: String,
    pub nickname: Option<String>,
    pub emails: Option<Vec<String>>,
}

/// The nickname if there is one, else the name.
pub fn display_name(user: &User) -> &str {
    todo!()
}

/// The first email, if the user has any.
pub fn primary_email(user: &User) -> Option<&str> {
    todo!()
}

/// The name, then the nickname if any, then every email.
pub fn handles(user: &User) -> Vec<&str> {
    todo!()
}

/// Uppercases the nickname (ASCII only) in place.
pub fn shout_nickname(user: &mut User) {
    todo!()
}

/// Appends `email`, creating the list if there is none.
pub fn add_email(user: &mut User, email: String) {
    todo!()
}
