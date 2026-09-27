use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub enum TemplateError {
    Unknown(String),
    Unclosed(usize),
    StrayBrace(usize),
}

pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
    let chars: Vec<char> = template.chars().collect();
    let mut out = String::with_capacity(template.len());
    let mut i = 0;
    while i < chars.len() {
        match chars[i] {
            '{' if chars.get(i + 1) == Some(&'{') => {
                out.push('{');
                i += 2;
            }
            '{' => {
                let close = (i..chars.len()).find(|&j| chars[j] == '}').ok_or(TemplateError::Unclosed(i))?;
                let name: String = chars[i + 1..close].iter().collect();
                let value = vars.get(name.as_str()).ok_or(TemplateError::Unknown(name.clone()))?;
                out.push_str(value);
                i = close + 1;
            }
            '}' if chars.get(i + 1) == Some(&'}') => {
                out.push('}');
                i += 2;
            }
            '}' => return Err(TemplateError::StrayBrace(i)),
            c => {
                out.push(c);
                i += 1;
            }
        }
    }
    Ok(out)
}
