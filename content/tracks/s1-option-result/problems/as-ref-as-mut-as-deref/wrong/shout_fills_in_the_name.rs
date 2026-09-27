pub struct User {
    pub name: String,
    pub nickname: Option<String>,
}

pub fn display_name(user: &User) -> &str {
    user.nickname.as_deref().unwrap_or(&user.name)
}

pub fn shout_nickname(user: &mut User) {
    let n = user.nickname.get_or_insert_with(|| user.name.clone());
    n.make_ascii_uppercase();
}
