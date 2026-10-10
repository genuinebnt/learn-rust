# Trie patterns: the exhaustive target list

The target list for the Tries topic (drafted 2026-10-10, same shape as [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md)), as the target for the Tries pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (array children / hash-map children) are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/tries.toml` has 3 techniques (trie, trie-dfs, trie-grid), each with one Python template and no tabs. Building the rest needs a mockup of the tabs first (rule 13), then lessons and picked example problems. Example problems below come only from `content/dsa/problems.json` and `content/dsa/practice.json`; a pattern with none there says so and needs one picked and checked against LeetCode, never from memory.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "array children / hash-map children"). Items are labelled (a), (b), ... so the example list below can point at them (pattern 3d is group 3, item d).

1. **Basic trie.** (a) Insert / search / startsWith with one node per letter, and one walk helper that search and startsWith share; (b) Array children (26 slots, fixed alphabet) / hash-map children (any alphabet, sparse); (c) End-of-word flag / the whole word stored at its end node / a count of words ending here (a multiset with erase); (d) A trie over a larger alphabet: path segments, digits, or whole words as the symbols.

2. **Wildcards and approximate matching (DFS through the trie).** (a) '.' wildcard: branch over every child at a wildcard, walk plainly elsewhere; (b) One wrong letter / at most k edits: carry an edit budget down the walk; (c) Glob patterns ('*' for any run, '?' for one letter): a skip-or-consume branch at each star; (d) Prefix-and-suffix queries: a forward and a reversed trie / one trie over 'suffix#word' keys / a hash map of every prefix-suffix pair; (e) Spell correction: an edit-distance row carried per node while walking (trie with a Levenshtein DP).

3. **Prefix counting, sums and autocomplete (counts on nodes, top-k at nodes).** (a) Words passing through a node / words ending at a node, kept as counts; (b) Sum of the counts along each word's path (prefix scores of every word); (c) Key-value sums by prefix: the value sits on the end node, an overwrite applies the difference along the path; (d) Autocomplete: collect every word under the prefix node (DFS) / keep the best k at each node / sorted array with binary search (search suggestions); (e) Lexicographic order: DFS in letter order / k-th word by subtree counts / an implicit trie over numbers.

4. **Word search on a grid with a trie (pruning).** (a) Many words on a grid: one backtracking DFS walking the trie alongside the board; (b) Pruning: step only where the trie has a child / clear the stored word when found / delete exhausted branches; (c) One word on a grid needs no trie (the contrast case: plain backtracking); (d) Dictionary-driven backtracking: word squares, crosswords, boggle, where each next row must match a prefix.

5. **Longest word, shortest root and common prefixes.** (a) Shortest root replacement: stop at the first end marker on the walk; (b) Longest word built one letter at a time: DFS only through end nodes / sort and keep a set of built words; (c) Suffix questions with a reversed trie: short encoding of words / longest common suffix with a best answer stored per node; (d) Sub-folders and sub-paths: keep only paths with no marked ancestor (trie / sort and compare neighbours); (e) Longest common prefix of a whole set: walk while a node has one child and no word ends; (f) Shortest unique prefix / abbreviation per word: walk until the pass count is one; (g) Shortest substring found in no other word: insert the substrings of the others and probe; (h) Greedy segmentation by a trie of segments seen so far (cut when the segment is new).

6. **XOR with a binary trie.** (a) Maximum XOR of a pair: for each number take the opposite bit at every level when it exists; (b) Maximum XOR with an element not above a bound: queries sorted by bound, insert while sweeping / keep the smallest value at each node; (c) Count pairs with XOR below a limit: pass counts on nodes and a walk against the limit's bits; (d) Maximum XOR subarray: insert the prefix XORs as you go; (e) XOR queries over a range or a tree path: a persistent binary trie with a count per version; (f) Binary strings as trie paths: substring values, all codes of length k present (count full-depth leaves).

7. **Deleting from a trie and trie updates.** (a) Delete a word: unmark it, then prune childless nodes on the way back (recursive / iterative with a path stack); (b) Reference counts: decrement along the path, drop a node when its count reaches zero (erase in a multiset trie); (c) A sliding window or multiset of numbers in a binary trie: insert and remove with counts; (d) Prune exhausted nodes during a search so that later searches skip them; (e) Overwrite a key's value: apply the difference along the path.

8. **Compressed trie, radix tree and relatives.** (a) Radix tree: edges labelled with strings, split an edge on insert, merge on delete; (b) Patricia trie: a binary radix tree over bit strings (keys with one child skipped); (c) Ternary search tree: a small binary search tree per level, less memory than child arrays; (d) DAWG / minimal automaton: share equal suffixes of a built trie; (e) Longest-prefix match: an IP routing table (CIDR) on a binary trie; (f) Memory layouts: double-array trie, succinct (LOUDS) tries, flat arrays of node ids.

9. **Suffix structures (cross-reference to string algorithms).** (a) Suffix trie / suffix tree (Ukkonen): every substring of a text in one structure; (b) Suffix automaton: distinct substrings, occurrence counts, longest common substring; (c) Suffix array with an LCP array (Kasai): repeated substrings, k-th substring, binary search on a pattern; (d) Longest repeated substring: suffix array and LCP / binary search on the length with a rolling hash / suffix automaton; (e) Longest common substring of two or more strings: generalized suffix structure / DP / binary search with hashing; (f) The linear-time matchers that are not tries but sit beside them: KMP / Z-function / Manacher / rolling hash; (g) Palindromic tree (eertree): one node per distinct palindrome of a string.

10. **Aho-Corasick multi-pattern matching.** (a) Build: a trie of the patterns, then failure links by BFS; (b) Output (dictionary) links: report every pattern that ends at the current state; (c) Precomputed transitions (a full goto function) so each text character costs O(1); (d) Match positions to intervals: mark every matched span (bold tags), count occurrences per pattern; (e) Aho-Corasick with DP: count strings of length n that avoid every forbidden pattern; (f) Online matching on a character stream: the automaton state / a reversed trie of the words; (g) Many words against one text: advance one walker per word / bucket words by the next letter needed / a trie of the words.

11. **Trie with DP (word break and its cousins).** (a) Word break: dp over positions, enumerate the words starting at i by walking a trie; (b) Fewest leftover characters: dp[i] is the best of skipping a letter or taking a word; (c) Word break II: enumerate all splits with a trie and memoise by index; (d) Concatenated words: word break of each word against the others (insert shortest first, test before inserting); (e) Ways to form a target from a dictionary: counts per column / per position over the words; (f) DP over trie nodes: count numbers or strings by walking the trie as the state (digit trie, automaton state); (g) A trie of rewrite rules combined with shortest paths and a DP over the string.

12. **Palindrome pairs and pairs of words.** (a) Palindrome pairs: a trie of reversed words with the 'rest is a palindrome' indexes kept on nodes; (b) Palindrome pairs: split every word at each position and look the halves up in a hash map; (c) Prefix-and-suffix pairs: a trie over (prefix letter, suffix letter) pairs / a hash of both ends; (d) Palindromic prefix of a word (shortest palindrome): KMP failure table / rolling hash.

13. **Design problems.** (a) Autocomplete and search suggestions: ranked results under a prefix, with history updates; (b) File system: a trie over path segments (create with a parent check, ls, mkdir, add and read content); (c) Stream of characters: a reversed trie of the words with a buffer of the last max-length characters / Aho-Corasick; (d) Encrypt and decrypt: precompute the dictionary's encryptions and count / a trie keyed by the cipher; (e) Key-value map with prefix sums; (f) Word filter by prefix and suffix, with a weight per word; (g) Dictionary classes: add a word, then query (wildcard or one-edit); (h) Phone directory, T9 and routing tables: a trie over digit sequences or address bits.

14. **Trie versus hash set, sorting and hashing (trade-offs).** (a) Prefix queries: a trie / a sorted array with binary search / a hash set of every prefix; (b) Exact membership only: a hash set (with a maximum word length) is simpler and faster; (c) Drop words that are prefixes or suffixes of others: a set minus suffixes / sort and compare neighbours instead of a trie; (d) Sort first, then compare only neighbours (longest common prefix, sub-folders, longest word); (e) Hashing prefixes instead of building nodes (rolling hash): less memory, a collision risk.

15. **Core implementation patterns.** (a) Node as a dict / a small class / parallel arrays indexed by node id (flat arrays for large inputs, an arena `Vec` with indices in Rust); (b) End marker: a reserved key such as '$' / a boolean / the stored word; keep reserved symbols out of the alphabet; (c) Recursive / iterative traversal; recursion depth on long words and deep tries; (d) Per-node aggregates: pass count, end count, best result, smallest index; updated on insert; (e) Child order for lexicographic output: sorted children / a fixed letter order; (f) Build order and cost: O(total characters); insertion order matters when a word is tested before it is added; (g) Reversed-key tries: insert words reversed for suffix questions.

## Coverage today

`content/dsa/lessons/tries.toml` holds three techniques, each with signals, one Python template (nested dicts with a `"$"` end marker) and three pitfalls. None has variant tabs.

| Technique today | Target patterns it covers | What it lacks |
|---|---|---|
| `Tries:trie` | 1a, 1c (flag only), 15b | no array-children tab (1b), no counts or stored word (1c, 3a), no prefix aggregates |
| `Tries:trie-dfs` | 2a | no edit budget (2b), no prefix-and-suffix keys (2d); the data also files binary-trie XOR (421) and longest word (720) here |
| `Tries:trie-grid` | 4a, 4b, 7d | the data also files non-grid problems here: short encoding (820), edits (2452), uncommon substring (3076), encrypt and decrypt (2227) |

Groups with no lesson at all today: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14; groups 3 and 15 are touched only by the basic template. Of the 88 patterns, 62 have at least one problem in the data and 26 have none.

Trie problems in the data (LeetCode tag Trie or pattern Tries; 38 distinct problems):

- 24 have the pattern Tries, all in techniques `trie`, `trie-dfs` and `trie-grid`. (One problem filed elsewhere, 3043 Find the Length of the Longest Common Prefix, also uses the `Tries:trie` technique.)
- 14 carry the Trie tag but belong to another pattern: Word Break and Concatenated Words (1-D DP), Word Break II (Backtracking), Longest Common Prefix and Find the Length of the Longest Common Prefix (Arrays & Hashing), Search Suggestions System (Binary Search), Add Bold Tag in String (Intervals), the lexicographic pair (Math & Geometry), Palindrome Pairs and Top K Frequent Words (Arrays & Hashing), and a few more in Advanced Graphs, 1-D DP and Bit Manipulation.
- Lists: 4 in the NeetCode 150 (Implement Trie, Design Add and Search Words, Word Search II, Word Break), 7 in the NeetCode 250, 17 in the Practice list, the rest only in All.

## Example problems per pattern

Format: `LeetCode <number> <title> (<difficulty>; <lists>)`, up to 4 per pattern, only problems present in the data files. Some fits are loose (marked in Gaps). Premium problems are in the data too, see Gaps.

### 1. Basic trie

- **1a.** Insert / search / startsWith with one node per letter, and one walk helper that search and startsWith share
    - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2185 Counting Words With a Given Prefix (easy; all)
- **1b.** Array children (26 slots, fixed alphabet) / hash-map children (any alphabet, sparse)
    - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 211 Design Add and Search Words Data Structure (medium; blind75, neetcode150, neetcode250, all)
- **1c.** End-of-word flag / the whole word stored at its end node / a count of words ending here (a multiset with erase)
    - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 677 Map Sum Pairs (medium; practice)
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **1d.** A trie over a larger alphabet: path segments, digits, or whole words as the symbols
    - LeetCode 1166 Design File System (medium; all)
    - LeetCode 1233 Remove Sub-Folders from the Filesystem (medium; all)
    - LeetCode 588 Design In-Memory File System (hard; all)

### 2. Wildcards and approximate matching (DFS through the trie)

- **2a.** '.' wildcard: branch over every child at a wildcard, walk plainly elsewhere
    - LeetCode 211 Design Add and Search Words Data Structure (medium; blind75, neetcode150, neetcode250, all)
- **2b.** One wrong letter / at most k edits: carry an edit budget down the walk
    - LeetCode 676 Implement Magic Dictionary (medium; practice)
    - LeetCode 2452 Words Within Two Edits of Dictionary (medium; practice)
- **2c.** Glob patterns ('*' for any run, '?' for one letter): a skip-or-consume branch at each star
    - no problem in the data: needs one from LeetCode
- **2d.** Prefix-and-suffix queries: a forward and a reversed trie / one trie over 'suffix#word' keys / a hash map of every prefix-suffix pair
    - LeetCode 745 Prefix and Suffix Search (hard; practice)
- **2e.** Spell correction: an edit-distance row carried per node while walking (trie with a Levenshtein DP)
    - no problem in the data: needs one from LeetCode

### 3. Prefix counting, sums and autocomplete (counts on nodes, top-k at nodes)

- **3a.** Words passing through a node / words ending at a node, kept as counts
    - LeetCode 2185 Counting Words With a Given Prefix (easy; all)
    - LeetCode 3043 Find the Length of the Longest Common Prefix (medium; all)
- **3b.** Sum of the counts along each word's path (prefix scores of every word)
    - LeetCode 2416 Sum of Prefix Scores of Strings (hard; all)
- **3c.** Key-value sums by prefix: the value sits on the end node, an overwrite applies the difference along the path
    - LeetCode 677 Map Sum Pairs (medium; practice)
- **3d.** Autocomplete: collect every word under the prefix node (DFS) / keep the best k at each node / sorted array with binary search (search suggestions)
    - LeetCode 642 Design Search Autocomplete System (hard; all)
    - LeetCode 1268 Search Suggestions System (medium; all)
    - LeetCode 692 Top K Frequent Words (medium; practice)
- **3e.** Lexicographic order: DFS in letter order / k-th word by subtree counts / an implicit trie over numbers
    - LeetCode 386 Lexicographical Numbers (medium; all)
    - LeetCode 440 K-th Smallest in Lexicographical Order (hard; all)

### 4. Word search on a grid with a trie (pruning)

- **4a.** Many words on a grid: one backtracking DFS walking the trie alongside the board
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **4b.** Pruning: step only where the trie has a child / clear the stored word when found / delete exhausted branches
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **4c.** One word on a grid needs no trie (the contrast case: plain backtracking)
    - LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)
- **4d.** Dictionary-driven backtracking: word squares, crosswords, boggle, where each next row must match a prefix
    - no problem in the data: needs one from LeetCode

### 5. Longest word, shortest root and common prefixes

- **5a.** Shortest root replacement: stop at the first end marker on the walk
    - LeetCode 648 Replace Words (medium; practice)
- **5b.** Longest word built one letter at a time: DFS only through end nodes / sort and keep a set of built words
    - LeetCode 720 Longest Word in Dictionary (medium; practice)
- **5c.** Suffix questions with a reversed trie: short encoding of words / longest common suffix with a best answer stored per node
    - LeetCode 820 Short Encoding of Words (medium; practice)
    - LeetCode 3093 Longest Common Suffix Queries (hard; practice)
- **5d.** Sub-folders and sub-paths: keep only paths with no marked ancestor (trie / sort and compare neighbours)
    - LeetCode 1233 Remove Sub-Folders from the Filesystem (medium; all)
- **5e.** Longest common prefix of a whole set: walk while a node has one child and no word ends
    - LeetCode 14 Longest Common Prefix (easy; neetcode250, all)
- **5f.** Shortest unique prefix / abbreviation per word: walk until the pass count is one
    - no problem in the data: needs one from LeetCode
- **5g.** Shortest substring found in no other word: insert the substrings of the others and probe
    - LeetCode 3076 Shortest Uncommon Substring in an Array (medium; practice)
- **5h.** Greedy segmentation by a trie of segments seen so far (cut when the segment is new)
    - LeetCode 3597 Partition String (medium; practice)

### 6. XOR with a binary trie

- **6a.** Maximum XOR of a pair: for each number take the opposite bit at every level when it exists
    - LeetCode 421 Maximum XOR of Two Numbers in an Array (medium; practice)
- **6b.** Maximum XOR with an element not above a bound: queries sorted by bound, insert while sweeping / keep the smallest value at each node
    - LeetCode 1707 Maximum XOR With an Element From Array (hard; practice)
- **6c.** Count pairs with XOR below a limit: pass counts on nodes and a walk against the limit's bits
    - no problem in the data: needs one from LeetCode
- **6d.** Maximum XOR subarray: insert the prefix XORs as you go
    - no problem in the data: needs one from LeetCode
- **6e.** XOR queries over a range or a tree path: a persistent binary trie with a count per version
    - no problem in the data: needs one from LeetCode
- **6f.** Binary strings as trie paths: substring values, all codes of length k present (count full-depth leaves)
    - LeetCode 2564 Substring XOR Queries (medium; practice)
    - LeetCode 1461 Check If a String Contains All Binary Codes of Size K (medium; all)

### 7. Deleting from a trie and trie updates

- **7a.** Delete a word: unmark it, then prune childless nodes on the way back (recursive / iterative with a path stack)
    - no problem in the data: needs one from LeetCode
- **7b.** Reference counts: decrement along the path, drop a node when its count reaches zero (erase in a multiset trie)
    - no problem in the data: needs one from LeetCode
- **7c.** A sliding window or multiset of numbers in a binary trie: insert and remove with counts
    - no problem in the data: needs one from LeetCode
- **7d.** Prune exhausted nodes during a search so that later searches skip them
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **7e.** Overwrite a key's value: apply the difference along the path
    - LeetCode 677 Map Sum Pairs (medium; practice)

### 8. Compressed trie, radix tree and relatives

- **8a.** Radix tree: edges labelled with strings, split an edge on insert, merge on delete
    - no problem in the data: needs one from LeetCode
- **8b.** Patricia trie: a binary radix tree over bit strings (keys with one child skipped)
    - no problem in the data: needs one from LeetCode
- **8c.** Ternary search tree: a small binary search tree per level, less memory than child arrays
    - no problem in the data: needs one from LeetCode
- **8d.** DAWG / minimal automaton: share equal suffixes of a built trie
    - no problem in the data: needs one from LeetCode
- **8e.** Longest-prefix match: an IP routing table (CIDR) on a binary trie
    - no problem in the data: needs one from LeetCode
- **8f.** Memory layouts: double-array trie, succinct (LOUDS) tries, flat arrays of node ids
    - no problem in the data: needs one from LeetCode

### 9. Suffix structures (cross-reference to string algorithms)

- **9a.** Suffix trie / suffix tree (Ukkonen): every substring of a text in one structure
    - no problem in the data: needs one from LeetCode
- **9b.** Suffix automaton: distinct substrings, occurrence counts, longest common substring
    - no problem in the data: needs one from LeetCode
- **9c.** Suffix array with an LCP array (Kasai): repeated substrings, k-th substring, binary search on a pattern
    - no problem in the data: needs one from LeetCode
- **9d.** Longest repeated substring: suffix array and LCP / binary search on the length with a rolling hash / suffix automaton
    - LeetCode 187 Repeated DNA Sequences (medium; all)
- **9e.** Longest common substring of two or more strings: generalized suffix structure / DP / binary search with hashing
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)
    - LeetCode 3076 Shortest Uncommon Substring in an Array (medium; practice)
- **9f.** The linear-time matchers that are not tries but sit beside them: KMP / Z-function / Manacher / rolling hash
    - LeetCode 28 Find the Index of the First Occurrence in a String (easy; all)
    - LeetCode 459 Repeated Substring Pattern (easy; practice)
    - LeetCode 5 Longest Palindromic Substring (medium; blind75, neetcode150, neetcode250, all)
- **9g.** Palindromic tree (eertree): one node per distinct palindrome of a string
    - no problem in the data: needs one from LeetCode

### 10. Aho-Corasick multi-pattern matching

- **10a.** Build: a trie of the patterns, then failure links by BFS
    - LeetCode 616 Add Bold Tag in String (medium; all)
- **10b.** Output (dictionary) links: report every pattern that ends at the current state
    - LeetCode 616 Add Bold Tag in String (medium; all)
- **10c.** Precomputed transitions (a full goto function) so each text character costs O(1)
    - no problem in the data: needs one from LeetCode
- **10d.** Match positions to intervals: mark every matched span (bold tags), count occurrences per pattern
    - LeetCode 616 Add Bold Tag in String (medium; all)
- **10e.** Aho-Corasick with DP: count strings of length n that avoid every forbidden pattern
    - no problem in the data: needs one from LeetCode
- **10f.** Online matching on a character stream: the automaton state / a reversed trie of the words
    - no problem in the data: needs one from LeetCode
- **10g.** Many words against one text: advance one walker per word / bucket words by the next letter needed / a trie of the words
    - LeetCode 792 Number of Matching Subsequences (medium; practice)
    - LeetCode 1408 String Matching in an Array (easy; all)
    - LeetCode 30 Substring with Concatenation of All Words (hard; practice)

### 11. Trie with DP (word break and its cousins)

- **11a.** Word break: dp over positions, enumerate the words starting at i by walking a trie
    - LeetCode 139 Word Break (medium; blind75, neetcode150, neetcode250, all)
- **11b.** Fewest leftover characters: dp[i] is the best of skipping a letter or taking a word
    - LeetCode 2707 Extra Characters in a String (medium; neetcode250, all)
- **11c.** Word break II: enumerate all splits with a trie and memoise by index
    - LeetCode 140 Word Break II (hard; neetcode250, all)
- **11d.** Concatenated words: word break of each word against the others (insert shortest first, test before inserting)
    - LeetCode 472 Concatenated Words (hard; all)
- **11e.** Ways to form a target from a dictionary: counts per column / per position over the words
    - LeetCode 1639 Number of Ways to Form a Target String Given a Dictionary (hard; all)
- **11f.** DP over trie nodes: count numbers or strings by walking the trie as the state (digit trie, automaton state)
    - no problem in the data: needs one from LeetCode
- **11g.** A trie of rewrite rules combined with shortest paths and a DP over the string
    - LeetCode 2977 Minimum Cost to Convert String II (hard; practice)

### 12. Palindrome pairs and pairs of words

- **12a.** Palindrome pairs: a trie of reversed words with the 'rest is a palindrome' indexes kept on nodes
    - LeetCode 336 Palindrome Pairs (hard; practice)
- **12b.** Palindrome pairs: split every word at each position and look the halves up in a hash map
    - LeetCode 336 Palindrome Pairs (hard; practice)
- **12c.** Prefix-and-suffix pairs: a trie over (prefix letter, suffix letter) pairs / a hash of both ends
    - LeetCode 3042 Count Prefix and Suffix Pairs I (easy; all)
    - LeetCode 3045 Count Prefix and Suffix Pairs II (hard; all)
- **12d.** Palindromic prefix of a word (shortest palindrome): KMP failure table / rolling hash
    - LeetCode 214 Shortest Palindrome (hard; all)

### 13. Design problems

- **13a.** Autocomplete and search suggestions: ranked results under a prefix, with history updates
    - LeetCode 642 Design Search Autocomplete System (hard; all)
    - LeetCode 1268 Search Suggestions System (medium; all)
- **13b.** File system: a trie over path segments (create with a parent check, ls, mkdir, add and read content)
    - LeetCode 1166 Design File System (medium; all)
    - LeetCode 588 Design In-Memory File System (hard; all)
- **13c.** Stream of characters: a reversed trie of the words with a buffer of the last max-length characters / Aho-Corasick
    - no problem in the data: needs one from LeetCode
- **13d.** Encrypt and decrypt: precompute the dictionary's encryptions and count / a trie keyed by the cipher
    - LeetCode 2227 Encrypt and Decrypt Strings (hard; practice)
- **13e.** Key-value map with prefix sums
    - LeetCode 677 Map Sum Pairs (medium; practice)
- **13f.** Word filter by prefix and suffix, with a weight per word
    - LeetCode 745 Prefix and Suffix Search (hard; practice)
- **13g.** Dictionary classes: add a word, then query (wildcard or one-edit)
    - LeetCode 211 Design Add and Search Words Data Structure (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 676 Implement Magic Dictionary (medium; practice)
- **13h.** Phone directory, T9 and routing tables: a trie over digit sequences or address bits
    - no problem in the data: needs one from LeetCode

### 14. Trie versus hash set, sorting and hashing (trade-offs)

- **14a.** Prefix queries: a trie / a sorted array with binary search / a hash set of every prefix
    - LeetCode 1268 Search Suggestions System (medium; all)
    - LeetCode 2185 Counting Words With a Given Prefix (easy; all)
    - LeetCode 3043 Find the Length of the Longest Common Prefix (medium; all)
- **14b.** Exact membership only: a hash set (with a maximum word length) is simpler and faster
    - LeetCode 139 Word Break (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2707 Extra Characters in a String (medium; neetcode250, all)
- **14c.** Drop words that are prefixes or suffixes of others: a set minus suffixes / sort and compare neighbours instead of a trie
    - LeetCode 820 Short Encoding of Words (medium; practice)
    - LeetCode 1233 Remove Sub-Folders from the Filesystem (medium; all)
- **14d.** Sort first, then compare only neighbours (longest common prefix, sub-folders, longest word)
    - LeetCode 14 Longest Common Prefix (easy; neetcode250, all)
    - LeetCode 1233 Remove Sub-Folders from the Filesystem (medium; all)
    - LeetCode 720 Longest Word in Dictionary (medium; practice)
- **14e.** Hashing prefixes instead of building nodes (rolling hash): less memory, a collision risk
    - LeetCode 3042 Count Prefix and Suffix Pairs I (easy; all)
    - LeetCode 3045 Count Prefix and Suffix Pairs II (hard; all)
    - LeetCode 3043 Find the Length of the Longest Common Prefix (medium; all)

### 15. Core implementation patterns

- **15a.** Node as a dict / a small class / parallel arrays indexed by node id (flat arrays for large inputs, an arena `Vec` with indices in Rust)
    - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2416 Sum of Prefix Scores of Strings (hard; all)
    - LeetCode 3045 Count Prefix and Suffix Pairs II (hard; all)
- **15b.** End marker: a reserved key such as '$' / a boolean / the stored word; keep reserved symbols out of the alphabet
    - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **15c.** Recursive / iterative traversal; recursion depth on long words and deep tries
    - LeetCode 211 Design Add and Search Words Data Structure (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
- **15d.** Per-node aggregates: pass count, end count, best result, smallest index; updated on insert
    - LeetCode 2416 Sum of Prefix Scores of Strings (hard; all)
    - LeetCode 3093 Longest Common Suffix Queries (hard; practice)
    - LeetCode 642 Design Search Autocomplete System (hard; all)
- **15e.** Child order for lexicographic output: sorted children / a fixed letter order
    - LeetCode 386 Lexicographical Numbers (medium; all)
    - LeetCode 720 Longest Word in Dictionary (medium; practice)
- **15f.** Build order and cost: O(total characters); insertion order matters when a word is tested before it is added
    - LeetCode 472 Concatenated Words (hard; all)
    - LeetCode 720 Longest Word in Dictionary (medium; practice)
- **15g.** Reversed-key tries: insert words reversed for suffix questions
    - LeetCode 820 Short Encoding of Words (medium; practice)
    - LeetCode 3093 Longest Common Suffix Queries (hard; practice)

## Gaps

**Patterns with no problem in the data** (26 of 88): 2c, 2e, 4d, 5f, 6c, 6d, 6e, 7a, 7b, 7c, 8a, 8b, 8c, 8d, 8e, 8f, 9a, 9b, 9c, 9g, 10c, 10e, 10f, 11f, 13c, 13h. Each needs an example (free preferred) picked from LeetCode and checked against it. The ones that matter most for interviews: 2c and 2e (wildcards beyond '.'), 7a and 7b (delete, erase with counts), 6c to 6e (the rest of the XOR family), 10c to 10f (Aho-Corasick beyond the one Premium bold-tag problem), 13c (stream of characters), 4d (word squares) and 6d (maximum XOR subarray). Groups 8 (radix, Patricia, ternary search trees, DAWG) and 9a to 9c, 9g (suffix structures) are mostly interview-rare, so they could stay lesson-only with examples marked as such.

**Loose fits to re-check when examples are picked:**

- Check If a String Contains All Binary Codes of Size K: a set of substrings or a rolling window solves it; a binary trie is one option, not the expected one (6f).
- Repeated DNA Sequences: fixed length 10, so a set or rolling hash suffices; it only shows the 'repeated substring' idea (9d).
- Maximum Length of Repeated Subarray: a DP or binary search with hashing; the suffix automaton fit is theoretical (9e).
- Find the Index of the First Occurrence in a String, Repeated Substring Pattern and Longest Palindromic Substring: string matchers beside tries, listed for the cross-reference only (9f).
- Number of Ways to Form a Target String Given a Dictionary: a DP over columns, no trie (11e).
- Substring with Concatenation of All Words and String Matching in an Array: multi-word matching by sliding window or brute force, no automaton needed (10g).
- Search Suggestions System is usually solved with a sort and binary search (3d, 14a).
- Words Within Two Edits of Dictionary is a brute-force comparison in the usual solution; the trie is optional (2b).
- Remove Sub-Folders from the Filesystem is often sort-and-compare; the trie is one of two answers (5d, 14d).

**Premium problems.** 4 of the trie problems in the data need LeetCode Premium: 616 Add Bold Tag in String, 588 Design In-Memory File System, 642 Design Search Autocomplete System, 1166 Design File System. They are the only examples for 10a, 10b and 10d (Add Bold Tag) and 13b (both file system problems), so a free example should be picked beside them (decision 3 keeps Premium and hides it with a filter).

**Technique assignment in the data is coarse.** Every problem with the pattern Tries is filed under `trie`, `trie-dfs` or `trie-grid`; the practice list therefore groups binary-trie XOR (421, 1707) under `trie-dfs` and non-grid problems (820, 2452, 3076, 2227) under `trie-grid`. When the lessons are split by the groups above, `tools/neetcode/techniques.py` and `assign_rest.py` need new technique ids, and the `PICKS` and `DROP` overrides in `practice.py` need a second pass, so that each new pattern has its own must-learn problem or is marked example-only (decision 32).

**Lesson gaps.**
- Only one Python template per technique and no tabs. Tabs needed first: array children / hash-map children (1b), search / startsWith (1a), recursive / iterative traversal (15c), reversed trie / sort-and-compare (14c, 14d).
- No Rust notes (arena `Vec<Node>` with indices, `Box` children, `HashMap<char, Node>` versus `[Option<usize>; 26]`); the Rust tracks would need them when this topic reaches them (decision 23).
- Cross-topic links to write: Word Break (1-D DP) and Concatenated Words, Word Search II to Backtracking and Graph flood fill, Search Suggestions to Binary Search, Top K Frequent Words to Heap, Maximum XOR to Bit Manipulation, Lexicographical Numbers to Math & Geometry. There is no String algorithms topic in the tracker yet (KMP, Z-function, Manacher, rolling hash, suffix structures), so groups 9 and 10 point at a topic that does not exist.
- The group list is a target for the owner to cut: groups 8 and 9 and parts of 10 and 15 are the first candidates if the topic should stay close to what interviews ask.
