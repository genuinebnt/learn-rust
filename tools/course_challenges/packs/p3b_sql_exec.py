from _c import C
M3D, M3E = "15-expressions-and-the-sql-front-end", "16-access-method-executors"
CH = []

CH.append(C("3d-c1", M3D, "90-challenge-a-hardened-lexer", "build", "Challenge: a hardened lexer", "medium", "stages_3d::s3d_c1",
  ["tokenising SQL with quoted strings, quoted identifiers and comments","reporting a lexical error with its byte position"],
  ["lexers-and-precedence-climbing","errors-as-values-with-result"],
  "`tokenize` in `src/sql/mini_lexer.rs`: split SQL text into tokens. Identifiers (`[A-Za-z_][A-Za-z0-9_]*`, kept as written), integers, single-quoted strings in which `''` is one quote, double-quoted identifiers in which `\"\"` is one quote, the symbols `( ) , ; * + - / = < > .` and the two-character `<= >= <> !=`, and whitespace and comments (`-- to end of line`, `/* ... */`) which produce **no** tokens. Errors carry the byte position where the bad token starts.",
  "A lexer is the first thing a hostile string meets. The details that matter are exactly the ones a happy-path lexer skips: a quote inside a string, a comment inside a string (not a comment), a comment that never ends, a character that belongs to no token, a multi-byte character. A good lexer says where the problem is and never panics.",
  ["`tokenize(sql)` returns `Ok(Vec<Tok>)` or `Err(LexError { pos, kind })`.","`''` inside a string is a quote character; the token holds the unescaped text. `\"\"` likewise in a quoted identifier.","`-- ...` runs to the end of the line; `/* ... */` does not nest. `--` and `/*` inside a string or quoted identifier are just text.","Kinds: `UnterminatedString`, `UnterminatedIdent`, `UnterminatedComment` (position of the opening), `BadChar` (position of the character), `IntegerOverflow`."],
  ["Every error position is a byte offset of a character boundary in the input.","The function never panics, on any input.","Tokens appear in the order of the input."],
  ["Inserting whitespace or a comment between tokens never changes the tokens.","Concatenating the text of a string token (re-escaped) reproduces the literal.","Cutting a valid statement in the middle of a string or comment gives the matching `Unterminated...` error."],
  ["SELECT 'it''s' -> Ident(SELECT) Str(it's)","a<=b -> Ident(a) Sym(<=) Ident(b)","'abc -> UnterminatedString at 0","/* x -> UnterminatedComment at 0"],
  ["Each token class; comments and quotes inside strings.","Each error kind and its position, including after multi-byte characters.","A property: random text never panics and error positions are character boundaries."],
  src=("src/sql/mini_lexer.rs", '''
//! A small SQL lexer.

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum Tok {
    Ident(String),
    QuotedIdent(String),
    Int(i64),
    Str(String),
    Sym(String),
}

#[derive(Debug, PartialEq, Eq)]
pub enum LexErrorKind {
    UnterminatedString,
    UnterminatedIdent,
    UnterminatedComment,
    BadChar,
    IntegerOverflow,
}

#[derive(Debug, PartialEq, Eq)]
pub struct LexError {
    pub pos: usize,
    pub kind: LexErrorKind,
}

pub fn tokenize(sql: &str) -> Result<Vec<Tok>, LexError> {
    // @begin 3d-c1
    let b = sql.as_bytes();
    let mut toks = Vec::new();
    let mut i = 0;
    let err = |pos, kind| Err(LexError { pos, kind });
    while i < b.len() {
        let c = b[i];
        if c.is_ascii_whitespace() {
            i += 1;
        } else if c == b'-' && b.get(i + 1) == Some(&b'-') {
            while i < b.len() && b[i] != b'\\n' {
                i += 1;
            }
        } else if c == b'/' && b.get(i + 1) == Some(&b'*') {
            match sql[i + 2..].find("*/") {
                Some(end) => i += 2 + end + 2,
                None => return err(i, LexErrorKind::UnterminatedComment),
            }
        } else if c == b'\\'' || c == b'"' {
            let start = i;
            let mut s = String::new();
            i += 1;
            loop {
                match sql[i..].find(c as char) {
                    None => return err(start, if c == b'\\'' { LexErrorKind::UnterminatedString } else { LexErrorKind::UnterminatedIdent }),
                    Some(at) => {
                        s.push_str(&sql[i..i + at]);
                        i += at + 1;
                        if b.get(i) == Some(&c) {
                            s.push(c as char);
                            i += 1;
                        } else {
                            break;
                        }
                    }
                }
            }
            toks.push(if c == b'\\'' { Tok::Str(s) } else { Tok::QuotedIdent(s) });
        } else if c.is_ascii_digit() {
            let start = i;
            while i < b.len() && b[i].is_ascii_digit() {
                i += 1;
            }
            match sql[start..i].parse::<i64>() {
                Ok(v) => toks.push(Tok::Int(v)),
                Err(_) => return err(start, LexErrorKind::IntegerOverflow),
            }
        } else if c.is_ascii_alphabetic() || c == b'_' {
            let start = i;
            while i < b.len() && (b[i].is_ascii_alphanumeric() || b[i] == b'_') {
                i += 1;
            }
            toks.push(Tok::Ident(sql[start..i].to_owned()));
        } else if let Some(two) = sql.get(i..i + 2).filter(|t| matches!(*t, "<=" | ">=" | "<>" | "!=")) {
            toks.push(Tok::Sym(two.to_owned()));
            i += 2;
        } else if b"(),;*+-/=<>.".contains(&c) {
            toks.push(Tok::Sym((c as char).to_string()));
            i += 1;
        } else {
            return err(i, LexErrorKind::BadChar);
        }
    }
    Ok(toks)
    //~ todo!("3d-c1: scan the bytes; strings and quoted identifiers with doubled quotes; comments; numbers; identifiers; symbols")
    // @end
}
'''),
  test=("tests/stages_3d.rs", '''
use bustub::sql::mini_lexer::{tokenize, LexError, LexErrorKind::*, Tok};

fn id(s: &str) -> Tok {
    Tok::Ident(s.to_owned())
}
fn sym(s: &str) -> Tok {
    Tok::Sym(s.to_owned())
}

#[test]
fn s3d_c1_identifiers_numbers_symbols_and_two_character_operators() {
    assert_eq!(tokenize("a<=b").unwrap(), vec![id("a"), sym("<="), id("b")]);
    assert_eq!(tokenize("t.x <> 12").unwrap(), vec![id("t"), sym("."), id("x"), sym("<>"), Tok::Int(12)]);
    assert_eq!(tokenize("(a,b);").unwrap(), vec![sym("("), id("a"), sym(","), id("b"), sym(")"), sym(";")]);
    assert_eq!(tokenize("a!=b").unwrap()[1], sym("!="));
}

#[test]
fn s3d_c1_a_doubled_quote_is_one_quote() {
    assert_eq!(tokenize("'it''s'").unwrap(), vec![Tok::Str("it's".into())]);
    assert_eq!(tokenize("\\"a\\"\\"b\\"").unwrap(), vec![Tok::QuotedIdent("a\\"b".into())]);
    assert_eq!(tokenize("''").unwrap(), vec![Tok::Str(String::new())]);
    assert_eq!(tokenize(&"'".repeat(4)).unwrap(), vec![Tok::Str("'".into())]);
}

#[test]
fn s3d_c1_comments_produce_no_tokens_and_are_not_comments_inside_strings() {
    assert_eq!(tokenize("a -- hi\\nb /* x */ c").unwrap(), vec![id("a"), id("b"), id("c")]);
    assert_eq!(tokenize("'-- not a comment'").unwrap(), vec![Tok::Str("-- not a comment".into())]);
    assert_eq!(tokenize("'/* nor this */'").unwrap(), vec![Tok::Str("/* nor this */".into())]);
    assert_eq!(tokenize("a--b").unwrap(), vec![id("a")]);
}

#[test]
fn s3d_c1_errors_carry_the_byte_position() {
    assert_eq!(tokenize("x 'abc"), Err(LexError { pos: 2, kind: UnterminatedString }));
    assert_eq!(tokenize("x \\"abc"), Err(LexError { pos: 2, kind: UnterminatedIdent }));
    assert_eq!(tokenize("a /* x"), Err(LexError { pos: 2, kind: UnterminatedComment }));
    assert_eq!(tokenize("a # b"), Err(LexError { pos: 2, kind: BadChar }));
    assert_eq!(tokenize("99999999999999999999"), Err(LexError { pos: 0, kind: IntegerOverflow }));
    assert_eq!(tokenize("é"), Err(LexError { pos: 0, kind: BadChar }), "a multi-byte character is one bad character, at its first byte");
    assert_eq!(tokenize("'é' é"), Err(LexError { pos: 5, kind: BadChar }), "positions count bytes");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: never panics, and an error position is a character boundary inside the input.
    #[test]
    fn s3d_c1_property_any_text_is_handled(s in "[ -~\\\\n\\\\té]{0,30}") {
        if let Err(e) = tokenize(&s) {
            prop_assert!(e.pos < s.len() || s.is_empty(), "position {} out of range for {:?}", e.pos, s);
            prop_assert!(s.is_char_boundary(e.pos));
        }
    }

    /// Property: whitespace and comments between tokens change nothing.
    #[test]
    fn s3d_c1_property_whitespace_and_comments_are_invisible(words in proptest::collection::vec("[a-z]{1,4}|[0-9]{1,3}|<=|,", 1..8), gap in prop_oneof![Just(" "), Just("  \\n"), Just(" /* c */ "), Just(" -- c\\n")]) {
        let plain = words.join(" ");
        let spaced = words.join(gap);
        prop_assert_eq!(tokenize(&plain), tokenize(&spaced));
    }
}
''')))

