from author import T, prob, write_track

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
     T("nested", '"{[]}"', 'is_valid("{[]}")', "true")],
    [T("interleaved", '"([)]"', 'is_valid("([)]")', "false"),
     T("unclosed", '"(("', 'is_valid("((")', "false"),
     T("close_first", '")"', 'is_valid(")")', "false"),
     T("empty", '""', 'is_valid("")', "true"),
     T("deep", "10⁵ nested pairs", "is_valid(&s)", "true", setup='let s = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));')],
    [("approach", "The most recent unclosed bracket must be the next to close. That's a stack."),
     ("rust", "Push the closer you expect, not the opener; then a close is just `pop() == Some(b)`.")],
    ("Pushing the expected closing byte turns the check into one comparison. `pop()` returning `None` on an extra closer falls out of the same comparison.", "O(n)", "O(n)"),
    "How would you report the position of the first bad bracket?",
    ["`Vec` as a stack: `push` / `pop` / `last`.", "`match` on byte literals."],
    examples=[('"()[]{}"', "true"), ('"([)]"', "false")],
))

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
     T("len", "push 3 values, pop 1", "(q.len(), q.is_empty())", "(2, false)", setup="let mut q = TwoStackQueue::new();\nfor x in [4, 5, 6] {\n    q.push(x);\n}\nq.pop();")],
    [T("empty", "new queue", "(q.peek(), q.pop(), q.is_empty())", "(None, None, true)", setup="let mut q = TwoStackQueue::new();"),
     T("million_ops", "10⁶ pushes interleaved with pops", "(last, q.len())", "(Some(499_999), 500_000)",
       setup="let mut q = TwoStackQueue::new();\nlet mut last = None;\nfor i in 0..1_000_000 {\n    q.push(i);\n    if i % 2 == 1 {\n        last = q.pop();\n    }\n}")],
    [("approach", "Push onto one stack. Pop from the other; when it's empty, move everything across, which reverses the order."),
     ("rust", "`self.outbox.extend(self.inbox.drain(..).rev())` moves all elements in one call.")],
    ("Each element is pushed and popped at most twice, so n operations cost O(n) in total even though a single `pop` can be O(n).", "O(1) amortised", "O(n)"),
    "Why would `VecDeque` be the better choice in real code?",
    ["Amortised analysis: pay for a move once.", "`drain(..).rev()` into `extend`."],
    related=["S5"],
))

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
     T("negatives", '["5","-2","4","C","D","9","+","+"]', 'cal_points(&["5", "-2", "4", "C", "D", "9", "+", "+"])', "Some(27)")],
    [T("plus_too_early", '["1","+"]', 'cal_points(&["1", "+"])', "None"),
     T("not_a_number", '["x"]', 'cal_points(&["x"])', "None"),
     T("cancel_all", '["1","C"]', 'cal_points(&["1", "C"])', "Some(0)"),
     T("cancel_nothing", '["C"]', 'cal_points(&["C"])', "None")],
    [("rust", "`let [.., a, b] = scores[..] else { return None };` takes the last two elements, or bails if there aren't two."),
     ("rust", "`?` works on `Option`: `scores.last()?`, `scores.pop()?`, `op.parse().ok()?`.")],
    ("Slice patterns and `?` on `Option` turn every 'not enough scores' check into part of the happy path.", "O(n)", "O(n)"),
    "How would you return which operation was invalid instead of `None`?",
    ["Slice patterns with `let ... else`.", "`?` on `Option`."],
    related=["S1"],
))

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
     T("empty", "new stack", "(s.min(), s.top(), s.pop())", "(None, None, None)", setup="let mut s = MinStack::new();")],
    [T("duplicates", "push 1, 1; pop; min", "(s.pop(), s.min())", "(Some(1), Some(1))", setup="let mut s = MinStack::new();\ns.push(1);\ns.push(1);"),
     T("extremes", "push i32::MAX, i32::MIN", "s.min()", "Some(i32::MIN)", setup="let mut s = MinStack::new();\ns.push(i32::MAX);\ns.push(i32::MIN);")],
    [("approach", "When something is popped, the minimum must go back to what it was. Store the minimum-so-far next to each value.")],
    ("A stack of `(value, min_below)` pairs costs one extra `i32` per element and makes every operation O(1).", "O(1)", "O(n)"),
    "Can you do it with O(1) extra space beyond the stack itself?",
    ["Stacks of tuples carrying derived state."],
))

