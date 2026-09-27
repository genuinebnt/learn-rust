from author import T, prob, write_track, tag_companies

P = []

# ---------------------------------------------------------------- stack basics (easy)

P.append(prob(
    "valid-parentheses", "Valid parentheses", "easy", "stack-basics", ["stack", "bytes", "Blind 75"],
    """
    `s` contains only `()[]{}`. Return whether every bracket is closed by the same kind of bracket, in the right order.
    """,
    """
    pub fn is_valid(s: &str) -> bool {
        todo!()
    }
    """,
    """
    pub fn is_valid(s: &str) -> bool {
        let mut expected = Vec::new();
        for b in s.bytes() {
            match b {
                b'(' => expected.push(b')'),
                b'[' => expected.push(b']'),
                b'{' => expected.push(b'}'),
                _ => {
                    if expected.pop() != Some(b) {
                        return false;
                    }
                }
            }
        }
        expected.is_empty()
    }
    """,
    [T("mixed", '"()[]{}"', 'is_valid("()[]{}")', "true"),
     T("wrong_kind", '"(]"', 'is_valid("(]")', "false"),
     T("nested", '"{[]}"', 'is_valid("{[]}")', "true"),
     T("one_pair", '"()"', 'is_valid("()")', "true"),
     T("nested_mixed", '"([])"', 'is_valid("([])")', "true"),
     T("interleaved", '"([)]"', 'is_valid("([)]")', "false"),
     T("empty", '""', 'is_valid("")', "true")],
    [T("unclosed", '"(("', 'is_valid("((")', "false"),
     T("close_first", '")"', 'is_valid(")")', "false"),
     T("deep", "10⁵ nested pairs", "is_valid(&s)", "true", setup='let s = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));'),
     T("single_open", '"["', 'is_valid("[")', "false"),
     T("reversed_pair", '")("', 'is_valid(")(")', "false"),
     T("counts_match_order_wrong", '"{(})"', 'is_valid("{(})")', "false"),
     T("extra_closer_at_end", '"(){}}"', 'is_valid("(){}}")', "false"),
     T("long_valid", '"{[()()]}[]"', 'is_valid("{[()()]}[]")', "true"),
     T("odd_length", '"(()"', 'is_valid("(()")', "false"),
     """
     #[test]
     fn random_vs_brute_force() {
         // Brute force: keep deleting adjacent matched pairs; valid iff nothing is left.
         fn brute(s: &str) -> bool {
             let mut s = s.to_string();
             loop {
                 let t = s.replace("()", "").replace("[]", "").replace("{}", "");
                 if t.len() == s.len() {
                     return t.is_empty();
                 }
                 s = t;
             }
         }
         let mut rng = anneal_prelude::Rng::new(3001);
         let pairs = ["()", "[]", "{}"];
         for _ in 0..400 {
             let mut s = String::new();
             let k = rng.below(6);
             for _ in 0..k {
                 // Inserting a matched pair anywhere keeps a valid string valid.
                 let at = rng.below(s.len() / 2 + 1) * 2;
                 let at = at.min(s.len());
                 let p = *rng.pick(&pairs);
                 s.insert_str(at, p);
             }
             if rng.bool() && !s.is_empty() {
                 let i = rng.below(s.len());
                 let c = *rng.pick(&['(', ')', '[', ']', '{', '}']);
                 s.replace_range(i..i + 1, &c.to_string());
             }
             check!(format!("s = {s:?}"), is_valid(&s), brute(&s));
         }
     }

     #[test]
     fn scale_200k_side_by_side() {
         let s = format!("{}{}", "([{".repeat(33_333), "}])".repeat(33_333)) + &"()".repeat(50_000);
         check!("33333 × \\"([{\\", 33333 × \\"}])\\", then 50000 × \\"()\\"", is_valid(&s), true);
     }
     """],
    [("approach", "The most recent unclosed bracket must be the next to close. That's a stack."),
     ("rust", "Push the closer you expect, not the opener; then a close is just `pop() == Some(b)`.")],
    ("Pushing the expected closing byte turns the check into one comparison. `pop()` returning `None` on an extra closer falls out of the same comparison.", "O(n)", "O(n)"),
    "How would you report the position of the first bad bracket?",
    ["`Vec` as a stack: `push` / `pop` / `last`.", "`match` on byte literals."],
    examples=[('"()[]{}"', "true"), ('"([)]"', "false")],
    wrong=dict(
        delete_pairs_until_stable="""
            pub fn is_valid(s: &str) -> bool {
                let mut s = s.to_string();
                loop {
                    let t = s.replace("()", "").replace("[]", "").replace("{}", "");
                    if t.len() == s.len() {
                        return t.is_empty();
                    }
                    s = t;
                }
            }
        """,
        counts_only="""
            pub fn is_valid(s: &str) -> bool {
                let mut open = [0i64; 3];
                for b in s.bytes() {
                    let (i, d) = match b {
                        b'(' => (0, 1),
                        b')' => (0, -1),
                        b'[' => (1, 1),
                        b']' => (1, -1),
                        b'{' => (2, 1),
                        _ => (2, -1),
                    };
                    open[i] += d;
                    if open[i] < 0 {
                        return false;
                    }
                }
                open == [0, 0, 0]
            }
        """,
        ignores_leftovers="""
            pub fn is_valid(s: &str) -> bool {
                let mut expected = Vec::new();
                for b in s.bytes() {
                    match b {
                        b'(' => expected.push(b')'),
                        b'[' => expected.push(b']'),
                        b'{' => expected.push(b'}'),
                        _ => {
                            if expected.pop() != Some(b) {
                                return false;
                            }
                        }
                    }
                }
                true
            }
        """,
    ),
))

QUEUE_WRONG = """
    #[derive(Default)]
    pub struct TwoStackQueue {
        inbox: Vec<i32>,
        outbox: Vec<i32>,
    }

    impl TwoStackQueue {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            self.inbox.push(x);
        }

        fn shift(&mut self) {
            SHIFT
        }

        fn unshift(&mut self) {
            UNSHIFT
        }

        pub fn pop(&mut self) -> Option<i32> {
            self.shift();
            let x = self.outbox.pop();
            self.unshift();
            x
        }

        pub fn peek(&mut self) -> Option<i32> {
            self.shift();
            let x = self.outbox.last().copied();
            self.unshift();
            x
        }

        pub fn len(&self) -> usize {
            self.inbox.len() + self.outbox.len()
        }

        pub fn is_empty(&self) -> bool {
            self.len() == 0
        }
    }
"""
P.append(prob(
    "queue-using-stacks", "Queue using two stacks", "easy", "stack-basics", ["amortised O(1)", "drain"],
    """
    Implement a FIFO queue with two `Vec`s used only as stacks (push and pop at the end). Every operation
    must be amortised O(1).
    """,
    """
    #[derive(Default)]
    pub struct TwoStackQueue {
        inbox: Vec<i32>,
        outbox: Vec<i32>,
    }

    impl TwoStackQueue {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            todo!()
        }

        pub fn pop(&mut self) -> Option<i32> {
            todo!()
        }

        /// The front element, without removing it.
        pub fn peek(&mut self) -> Option<i32> {
            todo!()
        }

        pub fn len(&self) -> usize {
            todo!()
        }

        pub fn is_empty(&self) -> bool {
            todo!()
        }
    }
    """,
    """
    #[derive(Default)]
    pub struct TwoStackQueue {
        inbox: Vec<i32>,
        outbox: Vec<i32>,
    }

    impl TwoStackQueue {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            self.inbox.push(x);
        }

        /// Refill the outbox, reversed, only when it's empty: each element moves once.
        fn shift(&mut self) {
            if self.outbox.is_empty() {
                self.outbox.extend(self.inbox.drain(..).rev());
            }
        }

        pub fn pop(&mut self) -> Option<i32> {
            self.shift();
            self.outbox.pop()
        }

        /// The front element, without removing it.
        pub fn peek(&mut self) -> Option<i32> {
            self.shift();
            self.outbox.last().copied()
        }

        pub fn len(&self) -> usize {
            self.inbox.len() + self.outbox.len()
        }

        pub fn is_empty(&self) -> bool {
            self.len() == 0
        }
    }
    """,
    [T("fifo", "push 1, 2; peek, pop; push 3; pop, pop, pop", "(q.peek(), q.pop(), { q.push(3); q.pop() }, q.pop(), q.pop())", "(Some(1), Some(1), Some(2), Some(3), None)",
       setup="let mut q = TwoStackQueue::new();\nq.push(1);\nq.push(2);"),
     T("len", "push 3 values, pop 1", "(q.len(), q.is_empty())", "(2, false)", setup="let mut q = TwoStackQueue::new();\nfor x in [4, 5, 6] {\n    q.push(x);\n}\nq.pop();"),
     T("leetcode_example", "push 1, push 2, peek, pop, empty", "(q.peek(), q.pop(), q.is_empty())", "(Some(1), Some(1), false)",
       setup="let mut q = TwoStackQueue::new();\nq.push(1);\nq.push(2);"),
     T("empty_queue", "new queue", "(q.peek(), q.pop(), q.len(), q.is_empty())", "(None, None, 0, true)", setup="let mut q = TwoStackQueue::new();"),
     T("push_between_pops", "push 1, 2; pop; push 3, 4; pop, pop, pop", "(a, q.pop(), q.pop(), q.pop())", "(Some(1), Some(2), Some(3), Some(4))",
       setup="let mut q = TwoStackQueue::new();\nq.push(1);\nq.push(2);\nlet a = q.pop();\nq.push(3);\nq.push(4);")],
    [T("empty", "new queue", "(q.peek(), q.pop(), q.is_empty())", "(None, None, true)", setup="let mut q = TwoStackQueue::new();"),
     T("million_ops", "10⁶ pushes interleaved with pops", "(last, q.len())", "(Some(499_999), 500_000)",
       setup="let mut q = TwoStackQueue::new();\nlet mut last = None;\nfor i in 0..1_000_000 {\n    q.push(i);\n    if i % 2 == 1 {\n        last = q.pop();\n    }\n}"),
     T("peek_twice", "push 7; peek, peek, len", "(q.peek(), q.peek(), q.len())", "(Some(7), Some(7), 1)", setup="let mut q = TwoStackQueue::new();\nq.push(7);"),
     T("drain_then_reuse", "push 1; pop; pop; push 2; peek", "(q.pop(), q.pop(), { q.push(2); q.peek() }, q.len())", "(Some(1), None, Some(2), 1)", setup="let mut q = TwoStackQueue::new();\nq.push(1);"),
     T("extremes", "push i32::MIN, i32::MAX; pop, pop", "(q.pop(), q.pop())", "(Some(i32::MIN), Some(i32::MAX))", setup="let mut q = TwoStackQueue::new();\nq.push(i32::MIN);\nq.push(i32::MAX);"),
     T("duplicates", "push 5, 5, 6; pop three times", "(q.pop(), q.pop(), q.pop())", "(Some(5), Some(5), Some(6))", setup="let mut q = TwoStackQueue::new();\nfor x in [5, 5, 6] {\n    q.push(x);\n}"),
     T("len_counts_both_stacks", "push 1, 2; peek; push 3", "(q.len(), q.is_empty())", "(3, false)", setup="let mut q = TwoStackQueue::new();\nq.push(1);\nq.push(2);\nq.peek();\nq.push(3);"),
     """
     #[test]
     fn random_vs_vecdeque() {
         let mut rng = anneal_prelude::Rng::new(3002);
         for _ in 0..300 {
             let mut q = TwoStackQueue::new();
             let mut model = std::collections::VecDeque::new();
             let mut log = Vec::new();
             let n = rng.below(20);
             for _ in 0..n {
                 match rng.below(3) {
                     0 => {
                         let x = rng.int(-9, 9) as i32;
                         q.push(x);
                         model.push_back(x);
                         log.push(format!("push {x}"));
                     }
                     1 => {
                         log.push("pop".to_string());
                         check!(log.join(", "), q.pop(), model.pop_front());
                     }
                     _ => {
                         log.push("peek".to_string());
                         check!(log.join(", "), q.peek(), model.front().copied());
                     }
                 }
                 check!(log.join(", "), (q.len(), q.is_empty()), (model.len(), model.is_empty()));
             }
         }
     }

     #[test]
     fn scale_peek_pop_200k() {
         let mut q = TwoStackQueue::new();
         for i in 0..200_000 {
             q.push(i);
         }
         let mut sum = 0i64;
         for _ in 0..100_000 {
             sum += i64::from(q.peek().unwrap_or(0));
             q.pop();
             q.push(-1);
         }
         check!("push 0..200000; then 100000 × (peek, pop, push -1)", (sum, q.len(), q.peek()), (4_999_950_000, 200_000, Some(100_000)));
     }
     """],
    [("approach", "Push onto one stack. Pop from the other; when it's empty, move everything across, which reverses the order."),
     ("rust", "`self.outbox.extend(self.inbox.drain(..).rev())` moves all elements in one call.")],
    ("Each element is pushed and popped at most twice, so n operations cost O(n) in total even though a single `pop` can be O(n).", "O(1) amortised", "O(n)"),
    "Why would `VecDeque` be the better choice in real code?",
    ["Amortised analysis: pay for a move once.", "`drain(..).rev()` into `extend`."],
    related=["S5"],
    wrong=dict(
        move_back_every_time=QUEUE_WRONG.replace("UNSHIFT", "self.inbox.extend(self.outbox.drain(..).rev());").replace("SHIFT", "self.outbox.extend(self.inbox.drain(..).rev());"),
        refill_when_not_empty=QUEUE_WRONG.replace("UNSHIFT", "").replace("SHIFT", "self.outbox.extend(self.inbox.drain(..).rev());"),
        lifo=QUEUE_WRONG.replace("UNSHIFT", "").replace("SHIFT", "").replace("self.outbox.pop()", "self.inbox.pop()").replace("self.outbox.last().copied()", "self.inbox.last().copied()"),
    ),
))

