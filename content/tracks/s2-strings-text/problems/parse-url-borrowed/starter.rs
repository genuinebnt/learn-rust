#[derive(Debug, PartialEq)]
pub struct Url<'a> {
    pub scheme: &'a str,
    pub host: &'a str,
    pub port: Option<u16>,
    pub path: &'a str,
    pub query: Vec<(&'a str, &'a str)>,
}

pub fn parse_url(s: &str) -> Option<Url<'_>> {
    todo!()
}
