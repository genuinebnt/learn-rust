from author import T, write_track

P = []

# Rust helper for hidden tests: word `i` written in base 10 with the letters a..j, `len` letters long.
# Tries built from these share prefixes, so 10⁵ words stay around 10⁵ nodes.
BASE10 = """
fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
"""

# ---------------------------------------------------------------- first tries (easy)

P.append(dict(
    slug="longest-common-prefix", title="Longest common prefix", level="easy", stage="first-tries", tags=["&str", "chars"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Adobe", "Bloomberg"],
    teaches=["Return a slice of the input (`&'a str`) instead of building a new `String`.",
             "Compare `chars()`, not bytes, so the prefix never ends inside a character."],
    statement="""
        Return the longest string that every string in `strs` starts with, as a slice of the first string.
        An empty list, or no shared first character, gives `""`.

        Strings can hold any Unicode text: compare whole characters, so the answer never ends in the middle of one.
    """,
    examples=[("strs = [\"flower\", \"flow\", \"flight\"]", "\"fl\""), ("strs = [\"dog\", \"racecar\", \"car\"]", "\"\"")],
    constraints=["0 ≤ strs.len() ≤ 10⁵", "total length ≤ 2·10⁶ bytes"],
    starter="""
        pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
            todo!()
        }
    """,
    solution="""
        pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
            let Some((&first, rest)) = strs.split_first() else {
                return "";
            };
            let mut prefix = first;
            for s in rest {
                // Byte length of the shared characters, so the cut is always on a char boundary.
                let len: usize = prefix.chars().zip(s.chars()).take_while(|(a, b)| a == b).map(|(a, _)| a.len_utf8()).sum();
                prefix = &prefix[..len];
            }
            prefix
        }
    """,
    visible=[
        T("leetcode_flower", "strs = [\"flower\", \"flow\", \"flight\"]", 'longest_common_prefix(&["flower", "flow", "flight"])', '"fl"'),
        T("leetcode_no_prefix", "strs = [\"dog\", \"racecar\", \"car\"]", 'longest_common_prefix(&["dog", "racecar", "car"])', '""'),
        T("empty_list", "strs = []", "longest_common_prefix(&[])", '""'),
        T("single_string", "strs = [\"alone\"]", 'longest_common_prefix(&["alone"])', '"alone"'),
        T("empty_string_inside", "strs = [\"abc\", \"\"]", 'longest_common_prefix(&["abc", ""])', '""'),
        T("whole_word_is_the_prefix", "strs = [\"ab\", \"abc\", \"abcd\"]", 'longest_common_prefix(&["ab", "abc", "abcd"])', '"ab"'),
        T("unicode_characters", "strs = [\"héllo\", \"hélium\"]", 'longest_common_prefix(&["héllo", "hélium"])', '"hél"'),
    ],
    hidden=[
        T("single_empty", "strs = [\"\"]", 'longest_common_prefix(&[""])', '""'),
        T("identical", "strs = [\"same\", \"same\", \"same\"]", 'longest_common_prefix(&["same", "same", "same"])', '"same"'),
        T("accents_share_a_byte", "strs = [\"café\", \"cafè\"] (é and è share their first byte)", 'longest_common_prefix(&["café", "cafè"])', '"caf"'),
        T("emoji", "strs = [\"🦀rust\", \"🦀rest\"]", 'longest_common_prefix(&["🦀rust", "🦀rest"])', '"🦀r"'),
        T("shortest_in_the_middle", "strs = [\"ab\", \"a\", \"ab\"]", 'longest_common_prefix(&["ab", "a", "ab"])', '"a"'),
        T("case_matters", "strs = [\"Ab\", \"ab\"]", 'longest_common_prefix(&["Ab", "ab"])', '""'),
        T("differs_only_in_last_string", "strs = [\"prefix\", \"prefix\", \"prelude\"]", 'longest_common_prefix(&["prefix", "prefix", "prelude"])', '"pre"'),
        T("first_is_longest", "strs = [\"interview\", \"inter\", \"internet\"]", 'longest_common_prefix(&["interview", "inter", "internet"])', '"inter"'),
        T("spaces_count", "strs = [\"a b\", \"a c\"]", 'longest_common_prefix(&["a b", "a c"])', '"a "'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1001);
            for _ in 0..300 {
                let n = rng.below(5);
                let mut strs: Vec<String> = Vec::new();
                for _ in 0..n {
                    let len = rng.below(6);
                    strs.push(rng.string(len, "abé"));
                }
                let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
                let chars: Vec<Vec<char>> = strs.iter().map(|s| s.chars().collect()).collect();
                let mut k = 0;
                while n > 0 && chars.iter().all(|c| k < c.len() && c[k] == chars[0][k]) {
                    k += 1;
                }
                let want: String = if n == 0 { String::new() } else { chars[0][..k].iter().collect() };
                check!(format!("strs = {refs:?}"), longest_common_prefix(&refs).to_string(), want);
            }
        }

        #[test]
        fn scale_100k_strings() {
            let strs: Vec<String> = (0..100_000).map(|i| format!("common-prefix-{i:06}")).collect();
            let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
            check!("strs = [\\"common-prefix-000000\\", …, \\"common-prefix-099999\\"]", longest_common_prefix(&refs), "common-prefix-0");
        }
        """,
    ],
    wrong=dict(
        byte_prefix="""
            pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
                let Some((&first, rest)) = strs.split_first() else {
                    return "";
                };
                let mut prefix = first;
                for s in rest {
                    let len = prefix.bytes().zip(s.bytes()).take_while(|(a, b)| a == b).count();
                    prefix = &prefix[..len];
                }
                prefix
            }
        """,
        first_and_last_only="""
            pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
                let (Some(&first), Some(&last)) = (strs.first(), strs.last()) else {
                    return "";
                };
                let len: usize = first.chars().zip(last.chars()).take_while(|(a, b)| a == b).map(|(a, _)| a.len_utf8()).sum();
                &first[..len]
            }
        """,
    ),
    hints=[("approach", "Start with the first string as the answer and shorten it against each of the others."),
           ("rust", "`a.chars().zip(b.chars()).take_while(|(x, y)| x == y)` walks the shared characters; sum their `len_utf8()` to get a byte length you can slice with."),
           ("edge case", "`\"café\"` and `\"cafè\"` share a first byte inside the last character. Slicing at a byte count there panics.")],
    notes=("The answer is a prefix of the first string, so it can be a slice of it: no allocation. Shortening against each string touches every character at most once. Comparing `char`s keeps the cut on a character boundary.", "O(total length)", "O(1)"),
    follow_up="If you had to answer this query many times for a changing set of strings, what structure would you keep?",
    related=["S2", "L3"],
))

P.append(dict(
    slug="implement-trie", title="Implement trie", level="easy", stage="first-tries", tags=["trie", "Box", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg", "Uber"],
    teaches=["A node is `[Option<Box<Node>>; 26]` plus an end-of-word flag.",
             "`get_or_insert_with` creates a child and hands back a cursor in one step."],
    statement="""
        Build a prefix tree over lowercase ASCII words:

        - `insert(word)` stores `word` (inserting it again changes nothing);
        - `search(word)` is `true` if `word` itself was inserted;
        - `starts_with(prefix)` is `true` if some inserted word starts with `prefix`.

        A prefix of a stored word is not a stored word: after `insert("apple")`, `search("app")` is `false`.
        The empty prefix walks nowhere, so `starts_with("")` is always `true`; `search("")` is `true` only after `insert("")`.
    """,
    examples=[("insert \"apple\"; search \"apple\", search \"app\", starts_with \"app\"", "true, false, true")],
    constraints=["words and prefixes: 0–100 lowercase ASCII letters", "up to 10⁵ calls"],
    starter="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            end: bool,
        }

        #[derive(Default)]
        pub struct Trie {
            root: Node,
        }

        impl Trie {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, word: &str) {
                todo!()
            }

            pub fn search(&self, word: &str) -> bool {
                todo!()
            }

            pub fn starts_with(&self, prefix: &str) -> bool {
                todo!()
            }
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            end: bool,
        }

        #[derive(Default)]
        pub struct Trie {
            root: Node,
        }

        impl Trie {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, word: &str) {
                let mut node = &mut self.root;
                for b in word.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                }
                node.end = true;
            }

            /// The node `s` leads to, if the path exists.
            fn walk(&self, s: &str) -> Option<&Node> {
                let mut node = &self.root;
                for b in s.bytes() {
                    node = node.children[(b - b'a') as usize].as_deref()?;
                }
                Some(node)
            }

            pub fn search(&self, word: &str) -> bool {
                self.walk(word).is_some_and(|n| n.end)
            }

            pub fn starts_with(&self, prefix: &str) -> bool {
                self.walk(prefix).is_some()
            }
        }
    """,
    visible=[
        T("leetcode_apple", "insert \"apple\"; search \"apple\", search \"app\", starts_with \"app\"; insert \"app\"; search \"app\"",
          "(a, b, c, t.search(\"app\"))", "(true, false, true, true)",
          setup='let mut t = Trie::new();\nt.insert("apple");\nlet (a, b, c) = (t.search("apple"), t.search("app"), t.starts_with("app"));\nt.insert("app");'),
        T("empty_trie", "new trie; search \"a\", starts_with \"a\"", '(t.search("a"), t.starts_with("a"))', "(false, false)", setup="let t = Trie::new();"),
        T("prefix_is_not_a_word", "insert \"apple\"; search \"app\"", 't.search("app")', "false", setup='let mut t = Trie::new();\nt.insert("apple");'),
        T("word_is_its_own_prefix", "insert \"apple\"; starts_with \"apple\"", 't.starts_with("apple")', "true", setup='let mut t = Trie::new();\nt.insert("apple");'),
        T("longer_than_any_word", "insert \"app\"; search \"apple\", starts_with \"apple\"", '(t.search("apple"), t.starts_with("apple"))', "(false, false)",
          setup='let mut t = Trie::new();\nt.insert("app");'),
        T("empty_prefix", "new trie; starts_with \"\", search \"\"", '(t.starts_with(""), t.search(""))', "(true, false)", setup="let t = Trie::new();"),
    ],
    hidden=[
        T("insert_empty_word", "insert \"\"; search \"\"", 't.search("")', "true", setup='let mut t = Trie::new();\nt.insert("");'),
        T("insert_twice", "insert \"a\" twice; search \"a\"", 't.search("a")', "true", setup='let mut t = Trie::new();\nt.insert("a");\nt.insert("a");'),
        T("single_letters", "insert \"a\", \"z\"; search a, z, b", '(t.search("a"), t.search("z"), t.search("b"))', "(true, true, false)",
          setup='let mut t = Trie::new();\nt.insert("a");\nt.insert("z");'),
        T("branching", "insert \"car\", \"cat\", \"cart\"; search ca, car, cat, cart, carts",
          '(t.search("ca"), t.search("car"), t.search("cat"), t.search("cart"), t.search("carts"))', "(false, true, true, true, false)",
          setup='let mut t = Trie::new();\nfor w in ["car", "cat", "cart"] {\n    t.insert(w);\n}'),
        T("shorter_word_after_longer", "insert \"cart\", then \"car\"; search car, starts_with cart",
          '(t.search("car"), t.starts_with("cart"))', "(true, true)", setup='let mut t = Trie::new();\nt.insert("cart");\nt.insert("car");'),
        T("longer_word_keeps_shorter", "insert \"car\", then \"cart\"; search car", 't.search("car")', "true", setup='let mut t = Trie::new();\nt.insert("car");\nt.insert("cart");'),
        T("different_branch", "insert \"abc\"; starts_with \"abd\", \"b\"", '(t.starts_with("abd"), t.starts_with("b"))', "(false, false)",
          setup='let mut t = Trie::new();\nt.insert("abc");'),
        T("long_word", "insert 'z' × 100; search it and 'z' × 99", "(t.search(&long), t.search(&long[..99]), t.starts_with(&long[..99]))", "(true, false, true)",
          setup='let mut t = Trie::new();\nlet long = "z".repeat(100);\nt.insert(&long);'),
        T("whole_alphabet", "insert every letter a..z; search each", "all", "true",
          setup='let mut t = Trie::new();\nlet letters: Vec<String> = (b\'a\'..=b\'z\').map(|b| (b as char).to_string()).collect();\nfor w in &letters {\n    t.insert(w);\n}\nlet all = letters.iter().all(|w| t.search(w));'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1002);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let w = rng.string(len, "abc");
                    match rng.below(3) {
                        0 => {
                            t.insert(&w);
                            log.push(format!("insert {w:?}"));
                            words.push(w);
                        }
                        1 => {
                            log.push(format!("search {w:?}"));
                            check!(log.join(", "), t.search(&w), words.contains(&w));
                        }
                        _ => {
                            log.push(format!("starts_with {w:?}"));
                            check!(log.join(", "), t.starts_with(&w), w.is_empty() || words.iter().any(|x| x.starts_with(w.as_str())));
                        }
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut t = Trie::new();
            for i in 0..100_000 {
                t.insert(&base10(i, 5));
            }
            let mut found = 0;
            for i in 0..100_000 {
                found += t.search(&base10(i, 5)) as usize + t.starts_with(&base10(i, 3)) as usize + t.search(&base10(i, 4)) as usize;
            }
            check!("insert all 100000 five-letter words over a..j; search each, starts_with its first 3 letters, search a 4-letter word", found, 200_000);
        }
        """ + BASE10,
    ],
    wrong=dict(
        list_of_words="""
            #[derive(Default)]
            pub struct Trie {
                words: Vec<String>,
            }

            impl Trie {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, word: &str) {
                    self.words.push(word.to_string());
                }

                pub fn search(&self, word: &str) -> bool {
                    self.words.iter().any(|w| w == word)
                }

                pub fn starts_with(&self, prefix: &str) -> bool {
                    prefix.is_empty() || self.words.iter().any(|w| w.starts_with(prefix))
                }
            }
        """,
        search_ignores_end="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
            }

            #[derive(Default)]
            pub struct Trie {
                root: Node,
            }

            impl Trie {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, word: &str) {
                    let mut node = &mut self.root;
                    for b in word.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    }
                }

                fn walk(&self, s: &str) -> Option<&Node> {
                    let mut node = &self.root;
                    for b in s.bytes() {
                        node = node.children[(b - b'a') as usize].as_deref()?;
                    }
                    Some(node)
                }

                pub fn search(&self, word: &str) -> bool {
                    self.walk(word).is_some()
                }

                pub fn starts_with(&self, prefix: &str) -> bool {
                    self.walk(prefix).is_some()
                }
            }
        """,
    ),
    hints=[("approach", "Each node has one slot per letter and a flag saying a word ends here. Insert walks down, creating missing nodes; search walks down and checks the flag."),
           ("rust", "`node = node.children[i].get_or_insert_with(Default::default);` moves a `&mut` cursor one level down. For lookups, `children[i].as_deref()?` turns `&Option<Box<Node>>` into `Option<&Node>`."),
           ("edge case", "`search` and `starts_with` share the walk; they differ only in whether the last node must end a word.")],
    notes=("A trie shares common prefixes, so every operation costs O(length of the word) no matter how many words are stored. `[Option<Box<Node>>; 26]` gives O(1) child lookup; `derive(Default)` builds an empty node because arrays up to 32 elements implement `Default`.", "O(L) per call", "O(total letters inserted × 26)"),
    follow_up="Twenty-six pointers per node is a lot when most are `None`. What would you use instead, and what does each choice cost?",
    related=["S7", "S4"],
))

P.append(dict(
    slug="fix-index-string-by-position", title="Fix: indexing a String by position", mode="fix", level="easy", stage="first-tries", tags=["E0277", "chars"],
    teaches=["`str` can't be indexed by `usize`: a position in characters isn't a position in bytes.",
             "`chars().nth(i)` walks to the i-th character and returns `None` past the end."],
    statement="""
        `nth_letter` should return the character at position `i` of `word` (counting characters, not bytes),
        or `None` when `word` has `i` characters or fewer. It doesn't compile: `str` cannot be indexed by an integer (E0277).
    """,
    examples=[("word = \"héllo\", i = 1", "Some('é')"), ("word = \"hello\", i = 5", "None")],
    starter="""
        /// The character at position `i` (in characters), or `None` past the end.
        pub fn nth_letter(word: &str, i: usize) -> Option<char> {
            if i < word.len() { Some(word[i]) } else { None }
        }
    """,
    solution="""
        /// The character at position `i` (in characters), or `None` past the end.
        pub fn nth_letter(word: &str, i: usize) -> Option<char> {
            word.chars().nth(i)
        }
    """,
    rules=dict(lines=2, unsafe=True),
    visible=[
        T("ascii", "word = \"hello\", i = 1", 'nth_letter("hello", 1)', "Some('e')"),
        T("past_the_end", "word = \"hello\", i = 5", 'nth_letter("hello", 5)', "None"),
        T("empty", "word = \"\", i = 0", 'nth_letter("", 0)', "None"),
        T("accented_letter", "word = \"héllo\", i = 1", 'nth_letter("héllo", 1)', "Some('é')"),
        T("after_an_accent", "word = \"héllo\", i = 2 (é is 2 bytes, but 1 character)", 'nth_letter("héllo", 2)', "Some('l')"),
        T("last_character", "word = \"héllo\", i = 4 (5 characters, 6 bytes)", 'nth_letter("héllo", 4)', "Some('o')"),
    ],
    hidden=[
        T("first", "word = \"rust\", i = 0", 'nth_letter("rust", 0)', "Some('r')"),
        T("crab", "word = \"a🦀b\", i = 1", 'nth_letter("a🦀b", 1)', "Some('🦀')"),
        T("after_crab", "word = \"a🦀b\", i = 2", 'nth_letter("a🦀b", 2)', "Some('b')"),
        T("byte_length_is_not_char_length", "word = \"héllo\", i = 5 (6 bytes, 5 characters)", 'nth_letter("héllo", 5)', "None"),
        T("huge_index", "word = \"abc\", i = usize::MAX", 'nth_letter("abc", usize::MAX)', "None"),
        T("cjk", "word = \"日本語\", i = 2", 'nth_letter("日本語", 2)', "Some('語')"),
        T("space", "word = \"a b\", i = 1", 'nth_letter("a b", 1)', "Some(' ')"),
        T("single", "word = \"x\", i = 0", 'nth_letter("x", 0)', "Some('x')"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1003);
            for _ in 0..300 {
                let len = rng.below(6);
                let word = rng.string(len, "aé🦀z");
                let i = rng.below(8);
                let chars: Vec<char> = word.chars().collect();
                check!(format!("word = {word:?}, i = {i}"), nth_letter(&word, i), chars.get(i).copied());
            }
        }
        """,
    ],
    wrong=dict(
        byte_as_char="""
            /// The character at position `i` (in characters), or `None` past the end.
            pub fn nth_letter(word: &str, i: usize) -> Option<char> {
                if i < word.len() { Some(word.as_bytes()[i] as char) } else { None }
            }
        """,
    ),
    hints=[("rust", "UTF-8 characters take 1 to 4 bytes, so Rust won't guess what `word[i]` means. Ask for characters explicitly with `word.chars()`."),
           ("edge case", "`word.len()` counts bytes. `\"héllo\".len()` is 6, but it has 5 characters.")],
    notes=("`chars().nth(i)` decodes characters from the start, so it's O(i), and it already returns `None` past the end, which makes the length check unnecessary. If you need many positions, collect `chars()` into a `Vec<char>` once.", "O(i)", "O(1)"),
    follow_up="When is indexing bytes (`word.as_bytes()[i]`) the right choice, and what must you know about the input first?",
    related=["S2", "L2"],
))

P.append(dict(
    slug="longest-word-in-dictionary", title="Longest word in dictionary", level="easy", stage="first-tries", tags=["trie", "DFS"],
    companies=["Amazon", "Google"],
    teaches=["Walk a trie only through nodes that end a word.", "Visiting children in `a..z` order gives the lexicographic tie-break for free."],
    statement="""
        A word can be *built* if you can type it one letter at a time and every prefix along the way is also in `words`
        (for `"abc"`: `"a"`, `"ab"` and `"abc"` must all be there).

        Return the longest word that can be built. On a tie, return the one that comes first alphabetically. If none can be built, return `""`.
        Words are non-empty lowercase ASCII.
    """,
    examples=[("words = [\"w\", \"wo\", \"wor\", \"worl\", \"world\"]", "\"world\""),
              ("words = [\"a\", \"banana\", \"app\", \"appl\", \"ap\", \"apply\", \"apple\"]", "\"apple\"")],
    constraints=["0 ≤ words.len() ≤ 2·10⁵", "1 ≤ words[i].len() ≤ 30"],
    starter="""
        pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
            todo!()
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            word: Option<usize>,
        }

        pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
            let mut root = Node::default();
            for (i, w) in words.iter().enumerate() {
                let mut node = &mut root;
                for b in w.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                }
                node.word = Some(i);
            }
            // Depth-first through nodes that end a word; each one is buildable.
            let mut best = "";
            let mut stack = vec![&root];
            while let Some(node) = stack.pop() {
                for child in node.children.iter().flatten() {
                    if let Some(i) = child.word {
                        let w = words[i];
                        if w.len() > best.len() || (w.len() == best.len() && w < best) {
                            best = w;
                        }
                        stack.push(child);
                    }
                }
            }
            best
        }
    """,
    visible=[
        T("leetcode_world", "words = [\"w\", \"wo\", \"wor\", \"worl\", \"world\"]", 'longest_word(&["w", "wo", "wor", "worl", "world"])', '"world"'),
        T("leetcode_tie_goes_to_apple", "words = [\"a\", \"banana\", \"app\", \"appl\", \"ap\", \"apply\", \"apple\"]",
          'longest_word(&["a", "banana", "app", "appl", "ap", "apply", "apple"])', '"apple"'),
        T("empty", "words = []", "longest_word(&[])", '""'),
        T("nothing_buildable", "words = [\"ab\", \"abc\"] (no one-letter word)", 'longest_word(&["ab", "abc"])', '""'),
        T("every_prefix_needed", "words = [\"b\", \"ab\", \"abc\"] (\"a\" is missing)", 'longest_word(&["b", "ab", "abc"])', '"b"'),
        T("single_letters_tie", "words = [\"c\", \"b\", \"a\"]", 'longest_word(&["c", "b", "a"])', '"a"'),
    ],
    hidden=[
        T("single", "words = [\"z\"]", 'longest_word(&["z"])', '"z"'),
        T("duplicates", "words = [\"a\", \"a\", \"ab\", \"ab\"]", 'longest_word(&["a", "a", "ab", "ab"])', '"ab"'),
        T("gap_in_the_chain", "words = [\"a\", \"ab\", \"abcd\"]", 'longest_word(&["a", "ab", "abcd"])', '"ab"'),
        T("longer_beats_smaller", "words = [\"a\", \"b\", \"ba\", \"bac\"]", 'longest_word(&["a", "b", "ba", "bac"])', '"bac"'),
        T("tie_on_long_words", "words = [\"y\", \"yz\", \"x\", \"xy\"]", 'longest_word(&["y", "yz", "x", "xy"])', '"xy"'),
        T("input_order_irrelevant", "words = [\"world\", \"worl\", \"wor\", \"wo\", \"w\"]", 'longest_word(&["world", "worl", "wor", "wo", "w"])', '"world"'),
        T("unbuildable_longer", "words = [\"k\", \"ki\", \"kiwi\", \"kiw\", \"kiwis\", \"bananas\"]", 'longest_word(&["k", "ki", "kiwi", "kiw", "kiwis", "bananas"])', '"kiwis"'),
        T("thirty_letters", "words = every prefix of 'z' × 30", "longest_word(&refs)", '"z".repeat(30)',
          setup='let words: Vec<String> = (1..=30).map(|n| "z".repeat(n)).collect();\nlet refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1004);
            for _ in 0..300 {
                let n = rng.below(10);
                let mut words: Vec<String> = Vec::new();
                for _ in 0..n {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "abc"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut want = "";
                for &w in &refs {
                    let buildable = (1..=w.len()).all(|k| refs.contains(&&w[..k]));
                    if buildable && (w.len() > want.len() || (w.len() == want.len() && w < want)) {
                        want = w;
                    }
                }
                check!(format!("words = {refs:?}"), longest_word(&refs), want);
            }
        }

        #[test]
        fn scale_111k_words() {
            // Every word of 1 to 5 letters over a..j except "aaaa", so nothing under "aaaa" can be built.
            let mut words: Vec<String> = Vec::new();
            for len in 1..=5 {
                let count = 10usize.pow(len as u32);
                for i in 0..count {
                    let w = base10(i, len);
                    if w != "aaaa" {
                        words.push(w);
                    }
                }
            }
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("words = every 1–5 letter word over a..j except \\"aaaa\\" (111109 words)", longest_word(&refs), "aaaba");
        }
        """ + BASE10,
    ],
    wrong=dict(
        only_parent_checked="""
            use std::collections::HashSet;

            pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
                let set: HashSet<&str> = words.iter().copied().collect();
                let mut best = "";
                for &w in words {
                    let ok = w.len() == 1 || set.contains(&w[..w.len() - 1]);
                    if ok && (w.len() > best.len() || (w.len() == best.len() && w < best)) {
                        best = w;
                    }
                }
                best
            }
        """,
        tie_goes_to_last="""
            use std::collections::HashSet;

            pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
                let set: HashSet<&str> = words.iter().copied().collect();
                let mut best = "";
                for &w in words {
                    if (1..=w.len()).all(|k| set.contains(&w[..k])) && w.len() >= best.len() {
                        best = w;
                    }
                }
                best
            }
        """,
        linear_lookups="""
            pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
                let mut best = "";
                for &w in words {
                    if (1..=w.len()).all(|k| words.contains(&&w[..k])) && (w.len() > best.len() || (w.len() == best.len() && w < best)) {
                        best = w;
                    }
                }
                best
            }
        """,
    ),
    hints=[("approach", "Put every word in a trie, marking where words end. A word is buildable exactly when every node on its path is marked."),
           ("rust", "Keep the word's index in the node (`Option<usize>`), then walk with a stack, pushing only marked children. Return `words[i]`, a slice of the input."),
           ("edge case", "Checking only the one-letter-shorter prefix isn't enough: `\"abc\"` with `\"ab\"` but no `\"a\"` can't be built.")],
    notes=("Walking only through marked nodes visits exactly the buildable words. Comparing length first and then the word itself handles ties. A `HashSet` of words plus a check of every prefix works too, at O(L²) per word for the slices.", "O(total letters)", "O(total letters × 26)"),
    follow_up="How would you return every longest buildable word instead of one?",
    related=["S4", "D9"],
))