BASEBALL_WRONG = """
    pub fn cal_points(ops: &[&str]) -> Option<i64> {
        let mut scores: Vec<INT> = Vec::new();
        for &op in ops {
            match op {
                "+" => {
                    PLUS
                    scores.push(a + b);
                }
                "D" => {
                    let last = *scores.last()?;
                    scores.push(last * 2);
                }
                "C" => {
                    CANCEL
                }
                _ => scores.push(op.parse().ok()?),
            }
        }
        Some(scores.iter().map(|&x| i64::from(x)).sum())
    }
"""
P.append(prob(
    "baseball-game", "Baseball game", "easy", "stack-basics", ["slice patterns", "Option"],
    """
    Score a game from `ops`. An integer records that score; `"+"` records the sum of the last two scores;
    `"D"` records double the last score; `"C"` removes the last score. Return the total, or `None` if an
    operation is invalid: not a number, or not enough previous scores.
    """,
    """
    pub fn cal_points(ops: &[&str]) -> Option<i64> {
        todo!()
    }
    """,
    """
    pub fn cal_points(ops: &[&str]) -> Option<i64> {
        let mut scores: Vec<i64> = Vec::new();
        for &op in ops {
            match op {
                "+" => {
                    let [.., a, b] = scores[..] else { return None };
                    scores.push(a + b);
                }
                "D" => {
                    let last = *scores.last()?;
                    scores.push(last * 2);
                }
                "C" => {
                    scores.pop()?;
                }
                _ => scores.push(op.parse().ok()?),
            }
        }
        Some(scores.iter().sum())
    }
    """,
    [T("example", '["5","2","C","D","+"]', 'cal_points(&["5", "2", "C", "D", "+"])', "Some(30)"),
     T("negatives", '["5","-2","4","C","D","9","+","+"]', 'cal_points(&["5", "-2", "4", "C", "D", "9", "+", "+"])', "Some(27)"),
     T("cancel_all", '["1","C"]', 'cal_points(&["1", "C"])', "Some(0)"),
     T("plus_too_early", '["1","+"]', 'cal_points(&["1", "+"])', "None"),
     T("double_needs_a_score", '["D"]', 'cal_points(&["D"])', "None")],
    [T("not_a_number", '["x"]', 'cal_points(&["x"])', "None"),
     T("cancel_nothing", '["C"]', 'cal_points(&["C"])', "None"),
     T("empty", "[]", "cal_points(&[])", "Some(0)"),
     T("plus_after_cancel", '["1","2","C","+"]', 'cal_points(&["1", "2", "C", "+"])', "None"),
     T("plus_uses_last_two", '["1","2","3","+"]', 'cal_points(&["1", "2", "3", "+"])', "Some(11)"),
     T("double_negative", '["-3","D"]', 'cal_points(&["-3", "D"])', "Some(-9)"),
     T("beyond_i32", '["2147483647","2147483647","+"]', 'cal_points(&["2147483647", "2147483647", "+"])', "Some(8_589_934_588)"),
     T("decimal_is_invalid", '["5.0"]', 'cal_points(&["5.0"])', "None"),
     T("lowercase_d_is_invalid", '["1","d"]', 'cal_points(&["1", "d"])', "None"),
     T("empty_token", '["1",""]', 'cal_points(&["1", ""])', "None"),
     """
     #[test]
     fn random_vs_model() {
         fn model(ops: &[&str]) -> Option<i64> {
             let mut s: Vec<i64> = Vec::new();
             for &op in ops {
                 if op == "+" {
                     if s.len() < 2 {
                         return None;
                     }
                     let v = s[s.len() - 1] + s[s.len() - 2];
                     s.push(v);
                 } else if op == "D" {
                     let v = *s.last()? * 2;
                     s.push(v);
                 } else if op == "C" {
                     s.pop()?;
                 } else {
                     s.push(op.parse().ok()?);
                 }
             }
             Some(s.iter().sum())
         }
         let mut rng = anneal_prelude::Rng::new(3003);
         let tokens = ["+", "D", "C", "1", "-2", "7", "30", "0", "x"];
         for _ in 0..400 {
             let n = rng.below(9);
             let ops: Vec<&str> = (0..n).map(|_| *rng.pick(&tokens)).collect();
             check!(format!("ops = {ops:?}"), cal_points(&ops), model(&ops));
         }
     }

     #[test]
     fn scale_200k() {
         let ops = vec!["1000000000"; 200_000];
         check!("200000 × \\"1000000000\\"", cal_points(&ops), Some(200_000_000_000_000));
     }
     """],
    [("rust", "`let [.., a, b] = scores[..] else { return None };` takes the last two elements, or bails if there aren't two."),
     ("rust", "`?` works on `Option`: `scores.last()?`, `scores.pop()?`, `op.parse().ok()?`.")],
    ("Slice patterns and `?` on `Option` turn every 'not enough scores' check into part of the happy path.", "O(n)", "O(n)"),
    "How would you return which operation was invalid instead of `None`?",
    ["Slice patterns with `let ... else`.", "`?` on `Option`."],
    related=["S1"],
    wrong=dict(
        i32_scores=BASEBALL_WRONG.replace("INT", "i32").replace("PLUS", "let [.., a, b] = scores[..] else { return None };").replace("CANCEL", "scores.pop()?;"),
        first_two_for_plus=BASEBALL_WRONG.replace("INT", "i64").replace("PLUS", "let [a, b, ..] = scores[..] else { return None };").replace("CANCEL", "scores.pop()?;"),
        cancel_on_empty_is_fine=BASEBALL_WRONG.replace("INT", "i64").replace("PLUS", "let [.., a, b] = scores[..] else { return None };").replace("CANCEL", "scores.pop();"),
    ),
))

MIN_WRONG = """
    #[derive(Default)]
    pub struct MinStack {
        items: Vec<(i32, i32)>,
    }

    impl MinStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            PUSH
        }

        pub fn pop(&mut self) -> Option<i32> {
            self.items.pop().map(|(x, _)| x)
        }

        pub fn top(&self) -> Option<i32> {
            self.items.last().map(|&(x, _)| x)
        }

        pub fn min(&self) -> Option<i32> {
            MIN
        }
    }
"""

P.append(prob(
    "min-stack", "Min stack", "easy", "stack-basics", ["stack of tuples"],
    "A stack that also reports its minimum element in O(1).",
    """
    #[derive(Default)]
    pub struct MinStack {
        items: Vec<(i32, i32)>,
    }

    impl MinStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            todo!()
        }

        pub fn pop(&mut self) -> Option<i32> {
            todo!()
        }

        pub fn top(&self) -> Option<i32> {
            todo!()
        }

        pub fn min(&self) -> Option<i32> {
            todo!()
        }
    }
    """,
    """
    /// Each entry stores the value and the minimum of everything at or below it.
    #[derive(Default)]
    pub struct MinStack {
        items: Vec<(i32, i32)>,
    }

    impl MinStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            let min = self.min().map_or(x, |m| m.min(x));
            self.items.push((x, min));
        }

        pub fn pop(&mut self) -> Option<i32> {
            self.items.pop().map(|(x, _)| x)
        }

        pub fn top(&self) -> Option<i32> {
            self.items.last().map(|&(x, _)| x)
        }

        pub fn min(&self) -> Option<i32> {
            self.items.last().map(|&(_, m)| m)
        }
    }
    """,
    [T("tracks_min", "push -2, 0, -3; min; pop; top; min", "(s.min(), s.pop(), s.top(), s.min())", "(Some(-3), Some(-3), Some(0), Some(-2))",
       setup="let mut s = MinStack::new();\ns.push(-2);\ns.push(0);\ns.push(-3);"),
     T("empty", "new stack", "(s.min(), s.top(), s.pop())", "(None, None, None)", setup="let mut s = MinStack::new();"),
     T("min_below_top", "push 3, 5; top, min", "(s.top(), s.min())", "(Some(5), Some(3))", setup="let mut s = MinStack::new();\ns.push(3);\ns.push(5);"),
     T("repeated_min", "push 2, 1, 1; pop; min", "(s.pop(), s.min())", "(Some(1), Some(1))", setup="let mut s = MinStack::new();\ns.push(2);\ns.push(1);\ns.push(1);"),
     T("min_restored", "push 1, 0; pop; min", "(s.pop(), s.min())", "(Some(0), Some(1))", setup="let mut s = MinStack::new();\ns.push(1);\ns.push(0);")],
    [T("duplicates", "push 1, 1; pop; min", "(s.pop(), s.min())", "(Some(1), Some(1))", setup="let mut s = MinStack::new();\ns.push(1);\ns.push(1);"),
     T("extremes", "push i32::MAX, i32::MIN", "s.min()", "Some(i32::MIN)", setup="let mut s = MinStack::new();\ns.push(i32::MAX);\ns.push(i32::MIN);"),
     T("pop_to_empty", "push 4; pop, pop, min, top", "(s.pop(), s.pop(), s.min(), s.top())", "(Some(4), None, None, None)", setup="let mut s = MinStack::new();\ns.push(4);"),
     T("push_after_empty", "push 5; pop; push 7; min", "(s.min(), s.top())", "(Some(7), Some(7))", setup="let mut s = MinStack::new();\ns.push(5);\ns.pop();\ns.push(7);"),
     T("descending", "push 5, 4, 3, 2, 1; min after each pop", "mins", "vec![Some(2), Some(3), Some(4), Some(5), None]",
       setup="let mut s = MinStack::new();\nfor x in [5, 4, 3, 2, 1] {\n    s.push(x);\n}\nlet mins: Vec<Option<i32>> = (0..5).map(|_| { s.pop(); s.min() }).collect();"),
     T("ascending", "push 1, 2, 3; min after each pop", "mins", "vec![Some(1), Some(1), None]",
       setup="let mut s = MinStack::new();\nfor x in [1, 2, 3] {\n    s.push(x);\n}\nlet mins: Vec<Option<i32>> = (0..3).map(|_| { s.pop(); s.min() }).collect();"),
     T("min_twice", "push i32::MIN twice; pop; min", "(s.pop(), s.min())", "(Some(i32::MIN), Some(i32::MIN))", setup="let mut s = MinStack::new();\ns.push(i32::MIN);\ns.push(i32::MIN);"),
     T("negatives", "push -1, -5, -3; min, pop, min, pop, min", "(s.min(), s.pop(), s.min(), s.pop(), s.min())", "(Some(-5), Some(-3), Some(-5), Some(-5), Some(-1))",
       setup="let mut s = MinStack::new();\ns.push(-1);\ns.push(-5);\ns.push(-3);"),
     """
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(3004);
         for _ in 0..300 {
             let mut s = MinStack::new();
             let mut model: Vec<i32> = Vec::new();
             let mut log = Vec::new();
             let n = rng.below(20);
             for _ in 0..n {
                 if rng.below(3) > 0 {
                     let x = rng.int(-9, 9) as i32;
                     s.push(x);
                     model.push(x);
                     log.push(format!("push {x}"));
                 } else {
                     log.push("pop".to_string());
                     check!(log.join(", "), s.pop(), model.pop());
                 }
                 check!(log.join(", "), (s.top(), s.min()), (model.last().copied(), model.iter().min().copied()));
             }
         }
     }

     #[test]
     fn scale_200k() {
         let mut s = MinStack::new();
         let mut sum = 0i64;
         for i in 0..200_000 {
             s.push(200_000 - i);
             sum += i64::from(s.min().unwrap_or(0));
         }
         for _ in 0..100_000 {
             s.pop();
             sum += i64::from(s.min().unwrap_or(0));
         }
         check!("push 200000 down to 1 (min after each), then pop 100000 (min after each)", sum, 25_000_250_000);
     }
     """],
    [("approach", "When something is popped, the minimum must go back to what it was. Store the minimum-so-far next to each value.")],
    ("A stack of `(value, min_below)` pairs costs one extra `i32` per element and makes every operation O(1).", "O(1)", "O(n)"),
    "Can you do it with O(1) extra space beyond the stack itself?",
    ["Stacks of tuples carrying derived state."],
    wrong=dict(
        scans_for_min=MIN_WRONG.replace("PUSH", "self.items.push((x, x));").replace("MIN", "self.items.iter().map(|&(x, _)| x).min()"),
        min_not_restored="""
            #[derive(Default)]
            pub struct MinStack {
                items: Vec<i32>,
                min: Option<i32>,
            }

            impl MinStack {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn push(&mut self, x: i32) {
                    self.items.push(x);
                    self.min = Some(self.min.map_or(x, |m| m.min(x)));
                }

                pub fn pop(&mut self) -> Option<i32> {
                    let x = self.items.pop();
                    if self.items.is_empty() {
                        self.min = None;
                    }
                    x
                }

                pub fn top(&self) -> Option<i32> {
                    self.items.last().copied()
                }

                pub fn min(&self) -> Option<i32> {
                    self.min
                }
            }
        """,
    ),
))

