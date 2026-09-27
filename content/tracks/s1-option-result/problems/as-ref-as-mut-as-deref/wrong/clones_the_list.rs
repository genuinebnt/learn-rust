pub struct User {
    pub name: String,
    pub nickname: Option<String>,
    pub emails: Option<Vec<String>>,
}

/// The nickname if there is one, else the name.
pub fn display_name(user: &User) -> &str {
    user.nickname.as_deref().unwrap_or(&user.name)
}

/// The first email, if the user has any.
pub fn primary_email(user: &User) -> Option<&str> {
    user.emails.as_deref()?.first().map(String::as_str)
}

/// The name, then the nickname if any, then every email.
pub fn handles(user: &User) -> Vec<&str> {
    std::iter::once(user.name.as_str())
        .chain(user.nickname.as_deref())
        .chain(user.emails.iter().flatten().map(String::as_str))
        .collect()
}

/// Uppercases the nickname (ASCII only) in place.
pub fn shout_nickname(user: &mut User) {
    if let Some(n) = user.nickname.as_deref_mut() {
        n.make_ascii_uppercase();
    }
}

/// Appends `email`, creating the list if there is none.
pub fn add_email(user: &mut User, email: String) {
    let mut es = user.emails.clone().unwrap_or_default();
    es.push(email);
    user.emails = Some(es);
}