P.append(dict(
    slug="map-sum-pairs", title="Map sum pairs", level="easy", stage="first-tries", tags=["trie", "HashMap", "i64"],
    companies=["Amazon"],
    teaches=["Store an aggregate in every trie node so a prefix query is one walk.", "Overwrites apply a delta, which needs the old value from a `HashMap`."],
    statement="""
        `MapSum` maps lowercase keys to values.

        - `insert(key, val)` sets `key` to `val`, replacing any earlier value for that key;
        - `sum(prefix)` returns the total of the values of every key that starts with `prefix` (0 if none).

        Values can be negative, and a sum can exceed `i32`.
    """,
    examples=[("insert(\"apple\", 3); sum(\"ap\"); insert(\"app\", 2); sum(\"ap\")", "3, then 5")],
    constraints=["keys: 1–50 lowercase ASCII letters", "values: any i32", "up to 10⁵ calls"],
    starter="""
        #[derive(Default)]
        pub struct MapSum {
            // your fields here
        }

        impl MapSum {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, key: &str, val: i32) {
                todo!()
            }

            pub fn sum(&self, prefix: &str) -> i64 {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::HashMap;

        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            /// Sum of the values of every key at or below this node.
            total: i64,
        }

        #[derive(Default)]
        pub struct MapSum {
            root: Node,
            values: HashMap<String, i32>,
        }

        impl MapSum {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, key: &str, val: i32) {
                let old = self.values.insert(key.to_string(), val).unwrap_or(0);
                let delta = i64::from(val) - i64::from(old);
                let mut node = &mut self.root;
                node.total += delta;
                for b in key.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    node.total += delta;
                }
            }

            pub fn sum(&self, prefix: &str) -> i64 {
                let mut node = &self.root;
                for b in prefix.bytes() {
                    match &node.children[(b - b'a') as usize] {
                        Some(child) => node = child,
                        None => return 0,
                    }
                }
                node.total
            }
        }
    """,
    visible=[
        T("leetcode_apple", "insert(\"apple\", 3); sum(\"ap\"); insert(\"app\", 2); sum(\"ap\")", "(first, m.sum(\"ap\"))", "(3, 5)",
          setup='let mut m = MapSum::new();\nm.insert("apple", 3);\nlet first = m.sum("ap");\nm.insert("app", 2);'),
        T("overwrite_replaces", "insert(\"apple\", 3); insert(\"apple\", 2); sum(\"ap\")", 'm.sum("ap")', "2",
          setup='let mut m = MapSum::new();\nm.insert("apple", 3);\nm.insert("apple", 2);'),
        T("empty_map", "new map; sum(\"a\")", 'm.sum("a")', "0", setup="let m = MapSum::new();"),
        T("prefix_is_the_whole_key", "insert(\"apple\", 3); sum(\"apple\")", 'm.sum("apple")', "3", setup='let mut m = MapSum::new();\nm.insert("apple", 3);'),
        T("no_key_matches", "insert(\"apple\", 3); sum(\"b\"), sum(\"apples\")", '(m.sum("b"), m.sum("apples"))', "(0, 0)",
          setup='let mut m = MapSum::new();\nm.insert("apple", 3);'),
        T("empty_prefix_sums_everything", "insert(\"a\", 1), (\"b\", 2), (\"c\", -4); sum(\"\")", 'm.sum("")', "-1",
          setup='let mut m = MapSum::new();\nm.insert("a", 1);\nm.insert("b", 2);\nm.insert("c", -4);'),
    ],
    hidden=[
        T("past_i32", "insert 3 keys with i32::MAX; sum(\"k\")", 'm.sum("k")', "3 * i64::from(i32::MAX)",
          setup='let mut m = MapSum::new();\nfor k in ["ka", "kb", "kc"] {\n    m.insert(k, i32::MAX);\n}'),
        T("negatives", "insert(\"ab\", -5), (\"abc\", 2); sum(\"ab\")", 'm.sum("ab")', "-3", setup='let mut m = MapSum::new();\nm.insert("ab", -5);\nm.insert("abc", 2);'),
        T("overwrite_to_zero", "insert(\"x\", 7); insert(\"x\", 0); sum(\"x\")", 'm.sum("x")', "0", setup='let mut m = MapSum::new();\nm.insert("x", 7);\nm.insert("x", 0);'),
        T("overwrite_min_to_max", "insert(\"x\", i32::MIN); insert(\"x\", i32::MAX); sum(\"\")", 'm.sum("")', "i64::from(i32::MAX)",
          setup='let mut m = MapSum::new();\nm.insert("x", i32::MIN);\nm.insert("x", i32::MAX);'),
        T("overwrite_leaves_others", "insert(\"a\", 1), (\"ab\", 2), (\"a\", 10); sum(\"a\"), sum(\"ab\")", '(m.sum("a"), m.sum("ab"))', "(12, 2)",
          setup='let mut m = MapSum::new();\nm.insert("a", 1);\nm.insert("ab", 2);\nm.insert("a", 10);'),
        T("longer_prefix_than_key", "insert(\"ab\", 4); sum(\"abc\")", 'm.sum("abc")', "0", setup='let mut m = MapSum::new();\nm.insert("ab", 4);'),
        T("sibling_keys", "insert(\"car\", 1), (\"cat\", 2), (\"cup\", 4); sum(\"ca\"), sum(\"c\")", '(m.sum("ca"), m.sum("c"))', "(3, 7)",
          setup='let mut m = MapSum::new();\nm.insert("car", 1);\nm.insert("cat", 2);\nm.insert("cup", 4);'),
        T("same_value_again", "insert(\"k\", 5) twice; sum(\"k\")", 'm.sum("k")', "5", setup='let mut m = MapSum::new();\nm.insert("k", 5);\nm.insert("k", 5);'),
        """
        #[test]
        fn random_vs_model() {
            use std::collections::HashMap;
            let mut rng = anneal_prelude::Rng::new(1005);
            for _ in 0..300 {
                let mut m = MapSum::new();
                let mut model: HashMap<String, i32> = HashMap::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let key = rng.string(len, "ab");
                    if rng.bool() && !key.is_empty() {
                        let val = rng.int(-9, 9) as i32;
                        m.insert(&key, val);
                        log.push(format!("insert({key:?}, {val})"));
                        model.insert(key, val);
                    } else {
                        log.push(format!("sum({key:?})"));
                        let want: i64 = model.iter().filter(|(k, _)| k.starts_with(key.as_str())).map(|(_, &v)| i64::from(v)).sum();
                        check!(log.join(", "), m.sum(&key), want);
                    }
                }
            }
        }

        #[test]
        fn scale_100k_keys_and_sums() {
            let mut m = MapSum::new();
            for i in 0..100_000 {
                m.insert(&base10(i, 5), 1_000);
            }
            let mut total = 0i64;
            for i in 0..100_000 {
                total += m.sum(&base10(i % 10, 1)) + m.sum("");
            }
            check!("insert 100000 keys with value 1000; then 100000 × (sum of a one-letter prefix + sum(\\"\\"))", total, 100_000 * (10_000_000 + 100_000_000));
        }
        """ + BASE10,
    ],
    wrong=dict(
        scan_every_key="""
            use std::collections::HashMap;

            #[derive(Default)]
            pub struct MapSum {
                values: HashMap<String, i32>,
            }

            impl MapSum {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, key: &str, val: i32) {
                    self.values.insert(key.to_string(), val);
                }

                pub fn sum(&self, prefix: &str) -> i64 {
                    self.values.iter().filter(|(k, _)| k.starts_with(prefix)).map(|(_, &v)| i64::from(v)).sum()
                }
            }
        """,
        overwrite_adds="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
                total: i64,
            }

            #[derive(Default)]
            pub struct MapSum {
                root: Node,
            }

            impl MapSum {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, key: &str, val: i32) {
                    let mut node = &mut self.root;
                    node.total += i64::from(val);
                    for b in key.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                        node.total += i64::from(val);
                    }
                }

                pub fn sum(&self, prefix: &str) -> i64 {
                    let mut node = &self.root;
                    for b in prefix.bytes() {
                        match &node.children[(b - b'a') as usize] {
                            Some(child) => node = child,
                            None => return 0,
                        }
                    }
                    node.total
                }
            }
        """,
    ),
    hints=[("approach", "Keep, in every trie node, the sum of the values below it. `sum` is then one walk down the prefix."),
           ("rust", "`HashMap::insert` returns the old value, so `val - old.unwrap_or(0)` is the delta to add along the key's path."),
           ("edge case", "Inserting an existing key replaces its value; adding `val` again would count it twice.")],
    notes=("Every node on a key's path counts that key, so adding the change in value along the path keeps all totals right. Each call is O(key length), independent of how many keys are stored.", "O(L) per call", "O(total letters × 26)"),
    follow_up="How would you support `remove(key)`?",
    related=["S4"],
))

# ---------------------------------------------------------------- tries at work (medium)

P.append(dict(
    slug="replace-words", title="Replace words", level="medium", stage="tries-at-work", tags=["trie", "split"],
    companies=["Amazon", "Uber"],
    teaches=["Stop a trie walk at the first node that ends a word: that's the shortest matching prefix.",
             "`split(' ')` borrows each word; `join` builds the one output `String`."],
    statement="""
        `sentence` is lowercase words separated by single spaces. Replace every word that starts with one of the `roots`
        by that root. When several roots match a word, use the **shortest** one. Words with no matching root stay as they are.
    """,
    examples=[("roots = [\"cat\", \"bat\", \"rat\"], sentence = \"the cattle was rattled by the battery\"", "\"the cat was rat by the bat\"")],
    constraints=["0 ≤ roots.len() ≤ 2·10⁵, roots are 1–100 lowercase letters", "sentence: up to 10⁶ bytes"],
    starter="""
        pub fn replace_words(roots: &[&str], sentence: &str) -> String {
            todo!()
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            end: bool,
        }

        /// Length of the shortest root that `word` starts with.
        fn shortest_root(root: &Node, word: &str) -> Option<usize> {
            let mut node = root;
            for (i, b) in word.bytes().enumerate() {
                node = node.children[(b - b'a') as usize].as_deref()?;
                if node.end {
                    return Some(i + 1);
                }
            }
            None
        }

        pub fn replace_words(roots: &[&str], sentence: &str) -> String {
            let mut trie = Node::default();
            for r in roots {
                let mut node = &mut trie;
                for b in r.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                }
                node.end = true;
            }
            sentence
                .split(' ')
                .map(|w| shortest_root(&trie, w).map_or(w, |n| &w[..n]))
                .collect::<Vec<&str>>()
                .join(" ")
        }
    """,
    visible=[
        T("leetcode_cattle", "roots = [\"cat\", \"bat\", \"rat\"], sentence = \"the cattle was rattled by the battery\"",
          'replace_words(&["cat", "bat", "rat"], "the cattle was rattled by the battery")', '"the cat was rat by the bat"'),
        T("leetcode_single_letters", "roots = [\"a\", \"b\", \"c\"], sentence = \"aadsfasf absbs bbab cadsfafs\"",
          'replace_words(&["a", "b", "c"], "aadsfasf absbs bbab cadsfafs")', '"a a b c"'),
        T("shortest_root_wins", "roots = [\"cat\", \"ca\"], sentence = \"cattle\"", 'replace_words(&["cat", "ca"], "cattle")', '"ca"'),
        T("no_roots", "roots = [], sentence = \"hello world\"", 'replace_words(&[], "hello world")', '"hello world"'),
        T("empty_sentence", "roots = [\"a\"], sentence = \"\"", 'replace_words(&["a"], "")', '""'),
        T("root_longer_than_word", "roots = [\"catalog\"], sentence = \"cat\"", 'replace_words(&["catalog"], "cat")', '"cat"'),
    ],
    hidden=[
        T("word_equals_root", "roots = [\"the\"], sentence = \"the theme\"", 'replace_words(&["the"], "the theme")', '"the the"'),
        T("duplicate_roots", "roots = [\"ab\", \"ab\"], sentence = \"abc\"", 'replace_words(&["ab", "ab"], "abc")', '"ab"'),
        T("root_must_be_prefix", "roots = [\"tle\"], sentence = \"cattle\"", 'replace_words(&["tle"], "cattle")', '"cattle"'),
        T("longer_root_listed_first", "roots = [\"abcd\", \"abc\", \"ab\"], sentence = \"abcde abx a\"", 'replace_words(&["abcd", "abc", "ab"], "abcde abx a")', '"ab ab a"'),
        T("single_word", "roots = [\"x\"], sentence = \"xylophone\"", 'replace_words(&["x"], "xylophone")', '"x"'),
        T("all_unchanged", "roots = [\"q\"], sentence = \"a b c\"", 'replace_words(&["q"], "a b c")', '"a b c"'),
        T("repeated_words", "roots = [\"re\"], sentence = \"redo redo undo\"", 'replace_words(&["re"], "redo redo undo")', '"re re undo"'),
        T("long_root_chain", "roots = ['z' × 1..=100], sentence = 'z' × 200", "replace_words(&refs, &\"z\".repeat(200))", '"z"',
          setup='let roots: Vec<String> = (1..=100).map(|n| "z".repeat(n)).collect();\nlet refs: Vec<&str> = roots.iter().rev().map(|s| s.as_str()).collect();'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1006);
            for _ in 0..300 {
                let mut roots: Vec<String> = Vec::new();
                for _ in 0..rng.below(5) {
                    let len = 1 + rng.below(3);
                    roots.push(rng.string(len, "ab"));
                }
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(5) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "abc"));
                }
                let sentence = words.join(" ");
                let refs: Vec<&str> = roots.iter().map(|s| s.as_str()).collect();
                let want: Vec<&str> = words
                    .iter()
                    .map(|w| refs.iter().filter(|r| w.starts_with(**r)).min_by_key(|r| r.len()).copied().unwrap_or(w.as_str()))
                    .collect();
                check!(format!("roots = {refs:?}, sentence = {sentence:?}"), replace_words(&refs, &sentence), want.join(" "));
            }
        }

        #[test]
        fn scale_100k_roots_and_words() {
            // Roots: 5-letter words for even i, 3-letter words for i divisible by 7.
            let mut roots: Vec<String> = (0..100_000).step_by(2).map(|i| base10(i, 5)).collect();
            roots.extend((0..1_000).step_by(7).map(|i| base10(i, 3)));
            let refs: Vec<&str> = roots.iter().map(|s| s.as_str()).collect();
            let js: Vec<usize> = (0..100_000).map(|i| i * 997 % 100_000_000).collect();
            let words: Vec<String> = js.iter().map(|&j| base10(j, 8)).collect();
            let sentence = words.join(" ");
            let want: Vec<&str> = js
                .iter()
                .zip(&words)
                .map(|(&j, w)| if (j / 100_000) % 7 == 0 { &w[..3] } else if (j / 1_000) % 2 == 0 { &w[..5] } else { w.as_str() })
                .collect();
            check!("50000 five-letter roots + 143 three-letter roots, a sentence of 100000 eight-letter words", replace_words(&refs, &sentence), want.join(" "));
        }
        """ + BASE10,
    ],
    wrong=dict(
        longest_root="""
            pub fn replace_words(roots: &[&str], sentence: &str) -> String {
                let mut sorted: Vec<&str> = roots.to_vec();
                sorted.sort_by_key(|r| std::cmp::Reverse(r.len()));
                sentence
                    .split(' ')
                    .map(|w| sorted.iter().find(|r| w.starts_with(**r)).copied().unwrap_or(w))
                    .collect::<Vec<&str>>()
                    .join(" ")
            }
        """,
        first_listed_root="""
            pub fn replace_words(roots: &[&str], sentence: &str) -> String {
                sentence
                    .split(' ')
                    .map(|w| roots.iter().find(|r| w.starts_with(**r)).copied().unwrap_or(w))
                    .collect::<Vec<&str>>()
                    .join(" ")
            }
        """,
        every_root_per_word="""
            pub fn replace_words(roots: &[&str], sentence: &str) -> String {
                sentence
                    .split(' ')
                    .map(|w| roots.iter().filter(|r| w.starts_with(**r)).min_by_key(|r| r.len()).copied().unwrap_or(w))
                    .collect::<Vec<&str>>()
                    .join(" ")
            }
        """,
    ),
    hints=[("approach", "Put the roots in a trie. For each word, walk down its letters and stop at the first node that ends a root."),
           ("rust", "Return the length of the root you found; `&word[..len]` is then a slice of the sentence, so the only allocation is the final `join`."),
           ("edge case", "Stop at the *first* marked node, not the deepest: with roots `cat` and `ca`, `cattle` becomes `ca`.")],
    notes=("Each word costs at most its own length in trie steps, independent of how many roots there are. Checking every root per word is O(roots × words), which the hidden test makes too slow.", "O(total root letters + sentence length)", "O(total root letters × 26)"),
    follow_up="How would you do this with a `HashSet` of roots instead of a trie, and what does it cost?",
    related=["S2", "S4"],
))

TRIE_FIX_STARTER = """
#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
}

fn idx(b: u8) -> usize {
    (b - b'a') as usize
}

/// Walks to the node for `word`, creating missing nodes on the way.
fn node_for<'a>(node: &'a mut Node, word: &[u8]) -> &'a mut Node {
    let Some((&b, rest)) = word.split_first() else {
        return node;
    };
    NODE_FOR
}

#[derive(Default)]
pub struct Trie {
    root: Node,
}

impl Trie {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, word: &str) {
        node_for(&mut self.root, word.as_bytes()).end = true;
    }

    pub fn contains(&self, word: &str) -> bool {
        let mut node = &self.root;
        for &b in word.as_bytes() {
            match &node.children[idx(b)] {
                Some(child) => node = child,
                None => return false,
            }
        }
        node.end
    }
}
"""

P.append(dict(
    slug="fix-recursive-trie-insert", title="Fix: recursive trie insert vs the borrow checker", mode="fix", level="medium", stage="tries-at-work",
    tags=["E0499", "get_or_insert_with", "NLL"],
    teaches=["Returning a borrow from one branch keeps it alive on the other branch too (E0499/E0506), a known limit of today's borrow checker.",
             "`Option::get_or_insert_with` does the check and the insert in one call and returns the `&mut` you need."],
    statement="""
        `node_for` walks down a trie, creating missing children, and returns the node where `word` ends.
        It doesn't compile: the early `return` in the `if let` keeps `node.children[..]` borrowed for the rest of the
        function, so the insert below it is rejected (E0506, E0499).

        Make it compile without changing what it does. The rest of the file is correct.
    """,
    examples=[("insert \"car\", \"cart\"; contains \"car\", \"ca\"", "true, false")],
    starter=TRIE_FIX_STARTER.replace("NODE_FOR", """if let Some(child) = node.children[idx(b)].as_mut() {
        return node_for(child, rest);
    }
    node.children[idx(b)] = Some(Box::new(Node::default()));
    node_for(node.children[idx(b)].as_mut().unwrap(), rest)"""),
    solution=TRIE_FIX_STARTER.replace("NODE_FOR", "node_for(node.children[idx(b)].get_or_insert_with(Default::default), rest)"),
    rules=dict(lines=5, unsafe=True),
    visible=[
        T("insert_and_find", "insert \"car\"; contains \"car\"", 't.contains("car")', "true", setup='let mut t = Trie::new();\nt.insert("car");'),
        T("empty_trie", "new trie; contains \"a\"", 't.contains("a")', "false", setup="let t = Trie::new();"),
        T("prefix_is_not_a_word", "insert \"car\"; contains \"ca\"", 't.contains("ca")', "false", setup='let mut t = Trie::new();\nt.insert("car");'),
        T("shared_prefix_keeps_both", "insert \"car\", \"cart\"; contains both", '(t.contains("car"), t.contains("cart"))', "(true, true)",
          setup='let mut t = Trie::new();\nt.insert("car");\nt.insert("cart");'),
        T("longer_first", "insert \"cart\", \"car\"; contains both", '(t.contains("car"), t.contains("cart"))', "(true, true)",
          setup='let mut t = Trie::new();\nt.insert("cart");\nt.insert("car");'),
    ],
    hidden=[
        T("empty_word", "insert \"\"; contains \"\"", 't.contains("")', "true", setup='let mut t = Trie::new();\nt.insert("");'),
        T("siblings", "insert \"cat\", \"car\", \"cab\"; contains each", '(t.contains("cat"), t.contains("car"), t.contains("cab"))', "(true, true, true)",
          setup='let mut t = Trie::new();\nfor w in ["cat", "car", "cab"] {\n    t.insert(w);\n}'),
        T("insert_twice", "insert \"z\" twice; contains \"z\"", 't.contains("z")', "true", setup='let mut t = Trie::new();\nt.insert("z");\nt.insert("z");'),
        T("longer_not_found", "insert \"ab\"; contains \"abc\"", 't.contains("abc")', "false", setup='let mut t = Trie::new();\nt.insert("ab");'),
        T("other_branch", "insert \"ab\"; contains \"b\"", 't.contains("b")', "false", setup='let mut t = Trie::new();\nt.insert("ab");'),
        T("deep_word", "insert 'q' × 1000; contains it and 'q' × 999", '(t.contains(&long), t.contains(&long[..999]))', "(true, false)",
          setup='let mut t = Trie::new();\nlet long = "q".repeat(1000);\nt.insert(&long);'),
        T("chain_of_prefixes", "insert a, ab, abc, abcd; contains each", "all", "true",
          setup='let mut t = Trie::new();\nlet ws = ["a", "ab", "abc", "abcd"];\nfor w in ws {\n    t.insert(w);\n}\nlet all = ws.iter().all(|w| t.contains(w));'),
        T("first_word_survives_many", "insert \"apple\" then 25 other words starting with 'a'; contains \"apple\"", 't.contains("apple")', "true",
          setup='let mut t = Trie::new();\nt.insert("apple");\nfor b in b\'b\'..=b\'z\' {\n    t.insert(&format!("a{}", b as char));\n}'),
        """
        #[test]
        fn random_vs_model() {
            use std::collections::HashSet;
            let mut rng = anneal_prelude::Rng::new(1007);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut model: HashSet<String> = HashSet::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let w = rng.string(len, "abc");
                    if rng.bool() {
                        t.insert(&w);
                        log.push(format!("insert {w:?}"));
                        model.insert(w);
                    } else {
                        log.push(format!("contains {w:?}"));
                        check!(log.join(", "), t.contains(&w), model.contains(&w));
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut t = Trie::new();
            for i in 0..100_000 {
                t.insert(&base10(i, 5));
            }
            let found = (0..100_000).filter(|&i| t.contains(&base10(i, 5))).count();
            check!("insert 100000 five-letter words over a..j, then look each one up", found, 100_000);
        }
        """ + BASE10,
    ],
    wrong=dict(
        always_new_child=TRIE_FIX_STARTER.replace("NODE_FOR", """node.children[idx(b)] = Some(Box::new(Node::default()));
    node_for(node.children[idx(b)].as_mut().unwrap(), rest)"""),
    ),
    hints=[("rust", "The borrow returned from the `if let` branch has lifetime `'a`, so the checker treats `node.children[i]` as borrowed for all of `'a`, even on the path that didn't return. Avoid holding a borrow across the check."),
           ("rust", "`slot.get_or_insert_with(Default::default)` returns `&mut Box<Node>`, creating the child only when the slot is `None`. One call, one borrow."),
           ("edge case", "Deleting the `if let` compiles too, but then every insert replaces existing children and loses the words below them.")],
    notes=("The original is correct code that today's borrow checker (NLL) rejects: a reference returned from a conditional branch extends the borrow over the whole function. Polonius, the next checker, accepts it. `get_or_insert_with` sidesteps the problem because there's no branch holding a borrow.", "O(L) per insert", "O(L) recursion depth"),
    follow_up="How would you write `node_for` as a loop instead of recursion, and does the same borrow problem appear?",
    related=["L2", "L3", "S1"],
))

