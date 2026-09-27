pub struct User {
    pub name: String,
    pub nickname: Option<String>,
}

pub fn display_name(user: &User) -> &str {
    user.nickname.as_deref().filter(|n| !n.is_empty()).unwrap_or(&user.name)
}

pub fn shout_nickname(user: &mut User) {
    if let Some(n) = user.nickname.as_mut() {
        n.make_ascii_uppercase();
    }
}
