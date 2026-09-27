from author import T, write_track

HM = "std::collections::HashMap"
P = []

P.append(dict(
    slug="most-common-word", title="Most common word", level="easy", stage="use-it", tags=["HashMap", "HashSet"],
    teaches=["Count into a `HashMap`, filter with a `HashSet`.", "`max_by` with a tie-breaker."],
    statement="""
        Return the most frequent word in `paragraph` that isn't in `banned`. Words are runs of ASCII
        letters, compared case-insensitively and returned in lowercase. Ties go to the alphabetically
        first word; return `""` if there are no words.
    """,
    examples=[("\"Bob hit a ball, the hit BALL flew far after it was hit.\", banned = [\"hit\"]", "\"ball\"")],
    starter="""
        pub fn most_common_word(paragraph: &str, banned: &[&str]) -> String {
            todo!()
        }
    """,
    solution="""
        use std::collections::{HashMap, HashSet};

        pub fn most_common_word(paragraph: &str, banned: &[&str]) -> String {
            let banned: HashSet<&str> = banned.iter().copied().collect();
            let mut counts: HashMap<String, usize> = HashMap::new();
            for w in paragraph.split(|c: char| !c.is_ascii_alphabetic()).filter(|w| !w.is_empty()) {
                let w = w.to_ascii_lowercase();
                if !banned.contains(w.as_str()) {
                    *counts.entry(w).or_insert(0) += 1;
                }
            }
            counts
                .into_iter()
                .max_by(|a, b| a.1.cmp(&b.1).then_with(|| b.0.cmp(&a.0)))
                .map(|(w, _)| w)
                .unwrap_or_default()
        }
    """,
    visible=[
        T("ball", "\"Bob hit a ball, the hit BALL flew far after it was hit.\", banned = [\"hit\"]", 'most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", &["hit"])', '"ball"'),
        T("single", "\"a.\", banned = []", 'most_common_word("a.", &[])', '"a"'),
    ],
    hidden=[
        T("tie_alphabetical", "\"b a b a\", banned = []", 'most_common_word("b a b a", &[])', '"a"'),
        T("all_banned", "\"x y\", banned = [\"x\", \"y\"]", 'most_common_word("x y", &["x", "y"])', '""'),
    ],
    hints=[("rust", "`str::split` with a closure splits on every non-letter; skip the empty pieces."),
           ("edge case", "Without a tie-breaker, iteration order over a HashMap decides the answer.")],
    notes=("`HashMap` iteration order is unspecified, so an explicit tie-break is what makes the answer deterministic.", "O(n)", "O(n)"),
    follow_up="How would you return the top three words efficiently?",
    related=["D1"],
))

P.append(dict(
    slug="group-by-length", title="Group borrowed words by length", level="easy", stage="use-it", tags=["entry API", "lifetimes"],
    teaches=["`entry(k).or_default().push(..)` for grouping.", "Keeping borrowed `&'a str` in the output instead of allocating Strings."],
    statement="Group `words` by length, keeping each group in input order. Don't copy the strings.",
    starter="""
        use std::collections::HashMap;

        pub fn group_by_len<'a>(words: &[&'a str]) -> HashMap<usize, Vec<&'a str>> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn group_by_len<'a>(words: &[&'a str]) -> HashMap<usize, Vec<&'a str>> {
            let mut groups: HashMap<usize, Vec<&'a str>> = HashMap::new();
            for &w in words {
                groups.entry(w.len()).or_default().push(w);
            }
            groups
        }
    """,
    visible=[
        T("mixed", "[\"hi\", \"yes\", \"no\", \"ok\"]", 'group_by_len(&["hi", "yes", "no", "ok"])', f'{HM}::from([(2, vec!["hi", "no", "ok"]), (3, vec!["yes"])])'),
        T("empty", "[]", "group_by_len(&[])", f"{HM}::new()"),
    ],
    hidden=[
        T("empty_string", "[\"\", \"a\", \"\"]", 'group_by_len(&["", "a", ""])', f'{HM}::from([(0, vec!["", ""]), (1, vec!["a"])])'),
    ],
    hints=[("rust", "`entry(len).or_default()` gives you the group's `Vec`, creating it if needed.")],
    notes=("The output borrows from the caller's strings, so the signature ties it to `'a`, the words' lifetime, not the slice's.", "O(n)", "O(n)"),
    follow_up="Why is the lifetime on `&'a str` and not on the outer slice?",
    related=["L3"],
))