CH.append(C("3d-c2", M3D, "91-challenge-printing-expressions", "build", "Challenge: printing expressions", "medium", "stages_3d::s3d_c2",
  ["printing a tree with only the parentheses it needs","precedence and associativity, from the printing side"],
  ["lexers-and-precedence-climbing","expression-trees"],
  "`print_expr` in `src/sql/mini_expr.rs`: print an arithmetic expression tree as text with **as few parentheses as possible**, such that parsing the text (a parser is given) gives the same tree back. `+ -` bind weaker than `* /`, all four are left-associative, unary minus binds tightest.",
  "`EXPLAIN`, error messages, view definitions and logged plans all print expressions, and a printer that parenthesises everything is unreadable while one that parenthesises too little changes the meaning. Knowing exactly when a parenthesis is needed is the same knowledge as writing the parser.",
  ["`Expr` is `Num(i64)`, `Neg(Box<Expr>)` or `Bin(Box<Expr>, Op, Box<Expr>)` with `Op` one of `+ - * /`.","Print a child in parentheses exactly when needed: a child of lower precedence than its parent; or of the **same** precedence on the **right** of a left-associative operator; or a `Bin` under `Neg`; a negative number on the right of an operator needs none beyond the `-` sign, but `Neg(Num(3))` prints `-3`.","Operators are printed with one space on each side."],
  ["`parse(print(e)) == Some(e)` for every tree.","The printed text has no pair of parentheses that could be removed without changing the parse."],
  ["Wrapping any subtree in redundant parentheses is never produced.","The number of parentheses pairs is the same for trees that differ only in the numbers.","`print` is deterministic and total."],
  ["Bin(1 - Bin(2 - 3)) -> 1 - (2 - 3)","Bin(Bin(1 - 2) - 3) -> 1 - 2 - 3","Bin(1 + Bin(2 * 3)) -> 1 + 2 * 3","Neg(Bin(1 + 2)) -> -(1 + 2)"],
  ["Parentheses on the right and the left, by precedence.","Negation.","A property: round trip and minimality over random trees."],
  src=("src/sql/mini_expr.rs", '''
//! A tiny arithmetic expression language: the tree, a parser (given) and a printer (yours).

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Expr {
    Num(i64),
    Neg(Box<Expr>),
    Bin(Box<Expr>, Op, Box<Expr>),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Op {
    Add,
    Sub,
    Mul,
    Div,
}

impl Op {
    pub fn prec(self) -> u8 {
        match self {
            Op::Add | Op::Sub => 1,
            Op::Mul | Op::Div => 2,
        }
    }

    pub fn symbol(self) -> char {
        match self {
            Op::Add => '+',
            Op::Sub => '-',
            Op::Mul => '*',
            Op::Div => '/',
        }
    }
}

/// Prints `e` with the fewest parentheses that keep its meaning.
pub fn print_expr(e: &Expr) -> String {
    // @begin 3d-c2
    fn go(e: &Expr, parent: Option<(u8, bool)>) -> String {
        // `parent` is (precedence, is_right_operand) of the enclosing binary operator
        match e {
            Expr::Num(n) => n.to_string(),
            Expr::Neg(inner) => {
                let s = match **inner {
                    Expr::Bin(..) => format!("-({})", go(inner, None)),
                    _ => format!("-{}", go(inner, None)),
                };
                s
            }
            Expr::Bin(l, op, r) => {
                let text = format!("{} {} {}", go(l, Some((op.prec(), false))), op.symbol(), go(r, Some((op.prec(), true))));
                match parent {
                    Some((p, right)) if op.prec() < p || (op.prec() == p && right) => format!("({text})"),
                    _ => text,
                }
            }
        }
    }
    go(e, None)
    //~ todo!("3d-c2: print children, parenthesising by precedence and associativity")
    // @end
}

/// Parses text into a tree (precedence climbing). Given code; the printer above must agree with it.
pub fn parse(s: &str) -> Option<Expr> {
    let toks: Vec<String> = {
        let mut v = Vec::new();
        let mut cur = String::new();
        for c in s.chars() {
            if c.is_ascii_digit() {
                cur.push(c);
            } else {
                if !cur.is_empty() {
                    v.push(std::mem::take(&mut cur));
                }
                if !c.is_whitespace() {
                    v.push(c.to_string());
                }
            }
        }
        if !cur.is_empty() {
            v.push(cur);
        }
        v
    };
    fn atom(t: &[String], i: &mut usize) -> Option<Expr> {
        let tok = t.get(*i)?;
        *i += 1;
        if tok == "(" {
            let e = expr(t, i, 0)?;
            if t.get(*i)? != ")" {
                return None;
            }
            *i += 1;
            Some(e)
        } else if tok == "-" {
            Some(Expr::Neg(Box::new(atom(t, i)?)))
        } else {
            tok.parse::<i64>().ok().map(Expr::Num)
        }
    }
    fn expr(t: &[String], i: &mut usize, min: u8) -> Option<Expr> {
        let mut lhs = atom(t, i)?;
        loop {
            let op = match t.get(*i).map(String::as_str) {
                Some("+") => Op::Add,
                Some("-") => Op::Sub,
                Some("*") => Op::Mul,
                Some("/") => Op::Div,
                _ => return Some(lhs),
            };
            if op.prec() < min.max(1) {
                return Some(lhs);
            }
            *i += 1;
            let rhs = expr(t, i, op.prec() + 1)?;
            lhs = Expr::Bin(Box::new(lhs), op, Box::new(rhs));
        }
    }
    let mut i = 0;
    let e = expr(&toks, &mut i, 0)?;
    if i == toks.len() {
        Some(e)
    } else {
        None
    }
}
'''),
  test=("tests/stages_3d.rs", '''
use bustub::sql::mini_expr::{parse, print_expr, Expr, Op};

fn n(v: i64) -> Box<Expr> {
    Box::new(Expr::Num(v))
}
fn bin(l: Box<Expr>, op: Op, r: Box<Expr>) -> Box<Expr> {
    Box::new(Expr::Bin(l, op, r))
}

#[test]
fn s3d_c2_a_right_operand_of_the_same_precedence_needs_parentheses() {
    assert_eq!(print_expr(&bin(n(1), Op::Sub, bin(n(2), Op::Sub, n(3)))), "1 - (2 - 3)");
    assert_eq!(print_expr(&bin(bin(n(1), Op::Sub, n(2)), Op::Sub, n(3))), "1 - 2 - 3");
    assert_eq!(print_expr(&bin(n(8), Op::Div, bin(n(4), Op::Mul, n(2)))), "8 / (4 * 2)");
}

#[test]
fn s3d_c2_a_stronger_child_needs_none_and_a_weaker_one_does() {
    assert_eq!(print_expr(&bin(n(1), Op::Add, bin(n(2), Op::Mul, n(3)))), "1 + 2 * 3");
    assert_eq!(print_expr(&bin(bin(n(1), Op::Add, n(2)), Op::Mul, n(3))), "(1 + 2) * 3");
}

#[test]
fn s3d_c2_negation() {
    assert_eq!(print_expr(&Expr::Neg(n(3))), "-3");
    assert_eq!(print_expr(&Expr::Neg(bin(n(1), Op::Add, n(2)))), "-(1 + 2)");
    assert_eq!(print_expr(&bin(n(1), Op::Sub, Box::new(Expr::Neg(n(2))))), "1 - -2");
}

fn arb_expr() -> impl Strategy<Value = Expr> {
    let leaf = (0i64..20).prop_map(Expr::Num);
    leaf.prop_recursive(4, 24, 2, |inner| {
        prop_oneof![
            inner.clone().prop_map(|e| Expr::Neg(Box::new(e))),
            (inner.clone(), prop_oneof![Just(Op::Add), Just(Op::Sub), Just(Op::Mul), Just(Op::Div)], inner).prop_map(|(l, o, r)| Expr::Bin(Box::new(l), o, Box::new(r))),
        ]
    })
}

#[test]
fn s3d_c2_redundant_parentheses_are_dropped_and_needed_ones_kept() {
    for (src, want) in [("(1 + 2) + 3", "1 + 2 + 3"), ("1 + (2 * 3)", "1 + 2 * 3"), ("1 - (2 + 3)", "1 - (2 + 3)"), ("((7))", "7")] {
        assert_eq!(print_expr(&parse(src).unwrap()), want, "{src}");
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: parsing the printed text gives the tree back, and no pair of parentheses can be removed.
    #[test]
    fn s3d_c2_property_round_trip_with_the_fewest_parentheses(e in arb_expr()) {
        let text = print_expr(&e);
        prop_assert_eq!(parse(&text), Some(e.clone()), "text was {:?}", text);
        // try removing each matching pair: the parse must change
        let chars: Vec<char> = text.chars().collect();
        let mut stack = Vec::new();
        for (i, &c) in chars.iter().enumerate() {
            if c == '(' { stack.push(i); }
            if c == ')' {
                let open = stack.pop().unwrap();
                let without: String = chars.iter().enumerate().filter(|&(j, _)| j != open && j != i).map(|(_, c)| *c).collect();
                prop_assert_ne!(parse(&without), Some(e.clone()), "the parentheses at {} and {} of {:?} are redundant", open, i, text);
            }
        }
    }
}
''')))