P.append(dict(
    slug="add-and-search-words", title="Add & search words", level="medium", stage="tries-at-work", tags=["trie", "DFS", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft"],
    teaches=["A wildcard turns a trie walk into a depth-first search over every child.",
             "Slice patterns (`split_first`) make the recursion read like the definition."],
    statement="""
        `WordDictionary` stores lowercase words.

        - `add_word(word)` stores `word`;
        - `search(pattern)` is `true` if some stored word matches `pattern`, where `.` matches any one letter.

        The whole word must match: `"b.."` matches `"bad"` but not `"ba"` or `"bads"`.
    """,
    examples=[("add \"bad\", \"dad\", \"mad\"; search \"pad\", \"bad\", \".ad\", \"b..\"", "false, true, true, true")],
    constraints=["words: 1–25 lowercase letters", "patterns: 1–25 characters from a–z and '.', at most 3 dots", "up to 10⁵ calls"],
    starter="""
        #[derive(Default)]
        pub struct WordDictionary {
            // your fields here
        }

        impl WordDictionary {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn add_word(&mut self, word: &str) {
                todo!()
            }

            pub fn search(&self, pattern: &str) -> bool {
                todo!()
            }
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            end: bool,
        }

        fn matches(node: &Node, pattern: &[u8]) -> bool {
            match pattern.split_first() {
                None => node.end,
                Some((b'.', rest)) => node.children.iter().flatten().any(|child| matches(child, rest)),
                Some((&b, rest)) => node.children[(b - b'a') as usize].as_deref().is_some_and(|child| matches(child, rest)),
            }
        }

        #[derive(Default)]
        pub struct WordDictionary {
            root: Node,
        }

        impl WordDictionary {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn add_word(&mut self, word: &str) {
                let mut node = &mut self.root;
                for b in word.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                }
                node.end = true;
            }

            pub fn search(&self, pattern: &str) -> bool {
                matches(&self.root, pattern.as_bytes())
            }
        }
    """,
    visible=[
        T("leetcode_bad_dad_mad", "add \"bad\", \"dad\", \"mad\"; search \"pad\", \"bad\", \".ad\", \"b..\"",
          '(d.search("pad"), d.search("bad"), d.search(".ad"), d.search("b.."))', "(false, true, true, true)",
          setup='let mut d = WordDictionary::new();\nfor w in ["bad", "dad", "mad"] {\n    d.add_word(w);\n}'),
        T("empty_dictionary", "new dictionary; search \"a\", \".\"", '(d.search("a"), d.search("."))', "(false, false)", setup="let d = WordDictionary::new();"),
        T("dot_matches_one_letter", "add \"ab\"; search \".\", \"..\", \"...\"", '(d.search("."), d.search(".."), d.search("..."))', "(false, true, false)",
          setup='let mut d = WordDictionary::new();\nd.add_word("ab");'),
        T("prefix_is_not_a_match", "add \"bad\"; search \"ba\", \"b.\"", '(d.search("ba"), d.search("b."))', "(false, false)",
          setup='let mut d = WordDictionary::new();\nd.add_word("bad");'),
        T("dot_must_try_every_branch", "add \"ab\", \"cd\"; search \".d\"", 'd.search(".d")', "true",
          setup='let mut d = WordDictionary::new();\nd.add_word("ab");\nd.add_word("cd");'),
    ],
    hidden=[
        T("all_dots", "add \"hello\"; search \".....\"", 'd.search(".....")', "true", setup='let mut d = WordDictionary::new();\nd.add_word("hello");'),
        T("dot_at_end", "add \"cat\", \"car\"; search \"ca.\", \"c.t\", \"c.x\"", '(d.search("ca."), d.search("c.t"), d.search("c.x"))', "(true, true, false)",
          setup='let mut d = WordDictionary::new();\nd.add_word("cat");\nd.add_word("car");'),
        T("longer_than_word", "add \"a\"; search \"a.\"", 'd.search("a.")', "false", setup='let mut d = WordDictionary::new();\nd.add_word("a");'),
        T("shorter_word_added_later", "add \"abc\", then \"ab\"; search \"a.\"", 'd.search("a.")', "true",
          setup='let mut d = WordDictionary::new();\nd.add_word("abc");\nd.add_word("ab");'),
        T("backtrack_after_dead_end", "add \"aab\", \"abc\"; search \"a.c\"", 'd.search("a.c")', "true",
          setup='let mut d = WordDictionary::new();\nd.add_word("aab");\nd.add_word("abc");'),
        T("last_child_matches", "add \"az\", \"bz\", \"zy\"; search \".y\"", 'd.search(".y")', "true",
          setup='let mut d = WordDictionary::new();\nfor w in ["az", "bz", "zy"] {\n    d.add_word(w);\n}'),
        T("no_dot_exact_miss", "add \"abc\"; search \"abd\"", 'd.search("abd")', "false", setup='let mut d = WordDictionary::new();\nd.add_word("abc");'),
        T("twenty_five_letters", "add 'y' × 25; search 'y' × 24 + \".\"", 'd.search(&format!("{}.", "y".repeat(24)))', "true",
          setup='let mut d = WordDictionary::new();\nd.add_word(&"y".repeat(25));'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1008);
            for _ in 0..300 {
                let mut d = WordDictionary::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = 1 + rng.below(3);
                    if rng.bool() {
                        let w = rng.string(len, "abc");
                        d.add_word(&w);
                        log.push(format!("add {w:?}"));
                        words.push(w);
                    } else {
                        let p = rng.string(len, "ab.");
                        let want = words.iter().any(|w| w.len() == p.len() && w.bytes().zip(p.bytes()).all(|(a, b)| b == b'.' || a == b));
                        log.push(format!("search {p:?}"));
                        check!(log.join(", "), d.search(&p), want);
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut d = WordDictionary::new();
            for i in 0..100_000 {
                d.add_word(&base10(i, 5));
            }
            let mut hits = 0;
            for i in 0..100_000 {
                let w = base10(i, 5);
                hits += d.search(&w) as usize + d.search(&format!("{}.", &w[..4])) as usize + d.search(&format!("{}k", &w[..4])) as usize;
            }
            for _ in 0..100 {
                hits += d.search("....k") as usize;
            }
            check!("add 100000 five-letter words over a..j; search each, each with a final '.', each with a final 'k'; then \\"....k\\" 100 times", hits, 200_000);
        }
        """ + BASE10,
    ],
    wrong=dict(
        list_of_words="""
            #[derive(Default)]
            pub struct WordDictionary {
                words: Vec<String>,
            }

            impl WordDictionary {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn add_word(&mut self, word: &str) {
                    self.words.push(word.to_string());
                }

                pub fn search(&self, pattern: &str) -> bool {
                    self.words.iter().any(|w| w.len() == pattern.len() && w.bytes().zip(pattern.bytes()).all(|(a, b)| b == b'.' || a == b))
                }
            }
        """,
        dot_takes_first_child="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
                end: bool,
            }

            #[derive(Default)]
            pub struct WordDictionary {
                root: Node,
            }

            impl WordDictionary {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn add_word(&mut self, word: &str) {
                    let mut node = &mut self.root;
                    for b in word.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    }
                    node.end = true;
                }

                pub fn search(&self, pattern: &str) -> bool {
                    let mut node = &self.root;
                    for b in pattern.bytes() {
                        let next = if b == b'.' { node.children.iter().flatten().next() } else { node.children[(b - b'a') as usize].as_ref() };
                        match next {
                            Some(child) => node = child,
                            None => return false,
                        }
                    }
                    node.end
                }
            }
        """,
    ),
    hints=[("approach", "Store the words in a trie. A letter follows one child; a `.` must try every child, so search is a depth-first search."),
           ("rust", "`match pattern.split_first()` gives three arms: `None` (check the end flag), `Some((b'.', rest))` (try `children.iter().flatten()` with `any`), and a letter."),
           ("edge case", "Following only the first child for a `.` misses words in other branches: `ab`, `cd` and the pattern `.d`.")],
    notes=("Without dots a search is one walk, O(L). Each dot multiplies the branches by at most 26, so a pattern with d dots costs O(26^d · L) in the worst case, but real tries are sparse and `any` stops at the first match.", "add O(L); search O(26^d · L) worst case", "O(total letters × 26)"),
    follow_up="If most searches had no dots, how would you make them O(1) on average?",
    related=["D11", "S1"],
))

P.append(dict(
    slug="search-suggestions-system", title="Search suggestions system", level="medium", stage="tries-at-work", tags=["trie", "autocomplete", "sorting"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Autocomplete keeps a cursor into the trie and moves it one node per typed letter.",
             "Insert products in sorted order and let each node remember its first three: suggestions are then a lookup, not a search."],
    statement="""
        A search box suggests products while you type `search_word`. After **each** typed letter, suggest up to three
        products that start with what's typed so far, the three smallest in alphabetical order.

        Return one list per typed letter: `result[i]` is the suggestions after typing `search_word[..=i]`.
        Once a prefix matches nothing, every later list is empty too.

        Products are distinct lowercase words.
    """,
    examples=[("products = [\"mobile\", \"mouse\", \"moneypot\", \"monitor\", \"mousepad\"], search_word = \"mouse\"",
               "[[mobile, moneypot, monitor], [mobile, moneypot, monitor], [mouse, mousepad], [mouse, mousepad], [mouse, mousepad]]")],
    constraints=["0 ≤ products.len() ≤ 2·10⁴, total length ≤ 2·10⁷", "0 ≤ search_word.len() ≤ 1000", "lowercase ASCII"],
    starter="""
        pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
            todo!()
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            /// Up to three products below this node, as indexes into the sorted list; the smallest come first.
            top: Vec<usize>,
        }

        pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
            let mut sorted = products.to_vec();
            sorted.sort_unstable();
            let mut root = Node::default();
            // Sorted order means the first three to reach a node are its three smallest.
            for (i, p) in sorted.iter().enumerate() {
                let mut node = &mut root;
                for b in p.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    if node.top.len() < 3 {
                        node.top.push(i);
                    }
                }
            }
            // One cursor, moved one letter per keystroke; `None` once the prefix has fallen off the trie.
            let mut cursor = Some(&root);
            search_word
                .bytes()
                .map(|b| {
                    cursor = cursor.and_then(|node| node.children[(b - b'a') as usize].as_deref());
                    cursor.map_or_else(Vec::new, |node| node.top.iter().map(|&i| sorted[i].to_string()).collect())
                })
                .collect()
        }
    """,
    visible=[
        T("typing_m", "products = [\"mobile\", \"mouse\", \"moneypot\", \"monitor\", \"mousepad\"], search_word = \"m\"",
          'suggested_products(&products, "m")', 'vec![vec!["mobile", "moneypot", "monitor"]]',
          setup='let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];'),
        T("typing_mo", "products = [\"mobile\", \"mouse\", \"moneypot\", \"monitor\", \"mousepad\"], search_word = \"mo\" (one list per letter typed)",
          'suggested_products(&products, "mo")', 'vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"]]',
          setup='let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];'),
        T("typing_mou", "products = [\"mobile\", \"mouse\", \"moneypot\", \"monitor\", \"mousepad\"], search_word = \"mou\" (\"mou\" narrows to two)",
          'suggested_products(&products, "mou")', 'vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"], vec!["mouse", "mousepad"]]',
          setup='let products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"];'),
        T("leetcode_mouse", "products = [\"mobile\", \"mouse\", \"moneypot\", \"monitor\", \"mousepad\"], search_word = \"mouse\"",
          'suggested_products(&["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse")',
          'vec![vec!["mobile", "moneypot", "monitor"], vec!["mobile", "moneypot", "monitor"], vec!["mouse", "mousepad"], vec!["mouse", "mousepad"], vec!["mouse", "mousepad"]]'),
        T("leetcode_havana", "products = [\"havana\"], search_word = \"havana\"", 'suggested_products(&["havana"], "havana")', 'vec![vec!["havana"]; 6]'),
        T("leetcode_bags", "products = [\"bags\", \"baggage\", \"banner\", \"box\", \"cloths\"], search_word = \"bags\"",
          'suggested_products(&["bags", "baggage", "banner", "box", "cloths"], "bags")',
          'vec![vec!["baggage", "bags", "banner"], vec!["baggage", "bags", "banner"], vec!["baggage", "bags"], vec!["bags"]]'),
        T("miss_stays_empty", "products = [\"havana\"], search_word = \"hat\" (\"hat\" matches nothing, so the third list is empty)",
          'suggested_products(&["havana"], "hat")', 'vec![vec!["havana"], vec!["havana"], vec![]]'),
        T("empty_search_word", "products = [\"a\"], search_word = \"\"", 'suggested_products(&["a"], "")', "Vec::<Vec<&str>>::new()"),
    ],
    hidden=[
        T("no_products", "products = [], search_word = \"ab\"", 'suggested_products(&[], "ab")', 'vec![Vec::<&str>::new(); 2]'),
        T("leetcode_tatiana", "products = [\"havana\"], search_word = \"tatiana\"", 'suggested_products(&["havana"], "tatiana")', 'vec![Vec::<&str>::new(); 7]'),
        T("only_three", "products = [\"dog\", \"cat\", \"cow\", \"car\", \"cub\"], search_word = \"c\"",
          'suggested_products(&["dog", "cat", "cow", "car", "cub"], "c")', 'vec![vec!["car", "cat", "cow"]]'),
        T("shorter_word_sorts_first", "products = [\"abc\", \"ab\", \"abd\", \"a\"], search_word = \"a\"",
          'suggested_products(&["abc", "ab", "abd", "a"], "a")', 'vec![vec!["a", "ab", "abc"]]'),
        T("miss_then_would_match", "products = [\"ab\", \"b\"], search_word = \"xb\"", 'suggested_products(&["ab", "b"], "xb")', 'vec![Vec::<&str>::new(); 2]'),
        T("longer_than_product", "products = [\"code\"], search_word = \"codes\"", 'suggested_products(&["code"], "codes")',
          'vec![vec!["code"], vec!["code"], vec!["code"], vec!["code"], vec![]]'),
        T("match_is_whole_prefix", "products = [\"ab\", \"xb\"], search_word = \"ab\" (\"xb\" has a 'b' second, but not the prefix \"ab\")",
          'suggested_products(&["ab", "xb"], "ab")', 'vec![vec!["ab"], vec!["ab"]]'),
        T("reverse_sorted_input", "products = [\"e\", \"d\", \"c\", \"b\", \"a\"] each prefixed with \"k\", search_word = \"k\"",
          'suggested_products(&["ke", "kd", "kc", "kb", "ka"], "k")', 'vec![vec!["ka", "kb", "kc"]]'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1009);
            for _ in 0..300 {
                let mut products: Vec<String> = Vec::new();
                for _ in 0..rng.below(8) {
                    let len = 1 + rng.below(4);
                    let p = rng.string(len, "abc");
                    if !products.contains(&p) {
                        products.push(p);
                    }
                }
                let len = rng.below(5);
                let word = rng.string(len, "abc");
                let refs: Vec<&str> = products.iter().map(|s| s.as_str()).collect();
                let want: Vec<Vec<String>> = (1..=word.len())
                    .map(|k| {
                        let mut m: Vec<String> = products.iter().filter(|p| p.starts_with(&word[..k])).cloned().collect();
                        m.sort();
                        m.truncate(3);
                        m
                    })
                    .collect();
                check!(format!("products = {refs:?}, search_word = {word:?}"), suggested_products(&refs, &word), want);
            }
        }

        #[test]
        fn scale_20k_long_products() {
            // Every product starts with 'a' × 1000, so every prefix of the search word matches all 20000 (listed in shuffled order).
            let base = "a".repeat(1000);
            let products: Vec<String> = (0..20_000).map(|i| format!("{base}{}", base10(i * 7919 % 20_000, 5))).collect();
            let refs: Vec<&str> = products.iter().map(|s| s.as_str()).collect();
            let got = suggested_products(&refs, &base);
            let want = vec![format!("{base}aaaaa"), format!("{base}aaaab"), format!("{base}aaaac")];
            check!("20000 products 'a' × 1000 + five letters, search_word = 'a' × 1000", (got.len(), got.iter().all(|row| *row == want)), (1000, true));
        }
        """ + BASE10,
    ],
    wrong=dict(
        sort_every_keystroke="""
            pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
                (1..=search_word.len())
                    .map(|k| {
                        let mut matches: Vec<&str> = products.iter().copied().filter(|p| p.starts_with(&search_word[..k])).collect();
                        matches.sort_unstable();
                        matches.iter().take(3).map(|p| p.to_string()).collect()
                    })
                    .collect()
            }
        """,
        input_order="""
            pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
                (1..=search_word.len())
                    .map(|k| products.iter().filter(|p| p.starts_with(&search_word[..k])).take(3).map(|p| p.to_string()).collect())
                    .collect()
            }
        """,
        matches_one_letter="""
            pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
                let mut sorted = products.to_vec();
                sorted.sort_unstable();
                search_word
                    .bytes()
                    .enumerate()
                    .map(|(k, b)| sorted.iter().filter(|p| p.as_bytes().get(k) == Some(&b)).take(3).map(|p| p.to_string()).collect())
                    .collect()
            }
        """,
    ),
    hints=[("approach", "Sort the products, then insert them into a trie in that order. Each node keeps the first three products that pass through it: those are its three smallest."),
           ("rust", "Keep the cursor as `Option<&Node>`: each keystroke does `cursor = cursor.and_then(|n| n.children[i].as_deref())`, and `None` means every later list is empty."),
           ("edge case", "Suggestions must match the whole typed prefix, not only the latest letter, and they're capped at three.")],
    notes=("Sorting first means no node ever needs re-sorting: the first three products to reach it are the smallest. Each keystroke is then one step down the trie plus copying at most three strings. Sort + binary search (`partition_point` on the prefix) is the other classic answer, O(log n) per keystroke with no trie.", "O(n log n · L) to build, O(1) steps per keystroke (plus copying the three results)", "O(total letters × 26)"),
    follow_up="Real search boxes rank by popularity, not alphabet, and learn from what people pick. How would the node data change? (The hard stage's autocomplete does this.)",
    related=["S3", "S1"],
))

P.append(dict(
    slug="trie-with-counts-and-erase", title="Trie with counts and erase", level="medium", stage="tries-at-work", tags=["trie", "counting"],
    teaches=["Counts in the nodes answer 'how many' queries in one walk.",
             "Check before you mutate: erasing a word that isn't there must change nothing."],
    statement="""
        A trie that stores words with multiplicity:

        - `insert(word)` adds one copy of `word`;
        - `count_words_equal_to(word)` returns how many copies of `word` are stored;
        - `count_words_starting_with(prefix)` returns how many stored copies start with `prefix` (every copy counts);
        - `erase(word)` removes one copy and returns `true`, or returns `false` and changes nothing if `word` isn't stored.
    """,
    examples=[("insert apple twice; count equal apple; count starting app; erase apple; count equal apple", "2, 2, true, 1")],
    constraints=["words: 1–100 lowercase letters (the empty word and prefix are allowed)", "up to 2·10⁵ calls"],
    starter="""
        #[derive(Default)]
        pub struct Trie {
            // your fields here
        }

        impl Trie {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, word: &str) {
                todo!()
            }

            pub fn count_words_equal_to(&self, word: &str) -> usize {
                todo!()
            }

            pub fn count_words_starting_with(&self, prefix: &str) -> usize {
                todo!()
            }

            pub fn erase(&mut self, word: &str) -> bool {
                todo!()
            }
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            /// Copies of words that pass through (or end at) this node.
            pass: usize,
            /// Copies of words that end here.
            end: usize,
        }

        #[derive(Default)]
        pub struct Trie {
            root: Node,
        }

        impl Trie {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn insert(&mut self, word: &str) {
                let mut node = &mut self.root;
                node.pass += 1;
                for b in word.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    node.pass += 1;
                }
                node.end += 1;
            }

            fn walk(&self, s: &str) -> Option<&Node> {
                let mut node = &self.root;
                for b in s.bytes() {
                    node = node.children[(b - b'a') as usize].as_deref()?;
                }
                Some(node)
            }

            pub fn count_words_equal_to(&self, word: &str) -> usize {
                self.walk(word).map_or(0, |n| n.end)
            }

            pub fn count_words_starting_with(&self, prefix: &str) -> usize {
                self.walk(prefix).map_or(0, |n| n.pass)
            }

            pub fn erase(&mut self, word: &str) -> bool {
                if self.count_words_equal_to(word) == 0 {
                    return false;
                }
                let mut node = &mut self.root;
                node.pass -= 1;
                for b in word.bytes() {
                    let slot = &mut node.children[(b - b'a') as usize];
                    // The last copy through this child: drop the whole branch.
                    if slot.as_ref().is_some_and(|child| child.pass == 1) {
                        *slot = None;
                        return true;
                    }
                    node = slot.as_deref_mut().expect("counted above");
                    node.pass -= 1;
                }
                node.end -= 1;
                true
            }
        }
    """,
    visible=[
        T("leetcode_apple", "insert apple, apple; equal apple; starting app; erase apple; equal apple; starting app; erase apple; starting app",
          "(a, b, c, d, t.count_words_starting_with(\"app\"))", "(2, 2, 1, 1, 0)",
          setup='let mut t = Trie::new();\nt.insert("apple");\nt.insert("apple");\nlet (a, b) = (t.count_words_equal_to("apple"), t.count_words_starting_with("app"));\nt.erase("apple");\nlet (c, d) = (t.count_words_equal_to("apple"), t.count_words_starting_with("app"));\nt.erase("apple");'),
        T("empty_trie", "new trie; equal \"a\", starting \"a\", starting \"\"", '(t.count_words_equal_to("a"), t.count_words_starting_with("a"), t.count_words_starting_with(""))', "(0, 0, 0)",
          setup="let t = Trie::new();"),
        T("erase_missing_changes_nothing", "insert apple; erase \"app\"; starting \"app\", equal \"apple\"",
          "(erased, t.count_words_starting_with(\"app\"), t.count_words_equal_to(\"apple\"))", "(false, 1, 1)",
          setup='let mut t = Trie::new();\nt.insert("apple");\nlet erased = t.erase("app");'),
        T("every_copy_counts", "insert a, ab, ab, abc; starting \"a\", starting \"ab\", equal \"ab\"",
          '(t.count_words_starting_with("a"), t.count_words_starting_with("ab"), t.count_words_equal_to("ab"))', "(4, 3, 2)",
          setup='let mut t = Trie::new();\nfor w in ["a", "ab", "ab", "abc"] {\n    t.insert(w);\n}'),
        T("erase_returns_true_then_false", "insert x; erase x; erase x", "(first, t.erase(\"x\"))", "(true, false)",
          setup='let mut t = Trie::new();\nt.insert("x");\nlet first = t.erase("x");'),
        T("erase_keeps_longer_word", "insert ab, abc; erase ab; equal abc, starting ab", '(t.count_words_equal_to("abc"), t.count_words_starting_with("ab"))', "(1, 1)",
          setup='let mut t = Trie::new();\nt.insert("ab");\nt.insert("abc");\nt.erase("ab");'),
    ],
    hidden=[
        T("empty_word", "insert \"\" twice; equal \"\", starting \"\", erase \"\", equal \"\"", "(a, b, c, t.count_words_equal_to(\"\"))", "(2, 2, true, 1)",
          setup='let mut t = Trie::new();\nt.insert("");\nt.insert("");\nlet (a, b) = (t.count_words_equal_to(""), t.count_words_starting_with(""));\nlet c = t.erase("");'),
        T("erase_longer_missing", "insert ab; erase abc; starting ab", "(erased, t.count_words_starting_with(\"ab\"))", "(false, 1)",
          setup='let mut t = Trie::new();\nt.insert("ab");\nlet erased = t.erase("abc");'),
        T("erase_prefix_of_word_missing", "insert abc; erase ab; equal abc, starting a", "(erased, t.count_words_equal_to(\"abc\"), t.count_words_starting_with(\"a\"))", "(false, 1, 1)",
          setup='let mut t = Trie::new();\nt.insert("abc");\nlet erased = t.erase("ab");'),
        T("reinsert_after_erase", "insert q; erase q; insert q; equal q, starting q", '(t.count_words_equal_to("q"), t.count_words_starting_with("q"))', "(1, 1)",
          setup='let mut t = Trie::new();\nt.insert("q");\nt.erase("q");\nt.insert("q");'),
        T("erase_shorter_keeps_branch", "insert abc, abd; erase abc; starting ab, equal abd", '(t.count_words_starting_with("ab"), t.count_words_equal_to("abd"))', "(1, 1)",
          setup='let mut t = Trie::new();\nt.insert("abc");\nt.insert("abd");\nt.erase("abc");'),
        T("erase_on_empty", "new trie; erase \"a\"", 't.erase("a")', "false", setup="let mut t = Trie::new();"),
        T("prefix_equals_word", "insert apple; starting apple, starting apples", '(t.count_words_starting_with("apple"), t.count_words_starting_with("apples"))', "(1, 0)",
          setup='let mut t = Trie::new();\nt.insert("apple");'),
        T("many_copies", "insert z 1000 times; erase 999; equal z", 't.count_words_equal_to("z")', "1",
          setup='let mut t = Trie::new();\nfor _ in 0..1000 {\n    t.insert("z");\n}\nfor _ in 0..999 {\n    t.erase("z");\n}'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1010);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(16) {
                    let len = rng.below(4);
                    let w = rng.string(len, "ab");
                    match rng.below(4) {
                        0 => {
                            t.insert(&w);
                            log.push(format!("insert {w:?}"));
                            words.push(w);
                        }
                        1 => {
                            log.push(format!("erase {w:?}"));
                            let pos = words.iter().position(|x| *x == w);
                            if let Some(p) = pos {
                                words.swap_remove(p);
                            }
                            check!(log.join(", "), t.erase(&w), pos.is_some());
                        }
                        2 => {
                            log.push(format!("count_words_equal_to {w:?}"));
                            check!(log.join(", "), t.count_words_equal_to(&w), words.iter().filter(|x| **x == w).count());
                        }
                        _ => {
                            log.push(format!("count_words_starting_with {w:?}"));
                            check!(log.join(", "), t.count_words_starting_with(&w), words.iter().filter(|x| x.starts_with(w.as_str())).count());
                        }
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut t = Trie::new();
            for i in 0..100_000 {
                t.insert(&base10(i, 5));
            }
            let mut total = 0;
            for i in (0..100_000).step_by(2) {
                total += t.erase(&base10(i, 5)) as usize;
            }
            for i in 0..100_000 {
                total += t.count_words_starting_with(&base10(i % 1000, 3)) + t.count_words_equal_to(&base10(i, 5));
            }
            check!("insert 100000 five-letter words, erase the even ones, then 100000 × (count starting with a 3-letter prefix + count equal to a word)", total, 50_000 + 5_000_000 + 50_000);
        }
        """ + BASE10,
    ],
    wrong=dict(
        list_of_words="""
            #[derive(Default)]
            pub struct Trie {
                words: Vec<String>,
            }

            impl Trie {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, word: &str) {
                    self.words.push(word.to_string());
                }

                pub fn count_words_equal_to(&self, word: &str) -> usize {
                    self.words.iter().filter(|w| *w == word).count()
                }

                pub fn count_words_starting_with(&self, prefix: &str) -> usize {
                    self.words.iter().filter(|w| w.starts_with(prefix)).count()
                }

                pub fn erase(&mut self, word: &str) -> bool {
                    match self.words.iter().position(|w| w == word) {
                        Some(i) => {
                            self.words.swap_remove(i);
                            true
                        }
                        None => false,
                    }
                }
            }
        """,
        erase_without_check="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
                pass: usize,
                end: usize,
            }

            #[derive(Default)]
            pub struct Trie {
                root: Node,
            }

            impl Trie {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn insert(&mut self, word: &str) {
                    let mut node = &mut self.root;
                    node.pass += 1;
                    for b in word.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                        node.pass += 1;
                    }
                    node.end += 1;
                }

                fn walk(&self, s: &str) -> Option<&Node> {
                    let mut node = &self.root;
                    for b in s.bytes() {
                        node = node.children[(b - b'a') as usize].as_deref()?;
                    }
                    Some(node)
                }

                pub fn count_words_equal_to(&self, word: &str) -> usize {
                    self.walk(word).map_or(0, |n| n.end)
                }

                pub fn count_words_starting_with(&self, prefix: &str) -> usize {
                    self.walk(prefix).map_or(0, |n| n.pass)
                }

                pub fn erase(&mut self, word: &str) -> bool {
                    let mut node = &mut self.root;
                    node.pass = node.pass.saturating_sub(1);
                    for b in word.bytes() {
                        match node.children[(b - b'a') as usize].as_deref_mut() {
                            Some(child) => node = child,
                            None => return false,
                        }
                        node.pass = node.pass.saturating_sub(1);
                    }
                    node.end = node.end.saturating_sub(1);
                    true
                }
            }
        """,
    ),
    hints=[("approach", "Give each node two counters: how many stored copies pass through it, and how many end at it. Every query is one walk."),
           ("rust", "Walk once with `&self` to check the word is stored before taking `&mut self.root`; that keeps `erase` from half-updating a path."),
           ("edge case", "Erasing `app` when only `apple` is stored must return `false` and leave every count alone.")],
    notes=("`pass` answers prefix counts and `end` answers exact counts, so every operation is O(L). Dropping a child whose `pass` falls to zero frees the branch, so memory tracks what's stored rather than everything ever inserted.", "O(L) per call", "O(total letters stored × 26)"),
    follow_up="How would you return the k most frequent stored words with a given prefix?",
    related=["S4"],
))

WORD_FILTER_TESTS_SETUP = 'let wf = WordFilter::new(&["apple"]);'

P.append(dict(
    slug="prefix-and-suffix-search", title="Prefix and suffix search", level="medium", stage="tries-at-work", tags=["trie", "design"],
    companies=["Meta", "Google"],
    teaches=["Turn a two-sided query into a one-sided one: store `suffix + '{' + word` so one trie walk checks both ends.",
             "`[Option<Box<Node>>; 27]`: `'{'` is the byte after `'z'`, so it gets index 26."],
    statement="""
        `WordFilter::new(words)` stores a list of lowercase words. `f(prefix, suffix)` returns the **largest index** `i`
        such that `words[i]` starts with `prefix` and ends with `suffix`, or `None` if no word does.

        Either part may be empty, and a word may appear more than once (the later index wins).
    """,
    examples=[("words = [\"apple\"], f(\"a\", \"e\")", "Some(0)")],
    constraints=["1 ≤ words.len() ≤ 10⁴", "1 ≤ words[i].len() ≤ 7", "prefix, suffix: 0–7 lowercase letters", "up to 2·10⁵ calls to f"],
    starter="""
        pub struct WordFilter {
            // your fields here
        }

        impl WordFilter {
            pub fn new(words: &[&str]) -> Self {
                todo!()
            }

            pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
                todo!()
            }
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            /// a..z, then '{' (the byte after 'z') as the separator.
            children: [Option<Box<Node>>; 27],
            /// Largest index of a word whose key passes through here.
            best: usize,
        }

        pub struct WordFilter {
            root: Node,
        }

        impl WordFilter {
            pub fn new(words: &[&str]) -> Self {
                let mut root = Node::default();
                for (i, w) in words.iter().enumerate() {
                    // For "apple": "{apple", "e{apple", "le{apple", …, "apple{apple".
                    for start in 0..=w.len() {
                        let mut node = &mut root;
                        for b in w[start..].bytes().chain([b'{']).chain(w.bytes()) {
                            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                            node.best = i;
                        }
                    }
                }
                WordFilter { root }
            }

            pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
                let mut node = &self.root;
                for b in suffix.bytes().chain([b'{']).chain(prefix.bytes()) {
                    node = node.children[(b - b'a') as usize].as_deref()?;
                }
                Some(node.best)
            }
        }
    """,
    visible=[
        T("leetcode_apple", "words = [\"apple\"], f(\"a\", \"e\")", 'wf.f("a", "e")', "Some(0)", setup=WORD_FILTER_TESTS_SETUP),
        T("no_match", "words = [\"apple\"], f(\"b\", \"e\"), f(\"a\", \"x\")", '(wf.f("b", "e"), wf.f("a", "x"))', "(None, None)", setup=WORD_FILTER_TESTS_SETUP),
        T("largest_index_wins", "words = [\"apple\", \"ample\", \"angle\"], f(\"a\", \"le\")", 'wf.f("a", "le")', "Some(2)",
          setup='let wf = WordFilter::new(&["apple", "ample", "angle"]);'),
        T("empty_prefix_and_suffix", "words = [\"cat\", \"dog\"], f(\"\", \"\"), f(\"\", \"t\"), f(\"d\", \"\")", '(wf.f("", ""), wf.f("", "t"), wf.f("d", ""))', "(Some(1), Some(0), Some(1))",
          setup='let wf = WordFilter::new(&["cat", "dog"]);'),
        T("prefix_and_suffix_overlap", "words = [\"abc\"], f(\"abc\", \"abc\"), f(\"ab\", \"bc\"), f(\"abc\", \"c\")", '(wf.f("abc", "abc"), wf.f("ab", "bc"), wf.f("abc", "c"))', "(Some(0), Some(0), Some(0))",
          setup='let wf = WordFilter::new(&["abc"]);'),
        T("both_must_hold_on_the_same_word", "words = [\"ab\", \"cd\"], f(\"a\", \"d\")", 'wf.f("a", "d")', "None", setup='let wf = WordFilter::new(&["ab", "cd"]);'),
    ],
    hidden=[
        T("longer_than_word", "words = [\"ab\"], f(\"abc\", \"\"), f(\"\", \"zab\")", '(wf.f("abc", ""), wf.f("", "zab"))', "(None, None)", setup='let wf = WordFilter::new(&["ab"]);'),
        T("duplicate_words", "words = [\"x\", \"y\", \"x\"], f(\"x\", \"x\")", 'wf.f("x", "x")', "Some(2)", setup='let wf = WordFilter::new(&["x", "y", "x"]);'),
        T("single_letter", "words = [\"a\"], f(\"a\", \"a\")", 'wf.f("a", "a")', "Some(0)", setup='let wf = WordFilter::new(&["a"]);'),
        T("earlier_word_only_match", "words = [\"pop\", \"pot\", \"top\"], f(\"p\", \"p\")", 'wf.f("p", "p")', "Some(0)", setup='let wf = WordFilter::new(&["pop", "pot", "top"]);'),
        T("suffix_not_substring", "words = [\"abcab\"], f(\"\", \"bc\")", 'wf.f("", "bc")', "None", setup='let wf = WordFilter::new(&["abcab"]);'),
        T("whole_word_both_sides", "words = [\"level\", \"lever\"], f(\"lev\", \"el\"), f(\"lever\", \"lever\")", '(wf.f("lev", "el"), wf.f("lever", "lever"))', "(Some(0), Some(1))",
          setup='let wf = WordFilter::new(&["level", "lever"]);'),
        T("seven_letters", "words = [\"abcdefg\"], f(\"abcdefg\", \"g\"), f(\"a\", \"abcdefg\")", '(wf.f("abcdefg", "g"), wf.f("a", "abcdefg"))', "(Some(0), Some(0))",
          setup='let wf = WordFilter::new(&["abcdefg"]);'),
        T("z_is_not_the_separator", "words = [\"zz\", \"az\"], f(\"z\", \"z\"), f(\"a\", \"z\")", '(wf.f("z", "z"), wf.f("a", "z"))', "(Some(0), Some(1))",
          setup='let wf = WordFilter::new(&["zz", "az"]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1011);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(6) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "ab"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let wf = WordFilter::new(&refs);
                for _ in 0..5 {
                    let (pl, sl) = (rng.below(3), rng.below(3));
                    let prefix = rng.string(pl, "ab");
                    let suffix = rng.string(sl, "ab");
                    let want = refs.iter().rposition(|w| w.starts_with(prefix.as_str()) && w.ends_with(suffix.as_str()));
                    check!(format!("words = {refs:?}, f({prefix:?}, {suffix:?})"), wf.f(&prefix, &suffix), want);
                }
            }
        }

        #[test]
        fn scale_10k_words_200k_queries() {
            let words: Vec<String> = (0..10_000).map(|i| base10(i, 4)).collect();
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let wf = WordFilter::new(&refs);
            let mut hits = 0usize;
            let mut sum = 0usize;
            for i in 0..200_000 {
                let w = &words[i % 10_000];
                // Matches only word 0 ("aaaa"), a word with no match, then the word itself by its two halves.
                if let Some(j) = wf.f("a", "aaa") {
                    sum += j;
                    hits += 1;
                }
                hits += wf.f(&w[..1], "k").is_some() as usize;
                sum += wf.f(&w[..2], &w[2..]).unwrap_or(0);
            }
            check!("words = every 4-letter word over a..j; 200000 × (f(\\"a\\", \\"aaa\\"), f(_, \\"k\\"), f(first half, second half))", (hits, sum), (200_000, 20 * (0..10_000usize).sum::<usize>()));
        }
        """ + BASE10,
    ],
    wrong=dict(
        scan_from_the_end="""
            pub struct WordFilter {
                words: Vec<String>,
            }

            impl WordFilter {
                pub fn new(words: &[&str]) -> Self {
                    WordFilter { words: words.iter().map(|w| w.to_string()).collect() }
                }

                pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
                    self.words.iter().rposition(|w| w.starts_with(prefix) && w.ends_with(suffix))
                }
            }
        """,
        first_index_kept="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 27],
                best: Option<usize>,
            }

            pub struct WordFilter {
                root: Node,
            }

            impl WordFilter {
                pub fn new(words: &[&str]) -> Self {
                    let mut root = Node::default();
                    for (i, w) in words.iter().enumerate() {
                        for start in 0..=w.len() {
                            let mut node = &mut root;
                            for b in w[start..].bytes().chain([b'{']).chain(w.bytes()) {
                                node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                                node.best.get_or_insert(i);
                            }
                        }
                    }
                    WordFilter { root }
                }

                pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
                    let mut node = &self.root;
                    for b in suffix.bytes().chain([b'{']).chain(prefix.bytes()) {
                        node = node.children[(b - b'a') as usize].as_deref()?;
                    }
                    node.best
                }
            }
        """,
    ),
    hints=[("approach", "For each word and each of its suffixes, insert `suffix + '{' + word` into one trie. A query walks `suffix + '{' + prefix`: the separator ends the suffix part and the rest is a prefix of the word."),
           ("rust", "`'{'` is `b'z' + 1`, so `(b - b'a') as usize` gives it index 26 in a 27-slot array. `w[start..].bytes().chain([b'{']).chain(w.bytes())` builds each key without allocating."),
           ("edge case", "Write the index into every node on the path as you insert words in order: later words overwrite, so each node holds the largest index.")],
    notes=("A word of length L makes L + 1 keys of length at most 2L + 1, so building is O(n · L²) and each query is O(|prefix| + |suffix|), independent of n. Scanning the words per query is O(n · L) each, too slow for 2·10⁵ queries.", "build O(n · L²), query O(|prefix| + |suffix|)", "O(n · L² × 27)"),
    follow_up="A `HashMap<(String, String), usize>` of every prefix/suffix pair also works. Compare its memory with the trie's.",
    related=["S4"],
))

# ---------------------------------------------------------------- string algorithms (medium)

P.append(dict(
    slug="find-the-first-occurrence", title="Find the first occurrence (KMP)", level="medium", stage="string-algorithms", tags=["KMP", "generics", "slices"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Adobe"],
    teaches=["The KMP failure table: after a mismatch, fall back to the longest border of what already matched instead of restarting.",
             "Generic over `T: PartialEq`: slices have no linear-time `find` for a sub-slice (`str::find` does), so here you write it."],
    statement="""
        Return the index of the first place `needle` occurs in `haystack`, or `None` if it never does.
        An empty `needle` occurs at index 0.

        Both are slices of any comparable type: bytes, characters, numbers. `str::find` is not available on slices,
        and checking every window is too slow for the largest inputs.
    """,
    examples=[("haystack = b\"sadbutsad\", needle = b\"sad\"", "Some(0)"), ("haystack = b\"leetcode\", needle = b\"leeto\"", "None")],
    constraints=["0 ≤ haystack.len(), needle.len() ≤ 10⁶"],
    starter="""
        pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        /// `border[i]`: length of the longest proper prefix of `needle[..=i]` that is also a suffix of it.
        fn borders<T: PartialEq>(needle: &[T]) -> Vec<usize> {
            let mut border = vec![0; needle.len()];
            let mut k = 0;
            for i in 1..needle.len() {
                while k > 0 && needle[i] != needle[k] {
                    k = border[k - 1];
                }
                if needle[i] == needle[k] {
                    k += 1;
                }
                border[i] = k;
            }
            border
        }

        pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
            if needle.is_empty() {
                return Some(0);
            }
            let border = borders(needle);
            // `k` items of the needle are matched so far; a mismatch falls back to a shorter border, never re-reads the haystack.
            let mut k = 0;
            for (i, x) in haystack.iter().enumerate() {
                while k > 0 && *x != needle[k] {
                    k = border[k - 1];
                }
                if *x == needle[k] {
                    k += 1;
                    if k == needle.len() {
                        return Some(i + 1 - k);
                    }
                }
            }
            None
        }
    """,
    visible=[
        T("leetcode_sadbutsad", "haystack = b\"sadbutsad\", needle = b\"sad\"", 'find_first(b"sadbutsad", b"sad")', "Some(0)"),
        T("leetcode_leeto", "haystack = b\"leetcode\", needle = b\"leeto\"", 'find_first(b"leetcode", b"leeto")', "None"),
        T("empty_needle", "haystack = b\"abc\", needle = b\"\"", 'find_first(b"abc", b"")', "Some(0)"),
        T("empty_haystack", "haystack = b\"\", needle = b\"a\"", 'find_first(b"", b"a")', "None"),
        T("first_of_several", "haystack = b\"abcabc\", needle = b\"bc\"", 'find_first(b"abcabc", b"bc")', "Some(1)"),
        T("mismatch_must_not_skip_a_start", "haystack = b\"aaab\", needle = b\"aab\" (the match starts inside the failed attempt)", 'find_first(b"aaab", b"aab")', "Some(1)"),
        T("numbers", "haystack = [1, 2, 1, 2, 3], needle = [1, 2, 3]", "find_first(&[1, 2, 1, 2, 3], &[1, 2, 3])", "Some(2)"),
    ],
    hidden=[
        T("needle_longer", "haystack = b\"ab\", needle = b\"abc\"", 'find_first(b"ab", b"abc")', "None"),
        T("equal", "haystack = b\"abc\", needle = b\"abc\"", 'find_first(b"abc", b"abc")', "Some(0)"),
        T("both_empty", "haystack = b\"\", needle = b\"\"", 'find_first(b"", b"")', "Some(0)"),
        T("at_the_end", "haystack = b\"xxxxy\", needle = b\"xy\"", 'find_first(b"xxxxy", b"xy")', "Some(3)"),
        T("overlapping_border", "haystack = b\"abababca\", needle = b\"ababca\"", 'find_first(b"abababca", b"ababca")', "Some(2)"),
        T("fallback_chain", "haystack = b\"aabaaabaaac\", needle = b\"aabaaac\"", 'find_first(b"aabaaabaaac", b"aabaaac")', "Some(4)"),
        T("chars", "haystack = chars of \"héllo wörld\", needle = chars of \"wö\"", "find_first(&h, &n)", "Some(6)",
          setup='let h: Vec<char> = "héllo wörld".chars().collect();\nlet n: Vec<char> = "wö".chars().collect();'),
        T("negatives", "haystack = [-1, -1, -2], needle = [-1, -2]", "find_first(&[-1, -1, -2], &[-1, -2])", "Some(1)"),
        T("strings_as_items", "haystack = [\"a\", \"b\", \"a\", \"c\"], needle = [\"a\", \"c\"]", 'find_first(&["a", "b", "a", "c"], &["a", "c"])', "Some(2)"),
        T("single_miss", "haystack = b\"a\", needle = b\"b\"", 'find_first(b"a", b"b")', "None"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1012);
            for _ in 0..400 {
                let (hl, nl) = (rng.below(14), rng.below(5));
                let h: Vec<u8> = rng.vec(hl, 0, 1);
                let n: Vec<u8> = rng.vec(nl, 0, 1);
                let want = if n.is_empty() { Some(0) } else { h.windows(n.len()).position(|w| w == n.as_slice()) };
                check!(format!("haystack = {h:?}, needle = {n:?}"), find_first(&h, &n), want);
            }
        }

        #[test]
        fn scale_million_words() {
            // A phrase search over words. Every window matches all but the needle's last word, so checking windows one by one is quadratic.
            let mut h = vec!["to"; 1_000_000];
            h.push("be");
            let mut n = vec!["to"; 100_000];
            n.push("be");
            check!("haystack = [\\"to\\"; 10⁶] + [\\"be\\"], needle = [\\"to\\"; 10⁵] + [\\"be\\"]", find_first(&h, &n), Some(900_000));
        }
        """,
    ],
    wrong=dict(
        every_window="""
            pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
                if needle.is_empty() {
                    return Some(0);
                }
                haystack.windows(needle.len()).position(|w| w == needle)
            }
        """,
        restart_without_fallback="""
            pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
                if needle.is_empty() {
                    return Some(0);
                }
                let mut k = 0;
                for (i, x) in haystack.iter().enumerate() {
                    if *x == needle[k] {
                        k += 1;
                        if k == needle.len() {
                            return Some(i + 1 - k);
                        }
                    } else {
                        k = 0;
                    }
                }
                None
            }
        """,
    ),
    hints=[("approach", "Precompute, for each prefix of the needle, the length of its longest proper prefix that is also its suffix (its border). On a mismatch after matching k items, the next useful attempt has already matched `border[k - 1]` items."),
           ("rust", "Keep one counter `k` of matched items and walk the haystack once with `iter().enumerate()`; the fallback is a `while k > 0 && x != needle[k]` loop. `T: PartialEq` is all you need."),
           ("edge case", "Resetting `k` to 0 on a mismatch skips matches: in `aaab` the needle `aab` starts at 1, inside the attempt that failed.")],
    notes=("KMP never moves backwards in the haystack: each mismatch shortens the current match to a border, and the total number of fallbacks is bounded by the number of advances, so it's linear. The border table is the same idea run on the needle against itself. `windows(m).position(..)` is O(n·m) in the worst case; `str::find` uses the Two-Way algorithm, linear with O(1) extra space, but only for strings.", "O(n + m)", "O(m)"),
    follow_up="How would you return every occurrence, including overlapping ones, and what changes after a full match?",
    related=["S2", "S3", "L5"],
))