# ---------------------------------------------------------------- monotonic & parsing (medium)

RPN_WRONG = """
    pub fn eval_rpn(tokens: &[&str]) -> i64 {
        let mut stack: Vec<INT> = Vec::new();
        for &t in tokens {
            if let Ok(n) = t.parse::<INT>() {
                stack.push(n);
                continue;
            }
            POPS
            stack.push(match t {
                "+" => a + b,
                "-" => a - b,
                "*" => a * b,
                "/" => a / b,
                _ => panic!("unknown operator {t}"),
            });
        }
        i64::from(stack.pop().expect("valid RPN"))
    }
"""

P.append(prob(
    "evaluate-rpn", "Evaluate reverse Polish notation", "medium", "monotonic-parsing", ["RPN", "parse"],
    """
    Evaluate an expression in reverse Polish notation. Tokens are integers or `+ - * /`; division truncates
    toward zero. The input is always valid.
    """,
    """
    pub fn eval_rpn(tokens: &[&str]) -> i64 {
        todo!()
    }
    """,
    """
    pub fn eval_rpn(tokens: &[&str]) -> i64 {
        let mut stack: Vec<i64> = Vec::new();
        for &t in tokens {
            if let Ok(n) = t.parse::<i64>() {
                stack.push(n);
                continue;
            }
            let b = stack.pop().expect("valid RPN");
            let a = stack.pop().expect("valid RPN");
            stack.push(match t {
                "+" => a + b,
                "-" => a - b,
                "*" => a * b,
                "/" => a / b,
                _ => panic!("unknown operator {t}"),
            });
        }
        stack.pop().expect("valid RPN")
    }
    """,
    [T("simple", '["2","1","+","3","*"]', 'eval_rpn(&["2", "1", "+", "3", "*"])', "9"),
     T("division", '["4","13","5","/","+"]', 'eval_rpn(&["4", "13", "5", "/", "+"])', "6"),
     T("long", '["10","6","9","3","+","-11","*","/","*","17","+","5","+"]', 'eval_rpn(&["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])', "22"),
     T("order_matters", '["3","5","-"]', 'eval_rpn(&["3", "5", "-"])', "-2"),
     T("negative_division_truncates", '["-7","2","/"]', 'eval_rpn(&["-7", "2", "/"])', "-3")],
    [T("single", '["-7"]', 'eval_rpn(&["-7"])', "-7"),
     T("divide_by_negative", '["7","-2","/"]', 'eval_rpn(&["7", "-2", "/"])', "-3"),
     T("zero_numerator", '["0","3","/"]', 'eval_rpn(&["0", "3", "/"])', "0"),
     T("beyond_i32", '["100000","100000","*"]', 'eval_rpn(&["100000", "100000", "*"])', "10_000_000_000"),
     T("negative_times_negative", '["-3","-4","*"]', 'eval_rpn(&["-3", "-4", "*"])', "12"),
     T("left_associative", '["1","2","-","3","-"]', 'eval_rpn(&["1", "2", "-", "3", "-"])', "-4"),
     T("negative_numbers", '["-11","-11","+"]', 'eval_rpn(&["-11", "-11", "+"])', "-22"),
     T("single_zero", '["0"]', 'eval_rpn(&["0"])', "0"),
     """
     #[test]
     fn random_vs_tree() {
         // Builds a random expression tree, writes it in RPN and returns its value.
         fn gen(rng: &mut anneal_prelude::Rng, depth: u32, out: &mut Vec<String>) -> i64 {
             if depth == 0 || rng.below(3) == 0 {
                 let x = rng.int(-9, 9);
                 out.push(x.to_string());
                 return x;
             }
             let a = gen(rng, depth - 1, out);
             let b = gen(rng, depth - 1, out);
             let (op, v) = match rng.below(4) {
                 0 => ("+", a + b),
                 1 => ("-", a - b),
                 2 => ("*", a * b),
                 _ if b != 0 => ("/", a / b),
                 _ => ("+", a + b),
             };
             out.push(op.to_string());
             v
         }
         let mut rng = anneal_prelude::Rng::new(3005);
         for _ in 0..400 {
             let mut tokens = Vec::new();
             let want = gen(&mut rng, 4, &mut tokens);
             let refs: Vec<&str> = tokens.iter().map(|t| t.as_str()).collect();
             check!(format!("tokens = {refs:?}"), eval_rpn(&refs), want);
         }
     }

     #[test]
     fn scale_numbers_then_operators() {
         let mut tokens = vec!["1"; 100_001];
         tokens.extend(vec!["+"; 100_000]);
         check!("100001 × \\"1\\", then 100000 × \\"+\\"", eval_rpn(&tokens), 100_001);
     }
     """],
    [("approach", "Numbers go on a stack; an operator pops two and pushes the result."),
     ("edge case", "Pop `b` first, then `a`: `a - b`, not `b - a`. And `\"-11\"` is a number, not an operator.")],
    ("Trying `parse` first means negative numbers are never mistaken for the `-` operator. Rust's `/` truncates toward zero, as required.", "O(n)", "O(n)"),
    "The input isn't always valid in practice. How would the signature change? (Next problem: the fix.)",
    ["Operand order when popping.", "Parse first, then treat the token as an operator."],
    wrong=dict(
        swapped_operands=RPN_WRONG.replace("INT", "i64").replace("POPS", """let a = stack.pop().expect("valid RPN");
                let b = stack.pop().expect("valid RPN");"""),
        i32_stack=RPN_WRONG.replace("INT", "i32").replace("POPS", """let b = stack.pop().expect("valid RPN");
                let a = stack.pop().expect("valid RPN");"""),
        reduce_first_operator="""
            pub fn eval_rpn(tokens: &[&str]) -> i64 {
                let mut items: Vec<Result<i64, &str>> = tokens.iter().map(|t| t.parse::<i64>().map_err(|_| *t)).collect();
                while items.len() > 1 {
                    let i = items.iter().position(|t| t.is_err()).expect("valid RPN");
                    let (a, b) = (items[i - 2].expect("number"), items[i - 1].expect("number"));
                    let v = match items[i] {
                        Err("+") => a + b,
                        Err("-") => a - b,
                        Err("*") => a * b,
                        _ => a / b,
                    };
                    items.splice(i - 2..=i, [Ok(v)]);
                }
                items[0].expect("valid RPN")
            }
        """,
    ),
))