CH.append(C("3d-c3", M3D, "92-challenge-the-subtraction-that-leans-right", "debug", "Challenge: the subtraction that leans right", "easy", "stages_3d::s3d_c3",
  ["finding an associativity bug in a precedence-climbing parser","reading a wrong tree shape from a failing evaluation"],
  ["lexers-and-precedence-climbing","expression-trees","property-testing-and-fuzzing"],
  "`src/sql/mini_parse.rs` is a precedence-climbing parser for `+ - * /` over integers. It gets `2 + 3 * 4` right, and `10 - 4 - 3` wrong. Find the bug and fix it.",
  "Left associativity is one `+ 1` in a precedence climber, and forgetting it produces a parser that passes every test with a single operator and silently mis-evaluates every long chain of subtractions and divisions. The tree is the output of the front end; a wrong shape here is a wrong query result there.",
  ["`parse_and_eval(text)` parses and evaluates with integer arithmetic (division truncates toward zero; `None` on a syntax error or division by zero).","`*` and `/` bind tighter than `+` and `-`; all four are **left**-associative; parentheses group."],
  ["The result equals evaluating the expression with the usual rules of arithmetic.","The parser consumes the whole input or fails."],
  ["Wrapping any left chain in parentheses from the left does not change the value.","`a - b - c == (a - b) - c` and `a / b / c == (a / b) / c`.","Adding spaces never changes the value."],
  ["10 - 4 - 3 = 3","100 / 10 / 5 = 2","2 + 3 * 4 = 14","2 * 3 - 4 - 1 = 1"],
  ["Chains of each operator.","Mixed precedence.","A property against a reference evaluator."],
  src=("src/sql/mini_parse.rs", '''
//! A precedence-climbing evaluator for + - * / over integers.

fn tokens(s: &str) -> Option<Vec<String>> {
    let mut v = Vec::new();
    let mut cur = String::new();
    for c in s.chars() {
        if c.is_ascii_digit() {
            cur.push(c);
        } else {
            if !cur.is_empty() {
                v.push(std::mem::take(&mut cur));
            }
            match c {
                ' ' => {}
                '+' | '-' | '*' | '/' | '(' | ')' => v.push(c.to_string()),
                _ => return None,
            }
        }
    }
    if !cur.is_empty() {
        v.push(cur);
    }
    Some(v)
}

fn prec(op: &str) -> Option<u8> {
    match op {
        "+" | "-" => Some(1),
        "*" | "/" => Some(2),
        _ => None,
    }
}

fn atom(t: &[String], i: &mut usize) -> Option<i64> {
    let tok = t.get(*i)?;
    *i += 1;
    if tok == "(" {
        let v = expr(t, i, 1)?;
        if t.get(*i)? != ")" {
            return None;
        }
        *i += 1;
        Some(v)
    } else {
        tok.parse().ok()
    }
}

fn expr(t: &[String], i: &mut usize, min_prec: u8) -> Option<i64> {
    let mut lhs = atom(t, i)?;
    while let Some(op) = t.get(*i) {
        let Some(p) = prec(op) else { break };
        if p < min_prec {
            break;
        }
        *i += 1;
        // @begin 3d-c3
        let rhs = expr(t, i, p + 1)?;
        //~ let rhs = expr(t, i, p)?;
        // @end
        lhs = match op.as_str() {
            "+" => lhs.checked_add(rhs)?,
            "-" => lhs.checked_sub(rhs)?,
            "*" => lhs.checked_mul(rhs)?,
            _ => lhs.checked_div(rhs)?,
        };
    }
    Some(lhs)
}

/// Parses and evaluates; `None` for a syntax error, overflow or division by zero.
pub fn parse_and_eval(s: &str) -> Option<i64> {
    let t = tokens(s)?;
    let mut i = 0;
    let v = expr(&t, &mut i, 1)?;
    if i == t.len() {
        Some(v)
    } else {
        None
    }
}
'''),
  test=("tests/stages_3d.rs", '''
use bustub::sql::mini_parse::parse_and_eval;

#[test]
fn s3d_c3_subtraction_associates_to_the_left() {
    assert_eq!(parse_and_eval("10 - 4 - 3"), Some(3));
    assert_eq!(parse_and_eval("10 - (4 - 3)"), Some(9));
}

#[test]
fn s3d_c3_division_associates_to_the_left() {
    assert_eq!(parse_and_eval("100 / 10 / 5"), Some(2));
    assert_eq!(parse_and_eval("100 / (10 / 5)"), Some(50));
}

#[test]
fn s3d_c3_precedence_still_works() {
    assert_eq!(parse_and_eval("2 + 3 * 4"), Some(14));
    assert_eq!(parse_and_eval("2 * 3 - 4 - 1"), Some(1));
    assert_eq!(parse_and_eval("(2 + 3) * 4"), Some(20));
}

#[test]
fn s3d_c3_errors_are_none() {
    assert_eq!(parse_and_eval("1 / 0"), None);
    assert_eq!(parse_and_eval("1 +"), None);
    assert_eq!(parse_and_eval("(1"), None);
    assert_eq!(parse_and_eval("1 2"), None);
    assert_eq!(parse_and_eval("a"), None);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a left-leaning chain without parentheses equals folding it from the left.
    #[test]
    fn s3d_c3_property_chains_fold_from_the_left(first in 1i64..50, rest in proptest::collection::vec((prop_oneof![Just('+'), Just('-'), Just('*')], 1i64..10), 0..6)) {
        let text = rest.iter().fold(first.to_string(), |s, (op, v)| format!("{s} {op} {v}"));
        // evaluate with the usual precedence by hand: collect additive terms
        let mut terms: Vec<i64> = vec![first];
        let mut signs: Vec<i64> = vec![1];
        for (op, v) in &rest {
            match op {
                '*' => { let last = terms.last_mut().unwrap(); *last *= v; }
                '+' => { terms.push(*v); signs.push(1); }
                _ => { terms.push(*v); signs.push(-1); }
            }
        }
        let want: i64 = terms.iter().zip(&signs).map(|(t, s)| t * s).sum();
        prop_assert_eq!(parse_and_eval(&text), Some(want), "{}", text);
    }
}
''')))