P.append(dict(
    slug="repeated-substring-pattern", title="Repeated substring pattern", level="medium", stage="string-algorithms", tags=["KMP", "&str"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["The border table answers periodicity: `s` is `t` repeated when `n - border[n - 1]` is a proper divisor of `n`.",
             "Working on bytes is safe here: a repetition of a whole string always splits on character boundaries."],
    statement="""
        Return `true` if `s` is some shorter string repeated two or more times (`"abcabc"` is `"abc"` twice).
        The empty string and a single character are not repetitions.

        `s` can hold any Unicode text.
    """,
    examples=[("s = \"abab\"", "true"), ("s = \"aba\"", "false"), ("s = \"abcabcabcabc\"", "true")],
    constraints=["0 ≤ s.len() ≤ 2·10⁵ bytes"],
    starter="""
        pub fn repeated_substring_pattern(s: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn repeated_substring_pattern(s: &str) -> bool {
            let b = s.as_bytes();
            let n = b.len();
            if n < 2 {
                return false;
            }
            // KMP border table: border[i] is the longest proper prefix of b[..=i] that is also its suffix.
            let mut border = vec![0; n];
            let mut k = 0;
            for i in 1..n {
                while k > 0 && b[i] != b[k] {
                    k = border[k - 1];
                }
                if b[i] == b[k] {
                    k += 1;
                }
                border[i] = k;
            }
            // The smallest period of s; s is a repetition exactly when that period divides n (and isn't n itself).
            let period = n - border[n - 1];
            period < n && n % period == 0
        }
    """,
    visible=[
        T("leetcode_abab", "s = \"abab\"", 'repeated_substring_pattern("abab")', "true"),
        T("leetcode_aba", "s = \"aba\"", 'repeated_substring_pattern("aba")', "false"),
        T("leetcode_abc_four_times", "s = \"abcabcabcabc\"", 'repeated_substring_pattern("abcabcabcabc")', "true"),
        T("single_character", "s = \"a\"", 'repeated_substring_pattern("a")', "false"),
        T("empty", "s = \"\"", 'repeated_substring_pattern("")', "false"),
        T("must_cover_the_whole_string", "s = \"abcabcab\" (\"abc\" repeats, but doesn't fill the string)", 'repeated_substring_pattern("abcabcab")', "false"),
        T("three_copies", "s = \"xyzxyzxyz\"", 'repeated_substring_pattern("xyzxyzxyz")', "true"),
    ],
    hidden=[
        T("two_same_letters", "s = \"zz\"", 'repeated_substring_pattern("zz")', "true"),
        T("two_different_letters", "s = \"ab\"", 'repeated_substring_pattern("ab")', "false"),
        T("border_but_no_period", "s = \"abaab\"", 'repeated_substring_pattern("abaab")', "false"),
        T("unit_with_inner_repeat", "s = \"abaababaab\" (\"abaab\" twice)", 'repeated_substring_pattern("abaababaab")', "true"),
        T("almost", "s = \"abcabcabd\"", 'repeated_substring_pattern("abcabcabd")', "false"),
        T("accented", "s = \"éaéa\"", 'repeated_substring_pattern("éaéa")', "true"),
        T("cjk", "s = \"日本日本日本\"", 'repeated_substring_pattern("日本日本日本")', "true"),
        T("single_multibyte_char", "s = \"é\" (2 bytes, 1 character)", 'repeated_substring_pattern("é")', "false"),
        T("same_letter_many_times", "s = 'q' × 7", 'repeated_substring_pattern(&"q".repeat(7))', "true"),
        T("prime_length_mixed", "s = \"aabaa\"", 'repeated_substring_pattern("aabaa")', "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1013);
            for _ in 0..400 {
                let s = if rng.bool() {
                    let (ul, k) = (1 + rng.below(3), 1 + rng.below(4));
                    rng.string(ul, "ab").repeat(k)
                } else {
                    let len = rng.below(10);
                    rng.string(len, "ab")
                };
                let n = s.len();
                let want = (1..n).any(|p| n % p == 0 && s[..p].repeat(n / p) == s);
                check!(format!("s = {s:?}"), repeated_substring_pattern(&s), want);
            }
        }

        #[test]
        fn scale_200k() {
            // Every candidate period matches until the very last byte.
            let no = format!("{}b", "a".repeat(199_999));
            let yes = format!("{}b", "a".repeat(99_999)).repeat(2);
            check!("s = 'a' × 199999 + \\"b\\"; s = ('a' × 99999 + \\"b\\") × 2", (repeated_substring_pattern(&no), repeated_substring_pattern(&yes)), (false, true));
        }
        """,
    ],
    wrong=dict(
        halves_only="""
            pub fn repeated_substring_pattern(s: &str) -> bool {
                let n = s.len();
                n >= 2 && n % 2 == 0 && s[..n / 2] == s[n / 2..]
            }
        """,
        doubled_contains_itself="""
            pub fn repeated_substring_pattern(s: &str) -> bool {
                s.len() >= 2 && format!("{s}{s}").contains(s)
            }
        """,
        every_period="""
            pub fn repeated_substring_pattern(s: &str) -> bool {
                let b = s.as_bytes();
                let n = b.len();
                (1..=n / 2).any(|p| (p..n).all(|i| b[i] == b[i - p]) && n % p == 0)
            }
        """,
    ),
    hints=[("approach", "Build the KMP border table of `s`. Its last entry gives the smallest period `p = n - border[n - 1]`: `s` repeats a unit exactly when `p < n` and `p` divides `n`."),
           ("rust", "`s.as_bytes()` is fine: the first byte of the repeated unit is the first byte of a character, so a period found on bytes never splits a character."),
           ("edge case", "`\"abcabcab\"` has period 3 but length 8; a unit that doesn't divide the length doesn't count. The doubled-string trick needs its first and last characters removed: `(s + s)[1..2n-1]` contains `s`.")],
    notes=("If `s` has a border of length `b`, it has period `n - b`, and the longest border gives the smallest period. A string is a whole number of copies of some unit exactly when its smallest period divides its length. The other classic answer checks whether `s` occurs inside `s + s` with the first and last characters cut off; with a linear search that's also O(n). Trying only divisors of `n` is O(n · d(n)), fine in practice; trying every period is O(n²).", "O(n)", "O(n)"),
    follow_up="Return the shortest repeating unit itself, as a slice of `s`.",
    related=["S2"],
))

P.append(dict(
    slug="longest-palindromic-substring", title="Longest palindromic substring", level="medium", stage="string-algorithms", tags=["palindrome", "chars", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Adobe", "Bloomberg"],
    teaches=["Expand around each of the 2n − 1 centres: a palindrome grows outwards while both ends match.",
             "Work on characters, return a byte slice: keep each character's byte offset so the answer is `&s[a..b]`."],
    statement="""
        Return the longest substring of `s` that reads the same forwards and backwards, as a slice of `s`.
        If several have that length, return the one that starts first. The empty string gives `""`.

        `s` can hold any Unicode text; palindromes are made of whole characters.
    """,
    examples=[("s = \"babad\"", "\"bab\""), ("s = \"cbbd\"", "\"bb\"")],
    constraints=["0 ≤ number of characters ≤ 5000"],
    starter="""
        pub fn longest_palindrome(s: &str) -> &str {
            todo!()
        }
    """,
    solution="""
        /// Grows the palindrome `chars[l..r]` outwards while both ends match.
        fn expand(chars: &[char], mut l: usize, mut r: usize) -> (usize, usize) {
            while l > 0 && r < chars.len() && chars[l - 1] == chars[r] {
                l -= 1;
                r += 1;
            }
            (l, r)
        }

        pub fn longest_palindrome(s: &str) -> &str {
            let chars: Vec<char> = s.chars().collect();
            // Byte offset of every character, plus the end, so a char range maps back to a slice of `s`.
            let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
            let (mut lo, mut hi) = (0, 0);
            for i in 0..chars.len() {
                // Odd length: centred on char i. Even length: centred on the gap before char i.
                for (l, r) in [expand(&chars, i, i + 1), expand(&chars, i, i)] {
                    // Strictly longer only, so the earliest start wins a tie.
                    if r - l > hi - lo {
                        (lo, hi) = (l, r);
                    }
                }
            }
            &s[offsets[lo]..offsets[hi]]
        }
    """,
    visible=[
        T("leetcode_babad", "s = \"babad\" (\"aba\" is as long, but \"bab\" starts first)", 'longest_palindrome("babad")', '"bab"'),
        T("leetcode_cbbd", "s = \"cbbd\"", 'longest_palindrome("cbbd")', '"bb"'),
        T("single", "s = \"a\"", 'longest_palindrome("a")', '"a"'),
        T("empty", "s = \"\"", 'longest_palindrome("")', '""'),
        T("no_repeat_takes_the_first_letter", "s = \"ac\"", 'longest_palindrome("ac")', '"a"'),
        T("unicode", "s = \"ñoño\"", 'longest_palindrome("ñoño")', '"ñoñ"'),
    ],
    hidden=[
        T("reverse_is_not_the_answer", "s = \"abacdfgdcaba\" (\"abacd\" appears reversed too, but isn't a palindrome)", 'longest_palindrome("abacdfgdcaba")', '"aba"'),
        T("all_same", "s = \"aaaa\"", 'longest_palindrome("aaaa")', '"aaaa"'),
        T("even_at_the_end", "s = \"abb\"", 'longest_palindrome("abb")', '"bb"'),
        T("long_even", "s = \"forgeeksskeegfor\"", 'longest_palindrome("forgeeksskeegfor")', '"geeksskeeg"'),
        T("lone_multibyte", "s = \"é\"", 'longest_palindrome("é")', '"é"'),
        T("emoji", "s = \"🦀a🦀\"", 'longest_palindrome("🦀a🦀")', '"🦀a🦀"'),
        T("distinct_letters", "s = \"abcde\"", 'longest_palindrome("abcde")', '"a"'),
        T("spaces_count", "s = \"ab ba\"", 'longest_palindrome("ab ba")', '"ab ba"'),
        T("case_sensitive", "s = \"Aa\"", 'longest_palindrome("Aa")', '"A"'),
        T("at_the_start", "s = \"xabax yz\"", 'longest_palindrome("xabax yz")', '"xabax"'),
        T("slice_of_the_input", "the answer points into s", "std::ptr::eq(got.as_ptr(), s[1..].as_ptr())", "true",
          setup='let s = String::from("xracecary");\nlet got = longest_palindrome(&s);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1014);
            for _ in 0..400 {
                let len = rng.below(12);
                let s = rng.string(len, "abé");
                let cs: Vec<char> = s.chars().collect();
                let mut want: Vec<char> = Vec::new();
                for i in 0..cs.len() {
                    for j in i + 1..=cs.len() {
                        let w = &cs[i..j];
                        if w.iter().eq(w.iter().rev()) && w.len() > want.len() {
                            want = w.to_vec();
                        }
                    }
                }
                check!(format!("s = {s:?}"), longest_palindrome(&s).to_string(), want.iter().collect::<String>());
            }
        }

        #[test]
        fn scale_5000_same_letter() {
            let s = "a".repeat(5000);
            check!("s = 'a' × 5000", longest_palindrome(&s).len(), 5000);
        }

        #[test]
        fn scale_5000_two_blocks() {
            // The answer is the block of b's at the end.
            let s = format!("{}{}", "abc".repeat(1000), "b".repeat(2000));
            let got = longest_palindrome(&s);
            check!("s = \\"abc\\" × 1000 + 'b' × 2000", (got.len(), std::ptr::eq(got.as_ptr(), s[3000..].as_ptr())), (2000, true));
        }
        """,
    ],
    wrong=dict(
        bytes_not_chars="""
            pub fn longest_palindrome(s: &str) -> &str {
                let b = s.as_bytes();
                let (mut lo, mut hi) = (0, 0);
                for i in 0..b.len() {
                    for (mut l, mut r) in [(i, i + 1), (i, i)] {
                        while l > 0 && r < b.len() && b[l - 1] == b[r] {
                            l -= 1;
                            r += 1;
                        }
                        if r - l > hi - lo {
                            (lo, hi) = (l, r);
                        }
                    }
                }
                &s[lo..hi]
            }
        """,
        last_on_a_tie="""
            pub fn longest_palindrome(s: &str) -> &str {
                let chars: Vec<char> = s.chars().collect();
                let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
                let (mut lo, mut hi) = (0, 0);
                for i in 0..chars.len() {
                    for (mut l, mut r) in [(i, i + 1), (i, i)] {
                        while l > 0 && r < chars.len() && chars[l - 1] == chars[r] {
                            l -= 1;
                            r += 1;
                        }
                        if r - l >= hi - lo {
                            (lo, hi) = (l, r);
                        }
                    }
                }
                &s[offsets[lo]..offsets[hi]]
            }
        """,
        check_every_substring="""
            pub fn longest_palindrome(s: &str) -> &str {
                let chars: Vec<char> = s.chars().collect();
                let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
                let (mut lo, mut hi) = (0, 0);
                for i in 0..chars.len() {
                    for j in i + 1..=chars.len() {
                        let w = &chars[i..j];
                        if w.iter().eq(w.iter().rev()) && j - i > hi - lo {
                            (lo, hi) = (i, j);
                        }
                    }
                }
                &s[offsets[lo]..offsets[hi]]
            }
        """,
    ),
    hints=[("approach", "Every palindrome has a centre: a character (odd length) or the gap between two (even length). From each of the 2n − 1 centres, grow outwards while the ends match, and keep the longest."),
           ("rust", "Collect `chars()` into a `Vec<char>` to index characters, and keep `char_indices()` offsets (plus `s.len()`) to turn the best char range back into `&s[a..b]`."),
           ("edge case", "Comparing bytes breaks on `\"é\"`: a one-byte \"palindrome\" there ends inside the character, and slicing it panics.")],
    notes=("Expanding from a centre costs the length of the palindrome found, so the total is O(n²) in the worst case (`\"aaaa…\"`) and much less on typical text. Checking every substring is O(n³). Manacher's algorithm reuses the mirror image of palindromes already found to get O(n). Replacing strictly-longer with longer-or-equal returns the last of the tied answers instead of the first.", "O(n²)", "O(n) for the characters"),
    follow_up="Manacher's algorithm finds the answer in O(n). What does it reuse from palindromes already found?",
    related=["D12", "S2"],
))

P.append(dict(
    slug="palindromic-substrings", title="Palindromic substrings", level="medium", stage="string-algorithms", tags=["palindrome", "chars", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Counting reuses the expand-around-centre loop: every step outwards is one more palindrome.",
             "Substrings at different positions count separately, even when they're equal."],
    statement="""
        Count the substrings of `s` that are palindromes. Substrings at different positions count separately,
        so `"aaa"` has six: three `"a"`, two `"aa"` and one `"aaa"`.

        `s` can hold any Unicode text; count substrings of whole characters.
    """,
    examples=[("s = \"abc\"", "3"), ("s = \"aaa\"", "6")],
    constraints=["0 ≤ number of characters ≤ 5000"],
    starter="""
        pub fn count_substrings(s: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn count_substrings(s: &str) -> usize {
            let chars: Vec<char> = s.chars().collect();
            let n = chars.len();
            let mut count = 0;
            for i in 0..n {
                // Odd palindromes centred on char i, then even ones centred on the gap after it.
                for (mut l, mut r) in [(i, i), (i, i + 1)] {
                    while r < n && chars[l] == chars[r] {
                        count += 1;
                        if l == 0 {
                            break;
                        }
                        l -= 1;
                        r += 1;
                    }
                }
            }
            count
        }
    """,
    visible=[
        T("leetcode_abc", "s = \"abc\"", 'count_substrings("abc")', "3"),
        T("leetcode_aaa", "s = \"aaa\" (a, a, a, aa, aa, aaa)", 'count_substrings("aaa")', "6"),
        T("empty", "s = \"\"", 'count_substrings("")', "0"),
        T("single", "s = \"a\"", 'count_substrings("a")', "1"),
        T("even_length", "s = \"abba\" (a, b, b, a, bb, abba)", 'count_substrings("abba")', "6"),
        T("characters_not_bytes", "s = \"éé\" (é, é, éé)", 'count_substrings("éé")', "3"),
    ],
    hidden=[
        T("four_same", "s = \"aaaa\"", 'count_substrings("aaaa")', "10"),
        T("odd_nested", "s = \"abcba\"", 'count_substrings("abcba")', "7"),
        T("alternating", "s = \"abab\"", 'count_substrings("abab")', "6"),
        T("racecar", "s = \"racecar\"", 'count_substrings("racecar")', "10"),
        T("emoji", "s = \"🦀🦀\"", 'count_substrings("🦀🦀")', "3"),
        T("case_sensitive", "s = \"Aa\"", 'count_substrings("Aa")', "2"),
        T("palindrome_then_noise", "s = \"abcdcbaxyz\"", 'count_substrings("abcdcbaxyz")', "13"),
        T("two_different", "s = \"ab\"", 'count_substrings("ab")', "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1015);
            for _ in 0..400 {
                let len = rng.below(12);
                let s = rng.string(len, "abé");
                let cs: Vec<char> = s.chars().collect();
                let mut want = 0;
                for i in 0..cs.len() {
                    for j in i + 1..=cs.len() {
                        let w = &cs[i..j];
                        want += w.iter().eq(w.iter().rev()) as usize;
                    }
                }
                check!(format!("s = {s:?}"), count_substrings(&s), want);
            }
        }

        #[test]
        fn scale_5000_same_letter() {
            let s = "a".repeat(5000);
            check!("s = 'a' × 5000", count_substrings(&s), 5000 * 5001 / 2);
        }
        """,
    ],
    wrong=dict(
        distinct_only="""
            use std::collections::HashSet;

            pub fn count_substrings(s: &str) -> usize {
                let chars: Vec<char> = s.chars().collect();
                let mut seen: HashSet<&[char]> = HashSet::new();
                for i in 0..chars.len() {
                    for (mut l, mut r) in [(i, i), (i, i + 1)] {
                        while r < chars.len() && chars[l] == chars[r] {
                            seen.insert(&chars[l..=r]);
                            if l == 0 {
                                break;
                            }
                            l -= 1;
                            r += 1;
                        }
                    }
                }
                seen.len()
            }
        """,
        odd_centres_only="""
            pub fn count_substrings(s: &str) -> usize {
                let chars: Vec<char> = s.chars().collect();
                let mut count = 0;
                for i in 0..chars.len() {
                    let (mut l, mut r) = (i, i);
                    while r < chars.len() && chars[l] == chars[r] {
                        count += 1;
                        if l == 0 {
                            break;
                        }
                        l -= 1;
                        r += 1;
                    }
                }
                count
            }
        """,
        check_every_substring="""
            pub fn count_substrings(s: &str) -> usize {
                let chars: Vec<char> = s.chars().collect();
                let mut count = 0;
                for i in 0..chars.len() {
                    for j in i + 1..=chars.len() {
                        let w = &chars[i..j];
                        count += w.iter().eq(w.iter().rev()) as usize;
                    }
                }
                count
            }
        """,
    ),
    hints=[("approach", "Expand around each centre as in the longest-palindrome problem, but count every step: each time both ends match, that's one more palindrome."),
           ("rust", "Index a `Vec<char>`, not the bytes. With `usize` indices, check `l == 0` before `l -= 1` instead of letting it underflow."),
           ("edge case", "There are two kinds of centre: a character (`\"aba\"`) and the gap between two (`\"abba\"`). Missing the gaps undercounts.")],
    notes=("Each expansion step finds a new palindrome, so the work equals the answer plus 2n − 1 failed steps: O(n²) worst case (all one letter, n(n+1)/2 palindromes), and the answer itself can be that big. Checking every substring is O(n³). Manacher's algorithm gives every centre's radius in O(n), and the count is the sum of the radii.", "O(n²)", "O(n) for the characters"),
    follow_up="With Manacher's radii, how do you get the count in O(n)?",
    related=["D12"],
))

P.append(dict(
    slug="string-to-integer", title="String to integer (atoi)", level="medium", stage="string-algorithms", tags=["parsing", "checked arithmetic", "i32"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg", "Goldman Sachs"],
    teaches=["Accumulate towards the sign with `checked_mul`/`checked_sub`: `i32::MIN` has no positive twin in `i32`.",
             "`trim_start` and `char::is_numeric` accept more than this format does; match the spec's exact bytes."],
    statement="""
        Read an `i32` from the start of `s`, the way C's `atoi` does:

        1. skip leading spaces (only `' '`, no other whitespace);
        2. read one optional sign, `'+'` or `'-'`;
        3. read ASCII digits until the first non-digit or the end, skipping leading zeros;
        4. clamp the result to `i32::MIN..=i32::MAX`.

        If no digits were read, the answer is 0. Anything after the digits is ignored.
    """,
    examples=[("s = \"42\"", "42"), ("s = \"   -042\"", "-42"), ("s = \"1337c0d3\"", "1337"), ("s = \"words and 987\"", "0")],
    constraints=["0 ≤ s.len() ≤ 10⁶ bytes, any Unicode"],
    starter="""
        pub fn my_atoi(s: &str) -> i32 {
            todo!()
        }
    """,
    solution="""
        pub fn my_atoi(s: &str) -> i32 {
            let s = s.trim_start_matches(' ');
            let (negative, digits) = match s.strip_prefix('-') {
                Some(rest) => (true, rest),
                None => (false, s.strip_prefix('+').unwrap_or(s)),
            };
            // Build the value on the sign's side of zero, so i32::MIN is reachable without overflowing.
            let mut n: i32 = 0;
            for b in digits.bytes().take_while(u8::is_ascii_digit) {
                let d = i32::from(b - b'0');
                let next = n.checked_mul(10).and_then(|n| if negative { n.checked_sub(d) } else { n.checked_add(d) });
                match next {
                    Some(v) => n = v,
                    None => return if negative { i32::MIN } else { i32::MAX },
                }
            }
            n
        }
    """,
    visible=[
        T("leetcode_42", "s = \"42\"", 'my_atoi("42")', "42"),
        T("leetcode_spaces_sign_zero", "s = \"   -042\"", 'my_atoi("   -042")', "-42"),
        T("leetcode_stops_at_letter", "s = \"1337c0d3\"", 'my_atoi("1337c0d3")', "1337"),
        T("leetcode_zero_then_minus", "s = \"0-1\"", 'my_atoi("0-1")', "0"),
        T("leetcode_words_first", "s = \"words and 987\"", 'my_atoi("words and 987")', "0"),
        T("clamps_below", "s = \"-91283472332\"", 'my_atoi("-91283472332")', "i32::MIN"),
        T("empty", "s = \"\"", 'my_atoi("")', "0"),
    ],
    hidden=[
        T("max", "s = \"2147483647\"", 'my_atoi("2147483647")', "i32::MAX"),
        T("one_past_max", "s = \"2147483648\"", 'my_atoi("2147483648")', "i32::MAX"),
        T("exact_min", "s = \"-2147483648\"", 'my_atoi("-2147483648")', "i32::MIN"),
        T("one_past_min", "s = \"-2147483649\"", 'my_atoi("-2147483649")', "i32::MIN"),
        T("two_signs", "s = \"+-12\"", 'my_atoi("+-12")', "0"),
        T("plus", "s = \"+1\"", 'my_atoi("+1")', "1"),
        T("tab_is_not_a_space", "s = \"\\t42\"", 'my_atoi("\\t42")', "0"),
        T("space_after_sign", "s = \" - 1\"", 'my_atoi(" - 1")', "0"),
        T("space_inside_digits", "s = \"   +0 123\"", 'my_atoi("   +0 123")', "0"),
        T("many_leading_zeros", "s = \"00000000000012345678\"", 'my_atoi("00000000000012345678")', "12345678"),
        T("thirty_nines", "s = '9' × 30", 'my_atoi(&"9".repeat(30))', "i32::MAX"),
        T("negative_thirty_nines", "s = \"-\" + '9' × 30", 'my_atoi(&format!("-{}", "9".repeat(30)))', "i32::MIN"),
        T("sign_only", "s = \"-\"", 'my_atoi("-")', "0"),
        T("only_spaces", "s = \"   \"", 'my_atoi("   ")', "0"),
        T("fullwidth_digits", "s = \"１２\" (not ASCII digits)", 'my_atoi("１２")', "0"),
        T("arabic_indic_digit", "s = \"٣\"", 'my_atoi("٣")', "0"),
        T("decimal_point", "s = \"3.14\"", 'my_atoi("3.14")', "3"),
        T("negative_zero", "s = \"-0\"", 'my_atoi("-0")', "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1016);
            for _ in 0..400 {
                let len = rng.below(14);
                let s = rng.string(len, " +-0123456789a9");
                // Reference: collect the digits, then do the arithmetic in i128 (at most 14 digits fit easily).
                let t = s.trim_start_matches(' ');
                let (sign, rest) = match t.as_bytes().first() {
                    Some(b'-') => (-1i128, &t[1..]),
                    Some(b'+') => (1i128, &t[1..]),
                    _ => (1i128, t),
                };
                let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
                let v = if digits.is_empty() { 0 } else { sign * digits.parse::<i128>().unwrap() };
                let want = v.clamp(i128::from(i32::MIN), i128::from(i32::MAX)) as i32;
                check!(format!("s = {s:?}"), my_atoi(&s), want);
            }
        }

        #[test]
        fn long_inputs() {
            let zeros = format!("{}42", "0".repeat(1_000_000));
            let spaces = format!("{}-7", " ".repeat(1_000_000));
            let nines = "9".repeat(1_000_000);
            check!("s = '0' × 10⁶ + \\"42\\"; ' ' × 10⁶ + \\"-7\\"; '9' × 10⁶", (my_atoi(&zeros), my_atoi(&spaces), my_atoi(&nines)), (42, -7, i32::MAX));
        }
        """,
    ],
    wrong=dict(
        trim_and_parse="""
            pub fn my_atoi(s: &str) -> i32 {
                let s = s.trim_start();
                let end = s.char_indices().position(|(i, c)| !(c.is_ascii_digit() || (i == 0 && (c == '+' || c == '-')))).unwrap_or(s.len());
                s[..end].parse::<i64>().map(|v| v.clamp(i64::from(i32::MIN), i64::from(i32::MAX)) as i32).unwrap_or(0)
            }
        """,
        signs_skipped_with_spaces="""
            pub fn my_atoi(s: &str) -> i32 {
                let negative = s.trim_start_matches(' ').starts_with('-');
                let digits = s.trim_start_matches([' ', '+', '-']);
                let mut n: i32 = 0;
                for b in digits.bytes().take_while(u8::is_ascii_digit) {
                    let d = i32::from(b - b'0');
                    let next = n.checked_mul(10).and_then(|n| if negative { n.checked_sub(d) } else { n.checked_add(d) });
                    match next {
                        Some(v) => n = v,
                        None => return if negative { i32::MIN } else { i32::MAX },
                    }
                }
                n
            }
        """,
        i64_accumulator="""
            pub fn my_atoi(s: &str) -> i32 {
                let s = s.trim_start_matches(' ');
                let (negative, digits) = match s.strip_prefix('-') {
                    Some(rest) => (true, rest),
                    None => (false, s.strip_prefix('+').unwrap_or(s)),
                };
                let mut n: i64 = 0;
                for b in digits.bytes().take_while(u8::is_ascii_digit) {
                    n = n * 10 + i64::from(b - b'0');
                }
                let n = if negative { -n } else { n };
                n.clamp(i64::from(i32::MIN), i64::from(i32::MAX)) as i32
            }
        """,
    ),
    hints=[("approach", "Walk the string once: skip spaces, read at most one sign, then digits. Stop at the first byte that doesn't fit the step you're on."),
           ("rust", "`trim_start_matches(' ')` skips only spaces, and `strip_prefix('-')` returns the rest if the sign is there. Accumulate with `checked_mul(10)` then `checked_add`/`checked_sub` so an overflow shows up as `None` and you clamp."),
           ("edge case", "A wider accumulator (`i64`) only delays the overflow: 30 nines don't fit either. Also, `\"-2147483648\"` is valid, but its magnitude doesn't fit in `i32`, so build negative numbers downwards.")],
    notes=("One pass, constant space. The traps are in the edges of the format: `trim_start` also skips tabs and Unicode spaces, `char::is_numeric` accepts non-ASCII digits, a second sign ends the number, and any fixed-width accumulator overflows on a long enough digit string, so the clamp has to happen as soon as the value leaves `i32`. Building the number on its sign's side of zero makes `i32::MIN` reachable.", "O(n)", "O(1)"),
    follow_up="How would you return an error that says why parsing failed (no digits, overflow) instead of 0 or a clamped value?",
    related=["S1", "S2", "L8"],
))

P.append(dict(
    slug="repeated-dna-sequences", title="Repeated DNA sequences", level="medium", stage="string-algorithms", tags=["rolling hash", "HashMap", "bits"],
    companies=["Amazon", "Google", "LinkedIn"],
    teaches=["A rolling hash updates in O(1) per step: drop the outgoing letter's weight, multiply by the base, add the new letter.",
             "With 4 letters and k ≤ 32, a base-4 key fits in a `u64` exactly, so equal keys mean equal windows."],
    statement="""
        `s` is a DNA string over the letters `A`, `C`, `G` and `T`. Return every sequence of length `k` that occurs
        more than once in `s` (occurrences may overlap), each once, as slices of `s`, ordered by where each first appears.

        LeetCode fixes `k` at 10; here it's a parameter from 1 to 32.
    """,
    examples=[("s = \"AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT\", k = 10", "[\"AAAAACCCCC\", \"CCCCCAAAAA\"]"), ("s = \"AAAAAAAAAAAAA\", k = 10", "[\"AAAAAAAAAA\"]")],
    constraints=["0 ≤ s.len() ≤ 10⁵, letters A, C, G, T only", "1 ≤ k ≤ 32"],
    starter="""
        pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        fn code(b: u8) -> u64 {
            match b {
                b'A' => 0,
                b'C' => 1,
                b'G' => 2,
                _ => 3,
            }
        }

        pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
            let b = s.as_bytes();
            if k > b.len() {
                return Vec::new();
            }
            // The window as a base-4 number. 4^k ≤ 2^64 for k ≤ 32, so different windows get different keys.
            let top = 4u64.pow(k as u32 - 1); // weight of the window's first letter
            let mut key = 0u64;
            // key -> (where it first starts, how many times it was seen)
            let mut seen: HashMap<u64, (usize, u32)> = HashMap::new();
            for i in 0..b.len() {
                if i >= k {
                    key -= code(b[i - k]) * top;
                }
                key = key * 4 + code(b[i]);
                if i + 1 >= k {
                    seen.entry(key).or_insert((i + 1 - k, 0)).1 += 1;
                }
            }
            let mut starts: Vec<usize> = seen.into_values().filter(|&(_, n)| n >= 2).map(|(start, _)| start).collect();
            starts.sort_unstable();
            starts.into_iter().map(|i| &s[i..i + k]).collect()
        }
    """,
    visible=[
        T("leetcode_two_sequences", "s = \"AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT\", k = 10", 'find_repeated_dna_sequences("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", 10)', 'vec!["AAAAACCCCC", "CCCCCAAAAA"]'),
        T("leetcode_overlapping", "s = \"AAAAAAAAAAAAA\", k = 10 (four overlapping copies, reported once)", 'find_repeated_dna_sequences("AAAAAAAAAAAAA", 10)', 'vec!["AAAAAAAAAA"]'),
        T("k_longer_than_s", "s = \"ACGT\", k = 10", 'find_repeated_dna_sequences("ACGT", 10)', "Vec::<&str>::new()"),
        T("empty", "s = \"\", k = 1", 'find_repeated_dna_sequences("", 1)', "Vec::<&str>::new()"),
        T("order_of_first_appearance", "s = \"ACGTCGAC\", k = 2 (AC first appears before CG, though CG repeats sooner)", 'find_repeated_dna_sequences("ACGTCGAC", 2)', 'vec!["AC", "CG"]'),
        T("single_letters", "s = \"AAAAAA\", k = 1", 'find_repeated_dna_sequences("AAAAAA", 1)', 'vec!["A"]'),
    ],
    hidden=[
        T("no_repeat", "s = \"ACGT\", k = 1", 'find_repeated_dna_sequences("ACGT", 1)', "Vec::<&str>::new()"),
        T("k_equals_len", "s = \"ACGT\", k = 4", 'find_repeated_dna_sequences("ACGT", 4)', "Vec::<&str>::new()"),
        T("k_32_repeat", "s = 'A' × 33, k = 32", "find_repeated_dna_sequences(&s, 32)", 'vec!["A".repeat(32)]', setup='let s = "A".repeat(33);'),
        T("k_32_first_letter_differs", "s = \"C\" + 'A' × 32, k = 32 (the two windows differ only in their first letter)", "find_repeated_dna_sequences(&s, 32)", "Vec::<&str>::new()",
          setup='let s = format!("C{}", "A".repeat(32));'),
        T("k_32_last_letter_differs", "s = 'T' × 32 + \"G\", k = 32", "find_repeated_dna_sequences(&s, 32)", "Vec::<&str>::new()", setup='let s = format!("{}G", "T".repeat(32));'),
        T("k_32_period_4", "s = \"ACGT\" × 16, k = 32", "find_repeated_dna_sequences(&s, 32)",
          'vec!["ACGT".repeat(8), "CGTA".repeat(8), "GTAC".repeat(8), "TACG".repeat(8)]', setup='let s = "ACGT".repeat(16);'),
        T("three_copies_once", "s = \"ACACAC\", k = 2", 'find_repeated_dna_sequences("ACACAC", 2)', 'vec!["AC", "CA"]'),
        T("all_t", "s = \"TTTT\", k = 3", 'find_repeated_dna_sequences("TTTT", 3)', 'vec!["TTT"]'),
        T("slices_of_s", "the answers point into s", "std::ptr::eq(got[0].as_ptr(), s.as_ptr())", "true",
          setup='let s = String::from("GATTGA");\nlet got = find_repeated_dna_sequences(&s, 2);'),
        """
        #[test]
        fn random_vs_brute_force() {
            use std::collections::HashMap;
            let mut rng = anneal_prelude::Rng::new(1017);
            for _ in 0..400 {
                let len = rng.below(20);
                let s = if rng.bool() { rng.string(len, "AC") } else { rng.string(len, "ACGT") };
                let k = 1 + rng.below(6);
                let mut count: HashMap<&str, usize> = HashMap::new();
                let mut order: Vec<&str> = Vec::new();
                for i in 0..(s.len() + 1).saturating_sub(k) {
                    let w = &s[i..i + k];
                    let c = count.entry(w).or_insert(0);
                    if *c == 0 {
                        order.push(w);
                    }
                    *c += 1;
                }
                let want: Vec<&str> = order.into_iter().filter(|w| count[w] >= 2).collect();
                check!(format!("s = {s:?}, k = {k}"), find_repeated_dna_sequences(&s, k), want);
            }
        }

        #[test]
        fn scale_100k() {
            use std::collections::HashMap;
            // Pseudo-random DNA with a planted 32-letter block repeated 5 times, plus a run of A's.
            let mut x: u64 = 12345;
            let mut dna: Vec<u8> = (0..100_000)
                .map(|_| {
                    x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                    b"ACGT"[(x >> 60) as usize & 3]
                })
                .collect();
            let block: Vec<u8> = dna[500..532].to_vec();
            for at in [20_000, 40_000, 60_000, 80_000] {
                dna[at..at + 32].copy_from_slice(&block);
            }
            dna[90_000..90_100].fill(b'A');
            let s = String::from_utf8(dna).unwrap();
            let mut count: HashMap<&str, (usize, usize)> = HashMap::new();
            for i in 0..=s.len() - 32 {
                count.entry(&s[i..i + 32]).or_insert((i, 0)).1 += 1;
            }
            let mut want: Vec<(usize, &str)> = count.into_iter().filter(|(_, (_, c))| *c >= 2).map(|(w, (i, _))| (i, w)).collect();
            want.sort_unstable();
            let want: Vec<&str> = want.into_iter().map(|(_, w)| w).collect();
            check!("s = 10⁵ pseudo-random letters with a 32-letter block planted 5 times and 100 A's, k = 32", find_repeated_dna_sequences(&s, 32), want);
        }
        """,
    ],
    wrong=dict(
        mask_with_shift="""
            use std::collections::HashMap;

            pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
                let b = s.as_bytes();
                if k > b.len() {
                    return Vec::new();
                }
                let mask = (1u64 << (2 * k)) - 1;
                let mut key = 0u64;
                let mut seen: HashMap<u64, (usize, u32)> = HashMap::new();
                for i in 0..b.len() {
                    let c = match b[i] {
                        b'A' => 0,
                        b'C' => 1,
                        b'G' => 2,
                        _ => 3,
                    };
                    key = ((key << 2) | c) & mask;
                    if i + 1 >= k {
                        seen.entry(key).or_insert((i + 1 - k, 0)).1 += 1;
                    }
                }
                let mut starts: Vec<usize> = seen.into_values().filter(|&(_, n)| n >= 2).map(|(start, _)| start).collect();
                starts.sort_unstable();
                starts.into_iter().map(|i| &s[i..i + k]).collect()
            }
        """,
        order_of_second_copy="""
            use std::collections::HashMap;

            pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
                let mut count: HashMap<&str, usize> = HashMap::new();
                let mut out = Vec::new();
                for i in 0..(s.len() + 1).saturating_sub(k) {
                    let w = &s[i..i + k];
                    let c = count.entry(w).or_insert(0);
                    *c += 1;
                    if *c == 2 {
                        out.push(w);
                    }
                }
                out
            }
        """,
        search_rest_for_each_window="""
            pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
                let mut out: Vec<&str> = Vec::new();
                for i in 0..(s.len() + 1).saturating_sub(k) {
                    let w = &s[i..i + k];
                    if !s[..i + k - 1].contains(w) && s[i + 1..].contains(w) {
                        out.push(w);
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Give each letter a 2-bit code and treat the window as a base-4 number. Sliding the window by one drops the first letter's term, shifts everything up one place, and adds the new letter: O(1) per step. Count keys in a `HashMap`."),
           ("rust", "Remember the first start of each key (`entry(key).or_insert((start, 0))`), then sort the repeated ones by start and slice `&s[i..i + k]`. For `k = 32`, `1u64 << 64` overflows (a panic in a debug build), so don't build a mask that way."),
           ("edge case", "A sequence seen three times is still reported once, and the order is by first appearance, not by when it first repeats.")],
    notes=("Each step updates the key in O(1), so the scan is O(n) plus hashing. With 4 letters, a window of k ≤ 32 letters is a base-4 number below 4^32 = 2^64: a perfect hash, no collisions to check. Hashing the `&str` windows directly also works at O(n·k). For longer windows or bigger alphabets you'd use a polynomial hash modulo 2^64 (`wrapping_mul`), and then equal hashes no longer prove equal windows: compare the slices on a hit. Thue–Morse strings make every base collide modulo 2^64.", "O(n)", "O(n)"),
    follow_up="Allow any k up to 10⁵. Which hash would you use, and how do you stay correct when two windows share a hash?",
    related=["S4", "D13"],
))

# ---------------------------------------------------------------- hard tries & strings (hard)

P.append(dict(
    slug="word-search-ii", title="Word search II", level="hard", stage="hard-tries-strings", tags=["trie", "backtracking", "grid", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Airbnb", "Uber"],
    teaches=["One depth-first search over the board, steered by a trie of all the words, instead of one search per word.",
             "Prune the trie as words are found: a branch with nothing left to find is cut, so later searches stop at once."],
    statement="""
        `board` is a grid of lowercase letters, one `&str` per row. A word is on the board if you can spell it by
        starting on any cell and stepping up, down, left or right, using each cell at most once in that word.

        Return the words from `words` that are on the board, sorted, each once. The answers are slices of `words`.
    """,
    examples=[("board = [\"oaan\", \"etae\", \"ihkr\", \"iflv\"], words = [\"oath\", \"pea\", \"eat\", \"rain\"]", "[\"eat\", \"oath\"]"),
              ("board = [\"ab\", \"cd\"], words = [\"abcb\"]", "[]")],
    constraints=["0 ≤ rows, columns ≤ 12, all rows the same length", "0 ≤ words.len() ≤ 3·10⁴", "1 ≤ words[i].len() ≤ 16, lowercase ASCII"],
    starter="""
        pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
            todo!()
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            /// The word ending here, until it's found.
            word: Option<usize>,
            /// Words not yet found at or below this node.
            left: usize,
        }

        /// Searches from cell (r, c), coming from `node`. Returns how many words were found, so callers can prune.
        fn dfs<'a>(grid: &mut [Vec<u8>], r: usize, c: usize, node: &mut Node, words: &[&'a str], out: &mut Vec<&'a str>) -> usize {
            let letter = grid[r][c];
            if letter == b'#' {
                return 0; // already on the current path
            }
            let i = (letter - b'a') as usize;
            let Some(child) = node.children[i].as_deref_mut() else {
                return 0;
            };
            let mut found = 0;
            if let Some(w) = child.word.take() {
                out.push(words[w]);
                found += 1;
            }
            grid[r][c] = b'#';
            let (rows, cols) = (grid.len(), grid[0].len());
            if r > 0 && child.left > found {
                found += dfs(grid, r - 1, c, child, words, out);
            }
            if r + 1 < rows && child.left > found {
                found += dfs(grid, r + 1, c, child, words, out);
            }
            if c > 0 && child.left > found {
                found += dfs(grid, r, c - 1, child, words, out);
            }
            if c + 1 < cols && child.left > found {
                found += dfs(grid, r, c + 1, child, words, out);
            }
            grid[r][c] = letter;
            child.left -= found;
            if child.left == 0 {
                node.children[i] = None; // nothing left to find down this branch
            }
            found
        }

        pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
            let mut unique: Vec<&'a str> = words.to_vec();
            unique.sort_unstable();
            unique.dedup();
            let mut root = Node::default();
            for (w, word) in unique.iter().enumerate() {
                let mut node = &mut root;
                node.left += 1;
                for b in word.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    node.left += 1;
                }
                node.word = Some(w);
            }
            let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
            let mut out = Vec::new();
            for r in 0..grid.len() {
                for c in 0..grid[r].len() {
                    if root.left > 0 {
                        let found = dfs(&mut grid, r, c, &mut root, &unique, &mut out);
                        root.left -= found;
                    }
                }
            }
            out.sort_unstable();
            out
        }
    """,
    visible=[
        T("leetcode_oath", "board = [\"oaan\", \"etae\", \"ihkr\", \"iflv\"], words = [\"oath\", \"pea\", \"eat\", \"rain\"]",
          'find_words(&["oaan", "etae", "ihkr", "iflv"], &["oath", "pea", "eat", "rain"])', 'vec!["eat", "oath"]'),
        T("leetcode_cell_used_twice", "board = [\"ab\", \"cd\"], words = [\"abcb\"] (spelling it would reuse the b)", 'find_words(&["ab", "cd"], &["abcb"])', "Vec::<&str>::new()"),
        T("no_words", "board = [\"a\"], words = []", 'find_words(&["a"], &[])', "Vec::<&str>::new()"),
        T("sorted_and_once", "board = [\"ab\"], words = [\"b\", \"a\", \"ab\", \"a\"]", 'find_words(&["ab"], &["b", "a", "ab", "a"])', 'vec!["a", "ab", "b"]'),
        T("path_turns_corners", "board = [\"ab\", \"dc\"], words = [\"abcd\", \"abdc\"] (no diagonal steps)", 'find_words(&["ab", "dc"], &["abcd", "abdc"])', 'vec!["abcd"]'),
        T("each_cell_once_per_word", "board = [\"aa\"], words = [\"a\", \"aa\", \"aaa\"]", 'find_words(&["aa"], &["a", "aa", "aaa"])', 'vec!["a", "aa"]'),
    ],
    hidden=[
        T("empty_board", "board = [], words = [\"a\"]", 'find_words(&[], &["a"])', "Vec::<&str>::new()"),
        T("single_cell", "board = [\"z\"], words = [\"z\", \"y\"]", 'find_words(&["z"], &["z", "y"])', 'vec!["z"]'),
        T("no_diagonals", "board = [\"ab\", \"cd\"], words = [\"ad\", \"bc\"]", 'find_words(&["ab", "cd"], &["ad", "bc"])', "Vec::<&str>::new()"),
        T("prefixes_and_words", "board = [\"abc\"], words = [\"a\", \"ab\", \"abc\", \"abcd\", \"cba\"]", 'find_words(&["abc"], &["a", "ab", "abc", "abcd", "cba"])', 'vec!["a", "ab", "abc", "cba"]'),
        T("snake_through_all", "board = [\"abc\", \"fed\", \"ghi\"], words = [\"abcdefghi\"]", 'find_words(&["abc", "fed", "ghi"], &["abcdefghi"])', 'vec!["abcdefghi"]'),
        T("leetcode_column", "board = [\"a\", \"a\"], words = [\"aaa\"]", 'find_words(&["a", "a"], &["aaa"])', "Vec::<&str>::new()"),
        T("found_by_many_paths", "board = [\"aa\", \"aa\"], words = [\"aa\"]", 'find_words(&["aa", "aa"], &["aa"])', 'vec!["aa"]'),
        T("one_row", "board = [\"hello\"], words = [\"hell\", \"olleh\", \"lol\"]", 'find_words(&["hello"], &["hell", "olleh", "lol"])', 'vec!["hell", "olleh"]'),
        T("answers_are_the_input_slices", "the answer points into words", "std::ptr::eq(got[0].as_ptr(), w.as_ptr())", "true",
          setup='let w = String::from("ba");\nlet got = find_words(&["ab"], &[&w]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            fn on_board(g: &mut Vec<Vec<u8>>, r: usize, c: usize, w: &[u8]) -> bool {
                if g[r][c] != w[0] {
                    return false;
                }
                if w.len() == 1 {
                    return true;
                }
                let keep = g[r][c];
                g[r][c] = b'#';
                let (rows, cols) = (g.len(), g[0].len());
                let ok = (r > 0 && on_board(g, r - 1, c, &w[1..]))
                    || (r + 1 < rows && on_board(g, r + 1, c, &w[1..]))
                    || (c > 0 && on_board(g, r, c - 1, &w[1..]))
                    || (c + 1 < cols && on_board(g, r, c + 1, &w[1..]));
                g[r][c] = keep;
                ok
            }
            let mut rng = anneal_prelude::Rng::new(1018);
            for _ in 0..300 {
                let (rows, cols) = (1 + rng.below(3), 1 + rng.below(3));
                let board: Vec<String> = (0..rows).map(|_| rng.string(cols, "ab")).collect();
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(6) {
                    let len = 1 + rng.below(5);
                    words.push(rng.string(len, "ab"));
                }
                let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
                let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut g: Vec<Vec<u8>> = board.iter().map(|s| s.as_bytes().to_vec()).collect();
                let mut want: Vec<&str> = w
                    .iter()
                    .copied()
                    .filter(|word| (0..rows).any(|r| (0..cols).any(|c| on_board(&mut g, r, c, word.as_bytes()))))
                    .collect();
                want.sort_unstable();
                want.dedup();
                check!(format!("board = {b:?}, words = {w:?}"), find_words(&b, &w), want);
            }
        }

        #[test]
        fn scale_30k_words_one_search() {
            // 12 × 12 a's with a b in the corner. 30000 words start with six a's and then leave the board,
            // so searching once per word repeats the same walk 30000 times.
            let mut board: Vec<String> = vec!["a".repeat(12); 12];
            board[11] = format!("{}b", "a".repeat(11));
            let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
            let mut words: Vec<String> = (0..30_000).map(|i| format!("aaaaaa{}", base10(i * 3, 5).replace('a', "k"))).collect();
            for w in ["b", "ba", "aab", "bab", "aaaaaaaaab"] {
                words.push(w.to_string());
            }
            let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("12 × 12 board of a's with a b in the corner; 30000 words 'a' × 6 + five letters from b..k, plus b, ba, aab, bab, aaaaaaaaab", find_words(&b, &w), vec!["aaaaaaaaab", "aab", "b", "ba"]);
        }

        #[test]
        fn scale_found_words_are_pruned() {
            // Every word is found on the first long path; without pruning, every cell starts a search through
            // all self-avoiding paths of 15 steps.
            let board = vec!["a".repeat(12); 12];
            let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
            let words: Vec<String> = (1..=16).map(|n| "a".repeat(n)).collect();
            let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("12 × 12 board of a's, words = 'a' × 1..=16", find_words(&b, &w), w.clone());
        }
        """ + BASE10,
    ],
    wrong=dict(
        search_per_word="""
            fn on_board(g: &mut [Vec<u8>], r: usize, c: usize, w: &[u8]) -> bool {
                if g[r][c] != w[0] {
                    return false;
                }
                if w.len() == 1 {
                    return true;
                }
                let keep = g[r][c];
                g[r][c] = b'#';
                let (rows, cols) = (g.len(), g[0].len());
                let ok = (r > 0 && on_board(g, r - 1, c, &w[1..]))
                    || (r + 1 < rows && on_board(g, r + 1, c, &w[1..]))
                    || (c > 0 && on_board(g, r, c - 1, &w[1..]))
                    || (c + 1 < cols && on_board(g, r, c + 1, &w[1..]));
                g[r][c] = keep;
                ok
            }

            pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
                let mut g: Vec<Vec<u8>> = board.iter().map(|s| s.as_bytes().to_vec()).collect();
                let rows = g.len();
                let mut out: Vec<&'a str> = Vec::new();
                for &word in words {
                    if (0..rows).any(|r| (0..g[r].len()).any(|c| on_board(&mut g, r, c, word.as_bytes()))) {
                        out.push(word);
                    }
                }
                out.sort_unstable();
                out.dedup();
                out
            }
        """,
        trie_without_pruning="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
                word: Option<usize>,
            }

            fn dfs<'a>(grid: &mut [Vec<u8>], r: usize, c: usize, node: &mut Node, words: &[&'a str], out: &mut Vec<&'a str>) {
                let letter = grid[r][c];
                if letter == b'#' {
                    return;
                }
                let Some(child) = node.children[(letter - b'a') as usize].as_deref_mut() else {
                    return;
                };
                if let Some(w) = child.word.take() {
                    out.push(words[w]);
                }
                grid[r][c] = b'#';
                let (rows, cols) = (grid.len(), grid[0].len());
                if r > 0 {
                    dfs(grid, r - 1, c, child, words, out);
                }
                if r + 1 < rows {
                    dfs(grid, r + 1, c, child, words, out);
                }
                if c > 0 {
                    dfs(grid, r, c - 1, child, words, out);
                }
                if c + 1 < cols {
                    dfs(grid, r, c + 1, child, words, out);
                }
                grid[r][c] = letter;
            }

            pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
                let mut root = Node::default();
                for (w, word) in words.iter().enumerate() {
                    let mut node = &mut root;
                    for b in word.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    }
                    node.word = Some(w);
                }
                let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
                let mut out = Vec::new();
                for r in 0..grid.len() {
                    for c in 0..grid[r].len() {
                        dfs(&mut grid, r, c, &mut root, words, &mut out);
                    }
                }
                out.sort_unstable();
                out.dedup();
                out
            }
        """,
        cells_reused="""
            #[derive(Default)]
            struct Node {
                children: [Option<Box<Node>>; 26],
                word: Option<usize>,
            }

            fn dfs<'a>(grid: &[Vec<u8>], r: usize, c: usize, node: &mut Node, depth: usize, words: &[&'a str], out: &mut Vec<&'a str>) {
                let Some(child) = node.children[(grid[r][c] - b'a') as usize].as_deref_mut() else {
                    return;
                };
                if let Some(w) = child.word.take() {
                    out.push(words[w]);
                }
                if depth == 16 {
                    return;
                }
                let (rows, cols) = (grid.len(), grid[0].len());
                if r > 0 {
                    dfs(grid, r - 1, c, child, depth + 1, words, out);
                }
                if r + 1 < rows {
                    dfs(grid, r + 1, c, child, depth + 1, words, out);
                }
                if c > 0 {
                    dfs(grid, r, c - 1, child, depth + 1, words, out);
                }
                if c + 1 < cols {
                    dfs(grid, r, c + 1, child, depth + 1, words, out);
                }
            }

            pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
                let mut root = Node::default();
                for (w, word) in words.iter().enumerate() {
                    let mut node = &mut root;
                    for b in word.bytes() {
                        node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    }
                    node.word = Some(w);
                }
                let grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
                let mut out = Vec::new();
                for r in 0..grid.len() {
                    for c in 0..grid[r].len() {
                        dfs(&grid, r, c, &mut root, 1, words, &mut out);
                    }
                }
                out.sort_unstable();
                out.dedup();
                out
            }
        """,
    ),
    hints=[("approach", "Put all the words in a trie, then start a depth-first search from every cell, moving down the trie as you move across the board. A cell's letter with no matching child ends that branch."),
           ("rust", "Mark the current path by writing `b'#'` into a `Vec<Vec<u8>>` copy of the board and restore the letter on the way back. Pass `&mut Node` down the recursion; `child.word.take()` reports each word once."),
           ("edge case", "Count, in each node, the words still unfound below it, and drop the child (`node.children[i] = None`) when that reaches 0. On a board full of one letter this is the difference between stopping after the first path and exploring every path.")],
    notes=("The trie lets one search check every word at once: a path is abandoned as soon as it isn't a prefix of any remaining word. Removing found words keeps the trie as small as what's left to find, which is what makes the all-same-letter boards fast. The worst case is still exponential in the word length (4 · 3^(L−1) paths from each cell), but the trie shares that work across all words.", "O(rows · cols · 4 · 3^(L−1)) worst case, L = longest word", "O(total letters in words)"),
    follow_up="If the board were huge and fixed and the words arrived one query at a time, what would you precompute instead?",
    related=["D11", "D9"],
))

AUTOCOMPLETE_HELPER = """
fn typed(sys: &mut AutocompleteSystem, keys: &str) -> Vec<Vec<String>> {
    keys.chars().map(|c| sys.input(c)).collect()
}
"""

AUTOCOMPLETE_LC = 'let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);'

P.append(dict(
    slug="autocomplete-system", title="Autocomplete system with hot counts", level="hard", stage="hard-tries-strings", tags=["trie", "design", "arena", "autocomplete"],
    companies=["Amazon", "Google", "Microsoft", "Uber"],
    teaches=["A cursor that lives between calls can't be a `&Node` inside the struct; keep the nodes in a `Vec` and the cursor as an index.",
             "Cache the three hottest sentences in every node and update them along one path when a count rises."],
    statement="""
        A search box suggests past sentences while the user types. `new(sentences, times)` loads each sentence with how
        many times it was typed before. Then `input(c)` is called once per keystroke:

        - for a letter or a space, return the three **hottest** past sentences that start with everything typed since the
          last `'#'`: highest count first, ties in ASCII order (a space sorts before letters). Fewer if fewer match;
        - for `'#'`, the sentence typed so far is finished: add 1 to its count (it may be new), start a fresh sentence,
          and return an empty list.

        Sentences are lowercase letters and spaces.
    """,
    examples=[("sentences = [\"i love you\", \"island\", \"iroman\", \"i love leetcode\"], times = [5, 3, 2, 2]; input 'i', ' ', 'a', '#'",
               "[\"i love you\", \"island\", \"i love leetcode\"], [\"i love you\", \"i love leetcode\"], [], []")],
    constraints=["0 ≤ sentences.len() ≤ 2·10⁴, 1 ≤ sentence length ≤ 100", "times[i] ≤ u32::MAX; counts can grow past it", "up to 10⁴ calls to input"],
    starter="""
        pub struct AutocompleteSystem {
            // your fields here
        }

        impl AutocompleteSystem {
            pub fn new(sentences: &[&str], times: &[u32]) -> Self {
                todo!()
            }

            pub fn input(&mut self, c: char) -> Vec<String> {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::HashMap;

        /// Child slot: a..z, then the space.
        fn slot(c: u8) -> usize {
            if c == b' ' { 26 } else { (c - b'a') as usize }
        }

        #[derive(Default)]
        struct Node {
            /// Indexes into `nodes`; the root (0) is never a child, so 0 means "none".
            children: [u32; 27],
            /// Up to three sentence ids, hottest first.
            top: Vec<u32>,
        }

        pub struct AutocompleteSystem {
            nodes: Vec<Node>,
            sentences: Vec<String>,
            counts: Vec<u64>,
            ids: HashMap<String, u32>,
            typed: String,
            /// The node for `typed`, or `None` once it has left the trie.
            cursor: Option<usize>,
        }

        impl AutocompleteSystem {
            pub fn new(sentences: &[&str], times: &[u32]) -> Self {
                let mut sys = AutocompleteSystem {
                    nodes: vec![Node::default()],
                    sentences: Vec::new(),
                    counts: Vec::new(),
                    ids: HashMap::new(),
                    typed: String::new(),
                    cursor: Some(0),
                };
                for (s, &t) in sentences.iter().zip(times) {
                    sys.add(s, u64::from(t));
                }
                sys
            }

            /// Adds `times` to `sentence`'s count and refreshes the top three of every node on its path.
            /// Only this sentence's count changed, so it's the only one that can move in those lists.
            fn add(&mut self, sentence: &str, times: u64) {
                let id = match self.ids.get(sentence) {
                    Some(&id) => id,
                    None => {
                        let id = self.sentences.len() as u32;
                        self.ids.insert(sentence.to_string(), id);
                        self.sentences.push(sentence.to_string());
                        self.counts.push(0);
                        id
                    }
                };
                self.counts[id as usize] += times;
                // Borrow the fields separately: `nodes` mutably, the others for the ordering.
                let Self { nodes, sentences, counts, .. } = self;
                let hotter = |a: &u32, b: &u32| {
                    let (a, b) = (*a as usize, *b as usize);
                    counts[b].cmp(&counts[a]).then_with(|| sentences[a].cmp(&sentences[b]))
                };
                let mut at = 0;
                for b in sentence.bytes() {
                    let next = nodes[at].children[slot(b)] as usize;
                    at = if next != 0 {
                        next
                    } else {
                        nodes.push(Node::default());
                        let n = nodes.len() - 1;
                        nodes[at].children[slot(b)] = n as u32;
                        n
                    };
                    let top = &mut nodes[at].top;
                    if !top.contains(&id) {
                        top.push(id);
                    }
                    top.sort_by(hotter);
                    top.truncate(3);
                }
            }

            pub fn input(&mut self, c: char) -> Vec<String> {
                if c == '#' {
                    let typed = std::mem::take(&mut self.typed);
                    self.add(&typed, 1);
                    self.cursor = Some(0);
                    return Vec::new();
                }
                self.typed.push(c);
                self.cursor = self.cursor.map(|at| self.nodes[at].children[slot(c as u8)] as usize).filter(|&n| n != 0);
                match self.cursor {
                    Some(at) => self.nodes[at].top.iter().map(|&id| self.sentences[id as usize].clone()).collect(),
                    None => Vec::new(),
                }
            }
        }
    """,
    visible=[
        AUTOCOMPLETE_HELPER,
        T("leetcode_type_i", "sentences = [\"i love you\", \"island\", \"iroman\", \"i love leetcode\"], times = [5, 3, 2, 2]; type \"i\"",
          'typed(&mut sys, "i")', 'vec![vec!["i love you", "island", "i love leetcode"]]', setup=AUTOCOMPLETE_LC),
        T("leetcode_type_i_space", "LeetCode's system; type \"i\", \" \"",
          'typed(&mut sys, "i ")', 'vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"]]', setup=AUTOCOMPLETE_LC),
        T("leetcode_type_i_space_a", "LeetCode's system; type \"i\", \" \", \"a\" (nothing starts with \"i a\")",
          'typed(&mut sys, "i a")', 'vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"], vec![]]', setup=AUTOCOMPLETE_LC),
        T("leetcode_type_i_space_a_hash", "LeetCode's system; type \"i\", \" \", \"a\", \"#\" ('#' returns nothing)",
          'typed(&mut sys, "i a#")', 'vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"], vec![], vec![]]', setup=AUTOCOMPLETE_LC),
        T("hash_saves_the_sentence", "LeetCode's system; type \"i a#\", then \"i \" (\"i a\" now has count 1)",
          'typed(&mut sys, "i ")', 'vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode", "i a"]]',
          setup=AUTOCOMPLETE_LC + '\ntyped(&mut sys, "i a#");'),
        T("ties_in_ascii_order", "sentences = [\"ab\", \"a b\", \"aa\"], times = [1, 1, 1]; type \"a\" (space sorts first)",
          'typed(&mut sys, "a")', 'vec![vec!["a b", "aa", "ab"]]', setup='let mut sys = AutocompleteSystem::new(&["ab", "a b", "aa"], &[1, 1, 1]);'),
        T("typing_makes_a_sentence_hotter", "sentences = [\"cat\", \"car\", \"cow\", \"cub\"], times = [1, 1, 1, 1]; type \"cub#\", then \"c\"",
          'typed(&mut sys, "c")', 'vec![vec!["cub", "car", "cat"]]',
          setup='let mut sys = AutocompleteSystem::new(&["cat", "car", "cow", "cub"], &[1, 1, 1, 1]);\ntyped(&mut sys, "cub#");'),
    ],
    hidden=[
        AUTOCOMPLETE_HELPER,
        T("no_sentences", "sentences = []; type \"ab#a\"", 'typed(&mut sys, "ab#a")', 'vec![vec![], vec![], vec![], vec!["ab"]]',
          setup='let mut sys = AutocompleteSystem::new(&[], &[]);'),
        T("hash_first", "LeetCode's system; type \"#i\"", 'typed(&mut sys, "#i")', 'vec![vec![], vec!["i love you", "island", "i love leetcode"]]', setup=AUTOCOMPLETE_LC),
        T("miss_then_hash_stores_everything_typed", "LeetCode's system; type \"iz#\", then \"iz\"", 'typed(&mut sys, "iz")', 'vec![vec!["i love you", "island", "i love leetcode"], vec!["iz"]]',
          setup=AUTOCOMPLETE_LC + '\ntyped(&mut sys, "iz#");'),
        T("overtakes_the_leader", "LeetCode's system; type \"island#\" three times, then \"i\"", 'typed(&mut sys, "i")', 'vec![vec!["island", "i love you", "i love leetcode"]]',
          setup=AUTOCOMPLETE_LC + '\nfor _ in 0..3 {\n    typed(&mut sys, "island#");\n}'),
        T("counts_past_u32", "sentences = [\"ab\", \"aa\"], times = [u32::MAX, u32::MAX]; type \"ab#\", then \"a\"", 'typed(&mut sys, "a")', 'vec![vec!["ab", "aa"]]',
          setup='let mut sys = AutocompleteSystem::new(&["ab", "aa"], &[u32::MAX, u32::MAX]);\ntyped(&mut sys, "ab#");'),
        T("sentence_is_prefix_of_another", "sentences = [\"i\", \"i love you\"], times = [1, 1]; type \"i \"", 'typed(&mut sys, "i ")', 'vec![vec!["i", "i love you"], vec!["i love you"]]',
          setup='let mut sys = AutocompleteSystem::new(&["i", "i love you"], &[1, 1]);'),
        T("only_three", "sentences = [\"d\", \"c\", \"b\", \"a\"], each with 1 prefixed \"x\"; type \"x\"", 'typed(&mut sys, "x")', 'vec![vec!["xa", "xb", "xc"]]',
          setup='let mut sys = AutocompleteSystem::new(&["xd", "xc", "xb", "xa"], &[1, 1, 1, 1]);'),
        T("stored_sentences_are_suggested", "sentences = [\"b\"], times = [1]; type \"a#\" twice, then \"b#a\"", 'typed(&mut sys, "b#a")', 'vec![vec!["b"], vec![], vec!["a"]]',
          setup='let mut sys = AutocompleteSystem::new(&["b"], &[1]);\ntyped(&mut sys, "a#a#");'),
        T("same_sentence_listed_twice", "sentences = [\"ab\", \"ac\", \"ab\"], times = [1, 3, 3]; type \"a\" (\"ab\" totals 4)", 'typed(&mut sys, "a")', 'vec![vec!["ab", "ac"]]',
          setup='let mut sys = AutocompleteSystem::new(&["ab", "ac", "ab"], &[1, 3, 3]);'),
        """
        #[test]
        fn random_vs_model() {
            use std::collections::HashMap;
            let mut rng = anneal_prelude::Rng::new(1019);
            for _ in 0..200 {
                let mut initial: Vec<String> = Vec::new();
                let mut times: Vec<u32> = Vec::new();
                for _ in 0..rng.below(6) {
                    let len = 1 + rng.below(3);
                    let s = rng.string(len, "ab ");
                    if !initial.contains(&s) {
                        initial.push(s);
                        times.push(1 + rng.below(3) as u32);
                    }
                }
                let refs: Vec<&str> = initial.iter().map(|s| s.as_str()).collect();
                let mut sys = AutocompleteSystem::new(&refs, &times);
                let mut model: HashMap<String, u64> = initial.iter().cloned().zip(times.iter().map(|&t| u64::from(t))).collect();
                let mut typed_so_far = String::new();
                let mut log = format!("sentences = {refs:?}, times = {times:?}; type ");
                for _ in 0..20 {
                    let c = *rng.pick(&['a', 'b', ' ', '#', '#']);
                    log.push(c);
                    let want: Vec<String> = if c == '#' {
                        *model.entry(std::mem::take(&mut typed_so_far)).or_insert(0) += 1;
                        Vec::new()
                    } else {
                        typed_so_far.push(c);
                        let mut m: Vec<(&String, u64)> = model.iter().filter(|(s, _)| s.starts_with(typed_so_far.as_str())).map(|(s, &n)| (s, n)).collect();
                        m.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
                        m.into_iter().take(3).map(|(s, _)| s.clone()).collect()
                    };
                    check!(log.clone(), sys.input(c), want);
                }
            }
        }

        #[test]
        fn scale_20k_sentences_shared_prefix() {
            // Every sentence starts with 60 a's, so every keystroke of the prefix matches all 20000 of them.
            let prefix = "a".repeat(60);
            let sentences: Vec<String> = (0..20_000).map(|i| format!("{prefix} {}", base10(i, 5))).collect();
            let times: Vec<u32> = (0..20_000u32).map(|i| i * 7919 % 20_000 + 1).collect();
            let refs: Vec<&str> = sentences.iter().map(|s| s.as_str()).collect();
            let mut sys = AutocompleteSystem::new(&refs, &times);
            let mut by_heat: Vec<usize> = (0..20_000).collect();
            by_heat.sort_by_key(|&i| std::cmp::Reverse(times[i]));
            let want: Vec<String> = by_heat[..3].iter().map(|&i| sentences[i].clone()).collect();
            let mut rows = 0;
            let mut all_match = true;
            for _ in 0..160 {
                for c in prefix.chars() {
                    rows += 1;
                    all_match &= sys.input(c) == want;
                }
                sys.input('#');
            }
            check!("20000 sentences 'a' × 60 + ' ' + five letters, distinct counts; type 'a' × 60 then '#', 160 times", (rows, all_match), (9600, true));
        }
        """ + BASE10,
    ],
    wrong=dict(
        scan_every_sentence="""
            use std::collections::HashMap;

            pub struct AutocompleteSystem {
                counts: HashMap<String, u64>,
                typed: String,
            }

            impl AutocompleteSystem {
                pub fn new(sentences: &[&str], times: &[u32]) -> Self {
                    let mut counts: HashMap<String, u64> = HashMap::new();
                    for (s, &t) in sentences.iter().zip(times) {
                        *counts.entry(s.to_string()).or_insert(0) += u64::from(t);
                    }
                    AutocompleteSystem { counts, typed: String::new() }
                }

                pub fn input(&mut self, c: char) -> Vec<String> {
                    if c == '#' {
                        *self.counts.entry(std::mem::take(&mut self.typed)).or_insert(0) += 1;
                        return Vec::new();
                    }
                    self.typed.push(c);
                    let mut m: Vec<(&String, u64)> = self.counts.iter().filter(|(s, _)| s.starts_with(self.typed.as_str())).map(|(s, &n)| (s, n)).collect();
                    m.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
                    m.into_iter().take(3).map(|(s, _)| s.clone()).collect()
                }
            }
        """,
        hash_only_adds_new="""
            use std::collections::HashMap;

            fn slot(c: u8) -> usize {
                if c == b' ' { 26 } else { (c - b'a') as usize }
            }

            #[derive(Default)]
            struct Node {
                children: [u32; 27],
                top: Vec<u32>,
            }

            pub struct AutocompleteSystem {
                nodes: Vec<Node>,
                sentences: Vec<String>,
                counts: Vec<u64>,
                ids: HashMap<String, u32>,
                typed: String,
                cursor: Option<usize>,
            }

            impl AutocompleteSystem {
                pub fn new(sentences: &[&str], times: &[u32]) -> Self {
                    let mut sys = AutocompleteSystem {
                        nodes: vec![Node::default()],
                        sentences: Vec::new(),
                        counts: Vec::new(),
                        ids: HashMap::new(),
                        typed: String::new(),
                        cursor: Some(0),
                    };
                    for (s, &t) in sentences.iter().zip(times) {
                        sys.add(s, u64::from(t));
                    }
                    sys
                }

                fn add(&mut self, sentence: &str, times: u64) {
                    if let Some(&id) = self.ids.get(sentence) {
                        // Known sentence: bump the count, but the cached lists keep their old order.
                        self.counts[id as usize] += times;
                        return;
                    }
                    let id = self.sentences.len() as u32;
                    self.ids.insert(sentence.to_string(), id);
                    self.sentences.push(sentence.to_string());
                    self.counts.push(times);
                    let Self { nodes, sentences, counts, .. } = self;
                    let hotter = |a: &u32, b: &u32| {
                        let (a, b) = (*a as usize, *b as usize);
                        counts[b].cmp(&counts[a]).then_with(|| sentences[a].cmp(&sentences[b]))
                    };
                    let mut at = 0;
                    for b in sentence.bytes() {
                        let next = nodes[at].children[slot(b)] as usize;
                        at = if next != 0 {
                            next
                        } else {
                            nodes.push(Node::default());
                            let n = nodes.len() - 1;
                            nodes[at].children[slot(b)] = n as u32;
                            n
                        };
                        let top = &mut nodes[at].top;
                        top.push(id);
                        top.sort_by(hotter);
                        top.truncate(3);
                    }
                }

                pub fn input(&mut self, c: char) -> Vec<String> {
                    if c == '#' {
                        let typed = std::mem::take(&mut self.typed);
                        self.add(&typed, 1);
                        self.cursor = Some(0);
                        return Vec::new();
                    }
                    self.typed.push(c);
                    self.cursor = self.cursor.map(|at| self.nodes[at].children[slot(c as u8)] as usize).filter(|&n| n != 0);
                    match self.cursor {
                        Some(at) => self.nodes[at].top.iter().map(|&id| self.sentences[id as usize].clone()).collect(),
                        None => Vec::new(),
                    }
                }
            }
        """,
        collect_subtree_each_keystroke="""
            use std::collections::BTreeMap;

            #[derive(Default)]
            struct Node {
                children: BTreeMap<char, Node>,
                count: u64,
            }

            fn collect(node: &Node, path: &mut String, out: &mut Vec<(u64, String)>) {
                if node.count > 0 {
                    out.push((node.count, path.clone()));
                }
                for (&c, child) in &node.children {
                    path.push(c);
                    collect(child, path, out);
                    path.pop();
                }
            }

            pub struct AutocompleteSystem {
                root: Node,
                typed: String,
            }

            impl AutocompleteSystem {
                pub fn new(sentences: &[&str], times: &[u32]) -> Self {
                    let mut sys = AutocompleteSystem { root: Node::default(), typed: String::new() };
                    for (s, &t) in sentences.iter().zip(times) {
                        sys.add(s, u64::from(t));
                    }
                    sys
                }

                fn add(&mut self, s: &str, times: u64) {
                    let mut node = &mut self.root;
                    for c in s.chars() {
                        node = node.children.entry(c).or_default();
                    }
                    node.count += times;
                }

                pub fn input(&mut self, c: char) -> Vec<String> {
                    if c == '#' {
                        let typed = std::mem::take(&mut self.typed);
                        self.add(&typed, 1);
                        return Vec::new();
                    }
                    self.typed.push(c);
                    let mut node = &self.root;
                    for ch in self.typed.chars() {
                        match node.children.get(&ch) {
                            Some(n) => node = n,
                            None => return Vec::new(),
                        }
                    }
                    let mut all = Vec::new();
                    let mut path = self.typed.clone();
                    collect(node, &mut path, &mut all);
                    all.sort_by(|a, b| b.0.cmp(&a.0).then_with(|| a.1.cmp(&b.1)));
                    all.into_iter().take(3).map(|(_, s)| s).collect()
                }
            }
        """,
    ),
    hints=[("approach", "Store the sentences in a trie. In every node, keep the ids of the three hottest sentences below it. A keystroke moves a cursor one node down and returns that node's list; `'#'` raises one sentence's count and refreshes the lists on its path only."),
           ("rust", "The cursor must survive between `input` calls, and a struct can't hold a reference into its own trie. Keep nodes in a `Vec<Node>`, children as `u32` indexes, and the cursor as `Option<usize>`. To sort a node's list by counts while `nodes` is borrowed mutably, destructure: `let Self { nodes, counts, sentences, .. } = self;`."),
           ("edge case", "When a known sentence is typed again, its count rises and it can climb into lists it wasn't in; the cached lists must be updated for old sentences too, not only new ones. Counts start at `u32::MAX` and still grow, so keep them in `u64`.")],
    notes=("Counts only ever rise, and only for the sentence just finished, so a node's top three can change only by that sentence moving up: insert or reorder it, sort at most four entries, truncate. That makes a keystroke O(1) (plus copying three strings) and `'#'` O(L). Collecting and sorting the whole subtree on every keystroke is the textbook answer and costs O(matches · log matches) per key, which the shared-prefix test makes too slow. The arena (`Vec<Node>` with `u32` links) is also what lets the cursor be plain data.", "input: O(1) per letter, O(L) for '#'; new: O(total length)", "O(total length × 27)"),
    follow_up="How would you make the suggestions favour recent sentences over old ones (decay the counts over time)?",
    related=["D14", "S7", "L3"],
))

P.append(dict(
    slug="max-xor-bit-trie", title="Maximum XOR of two numbers (bit trie)", level="hard", stage="hard-tries-strings", tags=["trie", "bits", "arena"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["A binary trie over the bits, highest first, answers \"which stored number differs most from x\" in 32 steps.",
             "Greedy works bit by bit: one higher bit outweighs all the lower bits together."],
    statement="""
        Return the largest value of `nums[i] ^ nums[j]` over all pairs `i < j`, or 0 when there are fewer than two numbers.

        Numbers use the full `u32` range, including the top bit.
    """,
    examples=[("nums = [3, 10, 5, 25, 2, 8]", "28 (5 ^ 25)"), ("nums = [14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]", "127")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "0 ≤ nums[i] ≤ u32::MAX"],
    starter="""
        pub fn find_maximum_xor(nums: &[u32]) -> u32 {
            todo!()
        }
    """,
    solution="""
        pub fn find_maximum_xor(nums: &[u32]) -> u32 {
            // A binary trie over bits 31..=0, as an arena: node = [child for bit 0, child for bit 1], 0 = none.
            let mut trie: Vec<[u32; 2]> = vec![[0, 0]];
            let mut best = 0;
            for (i, &x) in nums.iter().enumerate() {
                if i > 0 {
                    // Walk the stored numbers, taking the opposite bit whenever one exists.
                    let (mut at, mut xor) = (0, 0u32);
                    for bit in (0..32).rev() {
                        let b = (x >> bit & 1) as usize;
                        let other = trie[at][b ^ 1];
                        if other != 0 {
                            xor |= 1 << bit;
                            at = other as usize;
                        } else {
                            at = trie[at][b] as usize;
                        }
                    }
                    best = best.max(xor);
                }
                let mut at = 0;
                for bit in (0..32).rev() {
                    let b = (x >> bit & 1) as usize;
                    if trie[at][b] == 0 {
                        trie.push([0, 0]);
                        trie[at][b] = (trie.len() - 1) as u32;
                    }
                    at = trie[at][b] as usize;
                }
            }
            best
        }
    """,
    visible=[
        T("leetcode_28", "nums = [3, 10, 5, 25, 2, 8]", "find_maximum_xor(&[3, 10, 5, 25, 2, 8])", "28"),
        T("leetcode_127", "nums = [14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]", "find_maximum_xor(&[14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70])", "127"),
        T("empty", "nums = []", "find_maximum_xor(&[])", "0"),
        T("single", "nums = [7]", "find_maximum_xor(&[7])", "0"),
        T("best_pair_skips_the_max", "nums = [6, 5, 3] (5 ^ 3 = 6 beats anything with 6)", "find_maximum_xor(&[6, 5, 3])", "6"),
        T("top_bit_counts", "nums = [2147483648, 1] (2³¹ and 1)", "find_maximum_xor(&[1 << 31, 1])", "(1 << 31) | 1"),
    ],
    hidden=[
        T("zero_and_max", "nums = [0, u32::MAX]", "find_maximum_xor(&[0, u32::MAX])", "u32::MAX"),
        T("adjacent_maxes", "nums = [u32::MAX, u32::MAX - 1]", "find_maximum_xor(&[u32::MAX, u32::MAX - 1])", "1"),
        T("powers_of_two", "nums = [1, 2, 4, 8]", "find_maximum_xor(&[1, 2, 4, 8])", "12"),
        T("all_zero", "nums = [0, 0, 0]", "find_maximum_xor(&[0, 0, 0])", "0"),
        T("duplicates", "nums = [5, 5]", "find_maximum_xor(&[5, 5])", "0"),
        T("both_sides_of_the_top_bit", "nums = [2³¹, 2³¹ - 1]", "find_maximum_xor(&[1 << 31, (1 << 31) - 1])", "u32::MAX"),
        T("large_values", "nums = [3000000000, 1500000000, 123]", "find_maximum_xor(&[3_000_000_000, 1_500_000_000, 123])", "3954733312"),
        T("two_numbers", "nums = [10, 5]", "find_maximum_xor(&[10, 5])", "15"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1020);
            for _ in 0..400 {
                let n = rng.below(10);
                let nums: Vec<u32> = if rng.bool() { rng.vec(n, 0, 15) } else { rng.vec(n, 0, u32::MAX as i64) };
                let mut want = 0;
                for i in 0..nums.len() {
                    for j in i + 1..nums.len() {
                        want = want.max(nums[i] ^ nums[j]);
                    }
                }
                check!(format!("nums = {nums:?}"), find_maximum_xor(&nums), want);
            }
        }

        #[test]
        fn scale_131k() {
            // 0..2¹⁷ in shuffled order, then 2³¹: the best pair is 2³¹ with 2¹⁷ − 1, found only at the very end.
            let mut nums: Vec<u32> = (0..1u32 << 17).map(|i| i.wrapping_mul(40_503) % (1 << 17)).collect();
            nums.push(1 << 31);
            check!("nums = 0..131072 shuffled, then 2147483648", find_maximum_xor(&nums), (1 << 31) | ((1 << 17) - 1));
        }
        """,
    ],
    wrong=dict(
        every_pair="""
            pub fn find_maximum_xor(nums: &[u32]) -> u32 {
                let mut best = 0;
                for i in 0..nums.len() {
                    for j in i + 1..nums.len() {
                        best = best.max(nums[i] ^ nums[j]);
                    }
                }
                best
            }
        """,
        thirty_one_bits="""
            pub fn find_maximum_xor(nums: &[u32]) -> u32 {
                let mut trie: Vec<[u32; 2]> = vec![[0, 0]];
                let mut best = 0;
                for (i, &x) in nums.iter().enumerate() {
                    if i > 0 {
                        let (mut at, mut xor) = (0, 0u32);
                        for bit in (0..31).rev() {
                            let b = (x >> bit & 1) as usize;
                            let other = trie[at][b ^ 1];
                            if other != 0 {
                                xor |= 1 << bit;
                                at = other as usize;
                            } else {
                                at = trie[at][b] as usize;
                            }
                        }
                        best = best.max(xor);
                    }
                    let mut at = 0;
                    for bit in (0..31).rev() {
                        let b = (x >> bit & 1) as usize;
                        if trie[at][b] == 0 {
                            trie.push([0, 0]);
                            trie[at][b] = (trie.len() - 1) as u32;
                        }
                        at = trie[at][b] as usize;
                    }
                }
                best
            }
        """,
        xor_with_the_max="""
            pub fn find_maximum_xor(nums: &[u32]) -> u32 {
                let Some(&max) = nums.iter().max() else {
                    return 0;
                };
                nums.iter().map(|&x| x ^ max).max().unwrap_or(0)
            }
        """,
    ),
    hints=[("approach", "Insert the numbers into a trie keyed by their bits, highest bit first. For each number, walk the trie choosing the opposite bit whenever that child exists: each choice sets that bit of the XOR, and a higher bit is worth more than all lower bits combined."),
           ("rust", "A `Vec<[u32; 2]>` arena is a compact trie: node `i` has children `trie[i][0]` and `trie[i][1]`, with 0 meaning none (the root is never anyone's child). `x >> bit & 1` reads a bit."),
           ("edge case", "LeetCode's inputs stop below 2³¹, so solutions often walk 31 bits. With `u32` input the top bit matters: walk bits 31 down to 0.")],
    notes=("Each number costs 32 steps to insert and 32 to query, so the whole thing is O(32 · n). Querying before inserting means each pair is considered once. The other O(32 · n) answer builds the result bit by bit, checking with a `HashSet` of prefixes whether some pair can reach the candidate. Trying every pair is O(n²).", "O(32 · n)", "O(32 · n) trie nodes"),
    follow_up="Answer queries (x, limit): the maximum x ^ nums[j] over nums[j] ≤ limit. How does sorting the queries help?",
    related=["D13"],
))

