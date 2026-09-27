use std::collections::HashMap;

pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
    let v = cfg.get("port").map(String::as_str).unwrap_or("0");
    v.parse().map_err(|_| format!("invalid port: {v}"))
}