CH.append(C("3d-c4", M3D, "93-challenge-error-carets", "build", "Challenge: error carets", "easy", "stages_3d::s3d_c4",
  ["turning a byte offset into a line and column","rendering an error with the source line and a caret"],
  ["errors-as-values-with-result","designing-error-types"],
  "`line_col` and `render_error` in `src/sql/error_render.rs`: `line_col(src, offset)` turns a byte offset into a 1-based `(line, column)` where the column counts **characters**; `render_error(src, offset, len, msg)` prints the message, the offending source line, and a line of spaces and `^` marks under the error.",
  "`syntax error at byte 47` is a debugging session; ```ERROR: unknown column 'nmae'\\nLINE 1: SELECT nmae FROM t\\n               ^``` is a fix. Every SQL front end does this, and the traps are the usual ones: lines end with `\\r\\n` as well as `\\n`, columns count characters not bytes, and an error at the very end of the input has a position too.",
  ["Lines end at `\\n` (a preceding `\\r` is not part of the line). Line and column are 1-based; a tab counts as one column.","`line_col(src, offset)` for `offset == src.len()` is the position just after the last character.","`render_error` returns `msg`, then `LINE <n>: <line text>`, then a caret line aligned under the error (the `LINE <n>: ` prefix counted), with `max(len, 1)` carets, cut at the end of the line."],
  ["`line_col` is monotone: a later offset never has an earlier (line, column).","The caret column equals the error column plus the prefix width."],
  ["Splitting the source differently (`\\n` vs `\\r\\n`) gives the same line and column numbers.","Moving the error one character right moves the caret one place right (within the line).","An offset at a line start has column 1."],
  ["\"SELECT a\\nFROM t\" offset 12 -> (2, 4)","\"héllo\" offset 3 -> column 3 (the bytes of é count once)"],
  ["Positions on several lines, with CRLF and multi-byte characters.","The end of input.","Rendering with one and several carets."],
  src=("src/sql/error_render.rs", '''
//! Showing where in the SQL text an error is.

/// 1-based `(line, column)` of byte `offset` in `src`; the column counts characters. `offset` must be a character boundary at most `src.len()`.
pub fn line_col(src: &str, offset: usize) -> (usize, usize) {
    // @begin 3d-c4
    let before = &src[..offset];
    let line = before.matches('\\n').count() + 1;
    let line_start = before.rfind('\\n').map_or(0, |i| i + 1);
    (line, src[line_start..offset].chars().count() + 1)
    //~ todo!("3d-c4: count newlines before the offset, then the characters since the last one")
    // @end
}

/// The message, the source line, and carets under `len` bytes starting at `offset`.
pub fn render_error(src: &str, offset: usize, len: usize, msg: &str) -> String {
    // @begin 3d-c4
    let (line_no, col) = line_col(src, offset);
    let line_start = src[..offset].rfind('\\n').map_or(0, |i| i + 1);
    let line_end = src[offset..].find('\\n').map_or(src.len(), |i| offset + i);
    let line = src[line_start..line_end].trim_end_matches('\\r');
    let prefix = format!("LINE {line_no}: ");
    let width = (src[offset..(offset + len).min(line_end)].chars().count()).max(1);
    let carets = "^".repeat(width);
    format!("{msg}\\n{prefix}{line}\\n{}{}", " ".repeat(prefix.chars().count() + col - 1), carets)
    //~ todo!("3d-c4: the message, the line, and the caret line")
    // @end
}
'''),
  test=("tests/stages_3d.rs", '''
use bustub::sql::error_render::{line_col, render_error};

#[test]
fn s3d_c4_line_and_column_are_one_based() {
    let src = "SELECT a\\nFROM t";
    assert_eq!(line_col(src, 0), (1, 1));
    assert_eq!(line_col(src, 7), (1, 8));
    assert_eq!(line_col(src, 9), (2, 1));
    assert_eq!(line_col(src, 12), (2, 4));
}

#[test]
fn s3d_c4_columns_count_characters_and_the_end_of_input_has_a_position() {
    assert_eq!(line_col("héllo", 3), (1, 3));
    assert_eq!(line_col("héllo", 6), (1, 6));
    assert_eq!(line_col("a\\n", 2), (2, 1));
    assert_eq!(line_col("", 0), (1, 1));
}

#[test]
fn s3d_c4_crlf_line_ends_do_not_change_columns() {
    assert_eq!(line_col("a\\r\\nbc", 3), (2, 1));
    assert_eq!(line_col("a\\r\\nbc", 4), (2, 2));
    assert_eq!(line_col("a\\r\\nbc", 5), (2, 3));
}

#[test]
fn s3d_c4_the_rendering_shows_the_line_and_a_caret_under_the_error() {
    let src = "SELECT nmae FROM t";
    let out = render_error(src, 7, 4, "unknown column");
    assert_eq!(out, "unknown column\\nLINE 1: SELECT nmae FROM t\\n               ^^^^");
}

#[test]
fn s3d_c4_errors_on_later_lines_and_at_the_end() {
    let src = "SELECT 1\\nFROM";
    let out = render_error(src, src.len(), 0, "expected a table");
    assert_eq!(out, format!("expected a table\\nLINE 2: FROM\\n{}^", " ".repeat(12)));
    let long = render_error("ab\\ncd", 0, 50, "m");
    assert_eq!(long, "m\\nLINE 1: ab\\n        ^^", "carets stop at the end of the line");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: positions are monotone and agree with counting by hand.
    #[test]
    fn s3d_c4_property_positions_match_counting(src in "[a-é \\\\n]{0,30}") {
        let mut prev = (1, 0);
        let mut line = 1;
        let mut col = 1;
        for (off, ch) in src.char_indices() {
            let p = line_col(&src, off);
            prop_assert_eq!(p, (line, col));
            prop_assert!(p >= prev || p.0 > prev.0);
            prev = p;
            if ch == '\\n' { line += 1; col = 1; } else { col += 1; }
        }
        prop_assert_eq!(line_col(&src, src.len()), (line, col));
    }
}
''')))

CH.append(C("3d-c5", M3D, "94-challenge-which-column", "build", "Challenge: which column?", "easy", "stages_3d::s3d_c5",
  ["resolving a possibly qualified column name against the tables in scope","telling unknown from ambiguous"],
  ["name-resolution-and-the-binder","errors-as-values-with-result"],
  "`resolve_column` in `src/sql/resolve.rs`: given the tables in the `FROM` clause (each with an alias and its column names), find which table and column a name refers to. A name may be qualified (`t.x`) or not (`x`); matching is case-insensitive. An unqualified name that exists in more than one table is **ambiguous**.",
  "`SELECT id FROM a JOIN b` is an error in SQL, and the error message is the binder's job: *which* column, in *which* tables. Name resolution is small but it is where `unknown column`, `ambiguous column` and `missing FROM-clause entry` come from, and getting the three apart is what makes errors usable.",
  ["`resolve_column(tables, qualifier, name)` returns `Ok((table_index, column_index))`.","With a qualifier: the table with that alias, else `Err(UnknownTable)`; then the column in it, else `Err(UnknownColumn)`.","Without: every table that has the column; none is `Err(UnknownColumn)`, two or more is `Err(Ambiguous(table indexes))`.","A table that lists the same column name twice makes an unqualified or qualified lookup of it ambiguous too (`Ambiguous` with that table's index repeated)."],
  ["A successful answer names a column that exists, in a table in scope.","The answer does not depend on the case of the input."],
  ["Adding a table that lacks the name never changes the answer.","Adding a second table that has the name turns a success into `Ambiguous`, unless the lookup is qualified.","A qualified lookup is never ambiguous across tables."],
  ["a(id, x), b(id, y): id -> Ambiguous([0, 1]); a.id -> (0, 0); y -> (1, 1); z -> UnknownColumn; c.id -> UnknownTable"],
  ["Qualified, unqualified, ambiguous, unknown.","Case-insensitivity.","A property against a brute-force search."],
  src=("src/sql/resolve.rs", '''
//! Which table and column does a name refer to?

#[derive(Debug, PartialEq, Eq)]
pub enum ResolveError {
    UnknownTable,
    UnknownColumn,
    Ambiguous(Vec<usize>),
}

/// `tables[i] = (alias, column names)`.
pub fn resolve_column(tables: &[(&str, Vec<&str>)], qualifier: Option<&str>, name: &str) -> Result<(usize, usize), ResolveError> {
    // @begin 3d-c5
    let name = name.to_ascii_lowercase();
    let find_in = |t: usize| -> Vec<usize> {
        tables[t].1.iter().enumerate().filter(|(_, c)| c.to_ascii_lowercase() == name).map(|(i, _)| i).collect()
    };
    match qualifier {
        Some(q) => {
            let q = q.to_ascii_lowercase();
            let t = tables.iter().position(|(a, _)| a.to_ascii_lowercase() == q).ok_or(ResolveError::UnknownTable)?;
            let cols = find_in(t);
            match cols.len() {
                0 => Err(ResolveError::UnknownColumn),
                1 => Ok((t, cols[0])),
                _ => Err(ResolveError::Ambiguous(vec![t; cols.len()])),
            }
        }
        None => {
            let mut hits: Vec<(usize, usize)> = Vec::new();
            for t in 0..tables.len() {
                hits.extend(find_in(t).into_iter().map(|c| (t, c)));
            }
            match hits.len() {
                0 => Err(ResolveError::UnknownColumn),
                1 => Ok(hits[0]),
                _ => Err(ResolveError::Ambiguous(hits.into_iter().map(|(t, _)| t).collect())),
            }
        }
    }
    //~ todo!("3d-c5: find the column in the named table, or in every table when unqualified")
    // @end
}
'''),
  test=("tests/stages_3d.rs", '''
use bustub::sql::resolve::{resolve_column, ResolveError::*};

fn scope() -> Vec<(&'static str, Vec<&'static str>)> {
    vec![("a", vec!["id", "x"]), ("b", vec!["id", "y"])]
}

#[test]
fn s3d_c5_qualified_names_pick_the_table() {
    assert_eq!(resolve_column(&scope(), Some("a"), "id"), Ok((0, 0)));
    assert_eq!(resolve_column(&scope(), Some("B"), "ID"), Ok((1, 0)));
}

#[test]
fn s3d_c5_an_unqualified_name_found_once_resolves() {
    assert_eq!(resolve_column(&scope(), None, "y"), Ok((1, 1)));
    assert_eq!(resolve_column(&scope(), None, "X"), Ok((0, 1)));
}

#[test]
fn s3d_c5_an_unqualified_name_in_two_tables_is_ambiguous() {
    assert_eq!(resolve_column(&scope(), None, "id"), Err(Ambiguous(vec![0, 1])));
}

#[test]
fn s3d_c5_unknown_columns_and_tables_are_different_errors() {
    assert_eq!(resolve_column(&scope(), None, "z"), Err(UnknownColumn));
    assert_eq!(resolve_column(&scope(), Some("a"), "y"), Err(UnknownColumn));
    assert_eq!(resolve_column(&scope(), Some("c"), "id"), Err(UnknownTable));
}

#[test]
fn s3d_c5_a_table_that_repeats_a_column_name_is_ambiguous_even_when_qualified() {
    let t = vec![("t", vec!["a", "A"])];
    assert_eq!(resolve_column(&t, Some("t"), "a"), Err(Ambiguous(vec![0, 0])));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: unqualified lookup agrees with listing every (table, column) match.
    #[test]
    fn s3d_c5_property_unqualified_lookup_is_a_search(cols in proptest::collection::vec(proptest::collection::vec(prop::sample::select(vec!["a", "b", "c", "D"]), 0..4), 1..4), name in prop::sample::select(vec!["a", "b", "c", "d", "e"])) {
        let tables: Vec<(String, Vec<&str>)> = cols.into_iter().enumerate().map(|(i, c)| (format!("t{i}"), c)).collect();
        let view: Vec<(&str, Vec<&str>)> = tables.iter().map(|(a, c)| (a.as_str(), c.clone())).collect();
        let mut hits = Vec::new();
        for (t, (_, c)) in view.iter().enumerate() {
            for (i, col) in c.iter().enumerate() { if col.eq_ignore_ascii_case(name) { hits.push((t, i)); } }
        }
        let want = match hits.len() { 0 => Err(UnknownColumn), 1 => Ok(hits[0]), _ => Err(Ambiguous(hits.iter().map(|h| h.0).collect())) };
        prop_assert_eq!(resolve_column(&view, None, name), want);
    }
}
''')))

