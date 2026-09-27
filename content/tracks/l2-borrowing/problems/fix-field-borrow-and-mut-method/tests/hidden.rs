use solution::*;

#[test]
fn twice() {
    check!(r#"append "x" then "y""#, { let mut e = Editor { text: String::new(), history: vec![] }; e.append("x"); e.append("y"); e.history }, vec![String::new(), "x".to_string()]);
}