# ---------------------------------------------------------------- monotonic & parsing (medium)

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
     T("division", '["4","13","5","/","+"]', 'eval_rpn(&["4", "13", "5", "/", "+"])', "6")],
    [T("long", '["10","6","9","3","+","-11","*","/","*","17","+","5","+"]', 'eval_rpn(&["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])', "22"),
     T("single", '["-7"]', 'eval_rpn(&["-7"])', "-7"),
     T("order_matters", '["3","5","-"]', 'eval_rpn(&["3", "5", "-"])', "-2")],
    [("approach", "Numbers go on a stack; an operator pops two and pushes the result."),
     ("edge case", "Pop `b` first, then `a`: `a - b`, not `b - a`. And `\"-11\"` is a number, not an operator.")],
    ("Trying `parse` first means negative numbers are never mistaken for the `-` operator. Rust's `/` truncates toward zero, as required.", "O(n)", "O(n)"),
    "The input isn't always valid in practice. How would the signature change? (Next problem: the fix.)",
    ["Operand order when popping.", "Parse first, then treat the token as an operator."],
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
     T("rising", "[30,40,50,60]", "daily_temperatures(&[30, 40, 50, 60])", "vec![1, 1, 1, 0]")],
    [T("falling", "[60,50,40]", "daily_temperatures(&[60, 50, 40])", "vec![0, 0, 0]"),
     T("equal_is_not_warmer", "[50,50,51]", "daily_temperatures(&[50, 50, 51])", "vec![2, 1, 0]"),
     T("long_wait", "10⁵ falling days, then a hot one", "ok", "true",
       setup="let n = 100_000;\nlet mut t: Vec<i32> = (0..n as i32).map(|i| 50_000 - i).collect();\nt.push(100_000);\nlet ans = daily_temperatures(&t);\nlet ok = (0..n).all(|i| ans[i] == n - i) && ans[n] == 0;")],
    [("approach", "Keep the days that haven't found a warmer day yet. A new day resolves every colder day on top."),
     ("rust", "Store indices in the stack, not temperatures: you need the index for the distance and can look the temperature up.")],
    ("Each index is pushed and popped once, so the nested loop is O(n) overall. The stack's temperatures always decrease from bottom to top.", "O(n)", "O(n)"),
    "How would you answer 'days until at least 5 degrees warmer'?",
    ["Monotonic stacks of indices."],
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
     T("one_car", "target 10, position [3], speed [3]", "car_fleet(10, &[3], &[3])", "1")],
    [T("all_merge", "target 100, position [0,2,4], speed [4,2,1]", "car_fleet(100, &[0, 2, 4], &[4, 2, 1])", "1"),
     T("meet_at_target", "target 10, position [0,5], speed [2,1]", "car_fleet(10, &[0, 5], &[2, 1])", "1"),
     T("float_trap", "target 10⁹; arrival times 10⁻¹⁸ apart, equal in f64", "car_fleet(1_000_000_000, &[0, 1], &[1_000_000_001, 1_000_000_000])", "2"),
     T("none", "no cars", "car_fleet(5, &[], &[])", "0")],
    [("approach", "Sort by distance to the target. Going backwards from the front car, a car forms a new fleet only if it would arrive later than the fleet ahead of it."),
     ("rust", "Compare arrival times `d1/s1 > d2/s2` as `d1 * s2 > d2 * s1` in `u64`, with no floating point.")],
    ("Cross-multiplying keeps the comparison exact; with `f64`, two nearly equal arrival times can compare the wrong way. `Option::is_none_or` handles the first car.", "O(n log n)", "O(n)"),
    "What if cars could also have different lengths?",
    ["Exact comparisons of ratios by cross-multiplication.", "Processing sorted items against a running 'fleet ahead'."],
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
     T("both_explode", "[8,-8]", "asteroid_collision(&[8, -8])", "vec![]")],
    [T("chain", "[10,2,-5]", "asteroid_collision(&[10, 2, -5])", "vec![10]"),
     T("moving_apart", "[-2,-1,1,2]", "asteroid_collision(&[-2, -1, 1, 2])", "vec![-2, -1, 1, 2]"),
     T("left_wins", "[1,-2,-2,-2]", "asteroid_collision(&[1, -2, -2, -2])", "vec![-2, -2, -2]")],
    [("approach", "Only a left-mover can hit a right-mover already on the stack. Keep colliding with the top until one side wins."),
     ("rust", "A labelled `continue 'next` skips the push when the new asteroid is destroyed.")],
    ("Each asteroid is pushed and popped at most once. The labelled continue reads more clearly than a `destroyed` flag.", "O(n)", "O(n)"),
    "What changes if asteroids can have different speeds?",
    ["Labelled loops.", "Resolving a new item against the top of a stack repeatedly."],
))

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
     T("nested", '"3[a2[c]]"', 'decode_string("3[a2[c]]")', '"accaccacc".to_string()')],
    [T("tail", '"2[abc]3[cd]ef"', 'decode_string("2[abc]3[cd]ef")', '"abcabccdcdcdef".to_string()'),
     T("plain", '"abc"', 'decode_string("abc")', '"abc".to_string()'),
     T("two_digits", '"10[a]"', 'decode_string("10[a]")', '"a".repeat(10)'),
     T("zero", '"0[x]y"', 'decode_string("0[x]y")', '"y".to_string()')],
    [("approach", "At `[`, save what you have so far and the count; start fresh. At `]`, repeat what you built and append it to the saved text."),
     ("rust", "`std::mem::take(&mut current)` moves the String out and leaves an empty one: no clone.")],
    ("A stack of `(prefix, count)` frames handles any nesting depth. `mem::take` moves each partial string exactly where it's needed.", "O(output)", "O(output)"),
    "How would you stream the output instead of building it all in memory?",
    ["`std::mem::take` to move out of a `&mut`.", "A stack of frames for nested structure."],
    related=["S2", "L1"],
))

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
     T("bad_token", '["1","x","+"]', 'eval(&["1", "x", "+"])', 'Err(RpnError::BadToken("x".to_string()))')],
    [T("div_zero", '["1","0","/"]', 'eval(&["1", "0", "/"])', "Err(RpnError::DivideByZero)"),
     T("leftover", '["1","2"]', 'eval(&["1", "2"])', "Err(RpnError::LeftoverOperands)"),
     T("empty", "[]", "eval(&[])", "Err(RpnError::NotEnoughOperands)"),
     T("min_div_minus_one", '["-9223372036854775808","-1","/"]', 'eval(&["-9223372036854775808", "-1", "/"])', "Err(RpnError::DivideByZero)")],
    [("rust", "`stack.pop().ok_or(RpnError::NotEnoughOperands)?` turns `None` into an early `Err`."),
     ("rust", "`a.checked_div(b)` is `None` for division by zero, and also for `i64::MIN / -1`, which overflows."),
     ("edge case", "After the loop, exactly one value must be left.")],
    ("Every `unwrap` becomes an explicit error, and `?` keeps the happy path readable. `checked_div` covers both panicking divisions. (Overflow in `+ - *` would still panic in debug builds; `checked_add` and friends fix that the same way.)", "O(n)", "O(n)"),
    "Should `i64::MIN / -1` really be reported as division by zero? Design a better error.",
    ["`Option::ok_or` + `?` instead of `unwrap`.", "`checked_div` for panicking arithmetic."],
    mode="fix", rules=dict(methods=["unwrap", "expect", "unwrap_unchecked", "unwrap_or_default"]),
    related=["S1", "L8"],
))