CH.append(C("3e-c1", M3E, "90-challenge-executor-adapters", "build", "Challenge: executor adapters", "medium", "stages_3e::s3e_c1",
  ["composing pull-based operators with `Box<dyn Executor>`","not pulling more rows from a child than needed"],
  ["iterators-and-closures","generics-and-static-dispatch"],
  "`Filter`, `Project`, `Limit` and `Concat` in `src/execution/adapters.rs`: pull-based operators over the given `Executor` trait (`next() -> Option<Row>`, where a row is a `Vec<i64>`). Each wraps a child (or two); `Limit` takes a limit and an offset and must **stop pulling** from its child once it has what it needs.",
  "These four, and a scan under them, are the whole of a Volcano-style executor in miniature. The laziness is the point: `SELECT * FROM big LIMIT 10` must read ten rows, not ten million, and an operator that pre-reads its input to be safe makes every query pay for it.",
  ["`Filter::new(child, pred)` yields child rows for which `pred(&row)` is true, in order.","`Project::new(child, cols)` yields each row restricted to the columns `cols` (in that order).","`Limit::new(child, limit, offset)` skips `offset` rows, yields at most `limit` rows, and pulls nothing more from the child once `limit` rows have been yielded.","`Concat::new(a, b)` yields all of `a`, then all of `b`; it never touches `b` before `a` is exhausted."],
  ["Row order is the order the children produce them.","Every operator is exhausted after it returns `None` once (it keeps returning `None`).","The number of rows pulled from a child never exceeds what the operator needs."],
  ["`Limit(n)` over a scan of `m` rows pulls `min(m, offset + n)` rows from the scan.","`Filter` then `Project` equals the same on a `Vec`.","Composing operators in a `Box<dyn Executor>` tree equals the corresponding iterator chain."],
  ["scan [1..10] -> Filter(even) -> Limit(2, offset 1) -> 4, 6; the scan was pulled 6 times"],
  ["Each operator alone.","Composition, and the laziness counters.","A property against an iterator chain."],
  src=("src/execution/adapters.rs", '''
//! Pull-based operators over rows of integers.

use std::cell::Cell;
use std::rc::Rc;

pub type Row = Vec<i64>;

pub trait Executor {
    fn next(&mut self) -> Option<Row>;
}

/// A scan over in-memory rows that counts how many rows have been pulled from it.
pub struct VecScan {
    rows: std::vec::IntoIter<Row>,
    pulled: Rc<Cell<usize>>,
}

impl VecScan {
    pub fn new(rows: Vec<Row>) -> (VecScan, Rc<Cell<usize>>) {
        let pulled = Rc::new(Cell::new(0));
        (VecScan { rows: rows.into_iter(), pulled: pulled.clone() }, pulled)
    }
}

impl Executor for VecScan {
    fn next(&mut self) -> Option<Row> {
        let r = self.rows.next();
        if r.is_some() {
            self.pulled.set(self.pulled.get() + 1);
        }
        r
    }
}

pub struct Filter {
    // @begin 3e-c1
    child: Box<dyn Executor>,
    pred: Box<dyn Fn(&Row) -> bool>,
    //~ _filter: (),
    // @end
}

impl Filter {
    pub fn new(child: Box<dyn Executor>, pred: impl Fn(&Row) -> bool + 'static) -> Filter {
        // @begin 3e-c1
        Filter { child, pred: Box::new(pred) }
        //~ todo!("3e-c1: remember the child and the predicate")
        // @end
    }
}

impl Executor for Filter {
    fn next(&mut self) -> Option<Row> {
        // @begin 3e-c1
        while let Some(r) = self.child.next() {
            if (self.pred)(&r) {
                return Some(r);
            }
        }
        None
        //~ todo!("3e-c1: the next child row that passes")
        // @end
    }
}

pub struct Project {
    // @begin 3e-c1
    child: Box<dyn Executor>,
    cols: Vec<usize>,
    //~ _project: (),
    // @end
}

impl Project {
    pub fn new(child: Box<dyn Executor>, cols: Vec<usize>) -> Project {
        // @begin 3e-c1
        Project { child, cols }
        //~ todo!("3e-c1: remember the child and the columns")
        // @end
    }
}

impl Executor for Project {
    fn next(&mut self) -> Option<Row> {
        // @begin 3e-c1
        let r = self.child.next()?;
        Some(self.cols.iter().map(|&c| r[c]).collect())
        //~ todo!("3e-c1: the chosen columns of the next child row")
        // @end
    }
}

pub struct Limit {
    // @begin 3e-c1
    child: Box<dyn Executor>,
    remaining: usize,
    to_skip: usize,
    //~ _limit: (),
    // @end
}

impl Limit {
    pub fn new(child: Box<dyn Executor>, limit: usize, offset: usize) -> Limit {
        // @begin 3e-c1
        Limit { child, remaining: limit, to_skip: offset }
        //~ todo!("3e-c1: remember the child, the limit and the offset")
        // @end
    }
}

impl Executor for Limit {
    fn next(&mut self) -> Option<Row> {
        // @begin 3e-c1
        if self.remaining == 0 {
            return None;
        }
        while self.to_skip > 0 {
            self.child.next()?;
            self.to_skip -= 1;
        }
        let r = self.child.next()?;
        self.remaining -= 1;
        Some(r)
        //~ todo!("3e-c1: skip the offset once, then yield at most `limit` rows without pulling more")
        // @end
    }
}

pub struct Concat {
    // @begin 3e-c1
    a: Box<dyn Executor>,
    b: Box<dyn Executor>,
    a_done: bool,
    //~ _concat: (),
    // @end
}

impl Concat {
    pub fn new(a: Box<dyn Executor>, b: Box<dyn Executor>) -> Concat {
        // @begin 3e-c1
        Concat { a, b, a_done: false }
        //~ todo!("3e-c1: remember both children")
        // @end
    }
}

impl Executor for Concat {
    fn next(&mut self) -> Option<Row> {
        // @begin 3e-c1
        if !self.a_done {
            if let Some(r) = self.a.next() {
                return Some(r);
            }
            self.a_done = true;
        }
        self.b.next()
        //~ todo!("3e-c1: all of the first child, then all of the second")
        // @end
    }
}
'''),
  test=("tests/stages_3e.rs", '''
use bustub::execution::adapters::{Concat, Executor, Filter, Limit, Project, Row, VecScan};

fn rows(n: i64) -> Vec<Row> {
    (1..=n).map(|i| vec![i, i * 10]).collect()
}

fn drain(mut e: Box<dyn Executor>) -> Vec<Row> {
    let mut out = Vec::new();
    while let Some(r) = e.next() {
        out.push(r);
    }
    assert!(e.next().is_none(), "an exhausted executor stays exhausted");
    out
}

#[test]
fn s3e_c1_filter_and_project() {
    let (scan, _) = VecScan::new(rows(6));
    let f = Filter::new(Box::new(scan), |r| r[0] % 2 == 0);
    let p = Project::new(Box::new(f), vec![1, 0]);
    assert_eq!(drain(Box::new(p)), vec![vec![20, 2], vec![40, 4], vec![60, 6]]);
}

#[test]
fn s3e_c1_limit_with_an_offset_and_the_rows_it_pulled() {
    let (scan, pulled) = VecScan::new(rows(10));
    let f = Filter::new(Box::new(scan), |r| r[0] % 2 == 0);
    let l = Limit::new(Box::new(f), 2, 1);
    assert_eq!(drain(Box::new(l)), vec![vec![4, 40], vec![6, 60]]);
    assert_eq!(pulled.get(), 6, "rows 1..=6 were enough: nothing may be read ahead");
}

#[test]
fn s3e_c1_a_limit_of_zero_pulls_nothing() {
    let (scan, pulled) = VecScan::new(rows(5));
    assert_eq!(drain(Box::new(Limit::new(Box::new(scan), 0, 3))), Vec::<Row>::new());
    assert_eq!(pulled.get(), 0);
}

#[test]
fn s3e_c1_a_limit_past_the_end_just_ends() {
    let (scan, pulled) = VecScan::new(rows(3));
    assert_eq!(drain(Box::new(Limit::new(Box::new(scan), 10, 2))), vec![vec![3, 30]]);
    assert_eq!(pulled.get(), 3);
}

#[test]
fn s3e_c1_concat_reads_the_second_only_after_the_first() {
    let (a, pa) = VecScan::new(rows(2));
    let (b, pb) = VecScan::new(rows(2));
    let mut c = Concat::new(Box::new(a), Box::new(b));
    assert_eq!(c.next(), Some(vec![1, 10]));
    assert_eq!((pa.get(), pb.get()), (1, 0));
    c.next();
    assert_eq!(pb.get(), 0, "the first child is not exhausted until it says None");
    assert_eq!(c.next(), Some(vec![1, 10]));
    assert_eq!(pb.get(), 1);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a tree of operators equals the matching iterator chain, and the scan is pulled `min(len, needed)` times.
    #[test]
    fn s3e_c1_property_operators_equal_an_iterator_chain(n in 0i64..30, modulus in 1i64..5, limit in 0usize..8, offset in 0usize..8) {
        let (scan, pulled) = VecScan::new(rows(n));
        let f = Filter::new(Box::new(scan), move |r| r[0] % modulus == 0);
        let l = Limit::new(Box::new(f), limit, offset);
        let got = drain(Box::new(l));
        let want: Vec<Row> = rows(n).into_iter().filter(|r| r[0] % modulus == 0).skip(offset).take(limit).collect();
        prop_assert_eq!(got, want.clone());
        if limit > 0 {
            let needed = offset + limit;
            let all: Vec<i64> = (1..=n).filter(|i| i % modulus == 0).collect();
            let want_pulled = if all.len() >= needed { all[needed - 1] as usize } else { n as usize };
            prop_assert_eq!(pulled.get(), want_pulled);
        } else {
            prop_assert_eq!(pulled.get(), 0);
        }
    }
}
''')))