P.append(dict(
    slug="compare-tags", title="Set operations on tags", level="easy", stage="use-it", tags=["HashSet", "intersection"],
    teaches=["`intersection` and `difference` on `HashSet`.", "Sorting results that come out of a hash set."],
    statement="Given two tag lists, return (tags in both, tags only in `a`, tags only in `b`), each sorted and without duplicates.",
    starter="""
        pub fn compare_tags(a: &[&str], b: &[&str]) -> (Vec<String>, Vec<String>, Vec<String>) {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashSet;

        pub fn compare_tags(a: &[&str], b: &[&str]) -> (Vec<String>, Vec<String>, Vec<String>) {
            let a: HashSet<&str> = a.iter().copied().collect();
            let b: HashSet<&str> = b.iter().copied().collect();
            let sorted = |it: &mut dyn Iterator<Item = &&str>| {
                let mut v: Vec<String> = it.map(|s| s.to_string()).collect();
                v.sort();
                v
            };
            (sorted(&mut a.intersection(&b)), sorted(&mut a.difference(&b)), sorted(&mut b.difference(&a)))
        }
    """,
    visible=[
        T("overlap", "a = [rust, go, sql], b = [sql, rust, c]", 'compare_tags(&["rust", "go", "sql"], &["sql", "rust", "c"])', '(vec!["rust".to_string(), "sql".to_string()], vec!["go".to_string()], vec!["c".to_string()])'),
        T("disjoint", "a = [a], b = [b]", 'compare_tags(&["a"], &["b"])', '(vec![], vec!["a".to_string()], vec!["b".to_string()])'),
    ],
    hidden=[
        T("duplicates", "a = [x, x], b = [x]", 'compare_tags(&["x", "x"], &["x"])', '(vec!["x".to_string()], vec![], vec![])'),
    ],
    hints=[("rust", "Collect each side into a `HashSet<&str>`, then use `intersection` and `difference`.")],
    notes=("The set operations return lazy iterators of references; sorting afterwards is what makes the output stable.", "O(n + m + k log k)", "O(n + m)"),
    follow_up="When would you use `BTreeSet` instead and skip the sort?",
    related=["D1"],
))

P.append(dict(
    slug="index-by-first-letter", title="Index words by first letter", level="easy", stage="use-it", tags=["BTreeMap", "entry API"],
    teaches=["`BTreeMap` gives sorted keys for free.", "`chars().next()` for the first character."],
    statement="Build an index from lowercase first letter to the words starting with it, each list sorted. Skip empty strings.",
    starter="""
        use std::collections::BTreeMap;

        pub fn index(words: &[&str]) -> BTreeMap<char, Vec<String>> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BTreeMap;

        pub fn index(words: &[&str]) -> BTreeMap<char, Vec<String>> {
            let mut idx: BTreeMap<char, Vec<String>> = BTreeMap::new();
            for w in words {
                if let Some(first) = w.chars().next() {
                    idx.entry(first.to_ascii_lowercase()).or_default().push(w.to_string());
                }
            }
            for list in idx.values_mut() {
                list.sort();
            }
            idx
        }
    """,
    visible=[
        T("fruit", "[\"banana\", \"Apple\", \"avocado\"]", 'index(&["banana", "Apple", "avocado"]).into_iter().collect::<Vec<_>>()', "vec![('a', vec![\"Apple\".to_string(), \"avocado\".to_string()]), ('b', vec![\"banana\".to_string()])]"),
        T("empty_string", "[\"\"]", 'index(&[""]).len()', "0"),
    ],
    hidden=[
        T("keys_sorted", "[\"z\", \"m\", \"a\"]", 'index(&["z", "m", "a"]).keys().copied().collect::<Vec<_>>()', "vec!['a', 'm', 'z']"),
    ],
    hints=[("rust", "`BTreeMap` iterates in key order, so the index comes out alphabetised.")],
    notes=("Sorting each list once at the end is cheaper than inserting in order.", "O(n log n)", "O(n)"),
    follow_up="What would you change to index by the first Unicode grapheme instead of the first char?",
    related=["S2"],
))

