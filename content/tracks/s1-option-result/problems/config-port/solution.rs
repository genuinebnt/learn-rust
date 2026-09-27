use std::collections::HashMap;

pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
    cfg.get("port")
        .ok_or_else(|| "missing port".to_string())
        .and_then(|v| v.parse().map_err(|_| format!("invalid port: {v}")))
}