CH.append(C("3e-c2", M3E, "91-challenge-on-conflict", "build", "Challenge: ON CONFLICT", "easy", "stages_3e::s3e_c2",
  ["inserting a batch where some keys already exist","reporting what happened to each row"],
  ["maintaining-indexes-on-writes","model-based-testing"],
  "`upsert` in `src/execution/upsert.rs`: `INSERT ... ON CONFLICT` over a table keyed by `i64` with an `i64` value. Rows of the batch are applied **in order**; a row whose key already exists (including a key inserted earlier in the same batch) is handled by the conflict policy: `DoNothing`, `Replace` (the new value) or `Add` (the sum of old and new value).",
  "`INSERT` that fails on the first duplicate is useless for loading data, and read-then-insert in the application is a race. Upsert is the standard answer, and its semantics are all in the order and in what is reported: how many rows were inserted, how many changed an existing row, how many were skipped.",
  ["`upsert(table, rows, policy)` returns `Counts { inserted, updated, ignored }`.","A new key is inserted. An existing key: `DoNothing` ignores the row; `Replace` sets the value and counts as updated; `Add` adds the value (wrapping) and counts as updated.","Rows are applied one after the other, so a second row for the same key in the batch is a conflict with the first."],
  ["`inserted + updated + ignored` equals the number of rows in the batch.","The table has exactly one entry per key."],
  ["With `DoNothing`, the table afterwards is the old table plus the first row for each new key.","With `Replace`, it is the old table overridden by the last row for each key.","With `Add`, each key's value is its old value plus the sum of its rows."],
  ["table {1: 10}; rows (1, 5), (2, 7), (2, 1); Add -> {1: 15, 2: 8}; inserted 1, updated 2, ignored 0"],
  ["Each policy on a small batch.","Duplicates inside the batch.","A property against a model."],
  src=("src/execution/upsert.rs", '''
//! INSERT ... ON CONFLICT over a keyed table.

use std::collections::BTreeMap;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Conflict {
    DoNothing,
    Replace,
    Add,
}

#[derive(Debug, PartialEq, Eq, Default)]
pub struct Counts {
    pub inserted: usize,
    pub updated: usize,
    pub ignored: usize,
}

pub fn upsert(table: &mut BTreeMap<i64, i64>, rows: &[(i64, i64)], policy: Conflict) -> Counts {
    // @begin 3e-c2
    let mut c = Counts::default();
    for &(k, v) in rows {
        match table.get_mut(&k) {
            None => {
                table.insert(k, v);
                c.inserted += 1;
            }
            Some(old) => match policy {
                Conflict::DoNothing => c.ignored += 1,
                Conflict::Replace => {
                    *old = v;
                    c.updated += 1;
                }
                Conflict::Add => {
                    *old = old.wrapping_add(v);
                    c.updated += 1;
                }
            },
        }
    }
    c
    //~ todo!("3e-c2: apply the rows in order, counting what happened to each")
    // @end
}
'''),
  test=("tests/stages_3e.rs", '''
use bustub::execution::upsert::{upsert, Conflict, Counts};
use std::collections::BTreeMap;

#[test]
fn s3e_c2_add_sums_conflicting_values_and_counts_each_row() {
    let mut t = BTreeMap::from([(1, 10)]);
    let c = upsert(&mut t, &[(1, 5), (2, 7), (2, 1)], Conflict::Add);
    assert_eq!(t, BTreeMap::from([(1, 15), (2, 8)]));
    assert_eq!(c, Counts { inserted: 1, updated: 2, ignored: 0 });
}

#[test]
fn s3e_c2_do_nothing_keeps_the_first_row_for_a_key() {
    let mut t = BTreeMap::from([(1, 10)]);
    let c = upsert(&mut t, &[(1, 5), (2, 7), (2, 1)], Conflict::DoNothing);
    assert_eq!(t, BTreeMap::from([(1, 10), (2, 7)]));
    assert_eq!(c, Counts { inserted: 1, updated: 0, ignored: 2 });
}

#[test]
fn s3e_c2_replace_keeps_the_last_row_for_a_key() {
    let mut t = BTreeMap::new();
    let c = upsert(&mut t, &[(1, 1), (1, 2), (1, 3)], Conflict::Replace);
    assert_eq!(t, BTreeMap::from([(1, 3)]));
    assert_eq!(c, Counts { inserted: 1, updated: 2, ignored: 0 });
}

#[test]
fn s3e_c2_an_empty_batch_changes_nothing() {
    let mut t = BTreeMap::from([(1, 1)]);
    assert_eq!(upsert(&mut t, &[], Conflict::Add), Counts::default());
    assert_eq!(t.len(), 1);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: each policy against its one-line description, and the counts add up.
    #[test]
    fn s3e_c2_property_policies_match_their_definitions(init in proptest::collection::btree_map(0i64..5, -9i64..9, 0..5), rows in proptest::collection::vec((0i64..5, -9i64..9), 0..12)) {
        let mut a = init.clone();
        let c = upsert(&mut a, &rows, Conflict::DoNothing);
        let mut want = init.clone();
        for &(k, v) in &rows { want.entry(k).or_insert(v); }
        prop_assert_eq!(&a, &want);
        prop_assert_eq!(c.inserted + c.updated + c.ignored, rows.len());
        let mut r = init.clone();
        upsert(&mut r, &rows, Conflict::Replace);
        let mut want = init.clone();
        for &(k, v) in &rows { want.insert(k, v); }
        prop_assert_eq!(&r, &want);
        let mut s = init.clone();
        upsert(&mut s, &rows, Conflict::Add);
        let mut want = init;
        for &(k, v) in &rows { *want.entry(k).or_insert(0) += v; }
        prop_assert_eq!(&s, &want);
    }
}
''')))