P.append(dict(
    slug="btreemap-ranges", title="BTreeMap range queries", level="medium", stage="understand-it", tags=["BTreeMap::range"],
    teaches=["`range(a..=b)` walks only the keys in the range, in order.", "`range` panics if start > end, so check first."],
    statement="`events` maps a timestamp to a name. Return the names with timestamps in `from..=to`, in time order. If `from > to`, return nothing.",
    starter="""
        use std::collections::BTreeMap;

        pub fn between(events: &BTreeMap<u32, String>, from: u32, to: u32) -> Vec<&str> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BTreeMap;

        pub fn between(events: &BTreeMap<u32, String>, from: u32, to: u32) -> Vec<&str> {
            if from > to {
                return Vec::new();
            }
            events.range(from..=to).map(|(_, name)| name.as_str()).collect()
        }
    """,
    visible=[
        T("middle", "events at 1, 5, 9; from 2 to 9", "between(&m, 2, 9)", 'vec!["b", "c"]', setup='let m = std::collections::BTreeMap::from([(1, "a".to_string()), (5, "b".to_string()), (9, "c".to_string())]);'),
        T("none", "events at 1; from 2 to 3", "between(&m, 2, 3)", "Vec::<&str>::new()", setup='let m = std::collections::BTreeMap::from([(1, "a".to_string())]);'),
    ],
    hidden=[
        T("reversed_bounds", "from 9 to 1", "between(&m, 9, 1)", "Vec::<&str>::new()", setup='let m = std::collections::BTreeMap::from([(5, "b".to_string())]);'),
        T("exact_bounds", "events at 1 and 9; from 1 to 9", "between(&m, 1, 9)", 'vec!["a", "c"]', setup='let m = std::collections::BTreeMap::from([(1, "a".to_string()), (9, "c".to_string())]);'),
    ],
    hints=[("rust", "`BTreeMap::range` takes any range expression and yields entries in key order.")],
    notes=("A range query costs O(log n + k): find the start, then walk k entries. `range` panics on inverted bounds, hence the check.", "O(log n + k)", "O(k)"),
    follow_up="How would you find the latest event at or before a timestamp?",
    related=["D4"],
))