# ---------------------------------------------------------------- hard stacks

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
     T("two", "[2,4]", "largest_rectangle(&[2, 4])", "4")],
    [T("empty", "[]", "largest_rectangle(&[])", "0"),
     T("flat", "[3,3,3]", "largest_rectangle(&[3, 3, 3])", "9"),
     T("valley", "[5,0,5]", "largest_rectangle(&[5, 0, 5])", "5"),
     T("huge", "10⁵ bars of height 10⁹", "largest_rectangle(&h)", "100_000_000_000_000", setup="let h = vec![1_000_000_000u32; 100_000];")],
    [("approach", "For each bar, the widest rectangle of its height stretches to the nearest lower bar on each side. A stack of rising heights finds both."),
     ("rust", "`heights.get(i).copied().unwrap_or(0)` adds a height-0 sentinel at the end, which flushes the stack."),
     ("edge case", "Area can exceed `u32`: 10⁵ × 10⁹. Multiply in `u64`.")],
    ("When a bar is popped, the bar that pops it is its right limit and the new top is its left limit. Every bar is pushed and popped once.", "O(n)", "O(n)"),
    "Use this to find the largest rectangle of 1s in a binary matrix.",
    ["Monotonic stacks for nearest-smaller boundaries.", "Sentinels via `get(..).unwrap_or(..)`."],
))

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
     T("parens", '"(1+(4+5+2)-3)+(6+8)"', 'calculate("(1+(4+5+2)-3)+(6+8)")', "23")],
    [T("unary", '"-(2+3)"', 'calculate("-(2+3)")', "-5"),
     T("nested_unary", '"- (3 + (4 + 5))"', 'calculate("- (3 + (4 + 5))")', "-12"),
     T("double_negative", '"1-(     -2)"', 'calculate("1-(     -2)")', "3"),
     T("deep", "5000 nested parentheses around 1", "calculate(&s)", "1", setup='let s = format!("{}1{}", "(".repeat(5000), ")".repeat(5000));')],
    [("approach", "Without parentheses, keep a running sum and the sign of the next number. A parenthesis is a sub-expression with its own sum."),
     ("approach", "At `(`, push the outer sum and the sign in front of the parenthesis; at `)`, fold the inner sum back in with that sign."),
     ("edge case", "A leading `-` is just `0 - …`: the running sum starts at 0, so no special case is needed.")],
    ("An explicit stack means deep nesting can't overflow the call stack, unlike a recursive-descent parser.", "O(n)", "O(depth)"),
    "Add `*` and `/` with the usual precedence. What extra state do you need?",
    ["Iterative parsing with an explicit stack.", "Unary minus as '0 minus'."],
))

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
     T("empty", "new stack", "FreqStack::new().pop()", "None")],
    [T("drains", "push 5,7,5,7,4,5; pop seven times", "out", "vec![Some(5), Some(7), Some(5), Some(4), Some(7), Some(5), None]",
       setup="let mut s = FreqStack::new();\nfor x in [5, 7, 5, 7, 4, 5] {\n    s.push(x);\n}\nlet out: Vec<Option<i32>> = (0..7).map(|_| s.pop()).collect();"),
     T("push_after_pop", "push 1,1; pop; push 2; pop; pop", "(a, b, c)", "(Some(1), Some(2), Some(1))",
       setup="let mut s = FreqStack::new();\ns.push(1);\ns.push(1);\nlet a = s.pop();\ns.push(2);\nlet b = s.pop();\nlet c = s.pop();")],
    [("approach", "Group elements by the frequency they had when pushed. The last group holds the most frequent, and its last element is the most recent."),
     ("rust", "`self.freq.entry(x)` and `self.groups` are different fields, so both can be borrowed mutably at once.")],
    ("An element with frequency 3 sits in groups 1, 2 and 3. Popping from the top group automatically exposes its earlier copies in lower groups.", "O(1)", "O(n)"),
    "How would you support `pop` of the least frequent element too?",
    ["Bucketing by frequency: `Vec<Vec<T>>`.", "Split borrows across struct fields."],
    related=["S4"],
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
     T("negative_inside", "[2,-1,2], k = 3", "shortest_subarray(&[2, -1, 2], 3)", "Some(3)")],
    [T("mixed", "[84,-37,32,40,95], k = 167", "shortest_subarray(&[84, -37, 32, 40, 95], 167)", "Some(3)"),
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
))

STAGES = [
    ("stack-basics", "Stack basics", "easy"),
    ("monotonic-parsing", "Monotonic & parsing", "medium"),
    ("hard-stacks", "Hard stacks", "hard"),
]

if __name__ == "__main__":
    n = write_track("d3-stacks-queues", "D3", "Stacks & queues", "D", "core", 3,
                    "Vec as a stack, VecDeque as a queue, and monotonic stacks for nearest-greater problems. Parsers that return errors instead of panicking.",
                    STAGES, P)
    print("D3", n)
