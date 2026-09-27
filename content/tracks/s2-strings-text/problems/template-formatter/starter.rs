use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub enum TemplateError {
    Unknown(String),
    Unclosed(usize),
    StrayBrace(usize),
}

pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
    todo!()
}
