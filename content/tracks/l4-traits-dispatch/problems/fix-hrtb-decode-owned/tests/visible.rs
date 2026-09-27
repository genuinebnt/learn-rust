use solution::*;

#[test]
fn normalized_numbers() {
    check!(r#"decode_normalized::<u32>(" 42 \nx\n7")"#, decode_normalized::<u32>(" 42 \nx\n7"), vec![Some(42), None, Some(7)]);
}

#[test]
fn normalized_strings() {
    check!(r#"decode_normalized::<String>("  HeLLo ")"#, decode_normalized::<String>("  HeLLo "), vec![Some("hello".to_string())]);
}

#[test]
fn normalized_lists() {
    check!(r#"decode_normalized::<Vec<u32>>("1,2\n3,x")"#, decode_normalized::<Vec<u32>>("1,2\n3,x"), vec![Some(vec![1, 2]), None]);
}

#[test]
fn borrowed_lines_point_into_text() {
    let text = String::from("ab\ncd");
    let got = decode_lines::<&str>(&text);
    check!(r#"decode_lines::<&str>("ab\ncd")"#, std::ptr::eq(got[1].unwrap().as_ptr(), text[3..].as_ptr()), true);
}

#[test]
fn decode_owned_bound() {
    // With only `T: DecodeOwned`, T must decode from a local String.
    fn from_temp<T: DecodeOwned>(s: &str) -> Option<T> {
        let tmp = format!("{s}0");
        T::decode(&tmp)
    }
    check!("from_temp::<u32>(\"1\")", from_temp::<u32>("1"), Some(10));
    check!("from_temp::<Vec<u32>>(\"5,\")", from_temp::<Vec<u32>>("5,"), Some(vec![5, 0]));
}