CH.append(C("3e-c3", M3E, "92-challenge-limit-zero", "debug", "Challenge: LIMIT 0", "easy", "stages_3e::s3e_c3",
  ["finding a sentinel that collides with a legal value"],
  ["option-and-result-combinators","property-testing-and-fuzzing"],
  "`limit_offset` in `src/execution/limit_offset.rs` implements `LIMIT n OFFSET m` over a vector of rows (`limit: None` means no limit). It looks right, and `LIMIT 0` returns rows. Find the bug and fix it.",
  "`LIMIT 0` is not rare: it is how clients ask for the *shape* of a result without the rows, and how an optimiser proves a query empty. A sentinel `0 = unlimited` is a classic C idiom that a typed `Option` was supposed to retire; here it came back through a helper.",
  ["`limit_offset(rows, limit, offset)` skips `offset` rows and then yields at most `limit` rows (all the rest when `limit` is `None`).","An offset past the end gives no rows; `limit == Some(0)` gives no rows whatever the offset."],
  ["The output is a contiguous slice of the input, in order.","Its length is `min(limit, len - offset)` (or `len - offset` without a limit), never negative."],
  ["`limit_offset(r, Some(0), m)` is empty for every `m`.","`limit_offset(r, None, 0)` is the whole input.","`limit_offset(r, Some(a), m)` is a prefix of `limit_offset(r, Some(b), m)` for `a <= b`."],
  ["[1,2,3] LIMIT 0 -> []","[1,2,3] LIMIT 2 OFFSET 1 -> [2,3]","[1,2,3] OFFSET 5 -> []"],
  ["The usual cases and the zero.","Offsets at and past the end.","A property against slicing."],
  src=("src/execution/limit_offset.rs", '''
//! LIMIT and OFFSET over a vector of rows.

pub fn limit_offset(rows: &[i64], limit: Option<usize>, offset: usize) -> Vec<i64> {
    // @begin 3e-c3
    let take = limit.unwrap_or(usize::MAX);
    //~ let take = limit.filter(|&n| n > 0).unwrap_or(usize::MAX);
    // @end
    rows.iter().skip(offset).take(take).copied().collect()
}
'''),
  test=("tests/stages_3e.rs", '''
use bustub::execution::limit_offset::limit_offset;

#[test]
fn s3e_c3_limit_zero_returns_no_rows() {
    assert_eq!(limit_offset(&[1, 2, 3], Some(0), 0), Vec::<i64>::new());
    assert_eq!(limit_offset(&[1, 2, 3], Some(0), 2), Vec::<i64>::new());
}

#[test]
fn s3e_c3_limit_and_offset() {
    assert_eq!(limit_offset(&[1, 2, 3], Some(2), 1), vec![2, 3]);
    assert_eq!(limit_offset(&[1, 2, 3], Some(1), 0), vec![1]);
    assert_eq!(limit_offset(&[1, 2, 3], None, 1), vec![2, 3]);
}

#[test]
fn s3e_c3_offsets_at_and_past_the_end() {
    assert_eq!(limit_offset(&[1, 2, 3], None, 3), Vec::<i64>::new());
    assert_eq!(limit_offset(&[1, 2, 3], Some(5), 5), Vec::<i64>::new());
    assert_eq!(limit_offset(&[], Some(3), 0), Vec::<i64>::new());
}

#[test]
fn s3e_c3_a_limit_larger_than_what_is_left_returns_what_is_left() {
    assert_eq!(limit_offset(&[1, 2, 3, 4], Some(10), 2), vec![3, 4]);
    assert_eq!(limit_offset(&[1, 2, 3, 4], Some(2), 2), vec![3, 4]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a contiguous slice of the input with the right length, and a bigger limit extends a smaller one.
    #[test]
    fn s3e_c3_property_the_result_is_a_slice(rows in proptest::collection::vec(any::<i64>(), 0..10), limit in proptest::option::of(0usize..12), offset in 0usize..12, extra in 0usize..5) {
        let got = limit_offset(&rows, limit, offset);
        let start = offset.min(rows.len());
        let end = match limit { Some(n) => (start + n).min(rows.len()), None => rows.len() };
        prop_assert_eq!(&got[..], &rows[start..end]);
        if let Some(n) = limit {
            let more = limit_offset(&rows, Some(n + extra), offset);
            prop_assert!(more.starts_with(&got));
        }
    }
}
''')))

CH.append(C("3e-c4", M3E, "94-challenge-combining-index-scans", "build", "Challenge: combining index scans", "easy", "stages_3e::s3e_c4",
  ["union, intersection and difference of sorted row-id lists in one pass","why an OR of two index conditions must not return a row twice"],
  ["access-paths-index-vs-seq-scan","conjunctive-predicates","model-based-testing"],
  "`union_sorted`, `intersect_sorted` and `difference_sorted` in `src/execution/rid_sets.rs`: given row-id lists that are each **sorted and without duplicates**, produce the union, intersection and difference as sorted, duplicate-free lists in one linear pass (no sorting, no hashing).",
  "`WHERE a = 4 OR b = 9` can be answered by two index scans whose results are combined, and `AND` by intersecting them. A row that satisfies both sides of an OR must appear **once**: returning it twice was a real bug in this course's own index scan, found by a test with `v1 = 4 OR v1 = 4`. The combination of sorted lists is the merge step of a merge join, small and exact.",
  ["Inputs are strictly increasing.","`union_sorted(a, b)`: every id in either, once. `intersect_sorted(a, b)`: ids in both. `difference_sorted(a, b)`: ids in `a` and not in `b`.","Each returns a strictly increasing list and looks at each input element once."],
  ["Outputs are strictly increasing.","`|union| + |intersection| == |a| + |b|`."],
  ["`union(a, a) == a`, `intersect(a, a) == a`, `difference(a, a) == []`.","`difference(a, b) ∪ intersect(a, b) == a`.","All three equal the corresponding `BTreeSet` operation."],
  ["a = [1,3,5], b = [3,4,5,6]: union [1,3,4,5,6]; intersect [3,5]; difference [1]"],
  ["Small lists, one empty, identical lists.","A property against `BTreeSet`."],
  src=("src/execution/rid_sets.rs", '''
//! Combining the row ids of two index scans.

pub fn union_sorted(a: &[u64], b: &[u64]) -> Vec<u64> {
    // @begin 3e-c4
    let (mut i, mut j) = (0, 0);
    let mut out = Vec::with_capacity(a.len() + b.len());
    while i < a.len() || j < b.len() {
        let take_a = j >= b.len() || (i < a.len() && a[i] <= b[j]);
        let v = if take_a { a[i] } else { b[j] };
        if take_a {
            i += 1;
        }
        if j < b.len() && b[j] == v {
            j += 1;
        }
        out.push(v);
    }
    out
    //~ todo!("3e-c4: merge, emitting an id that is in both once")
    // @end
}

pub fn intersect_sorted(a: &[u64], b: &[u64]) -> Vec<u64> {
    // @begin 3e-c4
    let (mut i, mut j) = (0, 0);
    let mut out = Vec::new();
    while i < a.len() && j < b.len() {
        match a[i].cmp(&b[j]) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                out.push(a[i]);
                i += 1;
                j += 1;
            }
        }
    }
    out
    //~ todo!("3e-c4: advance the smaller side; emit when they are equal")
    // @end
}

pub fn difference_sorted(a: &[u64], b: &[u64]) -> Vec<u64> {
    // @begin 3e-c4
    let mut j = 0;
    let mut out = Vec::new();
    for &x in a {
        while j < b.len() && b[j] < x {
            j += 1;
        }
        if j >= b.len() || b[j] != x {
            out.push(x);
        }
    }
    out
    //~ todo!("3e-c4: the ids of `a` that `b` does not have")
    // @end
}
'''),
  test=("tests/stages_3e.rs", '''
use bustub::execution::rid_sets::{difference_sorted, intersect_sorted, union_sorted};
use std::collections::BTreeSet;

#[test]
fn s3e_c4_the_three_operations_on_a_small_example() {
    let (a, b) = ([1, 3, 5], [3, 4, 5, 6]);
    assert_eq!(union_sorted(&a, &b), vec![1, 3, 4, 5, 6]);
    assert_eq!(intersect_sorted(&a, &b), vec![3, 5]);
    assert_eq!(difference_sorted(&a, &b), vec![1]);
    assert_eq!(difference_sorted(&b, &a), vec![4, 6]);
}

#[test]
fn s3e_c4_an_id_in_both_lists_appears_once_in_the_union() {
    assert_eq!(union_sorted(&[4, 4 + 1], &[4, 5]), vec![4, 5], "v1 = 4 OR v1 = 4 returns each row once");
    assert_eq!(union_sorted(&[7], &[7]), vec![7]);
}

#[test]
fn s3e_c4_empty_inputs() {
    assert_eq!(union_sorted(&[], &[1, 2]), vec![1, 2]);
    assert_eq!(intersect_sorted(&[], &[1, 2]), Vec::<u64>::new());
    assert_eq!(difference_sorted(&[1, 2], &[]), vec![1, 2]);
    assert_eq!(difference_sorted(&[], &[1]), Vec::<u64>::new());
}

#[test]
fn s3e_c4_a_list_combined_with_itself() {
    let a = [2, 4, 6, 8];
    assert_eq!(union_sorted(&a, &a), a.to_vec());
    assert_eq!(intersect_sorted(&a, &a), a.to_vec());
    assert_eq!(difference_sorted(&a, &a), Vec::<u64>::new());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: each equals the `BTreeSet` operation, and the laws between them hold.
    #[test]
    fn s3e_c4_property_set_operations_match_btreeset(a in proptest::collection::btree_set(0u64..30, 0..12), b in proptest::collection::btree_set(0u64..30, 0..12)) {
        let (av, bv): (Vec<u64>, Vec<u64>) = (a.iter().copied().collect(), b.iter().copied().collect());
        prop_assert_eq!(union_sorted(&av, &bv), a.union(&b).copied().collect::<Vec<_>>());
        prop_assert_eq!(intersect_sorted(&av, &bv), a.intersection(&b).copied().collect::<Vec<_>>());
        prop_assert_eq!(difference_sorted(&av, &bv), a.difference(&b).copied().collect::<Vec<_>>());
        prop_assert_eq!(union_sorted(&av, &bv).len() + intersect_sorted(&av, &bv).len(), av.len() + bv.len());
    }
}
''')))

