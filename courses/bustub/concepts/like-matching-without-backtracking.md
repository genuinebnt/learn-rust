---
title: LIKE: matching wildcards without exponential backtracking
summary: LIKE is a tiny pattern language with two wildcards. The obvious recursive matcher is exponential on patterns with several %; remembering one position to go back to makes it linear in practice and quadratic at worst.
minutes: 8
---
`name like 'a%'` is the first thing anyone writes against a text column, and the matcher behind it is a small algorithm with a famous trap. The pattern language has only three ideas: `%` matches any run of characters (including none), `_` matches exactly one character, and everything else matches itself (a backslash makes the next character literal, so `\%` is a percent sign). That is much smaller than a regular expression, and yet a straightforward implementation can take longer than the age of the universe on `'aaaa…a' like '%a%a%a%a%a%b'`.

## The obvious matcher

Recursion mirrors the definition. To match `text` against `pattern`:

- if the pattern is empty, match only the empty text;
- if the pattern starts with `%`, try matching the rest of the pattern against **every suffix** of the text, and succeed if any does;
- if it starts with `_`, consume one character of each;
- otherwise the first characters must be equal.

It is correct, and it is exponential. With `k` percent signs and text of length `n`, the `%` case branches `n` ways and each branch meets the next `%`: about `n^k` calls. A pattern with a dozen percents against a few thousand characters never returns, and a database that accepts user patterns has just been given a denial-of-service lever.

## Why the branching is wasted

When the recursion for the first `%` has tried "this `%` swallows `i` characters" and the rest of the pattern failed, nothing the *second* `%` could do will make the first choice work better. The second `%` can swallow anything the first one left. So only the **last** `%` seen needs a retry: if the rest of the pattern fails at some position, go back to the last `%` and let it swallow one more character. Earlier percents never need to be reconsidered.

That is the whole algorithm, with two cursors into the text and the pattern and one remembered pair "(pattern position after the last `%`, text position it started from)":

1. If the pattern has a literal or `_` that matches here, advance both.
2. If the pattern has `%`, remember it (pattern position just after it, current text position) and advance only the pattern: let it match nothing first.
3. If nothing matches and a `%` was remembered, restore the pattern to just after it and advance the *text* start by one: the `%` swallows one more character.
4. If nothing matches and there is no remembered `%`, fail.
5. When the text is used up, the rest of the pattern must be only `%`.

Each text character is "swallowed" at most once per retry, and a retry costs a walk through the pattern, so the worst case is `n * m` steps, and typical patterns are linear.

## Details that bite

- **Characters, not bytes.** `_` matches one *character*; `'é' like '_'` is true although `é` is two bytes in UTF-8. Iterate `chars()` and never index a `&str` by byte position.
- **Case.** `LIKE` is case sensitive in PostgreSQL (`ILIKE` is not) and, on some collations, not in other systems. Say which one yours is.
- **Escapes.** A backslash before `%`, `_` or a backslash makes it literal. A pattern that ends with a lone backslash is either an error (PostgreSQL) or a literal backslash; pick one and test it.
- **NULL.** `x like NULL` and `NULL like 'a%'` are NULL, not false. The same holds for `NOT LIKE`.
- **Indexes.** `like 'abc%'` can use a B+ tree range scan (`>= 'abc' and < 'abd'`); `like '%abc'` cannot. That is the reason a database cares about the *shape* of a pattern, not just its result.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `const char *` walked with two pointers | `Vec<char>` and two indexes; or `chars().peekable()` |
| `std::regex` (slow, and backtracking) | not used; a hand-written matcher is faster and has a known bound |
| `std::string::find` for literal runs | `str::find`; useful to jump between `%` segments |

## In real code

### Using it: the two-cursor matcher against the obvious one

```rust test
#[derive(Clone, Copy)]
enum Tok {
    Lit(char),
    One,
    Many,
}

fn parse(pattern: &str) -> Vec<Tok> {
    let mut out = vec![];
    let mut chars = pattern.chars();
    while let Some(c) = chars.next() {
        out.push(match c {
            '%' => Tok::Many,
            '_' => Tok::One,
            '\\' => Tok::Lit(chars.next().unwrap_or('\\')),
            c => Tok::Lit(c),
        });
    }
    out
}

/// Linear in practice, at most text * pattern steps.
fn like(text: &str, pattern: &str) -> bool {
    let p = parse(pattern);
    let t: Vec<char> = text.chars().collect();
    let (mut i, mut j) = (0, 0);
    let mut back: Option<(usize, usize)> = None; // (pattern after the last %, text position it started at)
    while i < t.len() {
        match p.get(j) {
            Some(Tok::Many) => {
                back = Some((j + 1, i));
                j += 1;
            }
            Some(Tok::One) => {
                i += 1;
                j += 1;
            }
            Some(Tok::Lit(c)) if *c == t[i] => {
                i += 1;
                j += 1;
            }
            _ => match back {
                Some((pj, pi)) => {
                    // let the last % swallow one more character
                    j = pj;
                    i = pi + 1;
                    back = Some((pj, pi + 1));
                }
                None => return false,
            },
        }
    }
    p[j..].iter().all(|tok| matches!(tok, Tok::Many))
}

/// The definition, written as recursion: obviously right, exponential.
fn naive(t: &[char], p: &[Tok]) -> bool {
    match p.first() {
        None => t.is_empty(),
        Some(Tok::Many) => (0..=t.len()).any(|k| naive(&t[k..], &p[1..])),
        Some(Tok::One) => !t.is_empty() && naive(&t[1..], &p[1..]),
        Some(Tok::Lit(c)) => t.first() == Some(c) && naive(&t[1..], &p[1..]),
    }
}

#[test]
fn the_basic_wildcards() {
    assert!(like("apple", "a%"));
    assert!(like("apple", "%pl%"));
    assert!(like("apple", "a___e"));
    assert!(!like("apple", "a__e"), "_ is exactly one character");
    assert!(like("", "%"));
    assert!(like("é", "_"), "a character, not a byte");
    assert!(like("100%", "100\\%") && !like("1000", "100\\%"), "an escaped percent is literal");
}

#[test]
fn a_hostile_pattern_finishes() {
    let text = "a".repeat(3000);
    assert!(!like(&text, "%a%a%a%a%a%a%a%a%a%a%a%b"), "no b: it must fail quickly, not in 3000^11 steps");
}

#[test]
fn agrees_with_the_definition_on_small_cases() {
    let alphabet = ['a', 'b'];
    let mut texts = vec![String::new()];
    for _ in 0..4 {
        let next: Vec<String> = texts.iter().flat_map(|t| alphabet.iter().map(move |c| format!("{t}{c}"))).collect();
        texts.extend(next);
    }
    let patterns = ["", "%", "a%", "%b", "a%b", "_a", "%a%b%", "a_%", "%%a", "b%a%"];
    for t in &texts {
        for p in patterns {
            let chars: Vec<char> = t.chars().collect();
            assert_eq!(like(t, p), naive(&chars, &parse(p)), "{t:?} like {p:?}");
        }
    }
}
```

### In the exercises

- **3i-04:** `like_matches` is `like` above, and `LikeExpression` calls it for each row; the test with a long text and twelve `%` is the hostile pattern.

### Where it is used

- **PostgreSQL**: `like_match.c` (`MatchText`) is this algorithm: the comment in the source explains why only the last `%` needs a retry; it also takes a shortcut when the pattern ends in `%`.
- **SQLite**: `patternCompare` in `func.c`.
- **Shell globbing / `fnmatch`**: the same two wildcards (`*` and `?`) and the same remembered-star technique.