P.append(dict(
    slug="fix-hash-eq-consistency", title="Fix: Hash that disagrees with Eq", mode="fix", level="medium", stage="understand-it", tags=["Hash", "Eq", "HashSet"],
    teaches=["If `a == b`, then `hash(a) == hash(b)` must hold.", "Deriving `Hash` next to a hand-written `PartialEq` breaks that."],
    statement="""
        `Username` compares case-insensitively, but a `HashSet<Username>` still counts `"Alice"` and
        `"alice"` as different. Fix `Username` so `distinct` is right. Keep the case-insensitive comparison.
    """,
    starter="""
        use std::collections::HashSet;
        use std::hash::{Hash, Hasher};

        /// A username that compares case-insensitively.
        #[derive(Debug, Clone, Hash)]
        pub struct Username(pub String);

        impl PartialEq for Username {
            fn eq(&self, other: &Self) -> bool {
                self.0.eq_ignore_ascii_case(&other.0)
            }
        }

        impl Eq for Username {}

        /// How many different usernames there are, ignoring case.
        pub fn distinct(names: &[&str]) -> usize {
            names.iter().map(|n| Username(n.to_string())).collect::<HashSet<_>>().len()
        }
    """,
    solution="""
        use std::collections::HashSet;
        use std::hash::{Hash, Hasher};

        /// A username that compares case-insensitively.
        #[derive(Debug, Clone)]
        pub struct Username(pub String);

        impl PartialEq for Username {
            fn eq(&self, other: &Self) -> bool {
                self.0.eq_ignore_ascii_case(&other.0)
            }
        }

        impl Eq for Username {}

        /// Hashes exactly what `eq` compares: the lowercase bytes.
        impl Hash for Username {
            fn hash<H: Hasher>(&self, state: &mut H) {
                for b in self.0.bytes() {
                    state.write_u8(b.to_ascii_lowercase());
                }
                state.write_u8(0xff);
            }
        }

        /// How many different usernames there are, ignoring case.
        pub fn distinct(names: &[&str]) -> usize {
            names.iter().map(|n| Username(n.to_string())).collect::<HashSet<_>>().len()
        }
    """,
    visible=[
        T("case_folds", "[\"Alice\", \"alice\", \"Bob\"]", 'distinct(&["Alice", "alice", "Bob"])', "2"),
        T("already_distinct", "[\"a\", \"b\"]", 'distinct(&["a", "b"])', "2"),
    ],
    hidden=[
        T("many_cases", "[\"ADMIN\", \"admin\", \"Admin\", \"aDmIn\"]", 'distinct(&["ADMIN", "admin", "Admin", "aDmIn"])', "1"),
        T("empty", "[]", "distinct(&[])", "0"),
    ],
    hints=[("approach", "Two usernames that are equal must hash the same. Does the derived `Hash` know about case?"),
           ("rust", "Implement `Hash` yourself and feed the hasher the same thing `eq` compares.")],
    notes=("The derived `Hash` hashes the original bytes, so equal values land in different buckets and never get compared. clippy flags this pattern (`derived_hash_with_manual_eq`) as a correctness error. The trailing `0xff` mirrors how `str` hashes, so adjacent fields can't run together.", "O(n · len)", "O(n)"),
    follow_up="What goes wrong in a BTreeMap if `Ord` disagrees with `Eq`?",
    related=["S8"],
))

P.append(dict(
    slug="fix-borrowed-lookup", title="Fix: allocating on every lookup", mode="fix", level="medium", stage="understand-it", tags=["Borrow<str>", "HashMap::get"],
    teaches=["`HashMap<String, V>::get` accepts `&str` because `String: Borrow<str>`.", "Building a `String` just to look one up is an allocation per call."],
    statement="`Registry::id` runs on every request and allocates a `String` each time. Make it look the name up without allocating.",
    starter="""
        use std::collections::HashMap;

        pub struct Registry {
            ids: HashMap<String, u32>,
        }

        impl Registry {
            pub fn new(names: &[&str]) -> Self {
                let ids = names.iter().enumerate().map(|(i, n)| (String::from(*n), i as u32)).collect();
                Registry { ids }
            }

            /// The id for `name`. Called on every request, so it must not allocate.
            pub fn id(&self, name: &str) -> Option<u32> {
                self.ids.get(&name.to_string()).copied()
            }
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub struct Registry {
            ids: HashMap<String, u32>,
        }

        impl Registry {
            pub fn new(names: &[&str]) -> Self {
                let ids = names.iter().enumerate().map(|(i, n)| (String::from(*n), i as u32)).collect();
                Registry { ids }
            }

            /// The id for `name`. Called on every request, so it must not allocate.
            pub fn id(&self, name: &str) -> Option<u32> {
                self.ids.get(name).copied()
            }
        }
    """,
    rules=dict(methods=["to_string", "to_owned", "into", "clone"], lines=1),
    visible=[
        T("found", "names = [\"a\", \"b\"], id(\"b\")", 'Registry::new(&["a", "b"]).id("b")', "Some(1)"),
        T("missing", "names = [\"a\"], id(\"z\")", 'Registry::new(&["a"]).id("z")', "None"),
    ],
    hidden=[
        T("first", "names = [\"x\", \"y\"], id(\"x\")", 'Registry::new(&["x", "y"]).id("x")', "Some(0)"),
    ],
    hints=[("rust", "Look at the signature of `HashMap::get`: `fn get<Q>(&self, k: &Q) where K: Borrow<Q>`.")],
    notes=("`String: Borrow<str>` and the two hash identically, so the map can be queried with a `&str` directly. That's what the `Borrow` bound on `get` is for.", "O(len)", "O(1)"),
    follow_up="Why does `Borrow` require `Hash`, `Eq` and `Ord` to agree between the owned and borrowed forms?",
    related=["S8", "S2"],
))