P.append(prob(
    "daily-temperatures", "Daily temperatures", "medium", "monotonic-parsing", ["monotonic stack"],
    """
    For each day, return how many days until a warmer temperature, or 0 if none comes.
    """,
    """
    pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
        todo!()
    }
    """,
    """
    pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
        let mut answer = vec![0; temps.len()];
        // Indices of days still waiting for a warmer day; their temperatures are decreasing.
        let mut waiting: Vec<usize> = Vec::new();
        for (i, &t) in temps.iter().enumerate() {
            while let Some(&j) = waiting.last() {
                if temps[j] >= t {
                    break;
                }
                answer[j] = i - j;
                waiting.pop();
            }
            waiting.push(i);
        }
        answer
    }
    """,
    [T("example", "[73,74,75,71,69,72,76,73]", "daily_temperatures(&[73, 74, 75, 71, 69, 72, 76, 73])", "vec![1, 1, 4, 2, 1, 1, 0, 0]"),
     T("rising", "[30,40,50,60]", "daily_temperatures(&[30, 40, 50, 60])", "vec![1, 1, 1, 0]"),
     T("three", "[30,60,90]", "daily_temperatures(&[30, 60, 90])", "vec![1, 1, 0]"),
     T("falling", "[60,50,40]", "daily_temperatures(&[60, 50, 40])", "vec![0, 0, 0]"),
     T("equal_is_not_warmer", "[50,50,51]", "daily_temperatures(&[50, 50, 51])", "vec![2, 1, 0]")],
    [T("single", "[50]", "daily_temperatures(&[50])", "vec![0]"),
     T("empty", "[]", "daily_temperatures(&[])", "Vec::<usize>::new()"),
     T("all_equal", "[5,5,5]", "daily_temperatures(&[5, 5, 5])", "vec![0, 0, 0]"),
     T("negatives", "[-5,-10,-3]", "daily_temperatures(&[-5, -10, -3])", "vec![2, 1, 0]"),
     T("extremes", "[i32::MIN, i32::MAX]", "daily_temperatures(&[i32::MIN, i32::MAX])", "vec![1, 0]"),
     T("valley", "[3,1,2,4]", "daily_temperatures(&[3, 1, 2, 4])", "vec![3, 1, 1, 0]"),
     T("peak_later", "[1,5,2,3,4,6]", "daily_temperatures(&[1, 5, 2, 3, 4, 6])", "vec![1, 4, 1, 1, 1, 0]"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(3006);
         for _ in 0..300 {
             let n = rng.below(12);
             let t: Vec<i32> = rng.vec(n, 30, 40);
             let want: Vec<usize> = (0..n).map(|i| (i + 1..n).find(|&j| t[j] > t[i]).map_or(0, |j| j - i)).collect();
             check!(format!("temps = {t:?}"), daily_temperatures(&t), want);
         }
     }

     #[test]
     fn scale_200k_falling() {
         let mut t: Vec<i32> = (0..200_000).map(|i| 300_000 - i).collect();
         t.push(1_000_000);
         let ans = daily_temperatures(&t);
         check!("200000 falling days, then a hot one", (ans[0], ans[199_999], ans[200_000]), (200_000, 1, 0));
     }
     """,
     T("long_wait", "10⁵ falling days, then a hot one", "ok", "true",
       setup="let n = 100_000;\nlet mut t: Vec<i32> = (0..n as i32).map(|i| 50_000 - i).collect();\nt.push(100_000);\nlet ans = daily_temperatures(&t);\nlet ok = (0..n).all(|i| ans[i] == n - i) && ans[n] == 0;")],
    [("approach", "Keep the days that haven't found a warmer day yet. A new day resolves every colder day on top."),
     ("rust", "Store indices in the stack, not temperatures: you need the index for the distance and can look the temperature up.")],
    ("Each index is pushed and popped once, so the nested loop is O(n) overall. The stack's temperatures always decrease from bottom to top.", "O(n)", "O(n)"),
    "How would you answer 'days until at least 5 degrees warmer'?",
    ["Monotonic stacks of indices."],
    wrong=dict(
        scan_forward="""
            pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
                let n = temps.len();
                (0..n).map(|i| (i + 1..n).find(|&j| temps[j] > temps[i]).map_or(0, |j| j - i)).collect()
            }
        """,
        equal_counts_as_warmer="""
            pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
                let mut answer = vec![0; temps.len()];
                let mut waiting: Vec<usize> = Vec::new();
                for (i, &t) in temps.iter().enumerate() {
                    while let Some(&j) = waiting.last() {
                        if temps[j] > t {
                            break;
                        }
                        answer[j] = i - j;
                        waiting.pop();
                    }
                    waiting.push(i);
                }
                answer
            }
        """,
    ),
))

P.append(prob(
    "car-fleet", "Car fleet", "medium", "monotonic-parsing", ["sorting", "exact arithmetic"],
    """
    Cars drive toward `target` on a one-lane road; `position[i]` and `speed[i]` describe car `i`. A car
    that catches up with a slower car ahead joins it and drives at its speed, as one fleet; catching up
    exactly at the target counts. Return how many fleets arrive. Positions are distinct and below `target`.
    """,
    """
    pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
        todo!()
    }
    """,
    """
    pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
        // (distance left, speed), closest to the target first.
        let mut cars: Vec<(u64, u64)> = position
            .iter()
            .zip(speed)
            .map(|(&p, &s)| (u64::from(target - p), u64::from(s)))
            .collect();
        cars.sort_unstable();
        let mut fleets = 0;
        let mut lead: Option<(u64, u64)> = None;
        for (d, s) in cars {
            // Arrives later than the fleet ahead (d/s > ld/ls), compared without floats.
            if lead.is_none_or(|(ld, ls)| d * ls > ld * s) {
                fleets += 1;
                lead = Some((d, s));
            }
        }
        fleets
    }
    """,
    [T("three", "target 12, position [10,8,0,5,3], speed [2,4,1,1,3]", "car_fleet(12, &[10, 8, 0, 5, 3], &[2, 4, 1, 1, 3])", "3"),
     T("one_car", "target 10, position [3], speed [3]", "car_fleet(10, &[3], &[3])", "1"),
     T("all_merge", "target 100, position [0,2,4], speed [4,2,1]", "car_fleet(100, &[0, 2, 4], &[4, 2, 1])", "1"),
     T("meet_at_target", "target 10, position [0,5], speed [2,1]", "car_fleet(10, &[0, 5], &[2, 1])", "1"),
     T("none", "no cars", "car_fleet(5, &[], &[])", "0")],
    [T("float_trap", "target 10⁹; arrival times 10⁻¹⁸ apart, equal in f64", "car_fleet(1_000_000_000, &[0, 1], &[1_000_000_001, 1_000_000_000])", "2"),
     T("never_catch_up", "target 10, position [0,5], speed [1,2]", "car_fleet(10, &[0, 5], &[1, 2])", "2"),
     T("would_catch_after_target", "target 10, position [0,9], speed [9,1]", "car_fleet(10, &[0, 9], &[9, 1])", "2"),
     T("blocked_by_middle", "target 20, position [0,10,15], speed [5,1,10]", "car_fleet(20, &[0, 10, 15], &[5, 1, 10])", "2"),
     T("slow_front_car", "target 10, position [0,1,2,3], speed [4,3,2,1]", "car_fleet(10, &[0, 1, 2, 3], &[4, 3, 2, 1])", "1"),
     T("u32_extremes", "target u32::MAX, position [0,1], speed [u32::MAX, u32::MAX - 1]", "car_fleet(u32::MAX, &[0, 1], &[u32::MAX, u32::MAX - 1])", "1"),
     T("same_speed", "target 10, position [1,2,3], speed [1,1,1]", "car_fleet(10, &[1, 2, 3], &[1, 1, 1])", "3"),
     T("unsorted_input", "target 10, position [6,0,3], speed [1,3,2]", "car_fleet(10, &[6, 0, 3], &[1, 3, 2])", "1"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(3007);
         for _ in 0..300 {
             let target = 1 + rng.below(20) as u32;
             let mut all: Vec<u32> = (0..target).collect();
             rng.shuffle(&mut all);
             let n = rng.below(all.len().min(8) + 1);
             let position: Vec<u32> = all[..n].to_vec();
             let speed: Vec<u32> = rng.vec(n, 1, 5);
             // A car leads a fleet iff it arrives strictly later than every car ahead of it.
             let time = |i: usize| (u64::from(target - position[i]), u64::from(speed[i]));
             let want = (0..n)
                 .filter(|&i| (0..n).all(|j| position[j] <= position[i] || { let ((d, s), (dj, sj)) = (time(i), time(j)); d * sj > dj * s }))
                 .count();
             check!(format!("target {target}, position {position:?}, speed {speed:?}"), car_fleet(target, &position, &speed), want);
         }
     }

     #[test]
     fn scale_200k_all_separate() {
         let position: Vec<u32> = (0..200_000).collect();
         let speed = vec![1u32; 200_000];
         check!("target 200000, positions 0..200000, all speed 1", car_fleet(200_000, &position, &speed), 200_000);
     }
     """],
    [("approach", "Sort by distance to the target. Going backwards from the front car, a car forms a new fleet only if it would arrive later than the fleet ahead of it."),
     ("rust", "Compare arrival times `d1/s1 > d2/s2` as `d1 * s2 > d2 * s1` in `u64`, with no floating point.")],
    ("Cross-multiplying keeps the comparison exact; with `f64`, two nearly equal arrival times can compare the wrong way. `Option::is_none_or` handles the first car.", "O(n log n)", "O(n)"),
    "What if cars could also have different lengths?",
    ["Exact comparisons of ratios by cross-multiplication.", "Processing sorted items against a running 'fleet ahead'."],
    wrong=dict(
        float_times="""
            pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
                let mut cars: Vec<(u32, f64)> = position.iter().zip(speed).map(|(&p, &s)| (p, f64::from(target - p) / f64::from(s))).collect();
                cars.sort_by(|a, b| b.0.cmp(&a.0));
                let mut fleets = 0;
                let mut lead = 0.0f64;
                for (_, t) in cars {
                    if t > lead {
                        fleets += 1;
                        lead = t;
                    }
                }
                fleets
            }
        """,
        tie_is_a_new_fleet="""
            pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
                let mut cars: Vec<(u64, u64)> = position
                    .iter()
                    .zip(speed)
                    .map(|(&p, &s)| (u64::from(target - p), u64::from(s)))
                    .collect();
                cars.sort_unstable();
                let mut fleets = 0;
                let mut lead: Option<(u64, u64)> = None;
                for (d, s) in cars {
                    if lead.is_none_or(|(ld, ls)| d * ls >= ld * s) {
                        fleets += 1;
                        lead = Some((d, s));
                    }
                }
                fleets
            }
        """,
        compare_with_every_car_ahead="""
            pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
                let n = position.len();
                let time = |i: usize| (u64::from(target - position[i]), u64::from(speed[i]));
                (0..n)
                    .filter(|&i| (0..n).all(|j| position[j] <= position[i] || { let ((d, s), (dj, sj)) = (time(i), time(j)); d * sj > dj * s }))
                    .count()
            }
        """,
    ),
))