STREAM_HELPER = """
fn feed(sc: &mut StreamChecker, letters: &str) -> Vec<bool> {
    letters.chars().map(|c| sc.query(c)).collect()
}
"""

P.append(dict(
    slug="stream-of-characters", title="Stream of characters", level="hard", stage="hard-tries-strings", tags=["trie", "streaming", "VecDeque"],
    companies=["Amazon", "Google"],
    teaches=["Insert the words reversed; each new letter then walks the trie backwards through the most recent letters.",
             "Only the last `longest word` letters can matter, so the stream buffer is bounded."],
    statement="""
        `StreamChecker::new(words)` stores a list of lowercase words. Letters then arrive one at a time through `query(letter)`,
        which returns `true` if some word is a suffix of the stream so far, that is, the stream ends with that word.
    """,
    examples=[("words = [\"cd\", \"f\", \"kl\"]; letters a, b, c, …, l", "false ×3, true (\"cd\"), false, true (\"f\"), false ×5, true (\"kl\")")],
    constraints=["0 ≤ words.len() ≤ 2·10⁴, 1 ≤ words[i].len() ≤ 200, lowercase ASCII", "up to 10⁵ queries"],
    starter="""
        pub struct StreamChecker {
            // your fields here
        }

        impl StreamChecker {
            pub fn new(words: &[&str]) -> Self {
                todo!()
            }

            pub fn query(&mut self, letter: char) -> bool {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub struct StreamChecker {
            /// Trie of the reversed words, as an arena: (children, a word ends here). Child 0 means none.
            nodes: Vec<([u32; 26], bool)>,
            /// The last `longest` letters of the stream, oldest first.
            recent: VecDeque<u8>,
            longest: usize,
        }

        impl StreamChecker {
            pub fn new(words: &[&str]) -> Self {
                let mut nodes = vec![([0u32; 26], false)];
                for w in words {
                    let mut at = 0;
                    for b in w.bytes().rev() {
                        let i = (b - b'a') as usize;
                        if nodes[at].0[i] == 0 {
                            nodes.push(([0; 26], false));
                            nodes[at].0[i] = (nodes.len() - 1) as u32;
                        }
                        at = nodes[at].0[i] as usize;
                    }
                    nodes[at].1 = true;
                }
                let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
                StreamChecker { nodes, recent: VecDeque::with_capacity(longest + 1), longest }
            }

            pub fn query(&mut self, letter: char) -> bool {
                self.recent.push_back(letter as u8);
                if self.recent.len() > self.longest {
                    self.recent.pop_front();
                }
                // Newest letter first: this walks the reversed words.
                let mut at = 0;
                for &b in self.recent.iter().rev() {
                    at = self.nodes[at].0[(b - b'a') as usize] as usize;
                    if at == 0 {
                        return false;
                    }
                    if self.nodes[at].1 {
                        return true;
                    }
                }
                false
            }
        }
    """,
    visible=[
        STREAM_HELPER,
        T("leetcode_stream", "words = [\"cd\", \"f\", \"kl\"]; letters \"abcdefghijkl\"", 'feed(&mut sc, "abcdefghijkl")',
          "vec![false, false, false, true, false, true, false, false, false, false, false, true]", setup='let mut sc = StreamChecker::new(&["cd", "f", "kl"]);'),
        T("first_letter", "words = [\"a\"]; letters \"a\"", 'feed(&mut sc, "a")', "vec![true]", setup='let mut sc = StreamChecker::new(&["a"]);'),
        T("suffix_not_prefix", "words = [\"ab\"]; letters \"ba\" (the stream must end with the word)", 'feed(&mut sc, "ba")', "vec![false, false]",
          setup='let mut sc = StreamChecker::new(&["ab"]);'),
        T("overlapping_matches", "words = [\"aaa\"]; letters \"aaaa\"", 'feed(&mut sc, "aaaa")', "vec![false, false, true, true]", setup='let mut sc = StreamChecker::new(&["aaa"]);'),
        T("word_inside_a_longer_word", "words = [\"abc\", \"bc\"]; letters \"abc\"", 'feed(&mut sc, "abc")', "vec![false, false, true]",
          setup='let mut sc = StreamChecker::new(&["abc", "bc"]);'),
        T("match_again_later", "words = [\"ab\"]; letters \"abxab\"", 'feed(&mut sc, "abxab")', "vec![false, true, false, false, true]", setup='let mut sc = StreamChecker::new(&["ab"]);'),
    ],
    hidden=[
        STREAM_HELPER,
        T("no_words", "words = []; letters \"abc\"", 'feed(&mut sc, "abc")', "vec![false; 3]", setup="let mut sc = StreamChecker::new(&[]);"),
        T("duplicate_words", "words = [\"z\", \"z\"]; letters \"zz\"", 'feed(&mut sc, "zz")', "vec![true, true]", setup='let mut sc = StreamChecker::new(&["z", "z"]);'),
        T("longest_word_needs_the_whole_window", "words = ['a' × 199 + \"b\", \"c\"]; letters 'a' × 200 + \"b\"", "got[200]", "true",
          setup='let w = format!("{}b", "a".repeat(199));\nlet mut sc = StreamChecker::new(&[&w, "c"]);\nlet got = feed(&mut sc, &format!("{}b", "a".repeat(200)));'),
        T("long_then_short", "words = [\"abcd\", \"d\"]; letters \"xd\"", 'feed(&mut sc, "xd")', "vec![false, true]", setup='let mut sc = StreamChecker::new(&["abcd", "d"]);'),
        T("broken_by_one_letter", "words = [\"abc\"]; letters \"abxbc\"", 'feed(&mut sc, "abxbc")', "vec![false; 5]", setup='let mut sc = StreamChecker::new(&["abc"]);'),
        T("every_letter_a_word", "words = a..z as one-letter words; letters \"qz\"", 'feed(&mut sc, "qz")', "vec![true, true]",
          setup='let letters: Vec<String> = (b\'a\'..=b\'z\').map(|b| (b as char).to_string()).collect();\nlet refs: Vec<&str> = letters.iter().map(|s| s.as_str()).collect();\nlet mut sc = StreamChecker::new(&refs);'),
        T("shorter_word_matches_first", "words = [\"ba\", \"a\"]; letters \"ba\"", 'feed(&mut sc, "ba")', "vec![false, true]", setup='let mut sc = StreamChecker::new(&["ba", "a"]);'),
        T("same_letter_word_long", "words = ['q' × 5]; letters 'q' × 7", 'feed(&mut sc, &"q".repeat(7))', "vec![false, false, false, false, true, true, true]",
          setup='let mut sc = StreamChecker::new(&[&"q".repeat(5)]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1021);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(4) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "ab"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut sc = StreamChecker::new(&refs);
                let len = rng.below(16);
                let letters = rng.string(len, "abc");
                let mut stream = String::new();
                for c in letters.chars() {
                    stream.push(c);
                    let want = refs.iter().any(|w| stream.ends_with(w));
                    check!(format!("words = {refs:?}; letters {stream:?}"), sc.query(c), want);
                }
            }
        }

        #[test]
        fn scale_20k_words_100k_letters() {
            use std::collections::HashSet;
            let words: Vec<String> = (0..20_000).map(|i| base10(i * 37, 6)).collect();
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let set: HashSet<&str> = refs.iter().copied().collect();
            let mut sc = StreamChecker::new(&refs);
            let mut x: u64 = 7;
            let letters: String = (0..100_000)
                .map(|_| {
                    x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                    (b'a' + ((x >> 33) % 10) as u8) as char
                })
                .collect();
            let mut got = 0;
            let mut want = 0;
            for (i, c) in letters.char_indices() {
                got += sc.query(c) as usize;
                want += (i >= 5 && set.contains(&letters[i - 5..=i])) as usize;
            }
            check!("20000 six-letter words over a..j; 100000 pseudo-random letters (count of true answers)", got, want);
        }
        """ + BASE10,
    ],
    wrong=dict(
        check_every_word="""
            pub struct StreamChecker {
                words: Vec<String>,
                stream: String,
            }

            impl StreamChecker {
                pub fn new(words: &[&str]) -> Self {
                    StreamChecker { words: words.iter().map(|w| w.to_string()).collect(), stream: String::new() }
                }

                pub fn query(&mut self, letter: char) -> bool {
                    self.stream.push(letter);
                    self.words.iter().any(|w| self.stream.ends_with(w.as_str()))
                }
            }
        """,
        forget_after_a_match="""
            use std::collections::VecDeque;

            pub struct StreamChecker {
                nodes: Vec<([u32; 26], bool)>,
                recent: VecDeque<u8>,
                longest: usize,
            }

            impl StreamChecker {
                pub fn new(words: &[&str]) -> Self {
                    let mut nodes = vec![([0u32; 26], false)];
                    for w in words {
                        let mut at = 0;
                        for b in w.bytes().rev() {
                            let i = (b - b'a') as usize;
                            if nodes[at].0[i] == 0 {
                                nodes.push(([0; 26], false));
                                nodes[at].0[i] = (nodes.len() - 1) as u32;
                            }
                            at = nodes[at].0[i] as usize;
                        }
                        nodes[at].1 = true;
                    }
                    let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
                    StreamChecker { nodes, recent: VecDeque::new(), longest }
                }

                pub fn query(&mut self, letter: char) -> bool {
                    self.recent.push_back(letter as u8);
                    if self.recent.len() > self.longest {
                        self.recent.pop_front();
                    }
                    let mut at = 0;
                    for &b in self.recent.iter().rev() {
                        at = self.nodes[at].0[(b - b'a') as usize] as usize;
                        if at == 0 {
                            return false;
                        }
                        if self.nodes[at].1 {
                            // A match "uses up" the letters.
                            self.recent.clear();
                            return true;
                        }
                    }
                    false
                }
            }
        """,
        window_one_short="""
            use std::collections::VecDeque;

            pub struct StreamChecker {
                nodes: Vec<([u32; 26], bool)>,
                recent: VecDeque<u8>,
                longest: usize,
            }

            impl StreamChecker {
                pub fn new(words: &[&str]) -> Self {
                    let mut nodes = vec![([0u32; 26], false)];
                    for w in words {
                        let mut at = 0;
                        for b in w.bytes().rev() {
                            let i = (b - b'a') as usize;
                            if nodes[at].0[i] == 0 {
                                nodes.push(([0; 26], false));
                                nodes[at].0[i] = (nodes.len() - 1) as u32;
                            }
                            at = nodes[at].0[i] as usize;
                        }
                        nodes[at].1 = true;
                    }
                    let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
                    StreamChecker { nodes, recent: VecDeque::new(), longest }
                }

                pub fn query(&mut self, letter: char) -> bool {
                    self.recent.push_back(letter as u8);
                    if self.recent.len() >= self.longest {
                        self.recent.pop_front();
                    }
                    let mut at = 0;
                    for &b in self.recent.iter().rev() {
                        at = self.nodes[at].0[(b - b'a') as usize] as usize;
                        if at == 0 {
                            return false;
                        }
                        if self.nodes[at].1 {
                            return true;
                        }
                    }
                    false
                }
            }
        """,
    ),
    hints=[("approach", "Build a trie of the words written backwards. After each letter, walk it from the newest letter back through older ones; reaching a word's end means the stream ends with that word."),
           ("rust", "Keep only the last `longest` letters in a `VecDeque<u8>` (`push_back`, then `pop_front` when it's too long) and walk `recent.iter().rev()`."),
           ("edge case", "Matches overlap: with the word `aaa`, the stream `aaaa` matches at the third and the fourth letter. Don't clear anything after a match.")],
    notes=("A query walks at most `longest` letters and usually stops after a few, when the reversed trie has no child for the next letter. Checking every word per query is O(words · L) each. The Aho–Corasick automaton makes each query O(1) amortized by precomputing failure links; the reversed trie is the simpler answer interviews expect.", "O(L) per query, L = longest word", "O(total letters in words × 26)"),
    follow_up="Aho–Corasick answers each query in O(1) amortized. What do its failure links store?",
    related=["S5"],
))

P.append(dict(
    slug="concatenated-words", title="Concatenated words", level="hard", stage="hard-tries-strings", tags=["trie", "DP", "word break"],
    companies=["Amazon", "Google", "Uber"],
    teaches=["Word break on every word: `ok[i]` says the first i letters split into dictionary words; a trie walk from each reachable i finds the next pieces.",
             "The word itself is in the dictionary, so forbid the one piece that spans the whole word."],
    statement="""
        A word is **concatenated** if it can be split into at least two pieces that are all words from `words`
        (the same word may be used more than once). Return every concatenated word in `words`, in input order,
        as slices of the input.

        Words are distinct lowercase ASCII. The list may contain `""`, which is never a piece and never an answer.
    """,
    examples=[("words = [\"cat\", \"cats\", \"catsdogcats\", \"dog\", \"dogcatsdog\", \"hippopotamuses\", \"rat\", \"ratcatdogcat\"]",
               "[\"catsdogcats\", \"dogcatsdog\", \"ratcatdogcat\"]"),
              ("words = [\"cat\", \"dog\", \"catdog\"]", "[\"catdog\"]")],
    constraints=["0 ≤ words.len() ≤ 10⁴", "0 ≤ words[i].len() ≤ 30", "total length ≤ 10⁵"],
    starter="""
        pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
            todo!()
        }
    """,
    solution="""
        #[derive(Default)]
        struct Node {
            children: [Option<Box<Node>>; 26],
            end: bool,
        }

        /// Word break with at least two pieces: `ok[i]` is true when w[..i] splits into dictionary words.
        fn is_concatenated(root: &Node, w: &[u8]) -> bool {
            let n = w.len();
            let mut ok = vec![false; n + 1];
            ok[0] = true;
            for i in 0..n {
                if !ok[i] {
                    continue;
                }
                let mut node = root;
                for j in i..n {
                    match node.children[(w[j] - b'a') as usize].as_deref() {
                        Some(child) => node = child,
                        None => break,
                    }
                    // A piece w[i..=j]; the one piece that is the whole word doesn't count.
                    if node.end && !(i == 0 && j + 1 == n) {
                        ok[j + 1] = true;
                    }
                }
            }
            ok[n]
        }

        pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
            let mut root = Node::default();
            for w in words.iter().filter(|w| !w.is_empty()) {
                let mut node = &mut root;
                for b in w.bytes() {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                }
                node.end = true;
            }
            words.iter().copied().filter(|w| !w.is_empty() && is_concatenated(&root, w.as_bytes())).collect()
        }
    """,
    visible=[
        T("leetcode_cats_and_dogs", "words = [\"cat\", \"cats\", \"catsdogcats\", \"dog\", \"dogcatsdog\", \"hippopotamuses\", \"rat\", \"ratcatdogcat\"]",
          'find_all_concatenated_words(&["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"])',
          'vec!["catsdogcats", "dogcatsdog", "ratcatdogcat"]'),
        T("leetcode_catdog", "words = [\"cat\", \"dog\", \"catdog\"]", 'find_all_concatenated_words(&["cat", "dog", "catdog"])', 'vec!["catdog"]'),
        T("empty", "words = []", "find_all_concatenated_words(&[])", "Vec::<&str>::new()"),
        T("one_word_is_not_enough", "words = [\"a\"] (a word alone is one piece)", 'find_all_concatenated_words(&["a"])', "Vec::<&str>::new()"),
        T("same_piece_twice", "words = [\"a\", \"aaa\"]", 'find_all_concatenated_words(&["a", "aaa"])', 'vec!["aaa"]'),
        T("empty_string_is_no_piece", "words = [\"\", \"a\", \"aa\"]", 'find_all_concatenated_words(&["", "a", "aa"])', 'vec!["aa"]'),
    ],
    hidden=[
        T("only_empty", "words = [\"\"]", 'find_all_concatenated_words(&[""])', "Vec::<&str>::new()"),
        T("input_order", "words = [\"abab\", \"ab\", \"ababab\", \"b\", \"ba\"]", 'find_all_concatenated_words(&["abab", "ab", "ababab", "b", "ba"])', 'vec!["abab", "ababab"]'),
        T("three_pieces_needed", "words = [\"x\", \"y\", \"xyx\", \"yxy\", \"xyz\"]", 'find_all_concatenated_words(&["x", "y", "xyx", "yxy", "xyz"])', 'vec!["xyx", "yxy"]'),
        T("greedy_longest_piece_fails", "words = [\"ab\", \"abc\", \"cd\", \"abcd\"] (\"abc\" leaves \"d\"; \"ab\" + \"cd\" works)",
          'find_all_concatenated_words(&["ab", "abc", "cd", "abcd"])', 'vec!["abcd"]'),
        T("pieces_are_whole_words", "words = [\"ab\", \"cd\", \"abc\"]", 'find_all_concatenated_words(&["ab", "cd", "abc"])', "Vec::<&str>::new()"),
        T("longer_word_as_a_piece", "words = [\"abc\", \"d\", \"abcd\", \"abcdabc\"]", 'find_all_concatenated_words(&["abc", "d", "abcd", "abcdabc"])', 'vec!["abcd", "abcdabc"]'),
        T("thirty_letters", "words = [\"a\", 'a' × 30]", 'find_all_concatenated_words(&["a", &long])', 'vec!["a".repeat(30)]', setup='let long = "a".repeat(30);'),
        T("answers_are_the_input_slices", "the answer points into words", "std::ptr::eq(got[0].as_ptr(), w.as_ptr())", "true",
          setup='let w = String::from("xx");\nlet got = find_all_concatenated_words(&["x", &w]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1022);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(7) {
                    let len = rng.below(5);
                    let w = rng.string(len, "ab");
                    if !words.contains(&w) {
                        words.push(w);
                    }
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                // Brute force: ways[i] has bit 1 if w[..i] is one listed word, bit 2 if it splits into two or more.
                let want: Vec<&str> = refs
                    .iter()
                    .copied()
                    .filter(|w| {
                        let n = w.len();
                        let mut ways = vec![0u8; n + 1];
                        for i in 1..=n {
                            for j in 0..i {
                                if refs.contains(&&w[j..i]) {
                                    ways[i] |= if j == 0 { 1 } else if ways[j] != 0 { 2 } else { 0 };
                                }
                            }
                        }
                        n > 0 && ways[n] & 2 != 0
                    })
                    .collect();
                check!(format!("words = {refs:?}"), find_all_concatenated_words(&refs), want);
            }
        }

        #[test]
        fn scale_many_ways_to_fail() {
            // Runs of a's end in a letter no other word ends with, so no split works,
            // but a run of 29 a's splits into pieces of 1–10 a's in ~2²⁸ ways.
            let mut words: Vec<String> = (1..=10).map(|n| "a".repeat(n)).collect();
            for n in 20..=29 {
                words.push(format!("{}{}", "a".repeat(n), (b'b' + (29 - n) as u8) as char));
            }
            words.push("a".repeat(30));
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let mut want: Vec<String> = (2..=10).map(|n| "a".repeat(n)).collect();
            want.push("a".repeat(30));
            check!("words = 'a' × 1..=10, then 'a' × 29 + \\"b\\", 'a' × 28 + \\"c\\", …, 'a' × 20 + \\"k\\", then 'a' × 30", find_all_concatenated_words(&refs), want);
        }

        #[test]
        fn scale_10k_words() {
            // 8000 five-letter words and 2000 ten-letter words, each two of them joined.
            let mut words: Vec<String> = (0..8_000).map(|i| base10(i, 5)).collect();
            for i in 0..2_000 {
                words.push(format!("{}{}", base10(i * 3, 5), base10(i * 7 % 8_000, 5)));
            }
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let got = find_all_concatenated_words(&refs);
            check!("8000 five-letter words and 2000 pairs of them joined", (got.len(), got == refs[8_000..]), (2_000, true));
        }
        """ + BASE10,
    ],
    wrong=dict(
        whole_word_counts="""
            use std::collections::HashSet;

            pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
                let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
                words
                    .iter()
                    .copied()
                    .filter(|w| {
                        let n = w.len();
                        let mut ok = vec![false; n + 1];
                        ok[0] = true;
                        for i in 1..=n {
                            ok[i] = (0..i).any(|j| ok[j] && set.contains(&w[j..i]));
                        }
                        n > 0 && ok[n]
                    })
                    .collect()
            }
        """,
        no_memo="""
            use std::collections::HashSet;

            fn splits(set: &HashSet<&str>, w: &str, start: usize, pieces: usize) -> bool {
                if start == w.len() {
                    return pieces >= 2;
                }
                (start + 1..=w.len()).any(|end| set.contains(&w[start..end]) && splits(set, w, end, pieces + 1))
            }

            pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
                let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
                words.iter().copied().filter(|w| !w.is_empty() && splits(&set, w, 0, 0)).collect()
            }
        """,
        two_pieces_only="""
            use std::collections::HashSet;

            pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
                let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
                words.iter().copied().filter(|w| (1..w.len()).any(|k| set.contains(&w[..k]) && set.contains(&w[k..]))).collect()
            }
        """,
    ),
    hints=[("approach", "For each word, run word break: `ok[i]` is true when the first i letters split into words. From every reachable i, walk a trie of all words along the letters after i and mark each word end you pass."),
           ("rust", "Build one trie of the non-empty words, then `words.iter().copied().filter(..).collect()` returns the answers as the input's own `&'a str` slices, in order."),
           ("edge case", "Every word is in the dictionary, so a plain word break says yes to all of them. Skip the piece that starts at 0 and ends at the word's end. Without the `ok` table, a word like `aaaa…ab` is tried in exponentially many ways.")],
    notes=("Each word costs O(L²) trie steps at worst (a walk of up to L from each of L positions), so the total is O(Σ L²) with L ≤ 30. The `ok` table is the memo: a recursive search without it re-solves the same suffix for every way of reaching it. Sorting by length and testing each word against a trie of shorter words only is the other classic way to rule out the one-piece split.", "O(Σ L²)", "O(total letters × 26)"),
    follow_up="Return, for each concatenated word, one way to split it into pieces.",
    related=["D12", "D11"],
))