P.append(dict(
    slug="deterministic-report", title="A deterministic report from a HashMap", level="medium", stage="understand-it", tags=["HashMap order", "sort_by"],
    teaches=["`HashMap` iteration order is unspecified and changes between runs.", "Collect, then sort with an explicit key."],
    statement="Format each entry as `\"name: score\"`, highest score first, ties by name ascending.",
    starter="""
        use std::collections::HashMap;

        pub fn report(scores: &HashMap<String, u32>) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn report(scores: &HashMap<String, u32>) -> Vec<String> {
            let mut rows: Vec<(&String, &u32)> = scores.iter().collect();
            rows.sort_by(|a, b| b.1.cmp(a.1).then_with(|| a.0.cmp(b.0)));
            rows.into_iter().map(|(name, score)| format!("{name}: {score}")).collect()
        }
    """,
    visible=[
        T("ordered", "{ann: 5, bob: 9, cy: 5}", 'report(&std::collections::HashMap::from([("ann".to_string(), 5), ("bob".to_string(), 9), ("cy".to_string(), 5)]))', 'vec!["bob: 9", "ann: 5", "cy: 5"]'),
        T("empty", "{}", "report(&std::collections::HashMap::new())", "Vec::<String>::new()"),
    ],
    hidden=[
        T("many_ties", "{d: 1, c: 1, b: 1, a: 1}", 'report(&std::collections::HashMap::from([("d".to_string(), 1), ("c".to_string(), 1), ("b".to_string(), 1), ("a".to_string(), 1)]))', 'vec!["a: 1", "b: 1", "c: 1", "d: 1"]'),
    ],
    hints=[("rust", "Collect `(&String, &u32)` pairs into a Vec and sort it; no need to clone the names first.")],
    notes=("Sorting references avoids cloning keys until the final `format!`.", "O(n log n)", "O(n)"),
    follow_up="Why does std's HashMap randomise its hash seed?",
    related=["S3"],
))

P.append(dict(
    slug="floor-and-ceiling", title="Floor and ceiling with range", level="medium", stage="understand-it", tags=["BTreeSet", "range", "next_back"],
    teaches=["`range(..=x).next_back()` is the floor; `range(x..).next()` is the ceiling."],
    statement="Return the largest price ≤ `x` and the smallest price ≥ `x`, each `None` if there isn't one.",
    starter="""
        use std::collections::BTreeSet;

        pub fn nearest(prices: &BTreeSet<u32>, x: u32) -> (Option<u32>, Option<u32>) {
            todo!()
        }
    """,
    solution="""
        use std::collections::BTreeSet;

        pub fn nearest(prices: &BTreeSet<u32>, x: u32) -> (Option<u32>, Option<u32>) {
            let floor = prices.range(..=x).next_back().copied();
            let ceiling = prices.range(x..).next().copied();
            (floor, ceiling)
        }
    """,
    visible=[
        T("between", "prices = {10, 20, 30}, x = 25", "nearest(&std::collections::BTreeSet::from([10, 20, 30]), 25)", "(Some(20), Some(30))"),
        T("exact", "prices = {10, 20}, x = 20", "nearest(&std::collections::BTreeSet::from([10, 20]), 20)", "(Some(20), Some(20))"),
    ],
    hidden=[
        T("below_all", "prices = {10}, x = 3", "nearest(&std::collections::BTreeSet::from([10]), 3)", "(None, Some(10))"),
        T("empty", "prices = {}, x = 3", "nearest(&std::collections::BTreeSet::new(), 3)", "(None, None)"),
    ],
    hints=[("rust", "A range iterator is double-ended: `next_back` gives the last element of `..=x`.")],
    notes=("Both queries are O(log n) and neither scans the set.", "O(log n)", "O(1)"),
    follow_up="How would you find the k nearest prices to x?",
    related=["D4", "D14"],
))