CH.append(C("3e-c5", M3E, "95-challenge-rewinding-an-input", "build", "Challenge: rewinding an input", "medium", "stages_3e::s3e_c5",
  ["replaying part of a one-pass stream without buffering all of it","the inner side of a nested loop join"],
  ["iterators-and-closures","join-algorithms"],
  "`Rewindable` in `src/execution/rewindable.rs`: wrap any iterator so that `mark()` remembers the current position and `reset()` goes back to it: the items seen since the mark are replayed, then the underlying iterator continues. It must keep **only** the items since the mark.",
  "A nested loop join needs to read its inner side once per outer row, and an inner side that is an operator can only be read once. Re-executing it is expensive and sometimes wrong (a side-effecting or non-deterministic child); buffering the whole thing costs memory. Remembering what has been read since a mark is the middle road.",
  ["`next()` yields items in order. `mark()` records the position; items read after it are kept.","`reset()` returns to the marked position: the next items are the buffered ones, then the underlying iterator's.","`mark()` again drops what was buffered before the new mark; `buffered()` is the number of items held. Without a mark, nothing is kept (`buffered() == 0`)."],
  ["The sequence read through `next()` and `reset()` is exactly the underlying sequence from the mark, repeated.","The underlying iterator is pulled once per item, ever.","`buffered()` never exceeds the number of items read since the mark."],
  ["`mark; read k; reset; read k` gives the same k items twice.","A second `mark` after a `reset` costs nothing and keeps behaving.","The union of what was read equals the underlying sequence's prefix."],
  ["items 1..=5: mark; next=1, next=2; reset; next=1, next=2, next=3 (new from the source)"],
  ["Mark, read, reset, replay, continue.","Marks that move forward.","Pull counts.","A property against a vector model."],
  src=("src/execution/rewindable.rs", '''
//! An iterator that can go back to a marked position.

use std::collections::VecDeque;

pub struct Rewindable<I: Iterator> {
    // @begin 3e-c5
    inner: I,
    /// Items read from `inner` since the mark, kept for replay.
    since_mark: Vec<I::Item>,
    /// Items waiting to be replayed (front first) after a reset.
    replay: VecDeque<I::Item>,
    marked: bool,
    //~ _rewind: std::marker::PhantomData<I>,
    // @end
}

impl<I: Iterator> Rewindable<I>
where
    I::Item: Clone,
{
    pub fn new(inner: I) -> Rewindable<I> {
        // @begin 3e-c5
        Rewindable { inner, since_mark: Vec::new(), replay: VecDeque::new(), marked: false }
        //~ todo!("3e-c5: wrap the iterator, nothing marked")
        // @end
    }

    pub fn mark(&mut self) {
        // @begin 3e-c5
        // what is still waiting to be replayed is "after the mark" too: it stays buffered
        self.since_mark = self.replay.iter().cloned().collect();
        self.marked = true;
        //~ todo!("3e-c5: forget what was read before this point, keep what is yet to be replayed")
        // @end
    }

    pub fn reset(&mut self) {
        // @begin 3e-c5
        if self.marked {
            self.replay = self.since_mark.iter().cloned().collect();
        }
        //~ todo!("3e-c5: replay everything since the mark")
        // @end
    }

    /// How many items are being held for a possible reset.
    pub fn buffered(&self) -> usize {
        // @begin 3e-c5
        self.since_mark.len()
        //~ todo!("3e-c5: how many items are kept")
        // @end
    }
}

impl<I: Iterator> Iterator for Rewindable<I>
where
    I::Item: Clone,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        // @begin 3e-c5
        let item = match self.replay.pop_front() {
            Some(x) => x,
            None => {
                let x = self.inner.next()?;
                if self.marked {
                    self.since_mark.push(x.clone());
                }
                return Some(x);
            }
        };
        Some(item)
        //~ todo!("3e-c5: replayed items first, then the underlying iterator (keeping what is read since the mark)")
        // @end
    }
}
'''),
  test=("tests/stages_3e.rs", '''
use bustub::execution::rewindable::Rewindable;
use std::cell::Cell;
use std::rc::Rc;

fn counted(n: u32) -> (impl Iterator<Item = u32>, Rc<Cell<usize>>) {
    let pulls = Rc::new(Cell::new(0));
    let p = pulls.clone();
    ((1..=n).inspect(move |_| p.set(p.get() + 1)), pulls)
}

#[test]
fn s3e_c5_reset_replays_what_was_read_since_the_mark() {
    let (it, pulls) = counted(5);
    let mut r = Rewindable::new(it);
    r.mark();
    assert_eq!((r.next(), r.next()), (Some(1), Some(2)));
    r.reset();
    assert_eq!((r.next(), r.next(), r.next()), (Some(1), Some(2), Some(3)));
    assert_eq!(pulls.get(), 3, "the source is pulled once per item, ever");
}

#[test]
fn s3e_c5_nothing_is_kept_without_a_mark() {
    let (it, _) = counted(5);
    let mut r = Rewindable::new(it);
    r.next();
    r.next();
    assert_eq!(r.buffered(), 0);
    r.reset();
    assert_eq!(r.next(), Some(3), "reset without a mark goes nowhere");
}

#[test]
fn s3e_c5_a_later_mark_drops_the_older_items() {
    let (it, _) = counted(6);
    let mut r = Rewindable::new(it);
    r.mark();
    r.next();
    r.next();
    r.mark();
    assert_eq!(r.buffered(), 0);
    r.next();
    r.reset();
    assert_eq!(r.next(), Some(3));
}

#[test]
fn s3e_c5_several_resets_replay_the_same_items() {
    let (it, _) = counted(4);
    let mut r = Rewindable::new(it);
    r.mark();
    r.next();
    r.next();
    for _ in 0..3 {
        r.reset();
        assert_eq!((r.next(), r.next()), (Some(1), Some(2)));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a vector with a cursor and a mark.
    #[test]
    fn s3e_c5_property_rewinding_matches_a_cursor(n in 0u32..12, ops in proptest::collection::vec(0u8..3, 0..40)) {
        let (it, pulls) = counted(n);
        let mut r = Rewindable::new(it);
        let all: Vec<u32> = (1..=n).collect();
        let (mut pos, mut mark) = (0usize, None::<usize>);
        let mut high = 0usize;
        for op in ops {
            match op {
                0 => { let got = r.next(); prop_assert_eq!(got, all.get(pos).copied()); if got.is_some() { pos += 1; high = high.max(pos); } }
                1 => { r.mark(); mark = Some(pos); }
                _ => { r.reset(); if let Some(m) = mark { pos = m; } }
            }
            prop_assert_eq!(pulls.get(), high, "the source is pulled once per distinct item");
            if let Some(m) = mark { prop_assert!(r.buffered() <= high - m); } else { prop_assert_eq!(r.buffered(), 0); }
        }
    }
}
''')))