P.append(dict(
    slug="palindrome-pairs", title="Palindrome pairs", level="hard", stage="hard-tries-strings", tags=["palindrome", "HashMap", "split_at"],
    companies=["Meta", "Amazon", "Google", "Airbnb"],
    teaches=["Split each word at every position: if one side is a palindrome, the partner must be the other side reversed.",
             "Skip one of the two whole-word splits, or every equal-length pair is reported twice."],
    statement="""
        Return every pair of indexes `(i, j)`, `i != j`, such that `words[i] + words[j]` is a palindrome, sorted.

        Words are distinct lowercase ASCII; one of them may be `""`.
    """,
    examples=[("words = [\"abcd\", \"dcba\", \"lls\", \"s\", \"sssll\"]", "[(0, 1), (1, 0), (2, 4), (3, 2)]"),
              ("words = [\"bat\", \"tab\", \"cat\"]", "[(0, 1), (1, 0)]"), ("words = [\"a\", \"\"]", "[(0, 1), (1, 0)]")],
    constraints=["0 ≤ words.len() ≤ 2·10⁴", "0 ≤ words[i].len() ≤ 300, total length ≤ 3·10⁵"],
    starter="""
        pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        fn is_palindrome(b: &[u8]) -> bool {
            b.iter().eq(b.iter().rev())
        }

        pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
            // Each word reversed -> its index.
            let reversed: HashMap<Vec<u8>, usize> = words.iter().enumerate().map(|(i, w)| (w.bytes().rev().collect(), i)).collect();
            let mut out = Vec::new();
            for (i, w) in words.iter().enumerate() {
                let b = w.as_bytes();
                for cut in 0..=b.len() {
                    let (left, right) = b.split_at(cut);
                    // w + partner: the partner is `left` reversed, and `right` is the palindrome in the middle.
                    if is_palindrome(right) {
                        if let Some(&j) = reversed.get(left) {
                            if j != i {
                                out.push((i, j));
                            }
                        }
                    }
                    // partner + w: the partner is `right` reversed. cut = 0 would repeat the cut = len case of the partner.
                    if cut > 0 && is_palindrome(left) {
                        if let Some(&j) = reversed.get(right) {
                            if j != i {
                                out.push((j, i));
                            }
                        }
                    }
                }
            }
            out.sort_unstable();
            out
        }
    """,
    visible=[
        T("leetcode_lls", "words = [\"abcd\", \"dcba\", \"lls\", \"s\", \"sssll\"]", 'palindrome_pairs(&["abcd", "dcba", "lls", "s", "sssll"])', "vec![(0, 1), (1, 0), (2, 4), (3, 2)]"),
        T("leetcode_bat_tab", "words = [\"bat\", \"tab\", \"cat\"]", 'palindrome_pairs(&["bat", "tab", "cat"])', "vec![(0, 1), (1, 0)]"),
        T("leetcode_empty_word", "words = [\"a\", \"\"] (\"\" pairs with every palindrome, both ways)", 'palindrome_pairs(&["a", ""])', "vec![(0, 1), (1, 0)]"),
        T("no_words", "words = []", "palindrome_pairs(&[])", "Vec::<(usize, usize)>::new()"),
        T("no_pairs", "words = [\"a\", \"b\", \"c\"]", 'palindrome_pairs(&["a", "b", "c"])', "Vec::<(usize, usize)>::new()"),
        T("different_lengths", "words = [\"race\", \"car\", \"ecar\"]", 'palindrome_pairs(&["race", "car", "ecar"])', "vec![(0, 1), (0, 2), (2, 0)]"),
    ],
    hidden=[
        T("single_word", "words = [\"abc\"]", 'palindrome_pairs(&["abc"])', "Vec::<(usize, usize)>::new()"),
        T("palindrome_and_empty", "words = [\"aba\", \"\"]", 'palindrome_pairs(&["aba", ""])', "vec![(0, 1), (1, 0)]"),
        T("empty_with_non_palindrome", "words = [\"ab\", \"\"]", 'palindrome_pairs(&["ab", ""])', "Vec::<(usize, usize)>::new()"),
        T("same_letter_words", "words = [\"a\", \"aa\", \"aaa\"]", 'palindrome_pairs(&["a", "aa", "aaa"])', "vec![(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]"),
        T("mixed_with_empty", "words = [\"x\", \"xx\", \"\"]", 'palindrome_pairs(&["x", "xx", ""])', "vec![(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]"),
        T("reverse_pair_once", "words = [\"ab\", \"ba\", \"abab\"]", 'palindrome_pairs(&["ab", "ba", "abab"])', "vec![(0, 1), (1, 0)]"),
        T("only_one_order", "words = [\"abc\", \"ba\"] (\"abcba\" works, \"baabc\" doesn't)", 'palindrome_pairs(&["abc", "ba"])', "vec![(0, 1)]"),
        T("palindrome_suffix", "words = [\"cbaa\", \"abc\"] (\"cbaa\" + \"abc\" is \"cbaaabc\")", 'palindrome_pairs(&["cbaa", "abc"])', "vec![(0, 1)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1023);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(7) {
                    let len = rng.below(4);
                    let w = rng.string(len, "ab");
                    if !words.contains(&w) {
                        words.push(w);
                    }
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut want = Vec::new();
                for i in 0..refs.len() {
                    for j in 0..refs.len() {
                        let s = format!("{}{}", refs[i], refs[j]);
                        if i != j && s.bytes().eq(s.bytes().rev()) {
                            want.push((i, j));
                        }
                    }
                }
                check!(format!("words = {refs:?}"), palindrome_pairs(&refs), want);
            }
        }

        #[test]
        fn scale_20k_words() {
            use std::collections::HashMap;
            let mut words: Vec<String> = (0..20_000).map(|i| base10(i * 499_979, 10)).collect();
            let fifth_reversed: String = words[5].chars().rev().collect();
            words.push(fifth_reversed);
            words.extend(["qrstuvwxyz", "zyxwvutsrq", "klmnoonmlk", ""].map(String::from));
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            // Every word has 10 letters except "": pairs are a word with its reverse, or "" with a palindrome.
            let index: HashMap<&str, usize> = refs.iter().enumerate().map(|(i, &w)| (w, i)).collect();
            let empty = index[""];
            let mut want = Vec::new();
            for (i, w) in refs.iter().enumerate() {
                let r: String = w.chars().rev().collect();
                if let Some(&j) = index.get(r.as_str()) {
                    if j != i {
                        want.push((i, j));
                    } else if i != empty {
                        want.push((i, empty));
                        want.push((empty, i));
                    }
                }
            }
            want.sort_unstable();
            check!("20000 ten-letter words over a..j, one's reverse, qrstuvwxyz and its reverse, klmnoonmlk, \\"\\"", palindrome_pairs(&refs), want);
        }
        """ + BASE10,
    ],
    wrong=dict(
        every_pair="""
            pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
                let mut out = Vec::new();
                for i in 0..words.len() {
                    for j in 0..words.len() {
                        let s = format!("{}{}", words[i], words[j]);
                        if i != j && s.bytes().eq(s.bytes().rev()) {
                            out.push((i, j));
                        }
                    }
                }
                out
            }
        """,
        both_whole_word_splits="""
            use std::collections::HashMap;

            fn is_palindrome(b: &[u8]) -> bool {
                b.iter().eq(b.iter().rev())
            }

            pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
                let reversed: HashMap<Vec<u8>, usize> = words.iter().enumerate().map(|(i, w)| (w.bytes().rev().collect(), i)).collect();
                let mut out = Vec::new();
                for (i, w) in words.iter().enumerate() {
                    let b = w.as_bytes();
                    for cut in 0..=b.len() {
                        let (left, right) = b.split_at(cut);
                        if is_palindrome(right) {
                            if let Some(&j) = reversed.get(left) {
                                if j != i {
                                    out.push((i, j));
                                }
                            }
                        }
                        if is_palindrome(left) {
                            if let Some(&j) = reversed.get(right) {
                                if j != i {
                                    out.push((j, i));
                                }
                            }
                        }
                    }
                }
                out.sort_unstable();
                out
            }
        """,
        skips_the_empty_word="""
            use std::collections::HashMap;

            fn is_palindrome(b: &[u8]) -> bool {
                b.iter().eq(b.iter().rev())
            }

            pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
                let reversed: HashMap<Vec<u8>, usize> = words.iter().enumerate().map(|(i, w)| (w.bytes().rev().collect(), i)).collect();
                let mut out = Vec::new();
                for (i, w) in words.iter().enumerate() {
                    let b = w.as_bytes();
                    // Proper splits only: both sides non-empty, plus the plain reverse.
                    for cut in 1..b.len() {
                        let (left, right) = b.split_at(cut);
                        if is_palindrome(right) {
                            if let Some(&j) = reversed.get(left) {
                                out.push((i, j));
                            }
                        }
                        if is_palindrome(left) {
                            if let Some(&j) = reversed.get(right) {
                                out.push((j, i));
                            }
                        }
                    }
                    if let Some(&j) = reversed.get(b) {
                        if j != i {
                            out.push((i, j));
                        }
                    }
                }
                out.sort_unstable();
                out
            }
        """,
    ),
    hints=[("approach", "For `w + x` to be a palindrome with `w` the longer word, `x` reversed is a prefix of `w` and the rest of `w` is a palindrome. So split `w` at every position: if the right part is a palindrome, look up the left part reversed; if the left part is a palindrome, look up the right part reversed (that partner goes in front)."),
           ("rust", "Key a `HashMap<Vec<u8>, usize>` by each word reversed; `get(left)` works with a `&[u8]` because `Vec<u8>: Borrow<[u8]>`. `b.split_at(cut)` gives both sides without allocating."),
           ("edge case", "The split at 0 of one word and the split at the end of its reverse describe the same pair; handle the whole-word case on one side only. `\"\"` pairs with every palindrome, in both orders.")],
    notes=("Each word tries L + 1 splits, each with an O(L) palindrome check and an O(L) hash lookup: O(n · L²) overall, versus O(n² · L) for checking every pair. A trie of the reversed words (storing, at each node, the words whose remaining part is a palindrome) gives the same bound and is the other textbook answer.", "O(n · L²)", "O(n · L)"),
    follow_up="How would a trie of the reversed words replace the hash map, and what would each node store?",
    related=["S4", "D1"],
))

P.append(dict(
    slug="shortest-palindrome", title="Shortest palindrome (KMP)", level="hard", stage="hard-tries-strings", tags=["KMP", "palindrome", "chars"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["The longest palindromic prefix of `s` is the longest border of `s + separator + reverse(s)`.",
             "`Option<char>` gives a separator that equals no character, so input containing `#` can't break it."],
    statement="""
        Add as few characters as possible to the **front** of `s` to make it a palindrome, and return the result.

        `s` can hold any Unicode text; characters are whole `char`s.
    """,
    examples=[("s = \"aacecaaa\"", "\"aaacecaaa\""), ("s = \"abcd\"", "\"dcbabcd\"")],
    constraints=["0 ≤ number of characters ≤ 10⁶"],
    starter="""
        pub fn shortest_palindrome(s: &str) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn shortest_palindrome(s: &str) -> String {
            let chars: Vec<char> = s.chars().collect();
            // s, a separator equal to no character (None), then s reversed.
            let t: Vec<Option<char>> = chars.iter().copied().map(Some).chain([None]).chain(chars.iter().rev().copied().map(Some)).collect();
            // KMP border table of t.
            let mut border = vec![0; t.len()];
            let mut k = 0;
            for i in 1..t.len() {
                while k > 0 && t[i] != t[k] {
                    k = border[k - 1];
                }
                if t[i] == t[k] {
                    k += 1;
                }
                border[i] = k;
            }
            // The longest prefix of s that is also a suffix of reverse(s): the longest palindromic prefix.
            let keep = border[t.len() - 1];
            chars[keep..].iter().rev().chain(&chars).collect()
        }
    """,
    visible=[
        T("leetcode_aacecaaa", "s = \"aacecaaa\"", 'shortest_palindrome("aacecaaa")', '"aaacecaaa"'),
        T("leetcode_abcd", "s = \"abcd\"", 'shortest_palindrome("abcd")', '"dcbabcd"'),
        T("empty", "s = \"\"", 'shortest_palindrome("")', '""'),
        T("single", "s = \"a\"", 'shortest_palindrome("a")', '"a"'),
        T("already_a_palindrome", "s = \"aba\"", 'shortest_palindrome("aba")', '"aba"'),
        T("unicode", "s = \"éa\"", 'shortest_palindrome("éa")', '"aéa"'),
    ],
    hidden=[
        T("two_same", "s = \"aa\"", 'shortest_palindrome("aa")', '"aa"'),
        T("two_different", "s = \"ab\"", 'shortest_palindrome("ab")', '"bab"'),
        T("aab", "s = \"aab\"", 'shortest_palindrome("aab")', '"baab"'),
        T("abb", "s = \"abb\"", 'shortest_palindrome("abb")', '"bbabb"'),
        T("aabba", "s = \"aabba\"", 'shortest_palindrome("aabba")', '"abbaabba"'),
        T("emoji", "s = \"🦀\"", 'shortest_palindrome("🦀")', '"🦀"'),
        T("abac", "s = \"abac\"", 'shortest_palindrome("abac")', '"cabac"'),
        T("hash_in_the_input", "s = \"#a\" (a '#' separator would collide)", 'shortest_palindrome("#a")', '"a#a"'),
        T("hash_run", "s = \"a#a#\"", 'shortest_palindrome("a#a#")', '"#a#a#"'),
        T("abab", "s = \"abab\"", 'shortest_palindrome("abab")', '"babab"'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1024);
            for _ in 0..400 {
                let len = rng.below(10);
                let s = rng.string(len, "ab#é");
                let cs: Vec<char> = s.chars().collect();
                let keep = (0..=cs.len()).rev().find(|&k| cs[..k].iter().eq(cs[..k].iter().rev())).unwrap();
                let want: String = cs[keep..].iter().rev().chain(&cs).collect();
                check!(format!("s = {s:?}"), shortest_palindrome(&s), want);
            }
        }

        #[test]
        fn scale_million() {
            // The longest palindromic prefix is the first 500000 a's; every longer prefix almost matches.
            let m = 500_000;
            let s = format!("{}b{}", "a".repeat(m), "a".repeat(m - 1));
            let got = shortest_palindrome(&s);
            let want = format!("{}b{s}", "a".repeat(m - 1));
            check!("s = 'a' × 500000 + \\"b\\" + 'a' × 499999", (got.len(), got == want), (want.len(), true));
        }
        """,
    ],
    wrong=dict(
        no_separator="""
            pub fn shortest_palindrome(s: &str) -> String {
                let chars: Vec<char> = s.chars().collect();
                let t: Vec<char> = chars.iter().copied().chain(chars.iter().rev().copied()).collect();
                let mut border = vec![0; t.len()];
                let mut k = 0;
                for i in 1..t.len() {
                    while k > 0 && t[i] != t[k] {
                        k = border[k - 1];
                    }
                    if t[i] == t[k] {
                        k += 1;
                    }
                    border[i] = k;
                }
                let keep = border.last().copied().unwrap_or(0);
                chars[keep..].iter().rev().chain(&chars).collect()
            }
        """,
        hash_separator="""
            pub fn shortest_palindrome(s: &str) -> String {
                let chars: Vec<char> = s.chars().collect();
                let t: Vec<char> = chars.iter().copied().chain(['#']).chain(chars.iter().rev().copied()).collect();
                let mut border = vec![0; t.len()];
                let mut k = 0;
                for i in 1..t.len() {
                    while k > 0 && t[i] != t[k] {
                        k = border[k - 1];
                    }
                    if t[i] == t[k] {
                        k += 1;
                    }
                    border[i] = k;
                }
                let keep = border[t.len() - 1].min(chars.len());
                chars[keep..].iter().rev().chain(&chars).collect()
            }
        """,
        try_every_prefix="""
            pub fn shortest_palindrome(s: &str) -> String {
                let chars: Vec<char> = s.chars().collect();
                let keep = (0..=chars.len()).rev().find(|&k| chars[..k].iter().eq(chars[..k].iter().rev())).unwrap_or(0);
                chars[keep..].iter().rev().chain(&chars).collect()
            }
        """,
    ),
    hints=[("approach", "Only the longest palindromic prefix of `s` can stay unmirrored; the rest, reversed, goes in front. That prefix is the longest prefix of `s` that is also a suffix of `reverse(s)`: the last KMP border value of `s + separator + reverse(s)`."),
           ("rust", "Build the combined sequence as `Vec<Option<char>>` with `None` as the separator: it can't equal any character. Then `chars[keep..].iter().rev().chain(&chars).collect::<String>()`."),
           ("edge case", "Without a separator the border can run past the middle (`\"aa\"` gives 3 for `\"aaaa\"`). A `'#'` separator fails on input that contains `'#'`.")],
    notes=("The border table is linear, so the whole thing is O(n). The separator stops a border from spanning both halves, which would claim a palindromic prefix longer than `s`. Checking each prefix from the longest down is O(n²) in the worst case, as in the test where every long prefix is a near-palindrome.", "O(n)", "O(n)"),
    follow_up="How would you find the fewest characters to add at the end instead? And to make it a palindrome by adding anywhere?",
    related=["D12", "S2"],
))