P.append(dict(
    slug="open-addressing-map", title="A hash map with open addressing", level="hard", stage="build-it", tags=["linear probing", "tombstones"],
    teaches=["Linear probing, and why removal needs tombstones.", "Resizing before the table gets too full."],
    statement="""
        Build `OpenMap<V>`, a hash map from `u64` keys to `V`, on one `Vec<Slot<V>>` with linear probing.
        Implement `new`, `insert` (returning the old value if the key existed), `get`, `remove` and `len`.
        Keep the load factor below 3/4 by doubling. Removing must not break lookups of keys further along a probe chain.
    """,
    starter="""
        enum Slot<V> {
            Empty,
            Deleted,
            Full(u64, V),
        }

        pub struct OpenMap<V> {
            slots: Vec<Slot<V>>,
            len: usize,
        }

        impl<V> OpenMap<V> {
            pub fn new() -> Self {
                todo!()
            }

            pub fn insert(&mut self, key: u64, value: V) -> Option<V> {
                todo!()
            }

            pub fn get(&self, key: u64) -> Option<&V> {
                todo!()
            }

            pub fn remove(&mut self, key: u64) -> Option<V> {
                todo!()
            }

            pub fn len(&self) -> usize {
                todo!()
            }
        }
    """,
    solution="""
        enum Slot<V> {
            Empty,
            Deleted,
            Full(u64, V),
        }

        pub struct OpenMap<V> {
            slots: Vec<Slot<V>>,
            len: usize,
            /// Full plus Deleted slots: what probe chains have to walk past.
            used: usize,
        }

        impl<V> OpenMap<V> {
            pub fn new() -> Self {
                Self::with_slots(8)
            }

            fn with_slots(n: usize) -> Self {
                OpenMap { slots: (0..n).map(|_| Slot::Empty).collect(), len: 0, used: 0 }
            }

            /// Fibonacci hashing: multiply, then take the high bits.
            fn home(&self, key: u64) -> usize {
                let bits = self.slots.len().trailing_zeros();
                (key.wrapping_mul(0x9E37_79B9_7F4A_7C15) >> (64 - bits)) as usize
            }

            fn find(&self, key: u64) -> Option<usize> {
                let mask = self.slots.len() - 1;
                let mut i = self.home(key);
                for _ in 0..self.slots.len() {
                    match &self.slots[i] {
                        Slot::Empty => return None,
                        Slot::Full(k, _) if *k == key => return Some(i),
                        _ => i = (i + 1) & mask,
                    }
                }
                None
            }

            pub fn insert(&mut self, key: u64, value: V) -> Option<V> {
                if let Some(i) = self.find(key) {
                    if let Slot::Full(_, v) = &mut self.slots[i] {
                        return Some(std::mem::replace(v, value));
                    }
                }
                if (self.used + 1) * 4 > self.slots.len() * 3 {
                    self.grow();
                }
                let mask = self.slots.len() - 1;
                let mut i = self.home(key);
                // The key isn't present, so the first Empty or Deleted slot is where it goes.
                while let Slot::Full(..) = self.slots[i] {
                    i = (i + 1) & mask;
                }
                if let Slot::Empty = self.slots[i] {
                    self.used += 1;
                }
                self.slots[i] = Slot::Full(key, value);
                self.len += 1;
                None
            }

            pub fn get(&self, key: u64) -> Option<&V> {
                match &self.slots[self.find(key)?] {
                    Slot::Full(_, v) => Some(v),
                    _ => None,
                }
            }

            pub fn remove(&mut self, key: u64) -> Option<V> {
                let i = self.find(key)?;
                // A tombstone, not Empty: later keys in this probe chain must stay reachable.
                match std::mem::replace(&mut self.slots[i], Slot::Deleted) {
                    Slot::Full(_, v) => {
                        self.len -= 1;
                        Some(v)
                    }
                    _ => None,
                }
            }

            pub fn len(&self) -> usize {
                self.len
            }

            pub fn is_empty(&self) -> bool {
                self.len == 0
            }

            fn grow(&mut self) {
                let old = std::mem::replace(self, Self::with_slots(self.slots.len() * 2));
                for slot in old.slots {
                    if let Slot::Full(k, v) = slot {
                        self.insert(k, v);
                    }
                }
            }
        }

        impl<V> Default for OpenMap<V> {
            fn default() -> Self {
                Self::new()
            }
        }
    """,
    visible=[
        T("insert_get", "insert 1 → \"a\", 2 → \"b\"", '{ let mut m = OpenMap::new(); m.insert(1, "a"); m.insert(2, "b"); (m.get(1).copied(), m.get(3).copied(), m.len()) }', '(Some("a"), None, 2)'),
        T("replace", "insert 7 → 1 then 7 → 2", "{ let mut m = OpenMap::new(); let first = m.insert(7, 1); let second = m.insert(7, 2); (first, second, m.get(7).copied(), m.len()) }", "(None, Some(1), Some(2), 1)"),
        T("remove", "insert 5, remove 5", "{ let mut m = OpenMap::new(); m.insert(5, 'x'); (m.remove(5), m.get(5).copied(), m.remove(5), m.len()) }", "(Some('x'), None, None, 0)"),
    ],
    hidden=[
        """
        #[test]
        fn ten_thousand_keys_survive_resizes() {
            let mut m = OpenMap::new();
            for k in 0..10_000u64 {
                m.insert(k * 7919, k);
            }
            let all_found = (0..10_000u64).all(|k| m.get(k * 7919) == Some(&k));
            check!("insert 10000 keys", (m.len(), all_found), (10_000, true));
        }

        #[test]
        fn remove_keeps_probe_chains_intact() {
            let mut m = OpenMap::new();
            for k in 0..100u64 {
                m.insert(k, k);
            }
            for k in (0..100u64).step_by(2) {
                m.remove(k);
            }
            let odd_found = (1..100u64).step_by(2).all(|k| m.get(k) == Some(&k));
            let even_gone = (0..100u64).step_by(2).all(|k| m.get(k).is_none());
            check!("insert 0..100, remove the even keys", (m.len(), odd_found, even_gone), (50, true, true));
        }

        #[test]
        fn churn_reuses_tombstones() {
            let mut m = OpenMap::new();
            for round in 0..1000u64 {
                m.insert(round, round);
                m.remove(round);
            }
            m.insert(42, 1);
            check!("1000 insert/remove rounds", (m.len(), m.get(42).copied()), (1, Some(1)));
        }
        """,
    ],
    hints=[("approach", "A key lives at its home slot or further along; a lookup stops at the first Empty slot."),
           ("approach", "Removing by writing Empty would cut the chain for keys that probed past it. Write a tombstone instead."),
           ("rust", "`std::mem::replace(self, Self::with_slots(2 * n))` hands you the old table to reinsert from.")],
    notes=("Lookups skip tombstones; inserts reuse them. Counting tombstones toward the load factor stops a table full of tombstones from making every miss scan everything. Resizing drops the tombstones.", "O(1) expected", "O(n)"),
    follow_up="How does Robin Hood hashing or backward-shift deletion avoid tombstones?",
    related=["D14", "S8"],
))