P.append(prob(
    "asteroid-collision", "Asteroid collision", "medium", "monotonic-parsing", ["stack", "labelled continue"],
    """
    Asteroids move along a line: positive ones right, negative ones left, all at the same speed. When two
    meet, the smaller one explodes; equal sizes both explode. Return the asteroids left, in order.
    """,
    """
    pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
        todo!()
    }
    """,
    """
    pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
        let mut alive: Vec<i32> = Vec::new();
        'next: for &a in asteroids {
            if a < 0 {
                while let Some(&top) = alive.last() {
                    if top < 0 {
                        break;
                    }
                    if top < -a {
                        alive.pop();
                        continue;
                    }
                    if top == -a {
                        alive.pop();
                    }
                    continue 'next;
                }
            }
            alive.push(a);
        }
        alive
    }
    """,
    [T("right_survives", "[5,10,-5]", "asteroid_collision(&[5, 10, -5])", "vec![5, 10]"),
     T("both_explode", "[8,-8]", "asteroid_collision(&[8, -8])", "vec![]"),
     T("chain", "[10,2,-5]", "asteroid_collision(&[10, 2, -5])", "vec![10]"),
     T("left_mover_survives", "[3,5,-6,2,-1,4]", "asteroid_collision(&[3, 5, -6, 2, -1, 4])", "vec![-6, 2, 4]"),
     T("moving_apart", "[-2,-1,1,2]", "asteroid_collision(&[-2, -1, 1, 2])", "vec![-2, -1, 1, 2]")],
    [T("left_wins", "[1,-2,-2,-2]", "asteroid_collision(&[1, -2, -2, -2])", "vec![-2, -2, -2]"),
     T("empty", "[]", "asteroid_collision(&[])", "Vec::<i32>::new()"),
     T("single", "[-3]", "asteroid_collision(&[-3])", "vec![-3]"),
     T("all_right", "[1,2,3]", "asteroid_collision(&[1, 2, 3])", "vec![1, 2, 3]"),
     T("all_left", "[-1,-2]", "asteroid_collision(&[-1, -2])", "vec![-1, -2]"),
     T("equal_then_bigger", "[1,-1,-2]", "asteroid_collision(&[1, -1, -2])", "vec![-2]"),
     T("wins_then_ties", "[2,-1,-2]", "asteroid_collision(&[2, -1, -2])", "Vec::<i32>::new()"),
     T("big_left_mover_ties", "[10,-5,-10]", "asteroid_collision(&[10, -5, -10])", "Vec::<i32>::new()"),
     T("extremes", "[i32::MAX, -i32::MAX]", "asteroid_collision(&[i32::MAX, -i32::MAX])", "Vec::<i32>::new()"),
     """
     #[test]
     fn random_vs_simulation() {
         // Resolve any adjacent right-mover / left-mover pair until none is left.
         fn brute(a: &[i32]) -> Vec<i32> {
             let mut v = a.to_vec();
             while let Some(i) = (0..v.len().saturating_sub(1)).find(|&i| v[i] > 0 && v[i + 1] < 0) {
                 let (l, r) = (v[i], -v[i + 1]);
                 if l > r {
                     v.remove(i + 1);
                 } else if l < r {
                     v.remove(i);
                 } else {
                     v.drain(i..i + 2);
                 }
             }
             v
         }
         let mut rng = anneal_prelude::Rng::new(3008);
         for _ in 0..400 {
             let n = rng.below(10);
             let a: Vec<i32> = (0..n).map(|_| { let x = rng.int(-5, 4) as i32; if x >= 0 { x + 1 } else { x } }).collect();
             check!(format!("asteroids = {a:?}"), asteroid_collision(&a), brute(&a));
         }
     }

     #[test]
     fn scale_one_big_left_mover() {
         let mut a = vec![-1; 100_000];
         a.extend(vec![1; 100_000]);
         a.push(-200_000);
         let out = asteroid_collision(&a);
         check!("100000 × -1, 100000 × 1, then -200000", (out.len(), out[0], out[100_000]), (100_001, -1, -200_000));
     }
     """],
    [("approach", "Only a left-mover can hit a right-mover already on the stack. Keep colliding with the top until one side wins."),
     ("rust", "A labelled `continue 'next` skips the push when the new asteroid is destroyed.")],
    ("Each asteroid is pushed and popped at most once. The labelled continue reads more clearly than a `destroyed` flag.", "O(n)", "O(n)"),
    "What changes if asteroids can have different speeds?",
    ["Labelled loops.", "Resolving a new item against the top of a stack repeatedly."],
    constraints=["asteroids[i] ≠ 0", "asteroids[i] > i32::MIN"],
    wrong=dict(
        repeated_passes="""
            pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
                let mut v = asteroids.to_vec();
                while let Some(i) = (0..v.len().saturating_sub(1)).find(|&i| v[i] > 0 && v[i + 1] < 0) {
                    let (l, r) = (v[i], -v[i + 1]);
                    if l > r {
                        v.remove(i + 1);
                    } else if l < r {
                        v.remove(i);
                    } else {
                        v.drain(i..i + 2);
                    }
                }
                v
            }
        """,
        tie_keeps_the_new_one="""
            pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
                let mut alive: Vec<i32> = Vec::new();
                'next: for &a in asteroids {
                    if a < 0 {
                        while let Some(&top) = alive.last() {
                            if top < 0 {
                                break;
                            }
                            if top < -a {
                                alive.pop();
                                continue;
                            }
                            if top == -a {
                                alive.pop();
                                break;
                            }
                            continue 'next;
                        }
                    }
                    alive.push(a);
                }
                alive
            }
        """,
        opposite_signs_collide="""
            pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
                let mut alive: Vec<i32> = Vec::new();
                'next: for &a in asteroids {
                    while let Some(&top) = alive.last() {
                        if (top > 0) == (a > 0) {
                            break;
                        }
                        if top.abs() < a.abs() {
                            alive.pop();
                            continue;
                        }
                        if top.abs() == a.abs() {
                            alive.pop();
                        }
                        continue 'next;
                    }
                    alive.push(a);
                }
                alive
            }
        """,
    ),
))

DECODE_WRONG = """
    pub fn decode_string(s: &str) -> String {
        let mut frames: Vec<(String, usize)> = Vec::new();
        let (mut current, mut k) = (String::new(), 0usize);
        for b in s.bytes() {
            match b {
                b'0'..=b'9' => DIGIT,
                b'[' => {
                    frames.push((std::mem::take(&mut current), k));
                    RESET
                }
                b']' => {
                    let (before, n) = frames.pop().expect("balanced brackets");
                    current = before + &current.repeat(n);
                }
                _ => current.push(char::from(b)),
            }
        }
        current
    }
"""

P.append(prob(
    "decode-string", "Decode string", "medium", "monotonic-parsing", ["mem::take", "stack of frames"],
    """
    Decode strings like `3[a2[c]]`: `k[inner]` means `inner` repeated `k` times, and brackets nest. The input
    is valid; `k` can have several digits; letters are lowercase ASCII.
    """,
    """
    pub fn decode_string(s: &str) -> String {
        todo!()
    }
    """,
    """
    pub fn decode_string(s: &str) -> String {
        // Each frame: the text built before a '[' and its repeat count.
        let mut frames: Vec<(String, usize)> = Vec::new();
        let (mut current, mut k) = (String::new(), 0usize);
        for b in s.bytes() {
            match b {
                b'0'..=b'9' => k = k * 10 + usize::from(b - b'0'),
                b'[' => {
                    frames.push((std::mem::take(&mut current), k));
                    k = 0;
                }
                b']' => {
                    let (before, n) = frames.pop().expect("balanced brackets");
                    current = before + &current.repeat(n);
                }
                _ => current.push(char::from(b)),
            }
        }
        current
    }
    """,
    [T("flat", '"3[a]2[bc]"', 'decode_string("3[a]2[bc]")', '"aaabcbc".to_string()'),
     T("nested", '"3[a2[c]]"', 'decode_string("3[a2[c]]")', '"accaccacc".to_string()'),
     T("tail", '"2[abc]3[cd]ef"', 'decode_string("2[abc]3[cd]ef")', '"abcabccdcdcdef".to_string()'),
     T("two_digits", '"10[a]"', 'decode_string("10[a]")', '"a".repeat(10)'),
     T("plain", '"abc"', 'decode_string("abc")', '"abc".to_string()')],
    [T("zero", '"0[x]y"', 'decode_string("0[x]y")', '"y".to_string()'),
     T("empty", '""', 'decode_string("")', "String::new()"),
     T("one", '"1[a]"', 'decode_string("1[a]")', '"a".to_string()'),
     T("deep", '"2[2[2[a]]]"', 'decode_string("2[2[2[a]]]")', '"a".repeat(8)'),
     T("letters_around", '"a2[b]c"', 'decode_string("a2[b]c")', '"abbc".to_string()'),
     T("hundred", '"100[ab]"', 'decode_string("100[ab]")', '"ab".repeat(100)'),
     T("adjacent_groups", '"2[a]2[a]"', 'decode_string("2[a]2[a]")', '"aaaa".to_string()'),
     T("mixed_nesting", '"3[z]2[2[y]pq4[2[jk]e1[f]]]ef"', 'decode_string("3[z]2[2[y]pq4[2[jk]e1[f]]]ef")', '"zzzyypqjkjkefjkjkefjkjkefjkjkefyypqjkjkefjkjkefjkjkefjkjkefef".to_string()'),
     T("counts_after_letters", '"ab12[c]"', 'decode_string("ab12[c]")', 'format!("ab{}", "c".repeat(12))'),
     """
     #[test]
     fn random_vs_generator() {
         // Builds a random encoded string alongside what it decodes to.
         fn gen(rng: &mut anneal_prelude::Rng, depth: u32) -> (String, String) {
             let (mut enc, mut dec) = (String::new(), String::new());
             let parts = 1 + rng.below(3);
             for _ in 0..parts {
                 if depth > 0 && rng.bool() {
                     let k = rng.below(12);
                     let (e, d) = gen(rng, depth - 1);
                     enc.push_str(&format!("{k}[{e}]"));
                     dec.push_str(&d.repeat(k));
                 } else {
                     let l = 1 + rng.below(2);
                     let w = rng.string(l, "ab");
                     enc.push_str(&w);
                     dec.push_str(&w);
                 }
             }
             (enc, dec)
         }
         let mut rng = anneal_prelude::Rng::new(3009);
         for _ in 0..300 {
             let (enc, dec) = gen(&mut rng, 3);
             check!(format!("s = {enc:?}"), decode_string(&enc), dec);
         }
     }

     #[test]
     fn scale_1m_groups() {
         let s = "1[ab]".repeat(1_000_000);
         let out = decode_string(&s);
         check!("\\"1[ab]\\" × 1000000", (out.len(), &out[..4]), (2_000_000, "abab"));
     }
     """],
    [("approach", "At `[`, save what you have so far and the count; start fresh. At `]`, repeat what you built and append it to the saved text."),
     ("rust", "`std::mem::take(&mut current)` moves the String out and leaves an empty one: no clone.")],
    ("A stack of `(prefix, count)` frames handles any nesting depth. `mem::take` moves each partial string exactly where it's needed.", "O(output)", "O(output)"),
    "How would you stream the output instead of building it all in memory?",
    ["`std::mem::take` to move out of a `&mut`.", "A stack of frames for nested structure."],
    related=["S2", "L1"],
    wrong=dict(
        expand_innermost_repeatedly="""
            pub fn decode_string(s: &str) -> String {
                let mut s = s.to_string();
                while let Some(close) = s.find(']') {
                    let open = s[..close].rfind('[').expect("balanced brackets");
                    let start = s[..open].rfind(|c: char| !c.is_ascii_digit()).map_or(0, |i| i + 1);
                    let k: usize = s[start..open].parse().expect("a count before '['");
                    let inner = s[open + 1..close].repeat(k);
                    s.replace_range(start..=close, &inner);
                }
                s
            }
        """,
        single_digit_counts=DECODE_WRONG.replace("DIGIT", "k = usize::from(b - b'0')").replace("RESET", "k = 0;"),
        count_not_reset=DECODE_WRONG.replace("DIGIT", "k = k * 10 + usize::from(b - b'0')").replace("RESET", ""),
    ),
))

FIX_RPN_WRONG = """
    #[derive(Debug, PartialEq)]
    pub enum RpnError {
        NotEnoughOperands,
        BadToken(String),
        DivideByZero,
        LeftoverOperands,
    }

    /// Evaluates reverse Polish notation.
    pub fn eval(tokens: &[&str]) -> Result<i64, RpnError> {
        let mut stack: Vec<i64> = Vec::new();
        for &t in tokens {
            match t {
                "+" | "-" | "*" | "/" => {
                    POPS
                    stack.push(match t {
                        "+" => a + b,
                        "-" => a - b,
                        "*" => a * b,
                        _ => DIV,
                    });
                }
                _ => stack.push(t.parse().map_err(|_| RpnError::BadToken(t.to_string()))?),
            }
        }
        END
    }
"""