LEXER_TYPES = r"""
use std::borrow::Cow;
use std::ops::Range;

#[derive(Debug, Clone, PartialEq)]
pub enum Token<'a> {
    Ident(&'a str),
    Int(&'a str),
    /// The contents without the quotes, escapes resolved.
    Str(Cow<'a, str>),
    Op(&'a str),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LexError {
    /// The input ended inside a string; `at` is the opening quote.
    UnterminatedString { at: usize },
    /// A backslash followed by anything but `\`, `"`, `n` or `t`; `at` is the backslash.
    BadEscape { at: usize },
    /// A character that starts no token.
    Unexpected { at: usize, ch: char },
}
"""

LEXER_SOLUTION = LEXER_TYPES + r"""
/// Two-character operators come first, so the longest match wins.
const OPS: &[&str] = &[
    "==", "!=", "<=", ">=", "->", "=>", "&&", "||", "::", "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", ":", ";", ",", ".", "(", ")", "{", "}", "[", "]",
];

pub struct Lexer<'a> {
    src: &'a str,
    pos: usize,
    /// Set after the end or an error; the lexer is fused from then on.
    done: bool,
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a str) -> Self {
        Lexer { src, pos: 0, done: false }
    }

    /// Moves `pos` past whitespace and `//` comments.
    fn skip_trivia(&mut self) {
        loop {
            let rest = &self.src[self.pos..];
            let trimmed = rest.trim_start();
            self.pos += rest.len() - trimmed.len();
            if !trimmed.starts_with("//") {
                return;
            }
            self.pos += trimmed.find('\n').unwrap_or(trimmed.len());
        }
    }

    fn lex(&mut self) -> Option<Result<(Token<'a>, Range<usize>), LexError>> {
        self.skip_trivia();
        let src: &'a str = self.src;
        let start = self.pos;
        let rest = &src[start..];
        let c = rest.chars().next()?;
        let (token, len) = if c.is_ascii_alphabetic() || c == '_' {
            let len = rest.find(|c: char| !(c.is_ascii_alphanumeric() || c == '_')).unwrap_or(rest.len());
            (Token::Ident(&rest[..len]), len)
        } else if c.is_ascii_digit() {
            let len = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
            (Token::Int(&rest[..len]), len)
        } else if c == '"' {
            match string_literal(rest, start) {
                Ok(found) => found,
                Err(e) => return Some(Err(e)),
            }
        } else if let Some(op) = OPS.iter().find(|op| rest.starts_with(**op)) {
            (Token::Op(&rest[..op.len()]), op.len())
        } else {
            return Some(Err(LexError::Unexpected { at: start, ch: c }));
        };
        self.pos = start + len;
        Some(Ok((token, start..start + len)))
    }
}

/// Reads the string literal that `rest` starts with; `start` is its offset in the source.
/// Returns the token and its length in bytes, quotes included.
fn string_literal(rest: &str, start: usize) -> Result<(Token<'_>, usize), LexError> {
    let body = &rest[1..];
    // `None` until the first escape: up to then the contents are a plain slice of the source.
    let mut owned: Option<String> = None;
    let mut copied = 0; // bytes of `body` already copied into `owned`
    let mut chars = body.char_indices();
    while let Some((i, c)) = chars.next() {
        match c {
            '"' => {
                let text = match owned {
                    None => Cow::Borrowed(&body[..i]),
                    Some(mut s) => {
                        s.push_str(&body[copied..i]);
                        Cow::Owned(s)
                    }
                };
                return Ok((Token::Str(text), i + 2));
            }
            '\\' => {
                let Some((_, e)) = chars.next() else {
                    break; // the input ends right after the backslash
                };
                let resolved = match e {
                    '\\' => '\\',
                    '"' => '"',
                    'n' => '\n',
                    't' => '\t',
                    _ => return Err(LexError::BadEscape { at: start + 1 + i }),
                };
                let s = owned.get_or_insert_with(String::new);
                s.push_str(&body[copied..i]);
                s.push(resolved);
                copied = i + 1 + e.len_utf8();
            }
            _ => {}
        }
    }
    Err(LexError::UnterminatedString { at: start })
}

impl<'a> Iterator for Lexer<'a> {
    type Item = Result<(Token<'a>, Range<usize>), LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }
        let item = self.lex();
        self.done = !matches!(item, Some(Ok(_)));
        item
    }
}

impl std::iter::FusedIterator for Lexer<'_> {}
"""

