---
title: Parsing numbers from text
summary: str::parse and its errors, the "leading number" parse of C++'s stoi and stod, trimming, radix, and why a database cast of text to a number needs a policy.
minutes: 7
---
`CAST('42' AS INTEGER)`, `WHERE id = '42'`, the `42` in `INSERT ... VALUES (42)` as it comes out of the SQL text: databases constantly turn text into numbers, and the rules (white space, signs, trailing characters, overflow) have to be decided and applied everywhere.

## What `str::parse` does

```rust
"42".parse::<i32>()        // Ok(42)
"-7".parse::<i32>()        // Ok(-7)
"+7".parse::<i32>()        // Ok(7)
" 42".parse::<i32>()       // Err: leading space
"42 ".parse::<i32>()       // Err: trailing space
"12abc".parse::<i32>()     // Err(InvalidDigit)
"".parse::<i32>()          // Err(Empty)
"99999999999".parse::<i32>() // Err(PosOverflow)
```

Rust's parse is **strict**: the whole string must be a number. The error is a `ParseIntError` whose `kind()` is `Empty`, `InvalidDigit`, `PosOverflow`, `NegOverflow` or `Zero`: enough to tell "not a number" from "too big". `f64::from_str` accepts `"1e3"`, `"inf"`, `"NaN"`, `".5"`.

## What C++'s `std::stoi` does

`stoi` skips leading white space, accepts an optional sign and digits and **stops at the first character that is not part of the number**, ignoring the rest: `stoi("12abc")` is 12 and `stoi("abc")` throws `invalid_argument`. `stod` is the same for decimals (`"2.5e1x"` is 25).

BusTub's casts use these, so `CAST('12abc' AS INTEGER)` is 12 there. (PostgreSQL rejects it; both are defensible: the policy must be explicit.)

## Writing a "leading number" parse

Find the longest prefix that looks like a number, then hand *only that* to `parse`:

1. `trim_start()` the white space;
2. an optional `+`/`-`;
3. one or more digits (and for decimals: an optional `.` and digits, an optional `e`/`E` and a signed exponent);
4. if there were no digits, report "not a number"; else `parse` the prefix and map overflow to "out of range".

| tool | use |
|---|---|
| `str::trim`, `trim_start`, `trim_end` | white space |
| `strip_prefix("+")` | an optional prefix |
| `char::is_ascii_digit`, `to_digit(10)` | scanning digits |
| `i64::from_str_radix(s, 16)` | other bases |
| `str::parse::<T>()` | the strict conversion |
| `ParseIntError::kind()` | why it failed |

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::stoi(s)` (prefix parse; throws) | your own prefix scan + `parse` |
| `std::from_chars(first, last, value)` (no allocation, no locale) | `str::parse` (also locale-free) |
| `atoi("abc")` returns 0 silently | never: `parse` returns an `Err` |
| `strtol(s, &end, 10)` and checking `end` | the prefix scan returns where it stopped |

## In real code

### Using it: strict parse, its errors, and a leading-number parse

```rust test
use std::num::IntErrorKind;

/// The number at the start of `s`, like std::stoll: skips white space, takes a sign and digits, ignores the rest.
fn leading_int(s: &str) -> Result<i64, &'static str> {
    let s = s.trim_start();
    let end = s
        .char_indices()
        .take_while(|&(i, c)| c.is_ascii_digit() || (i == 0 && (c == '+' || c == '-')))
        .last()
        .map_or(0, |(i, c)| i + c.len_utf8());
    let prefix = &s[..end];
    if !prefix.chars().any(|c| c.is_ascii_digit()) {
        return Err("not a number");
    }
    prefix.parse::<i64>().map_err(|e| match e.kind() {
        IntErrorKind::PosOverflow | IntErrorKind::NegOverflow => "out of range",
        _ => "not a number",
    })
}

#[test]
fn strict_parse_and_its_error_kinds() {
    assert_eq!("42".parse::<i32>(), Ok(42));
    assert_eq!("+7".parse::<i32>(), Ok(7));
    assert!(" 42".parse::<i32>().is_err());
    assert!("12abc".parse::<i32>().is_err());
    assert_eq!("".parse::<i32>().unwrap_err().kind(), &IntErrorKind::Empty);
    assert_eq!("12x".parse::<i32>().unwrap_err().kind(), &IntErrorKind::InvalidDigit);
    assert_eq!("99999999999".parse::<i32>().unwrap_err().kind(), &IntErrorKind::PosOverflow);
    assert_eq!("-99999999999".parse::<i32>().unwrap_err().kind(), &IntErrorKind::NegOverflow);
    assert_eq!("1e3".parse::<f64>(), Ok(1000.0));
    assert_eq!(".5".parse::<f64>(), Ok(0.5));
    assert!("NaN".parse::<f64>().unwrap().is_nan());
    assert_eq!(i64::from_str_radix("ff", 16), Ok(255));
}

#[test]
fn the_leading_number_parse_matches_stoi() {
    assert_eq!(leading_int("32"), Ok(32));
    assert_eq!(leading_int("  -7"), Ok(-7));
    assert_eq!(leading_int("12abc"), Ok(12));
    assert_eq!(leading_int("+5 apples"), Ok(5));
    assert_eq!(leading_int("abc"), Err("not a number"));
    assert_eq!(leading_int(""), Err("not a number"));
    assert_eq!(leading_int("-"), Err("not a number"), "a sign alone has no digits");
    assert_eq!(leading_int("99999999999999999999"), Err("out of range"));
    assert_eq!(leading_int("1-2"), Ok(1), "the sign is only allowed at the start");
}
```

```rust test
#[test]
fn tools_for_scanning_text() {
    let s = "  x=12;y=-7 ";
    assert_eq!(s.trim(), "x=12;y=-7");
    let (k, v) = s.trim().split_once('=').unwrap();
    assert_eq!((k, v), ("x", "12;y=-7"));
    assert_eq!("+7".strip_prefix('+'), Some("7"));
    assert_eq!('7'.to_digit(10), Some(7));
    assert_eq!('f'.to_digit(16), Some(15));
    let digits: String = "a1b22c333".chars().filter(char::is_ascii_digit).collect();
    assert_eq!(digits, "122333");
    let numbers: Vec<i32> = "3,4,x,5".split(',').filter_map(|p| p.parse().ok()).collect();
    assert_eq!(numbers, vec![3, 4, 5]);
    assert_eq!("héllo".len(), 6, "len is bytes; slicing must land on character boundaries");
    assert_eq!("héllo".char_indices().nth(2), Some((3, 'l')));
}
```

### In the exercises

- **3a-02:** casting text to a number reads the leading number of the string (a sign, digits, for decimals a fraction and an exponent) and ignores the rest.
- **Module 3b:** the SQL front end gives you literals as text; the planner converts them with the same casts.

### Where it is used

- **Every config and CLI parser**: `clap`'s value parsing, `serde`'s number visitors, `toml`/`json` parsers (a JSON number is a scan followed by a `parse`).
- **Databases**: PostgreSQL's `int4in` rejects trailing garbage and reports "invalid input syntax for type integer"; SQLite's `CAST('12abc' AS INTEGER)` is 12 (like BusTub); MySQL gives 12 with a warning.
- **`std::from_chars` / `strtol`** in C and C++ are the same operation without exceptions.