P.append(prob(
    "fix-pop-unwrap-on-bad-input", "Fix: pop().unwrap() on bad input", "medium", "monotonic-parsing", ["Result", "?", "error enums"],
    """
    `eval` evaluates reverse Polish notation, but panics on bad input. Make it return an `RpnError` instead.
    It must never panic, including on division by zero.
    """,
    """
    #[derive(Debug, PartialEq)]
    pub enum RpnError {
        NotEnoughOperands,
        BadToken(String),
        DivideByZero,
        LeftoverOperands,
    }

    /// Evaluates reverse Polish notation.
    pub fn eval(tokens: &[&str]) -> Result<i64, RpnError> {
        let mut stack: Vec<i64> = Vec::new();
        for &t in tokens {
            match t {
                "+" | "-" | "*" | "/" => {
                    let b = stack.pop().unwrap();
                    let a = stack.pop().unwrap();
                    stack.push(match t {
                        "+" => a + b,
                        "-" => a - b,
                        "*" => a * b,
                        _ => a / b,
                    });
                }
                _ => stack.push(t.parse().unwrap()),
            }
        }
        Ok(stack.pop().unwrap())
    }
    """,
    """
    #[derive(Debug, PartialEq)]
    pub enum RpnError {
        NotEnoughOperands,
        BadToken(String),
        DivideByZero,
        LeftoverOperands,
    }

    /// Evaluates reverse Polish notation.
    pub fn eval(tokens: &[&str]) -> Result<i64, RpnError> {
        let mut stack: Vec<i64> = Vec::new();
        for &t in tokens {
            match t {
                "+" | "-" | "*" | "/" => {
                    let b = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                    let a = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                    stack.push(match t {
                        "+" => a + b,
                        "-" => a - b,
                        "*" => a * b,
                        _ => a.checked_div(b).ok_or(RpnError::DivideByZero)?,
                    });
                }
                _ => stack.push(t.parse().map_err(|_| RpnError::BadToken(t.to_string()))?),
            }
        }
        let result = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
        if !stack.is_empty() {
            return Err(RpnError::LeftoverOperands);
        }
        Ok(result)
    }
    """,
    [T("ok", '["2","1","+","3","*"]', 'eval(&["2", "1", "+", "3", "*"])', "Ok(9)"),
     T("underflow", '["+"]', 'eval(&["+"])', "Err(RpnError::NotEnoughOperands)"),
     T("bad_token", '["1","x","+"]', 'eval(&["1", "x", "+"])', 'Err(RpnError::BadToken("x".to_string()))'),
     T("div_zero", '["1","0","/"]', 'eval(&["1", "0", "/"])', "Err(RpnError::DivideByZero)"),
     T("leftover", '["1","2"]', 'eval(&["1", "2"])', "Err(RpnError::LeftoverOperands)")],
    [T("empty", "[]", "eval(&[])", "Err(RpnError::NotEnoughOperands)"),
     T("one_operand", '["1","-"]', 'eval(&["1", "-"])', "Err(RpnError::NotEnoughOperands)"),
     T("bad_first", '["x"]', 'eval(&["x"])', 'Err(RpnError::BadToken("x".to_string()))'),
     T("order", '["3","5","-"]', 'eval(&["3", "5", "-"])', "Ok(-2)"),
     T("negative_numbers", '["-3","4","*"]', 'eval(&["-3", "4", "*"])', "Ok(-12)"),
     T("first_error_wins", '["1","0","/","x"]', 'eval(&["1", "0", "/", "x"])', "Err(RpnError::DivideByZero)"),
     T("unknown_operator", '["1","2","%"]', 'eval(&["1", "2", "%"])', 'Err(RpnError::BadToken("%".to_string()))'),
     T("max", '["9223372036854775807"]', 'eval(&["9223372036854775807"])', "Ok(i64::MAX)"),
     T("too_big", '["9223372036854775808"]', 'eval(&["9223372036854775808"])', 'Err(RpnError::BadToken("9223372036854775808".to_string()))'),
     T("empty_token", '[""]', 'eval(&[""])', 'Err(RpnError::BadToken(String::new()))'),
     T("division_truncates", '["-7","2","/"]', 'eval(&["-7", "2", "/"])', "Ok(-3)"),
     """
     #[test]
     fn random_vs_model() {
         fn model(tokens: &[&str]) -> Result<i64, RpnError> {
             let mut st: Vec<i64> = Vec::new();
             for &t in tokens {
                 if ["+", "-", "*", "/"].contains(&t) {
                     if st.len() < 2 {
                         return Err(RpnError::NotEnoughOperands);
                     }
                     let (b, a) = (st.pop().unwrap(), st.pop().unwrap());
                     st.push(match t {
                         "+" => a + b,
                         "-" => a - b,
                         "*" => a * b,
                         _ if b == 0 || (a == i64::MIN && b == -1) => return Err(RpnError::DivideByZero),
                         _ => a / b,
                     });
                 } else {
                     match t.parse() {
                         Ok(n) => st.push(n),
                         Err(_) => return Err(RpnError::BadToken(t.to_string())),
                     }
                 }
             }
             match st.len() {
                 0 => Err(RpnError::NotEnoughOperands),
                 1 => Ok(st[0]),
                 _ => Err(RpnError::LeftoverOperands),
             }
         }
         let mut rng = anneal_prelude::Rng::new(3010);
         let pool = ["+", "-", "*", "/", "0", "1", "-2", "3", "7", "q"];
         for _ in 0..400 {
             let n = rng.below(7);
             let tokens: Vec<&str> = (0..n).map(|_| *rng.pick(&pool)).collect();
             check!(format!("tokens = {tokens:?}"), eval(&tokens), model(&tokens));
         }
     }
     """,
     T("min_div_minus_one", '["-9223372036854775808","-1","/"]', 'eval(&["-9223372036854775808", "-1", "/"])', "Err(RpnError::DivideByZero)")],
    [("rust", "`stack.pop().ok_or(RpnError::NotEnoughOperands)?` turns `None` into an early `Err`."),
     ("rust", "`a.checked_div(b)` is `None` for division by zero, and also for `i64::MIN / -1`, which overflows."),
     ("edge case", "After the loop, exactly one value must be left.")],
    ("Every `unwrap` becomes an explicit error, and `?` keeps the happy path readable. `checked_div` covers both panicking divisions. (Overflow in `+ - *` would still panic in debug builds; `checked_add` and friends fix that the same way.)", "O(n)", "O(n)"),
    "Should `i64::MIN / -1` really be reported as division by zero? Design a better error.",
    ["`Option::ok_or` + `?` instead of `unwrap`.", "`checked_div` for panicking arithmetic."],
    mode="fix", rules=dict(methods=["unwrap", "expect", "unwrap_unchecked", "unwrap_or_default"]),
    related=["S1", "L8"],
    wrong=dict(
        ignores_leftovers=FIX_RPN_WRONG.replace("POPS", """let b = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                    let a = stack.pop().ok_or(RpnError::NotEnoughOperands)?;""").replace("DIV", "a.checked_div(b).ok_or(RpnError::DivideByZero)?").replace("END", "stack.pop().ok_or(RpnError::NotEnoughOperands)"),
        checks_zero_only=FIX_RPN_WRONG.replace("POPS", """let b = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                    let a = stack.pop().ok_or(RpnError::NotEnoughOperands)?;""").replace("DIV", """{
                            if b == 0 {
                                return Err(RpnError::DivideByZero);
                            }
                            a / b
                        }""").replace("END", """let result = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
        if !stack.is_empty() {
            return Err(RpnError::LeftoverOperands);
        }
        Ok(result)"""),
        swapped_operands=FIX_RPN_WRONG.replace("POPS", """let a = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                    let b = stack.pop().ok_or(RpnError::NotEnoughOperands)?;""").replace("DIV", "a.checked_div(b).ok_or(RpnError::DivideByZero)?").replace("END", """let result = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
        if !stack.is_empty() {
            return Err(RpnError::LeftoverOperands);
        }
        Ok(result)"""),
    ),
))

# ---------------------------------------------------------------- hard stacks

RECT_WRONG = """
    pub fn largest_rectangle(heights: &[u32]) -> u64 {
        let mut best = 0u64;
        let mut rising: Vec<usize> = Vec::new();
        for i in RANGE {
            let h = heights.get(i).copied().unwrap_or(0);
            while let Some(&top) = rising.last() {
                if heights[top] < h {
                    break;
                }
                rising.pop();
                let left = rising.last().map_or(0, |&l| l + 1);
                best = best.max(AREA);
            }
            rising.push(i);
        }
        best
    }
"""

