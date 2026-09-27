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