P.append(dict(
    slug="interval-map", title="An interval map on BTreeMap", level="hard", stage="build-it", tags=["BTreeMap::range", "intervals"],
    teaches=["Keying intervals by their start makes point lookup a floor query.", "Returning the value back in `Err` when an insert is refused."],
    statement="""
        `IntervalMap<V>` stores non-overlapping half-open intervals `[start, end)`. `insert` refuses empty
        or overlapping intervals and hands the value back in `Err`. `get(point)` returns the value of the
        interval containing `point`.
    """,
    starter="""
        use std::collections::BTreeMap;

        pub struct IntervalMap<V> {
            /// start → (end, value)
            by_start: BTreeMap<u32, (u32, V)>,
        }

        impl<V> IntervalMap<V> {
            pub fn new() -> Self {
                todo!()
            }

            pub fn insert(&mut self, start: u32, end: u32, value: V) -> Result<(), V> {
                todo!()
            }

            pub fn get(&self, point: u32) -> Option<&V> {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::BTreeMap;

        pub struct IntervalMap<V> {
            /// start → (end, value)
            by_start: BTreeMap<u32, (u32, V)>,
        }

        impl<V> IntervalMap<V> {
            pub fn new() -> Self {
                IntervalMap { by_start: BTreeMap::new() }
            }

            pub fn insert(&mut self, start: u32, end: u32, value: V) -> Result<(), V> {
                if start >= end {
                    return Err(value);
                }
                let before_overlaps = self.by_start.range(..=start).next_back().is_some_and(|(_, (e, _))| *e > start);
                let after_overlaps = self.by_start.range(start..).next().is_some_and(|(s, _)| *s < end);
                if before_overlaps || after_overlaps {
                    return Err(value);
                }
                self.by_start.insert(start, (end, value));
                Ok(())
            }

            pub fn get(&self, point: u32) -> Option<&V> {
                self.by_start
                    .range(..=point)
                    .next_back()
                    .filter(|(_, (end, _))| point < *end)
                    .map(|(_, (_, v))| v)
            }
        }

        impl<V> Default for IntervalMap<V> {
            fn default() -> Self {
                Self::new()
            }
        }
    """,
    visible=[
        T("lookup", "[0, 10) → \"a\", [20, 30) → \"b\"", '{ let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(20, 30, "b").unwrap(); (m.get(5).copied(), m.get(10).copied(), m.get(25).copied()) }', '(Some("a"), None, Some("b"))'),
        T("overlap_refused", "[0, 10) then [5, 15)", '{ let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(5, 15, "b") }', 'Err("b")'),
    ],
    hidden=[
        T("touching_allowed", "[0, 10) then [10, 20)", '{ let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); (m.insert(10, 20, 2), m.get(10).copied()) }', "(Ok(()), Some(2))"),
        T("contains_existing", "[5, 6) then [0, 100)", '{ let mut m = IntervalMap::new(); m.insert(5, 6, 1).unwrap(); m.insert(0, 100, 2) }', "Err(2)"),
        T("empty_interval", "[3, 3)", "IntervalMap::new().insert(3, 3, 'x')", "Err('x')"),
    ],
    hints=[("approach", "An interval containing `point` must be the one with the largest start ≤ point."),
           ("approach", "A new interval overlaps only if its predecessor ends after `start` or its successor starts before `end`.")],
    notes=("Two neighbour checks are enough because the stored intervals never overlap each other. `Err(value)` gives ownership back so the caller can retry without cloning.", "O(log n)", "O(n)"),
    follow_up="How would you support overlapping intervals and 'all intervals containing x'?",
    related=["D8", "D14"],
))

STAGES = [("use-it", "Use it", "easy"), ("understand-it", "Understand it", "medium"), ("build-it", "Build it", "hard")]

if __name__ == "__main__":
    n = write_track("s4-maps-sets", "S4", "Maps & sets", "S", "core", 4,
                    "HashMap, HashSet, BTreeMap and BTreeSet: the entry API, ranges, Hash/Eq contracts, and a hash map from scratch.",
                    STAGES, P)
    print("S4", n)