P.append(prob(
    "largest-rectangle-in-histogram", "Largest rectangle in histogram", "hard", "hard-stacks", ["monotonic stack", "u64"],
    """
    `heights` are bar heights of width 1. Return the area of the largest rectangle that fits inside the histogram.
    """,
    """
    pub fn largest_rectangle(heights: &[u32]) -> u64 {
        todo!()
    }
    """,
    """
    pub fn largest_rectangle(heights: &[u32]) -> u64 {
        let mut best = 0u64;
        // Indices of bars with increasing heights; each is the tallest bar its rectangle can use.
        let mut rising: Vec<usize> = Vec::new();
        for i in 0..=heights.len() {
            let h = heights.get(i).copied().unwrap_or(0);
            while let Some(&top) = rising.last() {
                if heights[top] < h {
                    break;
                }
                rising.pop();
                let left = rising.last().map_or(0, |&l| l + 1);
                best = best.max(u64::from(heights[top]) * (i - left) as u64);
            }
            rising.push(i);
        }
        best
    }
    """,
    [T("example", "[2,1,5,6,2,3]", "largest_rectangle(&[2, 1, 5, 6, 2, 3])", "10"),
     T("two", "[2,4]", "largest_rectangle(&[2, 4])", "4"),
     T("empty", "[]", "largest_rectangle(&[])", "0"),
     T("flat", "[3,3,3]", "largest_rectangle(&[3, 3, 3])", "9"),
     T("valley", "[5,0,5]", "largest_rectangle(&[5, 0, 5])", "5")],
    [T("single", "[7]", "largest_rectangle(&[7])", "7"),
     T("increasing", "[1,2,3,4,5]", "largest_rectangle(&[1, 2, 3, 4, 5])", "9"),
     T("decreasing", "[5,4,3,2,1]", "largest_rectangle(&[5, 4, 3, 2, 1])", "9"),
     T("zeros", "[0,0]", "largest_rectangle(&[0, 0])", "0"),
     T("u32_max", "[u32::MAX]", "largest_rectangle(&[u32::MAX])", "4_294_967_295"),
     T("two_max", "[u32::MAX, u32::MAX]", "largest_rectangle(&[u32::MAX, u32::MAX])", "8_589_934_590"),
     T("classic", "[6,2,5,4,5,1,6]", "largest_rectangle(&[6, 2, 5, 4, 5, 1, 6])", "12"),
     T("dip", "[2,1,2]", "largest_rectangle(&[2, 1, 2])", "3"),
     T("zero_splits", "[4,2,0,3,2,5]", "largest_rectangle(&[4, 2, 0, 3, 2, 5])", "6"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(3011);
         for _ in 0..300 {
             let n = rng.below(10);
             let h: Vec<u32> = rng.vec(n, 0, 6);
             let mut want = 0u64;
             for i in 0..n {
                 let mut low = u32::MAX;
                 for j in i..n {
                     low = low.min(h[j]);
                     want = want.max(u64::from(low) * (j - i + 1) as u64);
                 }
             }
             check!(format!("heights = {h:?}"), largest_rectangle(&h), want);
         }
     }

     #[test]
     fn scale_200k_increasing() {
         let h: Vec<u32> = (1..=200_000).collect();
         check!("heights = [1, 2, …, 200000]", largest_rectangle(&h), 10_000_100_000);
     }
     """,
     T("huge", "10⁵ bars of height 10⁹", "largest_rectangle(&h)", "100_000_000_000_000", setup="let h = vec![1_000_000_000u32; 100_000];")],
    [("approach", "For each bar, the widest rectangle of its height stretches to the nearest lower bar on each side. A stack of rising heights finds both."),
     ("rust", "`heights.get(i).copied().unwrap_or(0)` adds a height-0 sentinel at the end, which flushes the stack."),
     ("edge case", "Area can exceed `u32`: 10⁵ × 10⁹. Multiply in `u64`.")],
    ("When a bar is popped, the bar that pops it is its right limit and the new top is its left limit. Every bar is pushed and popped once.", "O(n)", "O(n)"),
    "Use this to find the largest rectangle of 1s in a binary matrix.",
    ["Monotonic stacks for nearest-smaller boundaries.", "Sentinels via `get(..).unwrap_or(..)`."],
    wrong=dict(
        expand_each_bar="""
            pub fn largest_rectangle(heights: &[u32]) -> u64 {
                let mut best = 0u64;
                for i in 0..heights.len() {
                    let (mut l, mut r) = (i, i);
                    while l > 0 && heights[l - 1] >= heights[i] {
                        l -= 1;
                    }
                    while r + 1 < heights.len() && heights[r + 1] >= heights[i] {
                        r += 1;
                    }
                    best = best.max(u64::from(heights[i]) * (r - l + 1) as u64);
                }
                best
            }
        """,
        u32_area=RECT_WRONG.replace("RANGE", "0..=heights.len()").replace("AREA", "u64::from(heights[top] * (i - left) as u32)"),
        no_final_flush=RECT_WRONG.replace("RANGE", "0..heights.len()").replace("AREA", "u64::from(heights[top]) * (i - left) as u64"),
    ),
))

CALC_WRONG = """
    pub fn calculate(s: &str) -> i64 {
        let mut saved: Vec<(i64, i64)> = Vec::new();
        let (mut sum, mut sign, mut num) = (0i64, 1i64, 0i64);
        for b in s.bytes() {
            match b {
                b'0'..=b'9' => DIGIT,
                b'+' | b'-' => {
                    sum += sign * num;
                    num = 0;
                    sign = if b == b'+' { 1 } else { -1 };
                }
                b'(' => {
                    saved.push((sum, sign));
                    sum = 0;
                    sign = 1;
                }
                b')' => {
                    sum += sign * num;
                    num = 0;
                    let (outer, outer_sign) = saved.pop().expect("balanced parentheses");
                    let _ = outer_sign;
                    CLOSE
                    sign = 1;
                }
                _ => {}
            }
        }
        sum + sign * num
    }
"""

P.append(prob(
    "basic-calculator", "Basic calculator", "hard", "hard-stacks", ["parsing", "stack of (sum, sign)"],
    """
    Evaluate an expression with non-negative integers, `+`, `-`, parentheses and spaces. `-` can be unary,
    as in `-(2+3)`. The input is valid.
    """,
    """
    pub fn calculate(s: &str) -> i64 {
        todo!()
    }
    """,
    """
    pub fn calculate(s: &str) -> i64 {
        // On '(': save the running sum and the sign in front of the parenthesis.
        let mut saved: Vec<(i64, i64)> = Vec::new();
        let (mut sum, mut sign, mut num) = (0i64, 1i64, 0i64);
        for b in s.bytes() {
            match b {
                b'0'..=b'9' => num = num * 10 + i64::from(b - b'0'),
                b'+' | b'-' => {
                    sum += sign * num;
                    num = 0;
                    sign = if b == b'+' { 1 } else { -1 };
                }
                b'(' => {
                    saved.push((sum, sign));
                    sum = 0;
                    sign = 1;
                }
                b')' => {
                    sum += sign * num;
                    num = 0;
                    let (outer, outer_sign) = saved.pop().expect("balanced parentheses");
                    sum = outer + outer_sign * sum;
                    sign = 1;
                }
                _ => {}
            }
        }
        sum + sign * num
    }
    """,
    [T("plus", '"1 + 1"', 'calculate("1 + 1")', "2"),
     T("spaces", '" 2-1 + 2 "', 'calculate(" 2-1 + 2 ")', "3"),
     T("parens", '"(1+(4+5+2)-3)+(6+8)"', 'calculate("(1+(4+5+2)-3)+(6+8)")', "23"),
     T("unary", '"-(2+3)"', 'calculate("-(2+3)")', "-5"),
     T("double_negative", '"1-(     -2)"', 'calculate("1-(     -2)")', "3")],
    [T("nested_unary", '"- (3 + (4 + 5))"', 'calculate("- (3 + (4 + 5))")', "-12"),
     T("zero", '"0"', 'calculate("0")', "0"),
     T("i32_max", '"2147483647"', 'calculate("2147483647")', "2_147_483_647"),
     T("beyond_i32", '"2147483647 + 2147483647"', 'calculate("2147483647 + 2147483647")', "4_294_967_294"),
     T("leading_minus", '"- 1"', 'calculate("- 1")', "-1"),
     T("minus_distributes", '"1-(2-3)"', 'calculate("1-(2-3)")', "2"),
     T("redundant_parens", '"(((7)))"', 'calculate("(((7)))")', "7"),
     T("multi_digit", '"12 - 3"', 'calculate("12 - 3")', "9"),
     T("chain", '"10 - (2 + 3) - 4"', 'calculate("10 - (2 + 3) - 4")', "1"),
     """
     #[test]
     fn random_vs_tree() {
         // A random expression tree, printed with + - unary minus and parentheses, and its value.
         fn gen(rng: &mut anneal_prelude::Rng, depth: u32) -> (String, i64) {
             let pick = if depth == 0 { 0 } else { rng.below(5) };
             match pick {
                 0 => {
                     let n = rng.int(0, 99);
                     (n.to_string(), n)
                 }
                 1 | 2 => {
                     let (a, x) = gen(rng, depth - 1);
                     let (b, y) = gen(rng, depth - 1);
                     if pick == 1 { (format!("{a} + ({b})"), x + y) } else { (format!("{a}-({b})"), x - y) }
                 }
                 3 => {
                     let (a, x) = gen(rng, depth - 1);
                     (format!("-({a})"), -x)
                 }
                 _ => {
                     let (a, x) = gen(rng, depth - 1);
                     (format!("( {a} )"), x)
                 }
             }
         }
         let mut rng = anneal_prelude::Rng::new(3012);
         for _ in 0..300 {
             let (s, want) = gen(&mut rng, 4);
             check!(format!("s = {s:?}"), calculate(&s), want);
         }
     }

     #[test]
     fn scale_100k_nested() {
         let s = format!("{}1{}", "(".repeat(100_000), ")".repeat(100_000));
         check!("100000 nested parentheses around 1", calculate(&s), 1);
     }

     #[test]
     fn scale_100k_terms() {
         let s = "10-9+".repeat(100_000) + "0";
         check!("\\"10-9+\\" × 100000, then 0", calculate(&s), 100_000);
     }
     """,
     T("deep", "5000 nested parentheses around 1", "calculate(&s)", "1", setup='let s = format!("{}1{}", "(".repeat(5000), ")".repeat(5000));')],
    [("approach", "Without parentheses, keep a running sum and the sign of the next number. A parenthesis is a sub-expression with its own sum."),
     ("approach", "At `(`, push the outer sum and the sign in front of the parenthesis; at `)`, fold the inner sum back in with that sign."),
     ("edge case", "A leading `-` is just `0 - …`: the running sum starts at 0, so no special case is needed.")],
    ("An explicit stack means deep nesting can't overflow the call stack, unlike a recursive-descent parser.", "O(n)", "O(depth)"),
    "Add `*` and `/` with the usual precedence. What extra state do you need?",
    ["Iterative parsing with an explicit stack.", "Unary minus as '0 minus'."],
    wrong=dict(
        ignores_sign_before_paren=CALC_WRONG.replace("DIGIT", "num = num * 10 + i64::from(b - b'0')").replace("CLOSE", "sum = outer + sum;"),
        single_digit_numbers=CALC_WRONG.replace("DIGIT", "num = i64::from(b - b'0')").replace("CLOSE", "sum = outer + outer_sign * sum;"),
    ),
))

FREQ_WRONG = """
    use std::collections::HashMap;

    #[derive(Default)]
    pub struct FreqStack {
        freq: HashMap<i32, usize>,
        groups: Vec<Vec<i32>>,
    }

    impl FreqStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            let f = self.freq.entry(x).or_insert(0);
            *f += 1;
            if *f > self.groups.len() {
                self.groups.push(Vec::new());
            }
            self.groups[*f - 1].push(x);
        }

        #[allow(unreachable_code)]
        pub fn pop(&mut self) -> Option<i32> {
            let top = self.groups.last_mut()?;
            TAKE
            if top.is_empty() {
                self.groups.pop();
            }
            FORGET
            match self.freq.get_mut(&x) {
                Some(f) if *f > 1 => *f -= 1,
                _ => {
                    self.freq.remove(&x);
                }
            }
            Some(x)
        }
    }
"""

P.append(prob(
    "max-frequency-stack", "Maximum frequency stack", "hard", "hard-stacks", ["HashMap", "Vec<Vec<_>>"],
    """
    `push(x)` adds `x`. `pop()` removes and returns the most frequent element; if several are equally frequent,
    the one pushed most recently. `None` when empty. Both in O(1).
    """,
    """
    use std::collections::HashMap;

    #[derive(Default)]
    pub struct FreqStack {
        freq: HashMap<i32, usize>,
        /// groups[f - 1]: elements that reached frequency f, in push order.
        groups: Vec<Vec<i32>>,
    }

    impl FreqStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            todo!()
        }

        pub fn pop(&mut self) -> Option<i32> {
            todo!()
        }
    }
    """,
    """
    use std::collections::HashMap;

    #[derive(Default)]
    pub struct FreqStack {
        freq: HashMap<i32, usize>,
        /// groups[f - 1]: elements that reached frequency f, in push order.
        groups: Vec<Vec<i32>>,
    }

    impl FreqStack {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn push(&mut self, x: i32) {
            let f = self.freq.entry(x).or_insert(0);
            *f += 1;
            if *f > self.groups.len() {
                self.groups.push(Vec::new());
            }
            self.groups[*f - 1].push(x);
        }

        pub fn pop(&mut self) -> Option<i32> {
            let top = self.groups.last_mut()?;
            let x = top.pop()?;
            if top.is_empty() {
                self.groups.pop();
            }
            match self.freq.get_mut(&x) {
                Some(f) if *f > 1 => *f -= 1,
                _ => {
                    self.freq.remove(&x);
                }
            }
            Some(x)
        }
    }
    """,
    [T("example", "push 5,7,5,7,4,5; pop four times", "(s.pop(), s.pop(), s.pop(), s.pop())", "(Some(5), Some(7), Some(5), Some(4))",
       setup="let mut s = FreqStack::new();\nfor x in [5, 7, 5, 7, 4, 5] {\n    s.push(x);\n}"),
     T("empty", "new stack", "FreqStack::new().pop()", "None"),
     T("tie_most_recent", "push 1, 2; pop, pop", "(s.pop(), s.pop())", "(Some(2), Some(1))", setup="let mut s = FreqStack::new();\ns.push(1);\ns.push(2);"),
     T("frequency_drops", "push 3, 3, 4; pop three times", "(s.pop(), s.pop(), s.pop())", "(Some(3), Some(4), Some(3))", setup="let mut s = FreqStack::new();\nfor x in [3, 3, 4] {\n    s.push(x);\n}"),
     T("frequency_beats_recency", "push 1, 1, 2; pop", "s.pop()", "Some(1)", setup="let mut s = FreqStack::new();\nfor x in [1, 1, 2] {\n    s.push(x);\n}")],
    [T("drains", "push 5,7,5,7,4,5; pop seven times", "out", "vec![Some(5), Some(7), Some(5), Some(4), Some(7), Some(5), None]",
       setup="let mut s = FreqStack::new();\nfor x in [5, 7, 5, 7, 4, 5] {\n    s.push(x);\n}\nlet out: Vec<Option<i32>> = (0..7).map(|_| s.pop()).collect();"),
     T("push_after_pop", "push 1,1; pop; push 2; pop; pop", "(a, b, c)", "(Some(1), Some(2), Some(1))",
       setup="let mut s = FreqStack::new();\ns.push(1);\ns.push(1);\nlet a = s.pop();\ns.push(2);\nlet b = s.pop();\nlet c = s.pop();"),
     T("one_value", "push 9 three times; pop four times", "(s.pop(), s.pop(), s.pop(), s.pop())", "(Some(9), Some(9), Some(9), None)", setup="let mut s = FreqStack::new();\nfor _ in 0..3 {\n    s.push(9);\n}"),
     T("extremes", "push i32::MIN, i32::MAX, i32::MIN; pop three times", "(s.pop(), s.pop(), s.pop())", "(Some(i32::MIN), Some(i32::MAX), Some(i32::MIN))",
       setup="let mut s = FreqStack::new();\nfor x in [i32::MIN, i32::MAX, i32::MIN] {\n    s.push(x);\n}"),
     T("tie_not_by_value", "push 9, 1; pop", "s.pop()", "Some(1)", setup="let mut s = FreqStack::new();\ns.push(9);\ns.push(1);"),
     T("negatives", "push -1, -2; pop", "s.pop()", "Some(-2)", setup="let mut s = FreqStack::new();\ns.push(-1);\ns.push(-2);"),
     T("refill_after_empty", "push 1; pop; push 1, 2; pop", "(s.pop(), { s.push(1); s.push(2); s.pop() }, s.pop(), s.pop())", "(Some(1), Some(2), Some(1), None)", setup="let mut s = FreqStack::new();\ns.push(1);"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(3013);
         for _ in 0..300 {
             let mut s = FreqStack::new();
             let mut model: Vec<i32> = Vec::new();
             let mut log = Vec::new();
             let n = rng.below(24);
             for _ in 0..n {
                 if rng.below(3) > 0 {
                     let x = rng.int(0, 3) as i32;
                     s.push(x);
                     model.push(x);
                     log.push(format!("push {x}"));
                 } else {
                     let counts: Vec<usize> = model.iter().map(|&x| model.iter().filter(|&&y| y == x).count()).collect();
                     let want = counts.iter().max().map(|&b| {
                         let i = counts.iter().rposition(|&c| c == b).unwrap();
                         model.remove(i)
                     });
                     log.push("pop".to_string());
                     check!(log.join(", "), s.pop(), want);
                 }
             }
         }
     }

     #[test]
     fn scale_200k() {
         let mut s = FreqStack::new();
         for i in 0..100_000 {
             s.push(i % 50_000);
         }
         let mut first = Vec::new();
         for _ in 0..3 {
             first.push(s.pop());
         }
         let mut rest = 0;
         while s.pop().is_some() {
             rest += 1;
         }
         check!("push i % 50000 for i in 0..100000; pop everything", (first, rest), (vec![Some(49_999), Some(49_998), Some(49_997)], 99_997));
     }
     """],
    [("approach", "Group elements by the frequency they had when pushed. The last group holds the most frequent, and its last element is the most recent."),
     ("rust", "`self.freq.entry(x)` and `self.groups` are different fields, so both can be borrowed mutably at once.")],
    ("An element with frequency 3 sits in groups 1, 2 and 3. Popping from the top group automatically exposes its earlier copies in lower groups.", "O(1)", "O(n)"),
    "How would you support `pop` of the least frequent element too?",
    ["Bucketing by frequency: `Vec<Vec<T>>`.", "Split borrows across struct fields."],
    related=["S4"],
    wrong=dict(
        count_on_every_pop="""
            use std::collections::HashMap;

            #[derive(Default)]
            pub struct FreqStack {
                items: Vec<i32>,
            }

            impl FreqStack {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn push(&mut self, x: i32) {
                    self.items.push(x);
                }

                pub fn pop(&mut self) -> Option<i32> {
                    let mut freq: HashMap<i32, usize> = HashMap::new();
                    for &x in &self.items {
                        *freq.entry(x).or_insert(0) += 1;
                    }
                    let best = *freq.values().max()?;
                    let i = self.items.iter().rposition(|x| freq[x] == best)?;
                    Some(self.items.remove(i))
                }
            }
        """,
        largest_value_on_tie=FREQ_WRONG.replace("TAKE", """let i = (0..top.len()).max_by_key(|&i| top[i])?;
            let x = top.remove(i);""").replace("FORGET", ""),
        count_not_decremented=FREQ_WRONG.replace("TAKE", "let x = top.pop()?;").replace("FORGET", "return Some(x);"),
    ),
))

