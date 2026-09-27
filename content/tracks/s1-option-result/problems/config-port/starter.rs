use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq)]
pub struct Server {
    pub host: String,
    pub port: u16,
    pub tls: bool,
    pub name: String,
    pub workers: usize,
}

pub fn server(cfg: &HashMap<String, String>) -> Result<Server, String> {
    todo!()
}
