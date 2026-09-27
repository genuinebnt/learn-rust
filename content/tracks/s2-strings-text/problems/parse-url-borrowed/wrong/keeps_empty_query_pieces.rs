#[derive(Debug, PartialEq)]
pub struct Url<'a> {
    pub scheme: &'a str,
    pub host: &'a str,
    pub port: Option<u16>,
    pub path: &'a str,
    pub query: Vec<(&'a str, &'a str)>,
}

pub fn parse_url(s: &str) -> Option<Url<'_>> {
    let (scheme, rest) = s.split_once("://")?;
    let (rest, query) = match rest.split_once('?') {
        Some((r, q)) => (r, Some(q)),
        None => (rest, None),
    };
    let (authority, path) = match rest.find('/') {
        Some(i) => rest.split_at(i),
        None => (rest, "/"),
    };
    let (host, port) = match authority.split_once(':') {
        Some((h, p)) => (h, Some(p.parse().ok()?)),
        None => (authority, None),
    };
    if scheme.is_empty() || host.is_empty() {
        return None;
    }
    let query = match query {
        Some(q) => q.split('&').map(|kv| kv.split_once('=').unwrap_or((kv, ""))).collect(),
        None => Vec::new(),
    };
    Some(Url { scheme, host, port, path, query })
}