P.append(prob(
    "shortest-subarray-with-sum-at-least-k", "Shortest subarray with sum at least K", "hard", "hard-stacks", ["prefix sums", "monotonic deque"],
    """
    Return the length of the shortest non-empty contiguous subarray whose sum is at least `k`, or `None`.
    `nums` can contain negative numbers, so a plain sliding window doesn't work.
    """,
    """
    pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
        todo!()
    }
    """,
    """
    use std::collections::VecDeque;

    pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
        let mut prefix = vec![0i64; nums.len() + 1];
        for (i, &x) in nums.iter().enumerate() {
            prefix[i + 1] = prefix[i] + x;
        }
        let mut best: Option<usize> = None;
        // Start indices with increasing prefix sums: the only useful left ends.
        let mut starts: VecDeque<usize> = VecDeque::new();
        for (j, &pj) in prefix.iter().enumerate() {
            while let Some(&i) = starts.front() {
                if pj - prefix[i] < k {
                    break;
                }
                best = Some(best.map_or(j - i, |b| b.min(j - i)));
                starts.pop_front();
            }
            while starts.back().is_some_and(|&i| prefix[i] >= pj) {
                starts.pop_back();
            }
            starts.push_back(j);
        }
        best
    }
    """,
    [T("single", "[1], k = 1", "shortest_subarray(&[1], 1)", "Some(1)"),
     T("impossible", "[1,2], k = 4", "shortest_subarray(&[1, 2], 4)", "None"),
     T("negative_inside", "[2,-1,2], k = 3", "shortest_subarray(&[2, -1, 2], 3)", "Some(3)"),
     T("mixed", "[84,-37,32,40,95], k = 167", "shortest_subarray(&[84, -37, 32, 40, 95], 167)", "Some(3)"),
     T("whole_array", "[1,1,1], k = 3", "shortest_subarray(&[1, 1, 1], 3)", "Some(3)")],
    [T("empty", "[], k = 1", "shortest_subarray(&[], 1)", "None"),
     T("all_negative", "[-1,-2], k = 1", "shortest_subarray(&[-1, -2], 1)", "None"),
     T("alternating", "[1,-1,1,-1,1], k = 1", "shortest_subarray(&[1, -1, 1, -1, 1], 1)", "Some(1)"),
     T("two_windows", "[-1,5,-1,5], k = 9", "shortest_subarray(&[-1, 5, -1, 5], 9)", "Some(3)"),
     T("best_is_not_first", "[48,99,37,4,-31], k = 140", "shortest_subarray(&[48, 99, 37, 4, -31], 140)", "Some(2)"),
     T("drop_after_peak", "[17,85,93,-45,-21], k = 150", "shortest_subarray(&[17, 85, 93, -45, -21], 150)", "Some(2)"),
     T("large_values", "[10⁹, 10⁹, 10⁹], k = 3·10⁹", "shortest_subarray(&[1_000_000_000, 1_000_000_000, 1_000_000_000], 3_000_000_000)", "Some(3)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(3014);
         for _ in 0..400 {
             let n = rng.below(10);
             let nums: Vec<i64> = rng.vec(n, -10, 10);
             let k = rng.int(1, 20);
             let mut want: Option<usize> = None;
             for i in 0..n {
                 let mut sum = 0;
                 for j in i..n {
                     sum += nums[j];
                     if sum >= k && want.is_none_or(|w| j - i + 1 < w) {
                         want = Some(j - i + 1);
                     }
                 }
             }
             check!(format!("nums = {nums:?}, k = {k}"), shortest_subarray(&nums, k), want);
         }
     }

     #[test]
     fn scale_200k_unreachable() {
         let v = vec![1i64; 200_000];
         check!("200000 ones, k = 10⁹", shortest_subarray(&v, 1_000_000_000), None);
     }
     """,
     T("negative_prefix", "[-28,81,-20,28,-29], k = 89", "shortest_subarray(&[-28, 81, -20, 28, -29], 89)", "Some(3)"),
     T("big", "10⁵ values, k needs the last two", "shortest_subarray(&v, 3_000_000_000)", "Some(2)",
       setup="let mut v = vec![1i64; 100_000];\nv[99_998] = 1_500_000_000;\nv[99_999] = 1_500_000_000;")],
    [("approach", "A subarray sum is `prefix[j] - prefix[i]`. For each end `j`, you want the latest start `i` with `prefix[i] ≤ prefix[j] - k`."),
     ("approach", "Keep candidate starts in a deque with increasing prefix sums. A start with a larger prefix than a later one is never useful."),
     ("rust", "Pop from the front while the window qualifies (record the length), and from the back while the new prefix is smaller.")],
    ("Each index enters and leaves the deque once. Popping a start from the front after using it is safe, because any later end would only give a longer subarray.", "O(n)", "O(n)"),
    "Why does the two-pointer sliding window fail with negative numbers?",
    ["Prefix sums + a monotonic deque.", "`VecDeque` as a double-ended work list."],
    related=["D2", "S5"],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "k ≥ 1"],
    wrong=dict(
        sliding_window="""
            pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
                let (mut sum, mut left, mut best) = (0i64, 0usize, None::<usize>);
                for right in 0..nums.len() {
                    sum += nums[right];
                    while sum >= k && left <= right {
                        best = Some(best.map_or(right - left + 1, |b| b.min(right - left + 1)));
                        sum -= nums[left];
                        left += 1;
                    }
                }
                best
            }
        """,
        every_start="""
            pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
                let mut best: Option<usize> = None;
                for i in 0..nums.len() {
                    let mut sum = 0;
                    for j in i..nums.len() {
                        sum += nums[j];
                        if sum >= k {
                            best = Some(best.map_or(j - i + 1, |b| b.min(j - i + 1)));
                            break;
                        }
                    }
                }
                best
            }
        """,
        no_back_pops="""
            use std::collections::VecDeque;

            pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
                let mut prefix = vec![0i64; nums.len() + 1];
                for (i, &x) in nums.iter().enumerate() {
                    prefix[i + 1] = prefix[i] + x;
                }
                let mut best: Option<usize> = None;
                let mut starts: VecDeque<usize> = VecDeque::new();
                for (j, &pj) in prefix.iter().enumerate() {
                    while let Some(&i) = starts.front() {
                        if pj - prefix[i] < k {
                            break;
                        }
                        best = Some(best.map_or(j - i, |b| b.min(j - i)));
                        starts.pop_front();
                    }
                    starts.push_back(j);
                }
                best
            }
        """,
    ),
))

STAGES = [
    ("stack-basics", "Stack basics", "easy"),
    ("monotonic-parsing", "Monotonic & parsing", "medium"),
    ("hard-stacks", "Hard stacks", "hard"),
]

# Companies known to ask each problem (names from COMPANIES in crates/content/src/model.rs).
COMPANIES = {
    "valid-parentheses": ["Amazon", "Meta", "Google", "Microsoft", "Apple", "Bloomberg", "LinkedIn"],
    "queue-using-stacks": ["Amazon", "Microsoft", "Apple", "Bloomberg", "Goldman Sachs"],
    "baseball-game": ["Amazon"],
    "min-stack": ["Amazon", "Bloomberg", "Google", "Microsoft", "Meta", "Apple", "Goldman Sachs"],
    "evaluate-rpn": ["LinkedIn", "Amazon", "Google", "Microsoft", "Meta"],
    "daily-temperatures": ["Meta", "Amazon", "Google", "Microsoft", "Uber", "Salesforce"],
    "car-fleet": ["Google", "Amazon", "Meta"],
    "asteroid-collision": ["Amazon", "Google", "Microsoft", "Meta", "Uber", "Salesforce", "DoorDash"],
    "decode-string": ["Google", "Amazon", "Meta", "Microsoft", "Bloomberg", "Apple", "Atlassian"],
    "largest-rectangle-in-histogram": ["Amazon", "Google", "Microsoft", "Meta", "Apple", "Uber"],
    "basic-calculator": ["Google", "Meta", "Amazon", "Microsoft", "Uber", "DoorDash"],
    "max-frequency-stack": ["Amazon", "Apple", "Google", "Microsoft"],
    "shortest-subarray-with-sum-at-least-k": ["Google", "Amazon", "Meta", "Goldman Sachs"],
}
tag_companies(P, COMPANIES)

if __name__ == "__main__":
    n = write_track("d3-stacks-queues", "D3", "Stacks & queues", "D", "core", 3,
                    "Vec as a stack, VecDeque as a queue, and monotonic stacks for nearest-greater problems. Parsers that return errors instead of panicking.",
                    STAGES, P)
    print("D3", n)