LEXER_HELPER = r"""
use std::borrow::Cow;

fn kinds(src: &str) -> Result<Vec<Token<'_>>, LexError> {
    Lexer::new(src).map(|r| r.map(|(t, _)| t)).collect()
}
"""

P.append(dict(
    slug="zero-copy-tokenizer", title="Zero-copy tokenizer", level="hard", stage="hard-tries-strings", tags=["lifetimes", "Cow", "Iterator", "parsing"],
    teaches=["`Iterator<Item = Result<(Token<'a>, Range<usize>), LexError>>`: items borrow the source, not the lexer, so they outlive it.",
             "`Cow<'a, str>` keeps string literals zero-copy until an escape forces an owned `String`.",
             "An error ends the stream: a fused iterator stops instead of lexing garbage after it."],
    statement=r"""
        Write a lexer for a small language. `Lexer::new(src)` is an iterator of `Result<(Token, span), LexError>`,
        where `span` is the token's byte range in `src`.

        - Whitespace (any Unicode whitespace) and `//` comments, up to the end of the line, are skipped.
        - `Ident`: an ASCII letter or `_`, then ASCII letters, digits and `_`.
        - `Int`: a run of ASCII digits. `12ab` is `Int("12")` then `Ident("ab")`.
        - `Str`: `"…"`, holding any Unicode, newlines included. Escapes are `\\`, `\"`, `\n` and `\t`. The token holds the
          contents without the quotes: **borrowed** from `src` when there is no escape, owned only when one had to be
          resolved. Its span includes the quotes.
        - `Op`: the **longest** operator that matches: `== != <= >= -> => && || ::`, else one of `+ - * / % = < > ! & | : ; , . ( ) { } [ ]`.

        Errors: `Unexpected { at, ch }` for a character that starts no token, `BadEscape { at }` (the backslash) for an
        unknown escape, `UnterminatedString { at }` (the opening quote) when the input ends inside a string. After an
        error, or the end, `next` returns `None` forever.

        Tokens borrow from `src`, not from the lexer, and may outlive it.
    """,
    examples=[("src = \"let x1 = 42;\"", "Ident(\"let\") 0..3, Ident(\"x1\") 4..6, Op(\"=\") 7..8, Int(\"42\") 9..11, Op(\";\") 11..12"),
              ("src = \"a @ b\"", "Ok(Ident(\"a\")), Err(Unexpected { at: 2, ch: '@' }), then None")],
    constraints=["0 ≤ src.len() ≤ 2·10⁶ bytes"],
    starter=LEXER_TYPES + r"""
pub struct Lexer<'a> {
    src: &'a str,
    pos: usize,
    // add fields if you need them
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a str) -> Self {
        Lexer { src, pos: 0 }
    }
}

impl<'a> Iterator for Lexer<'a> {
    type Item = Result<(Token<'a>, Range<usize>), LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        todo!()
    }
}
""",
    solution=LEXER_SOLUTION,
    visible=[
        LEXER_HELPER,
        T("let_statement", "src = \"let x1 = 42;\"", 'kinds("let x1 = 42;")', 'Ok(vec![Token::Ident("let"), Token::Ident("x1"), Token::Op("="), Token::Int("42"), Token::Op(";")])'),
        T("spans_are_byte_ranges", r'src = "a == \"hé\"" (é is two bytes)', r'Lexer::new("a == \"hé\"").map(|r| r.unwrap()).collect::<Vec<_>>()',
          r'vec![(Token::Ident("a"), 0..1), (Token::Op("=="), 2..4), (Token::Str(Cow::Borrowed("hé")), 5..10)]'),
        T("longest_operator_wins", "src = \"a->b<=c\"", 'kinds("a->b<=c")', 'Ok(vec![Token::Ident("a"), Token::Op("->"), Token::Ident("b"), Token::Op("<="), Token::Ident("c")])'),
        T("plain_string_is_borrowed", r'src = "\"hi\"" (no escape: the token borrows src)', r'matches!(&kinds("\"hi\"").unwrap()[0], Token::Str(Cow::Borrowed("hi")))', "true"),
        T("escapes_make_an_owned_string", r'src = r#""a\"b\n""# (two escapes)', "match kinds(src).unwrap().remove(0) {\n        Token::Str(Cow::Owned(s)) => Some(s),\n        _ => None,\n    }",
          r'Some("a\"b\n".to_string())', setup=r'''let src = r#""a\"b\n""#;'''),
        T("comments_and_whitespace", r'src = "x // note\n\t y"', r'kinds("x // note\n\t y")', 'Ok(vec![Token::Ident("x"), Token::Ident("y")])'),
        T("error_ends_the_stream", "src = \"a @ b\"; next() three times", "(lx.next(), lx.next(), lx.next())",
          "(Some(Ok((Token::Ident(\"a\"), 0..1))), Some(Err(LexError::Unexpected { at: 2, ch: '@' })), None)", setup='let mut lx = Lexer::new("a @ b");'),
        T("unterminated_string", r'src = "x = \"abc"', r'kinds("x = \"abc")', "Err(LexError::UnterminatedString { at: 4 })"),
        T("empty", "src = \"\"", 'kinds("")', "Ok(vec![])"),
    ],
    hidden=[
        LEXER_HELPER,
        T("bad_escape", r'src = r#""a\q""#', "kinds(src)", "Err(LexError::BadEscape { at: 2 })", setup=r'''let src = r#""a\q""#;'''),
        T("backslash_at_the_end", r'src = r#""ab\"#', "kinds(src)", "Err(LexError::UnterminatedString { at: 0 })", setup=r'''let src = r#""ab\"#;'''),
        T("escaped_quote_then_end", r'src = r#""ab\""# (the quote is escaped, so the string never closes)', "kinds(src)", "Err(LexError::UnterminatedString { at: 0 })", setup=r'''let src = r#""ab\""#;'''),
        T("unicode_outside_a_string", "src = \"a é\"", 'kinds("a é")', "Err(LexError::Unexpected { at: 2, ch: 'é' })"),
        T("unicode_inside_a_string", r'src = "\"🦀\""', r'Lexer::new("\"🦀\"").map(|r| r.unwrap()).collect::<Vec<_>>()', r'vec![(Token::Str(Cow::Borrowed("🦀")), 0..6)]'),
        T("maximal_munch", "src = \"a-->b === ::< &&& !==\"", 'kinds("a-->b === ::< &&& !==")',
          'Ok(["a", "-", "->", "b", "==", "=", "::", "<", "&&", "&", "!=", "="].map(|s| if s == "a" || s == "b" { Token::Ident(s) } else { Token::Op(s) }).to_vec())'),
        T("comment_at_the_end", "src = \"x //end\"", 'kinds("x //end")', 'Ok(vec![Token::Ident("x")])'),
        T("only_a_comment", "src = \"// just a comment\"", 'kinds("// just a comment")', "Ok(vec![])"),
        T("slash_is_an_operator", "src = \"a / b/ /c\"", 'kinds("a / b/ /c")',
          'Ok(vec![Token::Ident("a"), Token::Op("/"), Token::Ident("b"), Token::Op("/"), Token::Op("/"), Token::Ident("c")])'),
        T("comment_marker_inside_a_string", r'src = "\"// not\" y"', r'kinds("\"// not\" y")', 'Ok(vec![Token::Str(Cow::Borrowed("// not")), Token::Ident("y")])'),
        T("numbers_then_idents", "src = \"12ab 007\"", 'kinds("12ab 007")', 'Ok(vec![Token::Int("12"), Token::Ident("ab"), Token::Int("007")])'),
        T("newline_inside_a_string", r'src = "\"a\nb\""', r'kinds("\"a\nb\"")', r'Ok(vec![Token::Str(Cow::Borrowed("a\nb"))])'),
        T("unicode_whitespace", r'src = "a\u{3000}b\u{a0}c"', r'kinds("a\u{3000}b\u{a0}c")', 'Ok(vec![Token::Ident("a"), Token::Ident("b"), Token::Ident("c")])'),
        T("fused_after_an_error", r'src = "\"x"; next() three times', "(lx.next(), lx.next(), lx.next())", "(Some(Err(LexError::UnterminatedString { at: 0 })), None, None)",
          setup=r'let mut lx = Lexer::new("\"x");'),
        T("escape_after_unicode", r'src = r#""é\té""#', "Lexer::new(src).map(|r| r.unwrap()).collect::<Vec<_>>()", r'vec![(Token::Str(Cow::Owned("é\té".to_string())), 0..8)]',
          setup=r'''let src = r#""é\té""#;'''),
        T("bad_escape_after_unicode", r'src = r#""é\é""# (é is two bytes)', "kinds(src)", "Err(LexError::BadEscape { at: 3 })", setup=r'''let src = r#""é\é""#;'''),
        T("punctuation", "src = \"(a,b)[0]{c};x.y%z*w\"", 'kinds("(a,b)[0]{c};x.y%z*w").unwrap().len()', "19"),
        T("zero_copy", "idents and plain strings point into src", "ok", "true",
          setup='let src = String::from("name \\"text\\"");\nlet toks: Vec<Token> = Lexer::new(&src).map(|r| r.unwrap().0).collect();\nlet ok = match (&toks[0], &toks[1]) {\n    (Token::Ident(a), Token::Str(Cow::Borrowed(b))) => std::ptr::eq(a.as_ptr(), src.as_ptr()) && std::ptr::eq(b.as_ptr(), src[6..].as_ptr()),\n    _ => false,\n};'),
        T("tokens_outlive_the_lexer", "src = \"fn main\"; keep the first item after the lexer is dropped", "first", 'Some(Ok((Token::Ident("fn"), 0..2)))',
          setup='let src = String::from("fn main");\nlet first;\n{\n    let mut lx = Lexer::new(&src);\n    first = lx.next();\n}'),
        r"""
        #[test]
        fn random_programs() {
            // Pieces with a known token, joined by trivia so they can't merge; sometimes an error at the end.
            let pieces: [(&str, Token); 12] = [
                ("abc", Token::Ident("abc")),
                ("_x1", Token::Ident("_x1")),
                ("42", Token::Int("42")),
                ("==", Token::Op("==")),
                ("=", Token::Op("=")),
                ("->", Token::Op("->")),
                ("-", Token::Op("-")),
                ("::", Token::Op("::")),
                ("\"hi\"", Token::Str(Cow::Borrowed("hi"))),
                ("\"a\\nb\"", Token::Str(Cow::Owned("a\nb".to_string()))),
                ("\"é\"", Token::Str(Cow::Borrowed("é"))),
                ("\"\"", Token::Str(Cow::Borrowed(""))),
            ];
            let gaps = [" ", "\n", "\t ", " // c\n"];
            let mut rng = anneal_prelude::Rng::new(1025);
            for _ in 0..300 {
                let mut src = String::new();
                let mut want: Vec<Result<(Token, std::ops::Range<usize>), LexError>> = Vec::new();
                let mut owned = Vec::new();
                for _ in 0..rng.below(8) {
                    let (text, tok) = rng.pick(&pieces).clone();
                    let start = src.len();
                    src.push_str(text);
                    owned.push(matches!(tok, Token::Str(Cow::Owned(_))));
                    want.push(Ok((tok, start..src.len())));
                    let gap: &str = *rng.pick(&gaps);
            src.push_str(gap);
                }
                match rng.below(4) {
                    0 => {
                        want.push(Err(LexError::Unexpected { at: src.len(), ch: '@' }));
                        src.push_str("@ x");
                    }
                    1 => {
                        want.push(Err(LexError::UnterminatedString { at: src.len() }));
                        src.push_str("\"open");
                    }
                    2 => {
                        want.push(Err(LexError::BadEscape { at: src.len() + 2 }));
                        src.push_str("\"b\\q\" x");
                    }
                    _ => {}
                }
                let got: Vec<_> = Lexer::new(&src).collect();
                let got_owned: Vec<bool> = got.iter().filter_map(|r| r.as_ref().ok()).map(|(t, _)| matches!(t, Token::Str(Cow::Owned(_)))).collect();
                check!(format!("src = {src:?}"), got, want.clone());
                check!(format!("src = {src:?}: which strings are owned"), got_owned, owned);
            }
        }

        #[test]
        fn scale_million_bytes() {
            let line = "let x_1 = \"str\\n\" + 42; // c\n";
            let src = line.repeat(40_000);
            let (mut count, mut owned, mut last) = (0, 0, 0..0);
            for item in Lexer::new(&src) {
                let (tok, span) = item.unwrap();
                count += 1;
                owned += matches!(tok, Token::Str(Cow::Owned(_))) as usize;
                last = span;
            }
            let semi = src.len() - line.len() + line.find(';').unwrap();
            check!("src = 40000 lines of `let x_1 = \"str\\n\" + 42; // c`", (count, owned, last), (280_000, 40_000, semi..semi + 1));
        }
        """,
    ],
    wrong=dict(
        always_owned=LEXER_SOLUTION.replace("""                let text = match owned {
                    None => Cow::Borrowed(&body[..i]),
                    Some(mut s) => {
                        s.push_str(&body[copied..i]);
                        Cow::Owned(s)
                    }
                };""", """                let mut s = owned.unwrap_or_default();
                s.push_str(&body[copied..i]);
                let text = Cow::Owned(s);"""),
        keeps_going_after_an_error=LEXER_SOLUTION.replace("        self.done = !matches!(item, Some(Ok(_)));\n", "        self.done = item.is_none();\n"),
        rescans_from_the_start=LEXER_SOLUTION.replace("""    fn lex(&mut self) -> Option<Result<(Token<'a>, Range<usize>), LexError>> {
        self.skip_trivia();""", """    fn lex(&mut self) -> Option<Result<(Token<'a>, Range<usize>), LexError>> {
        // Keep the position in characters and find its byte offset from the start every time.
        let chars_done = self.src[..self.pos].chars().count();
        self.pos = self.src.char_indices().nth(chars_done).map_or(self.src.len(), |(i, _)| i);
        self.skip_trivia();"""),
    ),
    hints=[("approach", "Skip trivia, look at the first character, and pick the rule: identifier, number, string or operator. Try the two-character operators before the one-character ones. For strings, scan for the closing quote, handling a backslash and the character after it together."),
           ("rust", "`type Item = Result<(Token<'a>, Range<usize>), LexError>` ties tokens to the source's `'a`, not to `&mut self`. Keep `Option<String>` while scanning a string: `None` means no escape yet, so the result is `Cow::Borrowed(&body[..i])`; the first escape copies what came before into a `String`."),
           ("edge case", "After an error, set a flag and return `None` from then on (and you may `impl FusedIterator`). A backslash just before the end is an unterminated string, not a bad escape; `\"ab\\\"` never closes.")],
    notes=("One pass: every byte is looked at once, so lexing is O(n), and only strings with escapes allocate. The lifetime parameter is what makes it zero-copy: `Token<'a>` borrows the source, so tokens outlive the lexer and cost nothing to produce. `Cow` lets one type carry both the borrowed common case and the owned escaped case. Maximal munch (`->` before `-`) is why the operator list is ordered by length. Finding the byte offset from the start again for every token (or counting characters to get there) makes it O(n²).", "O(n)", "O(1) besides owned strings"),
    follow_up="How would you add line and column numbers to errors without making every token pay for them?",
    related=["L3", "S2", "S6"],
))

STAGES = [
    ("first-tries", "First tries", "easy"),
    ("tries-at-work", "Tries at work", "medium"),
    ("string-algorithms", "String algorithms", "medium"),
    ("hard-tries-strings", "Hard tries & strings", "hard"),
]

if __name__ == "__main__":
    n = write_track("d10-tries-strings", "D10", "Tries & strings", "D", "core", 11,
                    "Prefix trees for lookup and autocomplete, then the string algorithms interviews reach for: KMP, palindromes, rolling hashes.",
                    STAGES, P)
    print("D10", n)
