from author import T, write_track

P = []

# ---------------------------------------------------------------- first greedy

P.append(dict(
    slug="assign-cookies", title="Assign cookies", level="easy", stage="first-greedy", tags=["greedy", "sorting", "two pointers"],
    companies=["Amazon"],
    teaches=["Sort both sides, then match the smallest cookie that still works.", "`to_vec()` plus `sort_unstable()` when the caller's slice must stay untouched."],
    statement="""
        Child `i` is happy with any cookie of size at least `greed[i]`. Each child gets at most one cookie and
        each cookie goes to at most one child. Return the largest number of children you can make happy.
    """,
    examples=[("greed = [1, 2, 3], cookies = [1, 1]", "1"), ("greed = [1, 2], cookies = [1, 2, 3]", "2")],
    constraints=["0 ≤ greed.len(), cookies.len() ≤ 2·10⁵", "1 ≤ greed[i], cookies[j] ≤ 2³² − 1"],
    starter="""
        pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
            let mut greed = greed.to_vec();
            let mut cookies = cookies.to_vec();
            greed.sort_unstable();
            cookies.sort_unstable();
            let mut happy = 0;
            for &size in &cookies {
                if happy < greed.len() && size >= greed[happy] {
                    happy += 1;
                }
            }
            happy
        }
    """,
    visible=[
        T("leetcode_one_fits", "greed = [1, 2, 3], cookies = [1, 1]", "find_content_children(&[1, 2, 3], &[1, 1])", "1"),
        T("leetcode_all_fit", "greed = [1, 2], cookies = [1, 2, 3]", "find_content_children(&[1, 2], &[1, 2, 3])", "2"),
        T("no_cookies", "greed = [1, 2], cookies = []", "find_content_children(&[1, 2], &[])", "0"),
        T("no_children", "greed = [], cookies = [4]", "find_content_children(&[], &[4])", "0"),
        T("equal_size_is_enough", "greed = [5], cookies = [5]", "find_content_children(&[5], &[5])", "1"),
        T("one_cookie_per_child", "greed = [1], cookies = [1, 1, 1]", "find_content_children(&[1], &[1, 1, 1])", "1"),
        T("inputs_unsorted", "greed = [3, 1, 2], cookies = [3, 1]", "find_content_children(&[3, 1, 2], &[3, 1])", "2"),
    ],
    hidden=[
        T("too_small", "greed = [2], cookies = [1]", "find_content_children(&[2], &[1])", "0"),
        T("both_empty", "greed = [], cookies = []", "find_content_children(&[], &[])", "0"),
        T("duplicates", "greed = [2, 2, 2], cookies = [2, 2]", "find_content_children(&[2, 2, 2], &[2, 2])", "2"),
        T("max_values", "greed = [4294967295, 1], cookies = [4294967295]", "find_content_children(&[u32::MAX, 1], &[u32::MAX])", "1"),
        T("big_cookie_not_wasted", "greed = [1, 3], cookies = [3, 1]", "find_content_children(&[1, 3], &[3, 1])", "2"),
        T("all_cookies_too_small", "greed = [10, 20], cookies = [1, 2, 3]", "find_content_children(&[10, 20], &[1, 2, 3])", "0"),
        T("more_cookies_than_children", "greed = [2, 1], cookies = [1, 1, 2, 2, 3]", "find_content_children(&[2, 1], &[1, 1, 2, 2, 3])", "2"),
        T("greedy_child_skipped", "greed = [1, 2, 100], cookies = [1, 2, 3]", "find_content_children(&[1, 2, 100], &[1, 2, 3])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(greed: &[u32], cookies: &[u32], used: &mut Vec<bool>) -> usize {
                let Some((&g, rest)) = greed.split_first() else { return 0 };
                let mut out = best(rest, cookies, used);
                for j in 0..cookies.len() {
                    if !used[j] && cookies[j] >= g {
                        used[j] = true;
                        out = out.max(1 + best(rest, cookies, used));
                        used[j] = false;
                    }
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(801);
            for _ in 0..300 {
                let n = rng.below(6);
                let m = rng.below(6);
                let greed: Vec<u32> = rng.vec(n, 1, 8);
                let cookies: Vec<u32> = rng.vec(m, 1, 8);
                let want = best(&greed, &cookies, &mut vec![false; m]);
                check!(format!("greed = {greed:?}, cookies = {cookies:?}"), find_content_children(&greed, &cookies), want);
            }
        }

        #[test]
        fn scale_200k() {
            let greed: Vec<u32> = (1..=200_000).collect();
            let cookies: Vec<u32> = (1..=200_000).rev().collect();
            check!("greed = 1..=200000, cookies = 200000 down to 1", find_content_children(&greed, &cookies), 200_000);
        }
        """,
    ],
    wrong=dict(
        quadratic_search="""
            pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
                let mut greed = greed.to_vec();
                let mut cookies = cookies.to_vec();
                greed.sort_unstable();
                cookies.sort_unstable();
                let mut used = vec![false; cookies.len()];
                let mut happy = 0;
                for &g in &greed {
                    if let Some(j) = (0..cookies.len()).find(|&j| !used[j] && cookies[j] >= g) {
                        used[j] = true;
                        happy += 1;
                    }
                }
                happy
            }
        """,
        first_fit_unsorted="""
            pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
                let mut used = vec![false; cookies.len()];
                let mut happy = 0;
                for &g in greed {
                    if let Some(j) = (0..cookies.len()).find(|&j| !used[j] && cookies[j] >= g) {
                        used[j] = true;
                        happy += 1;
                    }
                }
                happy
            }
        """,
    ),
    hints=[("approach", "The least greedy child is the easiest to please. Give each cookie, smallest first, to the least greedy child it satisfies."),
           ("rust", "Copy each slice with `to_vec()`, `sort_unstable()` both, then walk the cookies with one index into the children.")],
    notes=("After sorting, a cookie too small for the least greedy waiting child is too small for everyone, so skip it; otherwise using it on that child never hurts (exchange argument).", "O(n log n + m log m)", "O(n + m) for the sorted copies"),
    follow_up="If each child could take several cookies whose sizes add up to their greed, is greedy still optimal?",
    related=["D2", "S3"],
))

P.append(dict(
    slug="lemonade-change", title="Lemonade change", level="easy", stage="first-greedy", tags=["greedy", "simulation"],
    companies=["Amazon"],
    teaches=["Greedy means spending the least flexible resource first.", "Early `return false` from inside a `for` loop."],
    statement="""
        Lemonade costs 5. Customers arrive in the order of `bills`, each paying with one 5, 10 or 20 bill, and
        you must hand back exact change straight away using only bills taken earlier. You start with no money.
        Return `true` if every customer gets correct change.
    """,
    examples=[("bills = [5, 5, 5, 10, 20]", "true"), ("bills = [5, 5, 10, 10, 20]", "false")],
    constraints=["0 ≤ bills.len() ≤ 2·10⁵", "bills[i] ∈ {5, 10, 20}"],
    starter="""
        pub fn lemonade_change(bills: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn lemonade_change(bills: &[u32]) -> bool {
            let (mut fives, mut tens) = (0u32, 0u32);
            for &bill in bills {
                match bill {
                    5 => fives += 1,
                    10 => {
                        if fives == 0 {
                            return false;
                        }
                        fives -= 1;
                        tens += 1;
                    }
                    _ => {
                        if tens > 0 && fives > 0 {
                            tens -= 1;
                            fives -= 1;
                        } else if fives >= 3 {
                            fives -= 3;
                        } else {
                            return false;
                        }
                    }
                }
            }
            true
        }
    """,
    visible=[
        T("leetcode_yes", "bills = [5, 5, 5, 10, 20]", "lemonade_change(&[5, 5, 5, 10, 20])", "true"),
        T("leetcode_no", "bills = [5, 5, 10, 10, 20]", "lemonade_change(&[5, 5, 10, 10, 20])", "false"),
        T("no_customers", "bills = []", "lemonade_change(&[])", "true"),
        T("first_pays_ten", "bills = [10]", "lemonade_change(&[10])", "false"),
        T("three_fives_for_twenty", "bills = [5, 5, 5, 20]", "lemonade_change(&[5, 5, 5, 20])", "true"),
        T("give_the_ten_first", "bills = [5, 5, 5, 5, 10, 20, 10, 10]", "lemonade_change(&[5, 5, 5, 5, 10, 20, 10, 10])", "true"),
    ],
    hidden=[
        T("single_five", "bills = [5]", "lemonade_change(&[5])", "true"),
        T("first_pays_twenty", "bills = [20]", "lemonade_change(&[20])", "false"),
        T("ten_but_no_five", "bills = [5, 10, 20]", "lemonade_change(&[5, 10, 20])", "false"),
        T("ten_and_five", "bills = [5, 5, 10, 20]", "lemonade_change(&[5, 5, 10, 20])", "true"),
        T("fives_run_out", "bills = [5, 5, 5, 20, 20]", "lemonade_change(&[5, 5, 5, 20, 20])", "false"),
        T("later_five_too_late", "bills = [10, 5]", "lemonade_change(&[10, 5])", "false"),
        T("twenties_are_not_change", "bills = [5, 5, 5, 20, 10]", "lemonade_change(&[5, 5, 5, 20, 10])", "false"),
        T("many_fives", "bills = [5; 1000]", "lemonade_change(&vec![5; 1000])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Tries both ways of changing every 20.
            fn ok(bills: &[u32], fives: i32, tens: i32) -> bool {
                let Some((&b, rest)) = bills.split_first() else { return true };
                match b {
                    5 => ok(rest, fives + 1, tens),
                    10 => fives > 0 && ok(rest, fives - 1, tens + 1),
                    _ => (tens > 0 && fives > 0 && ok(rest, fives - 1, tens - 1)) || (fives >= 3 && ok(rest, fives - 3, tens)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(802);
            for _ in 0..400 {
                let n = rng.below(13);
                let bills: Vec<u32> = (0..n).map(|_| *rng.pick(&[5, 5, 5, 10, 10, 20])).collect();
                check!(format!("bills = {bills:?}"), lemonade_change(&bills), ok(&bills, 0, 0));
            }
        }

        #[test]
        fn scale_200k() {
            let bills: Vec<u32> = [5, 5, 5, 10, 20].repeat(40_000);
            let mut late_ten = bills.clone();
            late_ten.insert(0, 10);
            check!("bills = [5, 5, 5, 10, 20] × 40000, then with a 10 in front", (lemonade_change(&bills), lemonade_change(&late_ten)), (true, false));
        }
        """,
    ],
    wrong=dict(
        fives_first="""
            pub fn lemonade_change(bills: &[u32]) -> bool {
                let (mut fives, mut tens) = (0u32, 0u32);
                for &bill in bills {
                    match bill {
                        5 => fives += 1,
                        10 => {
                            if fives == 0 {
                                return false;
                            }
                            fives -= 1;
                            tens += 1;
                        }
                        _ => {
                            if fives >= 3 {
                                fives -= 3;
                            } else if tens > 0 && fives > 0 {
                                tens -= 1;
                                fives -= 1;
                            } else {
                                return false;
                            }
                        }
                    }
                }
                true
            }
        """,
        checks_only_at_end="""
            pub fn lemonade_change(bills: &[u32]) -> bool {
                let (mut fives, mut tens) = (0i32, 0i32);
                for &bill in bills {
                    match bill {
                        5 => fives += 1,
                        10 => {
                            fives -= 1;
                            tens += 1;
                        }
                        _ => {
                            if tens > 0 {
                                tens -= 1;
                                fives -= 1;
                            } else {
                                fives -= 3;
                            }
                        }
                    }
                }
                fives >= 0 && tens >= 0
            }
        """,
    ),
    hints=[("approach", "Only the count of 5s and 10s in the till matters. A 20 can never be given back as change."),
           ("edge case", "For a 20, give a 10 and a 5 when you can: a 10 only helps with 20s, while 5s help with everyone.")],
    notes=("Keep two counters. Paying 15 with 10 + 5 keeps more 5s than 5 + 5 + 5, and 5s are strictly more useful, so that choice is always safe.", "O(n)", "O(1)"),
    follow_up="If lemonade cost 5 and bills could be any of 5, 10, 20, 50, would the same greedy rule still work?",
    related=["S1"],
))

P.append(dict(
    slug="can-place-flowers", title="Can place flowers", level="easy", stage="first-greedy", tags=["greedy", "slices"],
    companies=["Meta", "Amazon", "Google", "LinkedIn"],
    teaches=["`slice.get(i + 1)` reads a neighbour that might be past the end without panicking.", "Planting as early as possible never blocks a better plan."],
    statement="""
        A flowerbed is a row of plots; `bed[i]` is `true` when plot `i` already has a flower. No two flowers may
        sit in adjacent plots. Return `true` if you can plant `n` more flowers without breaking that rule.
        Plots past either end count as empty.
    """,
    examples=[("bed = [1, 0, 0, 0, 1], n = 1", "true"), ("bed = [1, 0, 0, 0, 1], n = 2", "false")],
    constraints=["0 ≤ bed.len() ≤ 2·10⁵", "bed never has two adjacent flowers", "0 ≤ n ≤ bed.len() + 1"],
    starter="""
        pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
            let mut planted = 0;
            let mut left_full = false;
            for i in 0..bed.len() {
                if bed[i] {
                    left_full = true;
                    continue;
                }
                let right_full = bed.get(i + 1).copied().unwrap_or(false);
                if !left_full && !right_full {
                    planted += 1;
                    left_full = true;
                } else {
                    left_full = false;
                }
            }
            planted >= n
        }
    """,
    visible=[
        """
        /// "10001" → [true, false, false, false, true]
        fn bed(s: &str) -> Vec<bool> {
            s.bytes().map(|b| b == b'1').collect()
        }
        """,
        T("leetcode_one", "bed = [1, 0, 0, 0, 1], n = 1", 'can_place_flowers(&bed("10001"), 1)', "true"),
        T("leetcode_two", "bed = [1, 0, 0, 0, 1], n = 2", 'can_place_flowers(&bed("10001"), 2)', "false"),
        T("empty_bed_zero", "bed = [], n = 0", "can_place_flowers(&[], 0)", "true"),
        T("empty_bed_one", "bed = [], n = 1", "can_place_flowers(&[], 1)", "false"),
        T("single_empty_plot", "bed = [0], n = 1", 'can_place_flowers(&bed("0"), 1)', "true"),
        T("ends_count_as_empty", "bed = [0, 0, 1, 0, 0], n = 2", 'can_place_flowers(&bed("00100"), 2)', "true"),
        T("zero_flowers_always_fit", "bed = [1], n = 0", 'can_place_flowers(&bed("1"), 0)', "true"),
    ],
    hidden=[
        """
        fn bed(s: &str) -> Vec<bool> {
            s.bytes().map(|b| b == b'1').collect()
        }
        """,
        T("three_empty", "bed = [0, 0, 0], n = 2", 'can_place_flowers(&bed("000"), 2)', "true"),
        T("two_empty", "bed = [0, 0], n = 2", 'can_place_flowers(&bed("00"), 2)', "false"),
        T("left_edge", "bed = [0, 0, 1], n = 1", 'can_place_flowers(&bed("001"), 1)', "true"),
        T("right_edge", "bed = [1, 0, 0], n = 1", 'can_place_flowers(&bed("100"), 1)', "true"),
        T("gap_of_one", "bed = [1, 0, 1], n = 1", 'can_place_flowers(&bed("101"), 1)', "false"),
        T("between_is_blocked", "bed = [0, 1, 0], n = 1", 'can_place_flowers(&bed("010"), 1)', "false"),
        T("five_empty", "bed = [0, 0, 0, 0, 0], n = 3", 'can_place_flowers(&bed("00000"), 3)', "true"),
        T("four_inside", "bed = [1, 0, 0, 0, 0, 1], n = 2", 'can_place_flowers(&bed("100001"), 2)', "false"),
        T("exactly_enough", "bed = [0, 0, 0, 1, 0, 0, 0, 0], n = 3", 'can_place_flowers(&bed("00010000"), 3)', "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(803);
            for _ in 0..300 {
                let len = rng.below(13);
                let mut plots = vec![false; len];
                for i in 0..len {
                    if rng.below(3) == 0 && (i == 0 || !plots[i - 1]) {
                        plots[i] = true;
                    }
                }
                // The most flowers any set of empty plots can take.
                let mut most = 0;
                for mask in 0u32..1 << len {
                    let ok = (0..len).all(|i| mask >> i & 1 == 0 || !plots[i])
                        && (0..len).all(|i| {
                            let full = |j: usize| plots[j] || mask >> j & 1 == 1;
                            !(i + 1 < len && full(i) && full(i + 1))
                        });
                    if ok {
                        most = most.max(mask.count_ones() as usize);
                    }
                }
                let n = rng.below(len + 2);
                let shown: String = plots.iter().map(|&p| if p { '1' } else { '0' }).collect();
                check!(format!("bed = {shown}, n = {n}"), can_place_flowers(&plots, n), n <= most);
            }
        }

        #[test]
        fn scale_200k() {
            let plots = vec![false; 200_000];
            check!("bed = 200000 empty plots, n = 100000 and 100001", (can_place_flowers(&plots, 100_000), can_place_flowers(&plots, 100_001)), (true, false));
        }
        """,
    ],
    wrong=dict(
        rescan_per_flower="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                for _ in 0..n {
                    let spot = (0..bed.len()).find(|&i| {
                        !bed[i] && (i == 0 || !bed[i - 1]) && (i + 1 == bed.len() || !bed[i + 1])
                    });
                    match spot {
                        Some(i) => bed[i] = true,
                        None => return false,
                    }
                }
                true
            }
        """,
        edges_count_as_full="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                let mut planted = 0;
                for i in 0..bed.len() {
                    let left = i > 0 && !bed[i - 1];
                    let right = i + 1 < bed.len() && !bed[i + 1];
                    if !bed[i] && left && right {
                        bed[i] = true;
                        planted += 1;
                    }
                }
                planted >= n
            }
        """,
        strictly_more="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                let mut planted = 0;
                for i in 0..bed.len() {
                    let left = i == 0 || !bed[i - 1];
                    let right = i + 1 == bed.len() || !bed[i + 1];
                    if !bed[i] && left && right {
                        bed[i] = true;
                        planted += 1;
                    }
                }
                planted > n || n == 0
            }
        """,
    ),
    hints=[("approach", "Walk left to right and plant in every empty plot whose neighbours are both empty. Planting early never costs you a spot later."),
           ("rust", "`bed.get(i + 1).copied().unwrap_or(false)` treats the plot past the end as empty; keep a flag for the left neighbour so you don't need to mutate the input."),
           ("edge case", "The first and last plots only have one neighbour, and `n = 0` is always possible.")],
    notes=("Planting at the leftmost legal plot leaves at least as much room to the right as any other choice, so one greedy pass finds the maximum.", "O(n)", "O(1)"),
    follow_up="How would you answer many queries of different `n` on the same bed without rescanning?",
    related=["S3"],
))

P.append(dict(
    slug="meeting-rooms", title="Meeting rooms", level="easy", stage="first-greedy", tags=["intervals", "sorting", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["`sort_unstable_by_key(|m| m.0)` orders tuples by one field.", "`windows(2)` compares each pair of neighbours."],
    statement="""
        Each meeting is `(start, end)` with `start < end`, and it covers the time from `start` up to but not
        including `end`, so one meeting may start the moment another ends. Return `true` if one person can
        attend every meeting, that is, no two meetings overlap.
    """,
    examples=[("meetings = [(0, 30), (5, 10), (15, 20)]", "false"), ("meetings = [(7, 10), (2, 4)]", "true")],
    constraints=["0 ≤ meetings.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
            let mut sorted = meetings.to_vec();
            sorted.sort_unstable_by_key(|m| m.0);
            sorted.windows(2).all(|w| w[0].1 <= w[1].0)
        }
    """,
    visible=[
        T("leetcode_clash", "meetings = [(0, 30), (5, 10), (15, 20)]", "can_attend_all(&[(0, 30), (5, 10), (15, 20)])", "false"),
        T("leetcode_fine", "meetings = [(7, 10), (2, 4)]", "can_attend_all(&[(7, 10), (2, 4)])", "true"),
        T("no_meetings", "meetings = []", "can_attend_all(&[])", "true"),
        T("one_meeting", "meetings = [(1, 2)]", "can_attend_all(&[(1, 2)])", "true"),
        T("back_to_back_is_fine", "meetings = [(1, 5), (5, 8)]", "can_attend_all(&[(1, 5), (5, 8)])", "true"),
        T("unsorted_overlap", "meetings = [(10, 20), (1, 11)]", "can_attend_all(&[(10, 20), (1, 11)])", "false"),
    ],
    hidden=[
        T("nested", "meetings = [(1, 10), (2, 3)]", "can_attend_all(&[(1, 10), (2, 3)])", "false"),
        T("same_start", "meetings = [(1, 2), (1, 3)]", "can_attend_all(&[(1, 2), (1, 3)])", "false"),
        T("identical", "meetings = [(1, 2), (1, 2)]", "can_attend_all(&[(1, 2), (1, 2)])", "false"),
        T("negative_times", "meetings = [(-5, -1), (-1, 3)]", "can_attend_all(&[(-5, -1), (-1, 3)])", "true"),
        T("i32_extremes_touch", "meetings = [(i32::MIN, 0), (0, i32::MAX)]", "can_attend_all(&[(i32::MIN, 0), (0, i32::MAX)])", "true"),
        T("everything_covered", "meetings = [(i32::MIN, i32::MAX), (0, 1)]", "can_attend_all(&[(i32::MIN, i32::MAX), (0, 1)])", "false"),
        T("clash_not_adjacent_in_input", "meetings = [(1, 5), (10, 12), (3, 4)]", "can_attend_all(&[(1, 5), (10, 12), (3, 4)])", "false"),
        T("many_back_to_back", "meetings = [(4, 6), (0, 2), (2, 4), (6, 9)]", "can_attend_all(&[(4, 6), (0, 2), (2, 4), (6, 9)])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(804);
            for _ in 0..400 {
                let n = rng.below(7);
                let meetings: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 20) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                let want = (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0));
                check!(format!("meetings = {meetings:?}"), can_attend_all(&meetings), want);
            }
        }

        #[test]
        fn scale_200k() {
            let fine: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 2)).collect();
            let mut clash = fine.clone();
            clash[0].0 -= 1;
            check!("200000 back-to-back meetings in reverse order; then the last one starts 1 early", (can_attend_all(&fine), can_attend_all(&clash)), (true, false));
        }
        """,
    ],
    wrong=dict(
        every_pair="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                let n = meetings.len();
                (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0))
            }
        """,
        touching_overlaps="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                let mut sorted = meetings.to_vec();
                sorted.sort_unstable_by_key(|m| m.0);
                sorted.windows(2).all(|w| w[0].1 < w[1].0)
            }
        """,
        input_order="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                meetings.windows(2).all(|w| w[0].1 <= w[1].0 || w[1].1 <= w[0].0)
            }
        """,
    ),
    hints=[("approach", "Sort by start time. Then only neighbours can clash: check each meeting ends by the time the next one starts."),
           ("rust", "Copy with `to_vec()`, `sort_unstable_by_key(|m| m.0)`, then `windows(2).all(|w| w[0].1 <= w[1].0)`."),
           ("edge case", "`end == next start` is not an overlap.")],
    notes=("After sorting by start, if any two meetings overlap then some adjacent pair does, so one pass over neighbours decides it.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="If they do overlap, how many rooms would you need? (That's Meeting rooms II.)",
    related=["S3", "D7"],
))

P.append(dict(
    slug="maximum-subarray", title="Maximum subarray", level="easy", stage="first-greedy", tags=["Kadane", "greedy", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Kadane's rule: drop a running sum the moment it would only drag the next element down.", "`split_first()?` returns `None` for an empty slice in one step."],
    statement="""
        Return the largest sum of a non-empty contiguous run of `nums`, or `None` when `nums` is empty.
        The sum can be larger than an `i32` holds.
    """,
    examples=[("nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "Some(6)"), ("nums = [5, 4, -1, 7, 8]", "Some(23)")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "nums[i] is any i32"],
    starter="""
        pub fn max_subarray(nums: &[i32]) -> Option<i64> {
            todo!()
        }
    """,
    solution="""
        pub fn max_subarray(nums: &[i32]) -> Option<i64> {
            let (&first, rest) = nums.split_first()?;
            let mut best = first as i64;
            let mut current = first as i64;
            for &x in rest {
                let x = x as i64;
                current = (current + x).max(x);
                best = best.max(current);
            }
            Some(best)
        }
    """,
    visible=[
        T("leetcode_mixed", "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "max_subarray(&[-2, 1, -3, 4, -1, 2, 1, -5, 4])", "Some(6)"),
        T("leetcode_single", "nums = [1]", "max_subarray(&[1])", "Some(1)"),
        T("leetcode_whole", "nums = [5, 4, -1, 7, 8]", "max_subarray(&[5, 4, -1, 7, 8])", "Some(23)"),
        T("empty", "nums = []", "max_subarray(&[])", "None"),
        T("all_negative", "nums = [-3, -1, -2]", "max_subarray(&[-3, -1, -2])", "Some(-1)"),
        T("wider_than_i32", "nums = [2147483647, 2147483647]", "max_subarray(&[i32::MAX, i32::MAX])", "Some(4_294_967_294)"),
    ],
    hidden=[
        T("single_negative", "nums = [-7]", "max_subarray(&[-7])", "Some(-7)"),
        T("i32_min", "nums = [-2147483648]", "max_subarray(&[i32::MIN])", "Some(-2_147_483_648)"),
        T("zeros", "nums = [0, 0]", "max_subarray(&[0, 0])", "Some(0)"),
        T("zero_among_negatives", "nums = [-1, 0, -2]", "max_subarray(&[-1, 0, -2])", "Some(0)"),
        T("dip_worth_keeping", "nums = [3, -2, 5]", "max_subarray(&[3, -2, 5])", "Some(6)"),
        T("dip_not_worth_keeping", "nums = [2, -5, 3]", "max_subarray(&[2, -5, 3])", "Some(3)"),
        T("best_at_end", "nums = [8, -19, 5, -4, 20]", "max_subarray(&[8, -19, 5, -4, 20])", "Some(21)"),
        T("min_values", "nums = [i32::MIN; 3]", "max_subarray(&[i32::MIN; 3])", "Some(-2_147_483_648)"),
        T("big_total", "nums = [100000; 200000]", "max_subarray(&vec![100_000; 200_000])", "Some(20_000_000_000)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(805);
            for _ in 0..400 {
                let n = rng.below(16);
                let nums: Vec<i32> = rng.vec(n, -20, 20);
                let mut want: Option<i64> = None;
                for i in 0..n {
                    for j in i..n {
                        let s: i64 = nums[i..=j].iter().map(|&x| x as i64).sum();
                        want = Some(want.map_or(s, |w| w.max(s)));
                    }
                }
                check!(format!("nums = {nums:?}"), max_subarray(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i32> = (0..200_000).map(|i| if i % 2 == 0 { 1_000_000_000 } else { -999_999_999 }).collect();
            check!("nums = [10⁹, -(10⁹ - 1), …] (200000 values)", max_subarray(&nums), Some(1_000_099_999));
        }
        """,
    ],
    wrong=dict(
        every_start="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                let mut best: Option<i64> = None;
                for i in 0..nums.len() {
                    let mut s = 0i64;
                    for &x in &nums[i..] {
                        s += x as i64;
                        best = Some(best.map_or(s, |b| b.max(s)));
                    }
                }
                best
            }
        """,
        floor_at_zero="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                if nums.is_empty() {
                    return None;
                }
                let (mut best, mut current) = (0i64, 0i64);
                for &x in nums {
                    current = (current + x as i64).max(0);
                    best = best.max(current);
                }
                Some(best)
            }
        """,
        i32_sum="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                let (&first, rest) = nums.split_first()?;
                let (mut best, mut current) = (first, first);
                for &x in rest {
                    current = current.wrapping_add(x).max(x);
                    best = best.max(current);
                }
                Some(best as i64)
            }
        """,
    ),
    hints=[("approach", "At each element decide: extend the best run ending just before it, or start fresh here. Start fresh when the previous run's sum is negative."),
           ("rust", "Work in `i64` so the sum can't overflow; `let (&first, rest) = nums.split_first()?;` handles the empty slice."),
           ("edge case", "When every number is negative the answer is the largest single number, not 0.")],
    notes=("`current` is the best sum of a run ending at this element: either the element alone or the element plus the best run ending just before it. The answer is the best `current` seen.", "O(n)", "O(1)"),
    follow_up="How would you also return the start and end indices of the best run?",
    related=["D12", "D2"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-ii", title="Best time to buy and sell stock II", level="easy", stage="first-greedy", tags=["greedy", "windows"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["A total of many trades equals the sum of every single-day rise.", "Widen to `u64` before summing `u32` values."],
    statement="""
        `prices[i]` is a stock's price on day `i`. You may hold at most one share at a time, but you can buy and
        sell as often as you like, even selling and buying again on the same day. Return the largest total profit.
    """,
    examples=[("prices = [7, 1, 5, 3, 6, 4]", "7"), ("prices = [1, 2, 3, 4, 5]", "4")],
    constraints=["0 ≤ prices.len() ≤ 2·10⁵", "prices[i] is any u32"],
    starter="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()
        }
    """,
    visible=[
        T("leetcode_two_trades", "prices = [7, 1, 5, 3, 6, 4]", "max_profit(&[7, 1, 5, 3, 6, 4])", "7"),
        T("leetcode_rising", "prices = [1, 2, 3, 4, 5]", "max_profit(&[1, 2, 3, 4, 5])", "4"),
        T("leetcode_falling", "prices = [7, 6, 4, 3, 1]", "max_profit(&[7, 6, 4, 3, 1])", "0"),
        T("no_days", "prices = []", "max_profit(&[])", "0"),
        T("one_day", "prices = [5]", "max_profit(&[5])", "0"),
        T("trade_every_rise", "prices = [1, 5, 1, 5]", "max_profit(&[1, 5, 1, 5])", "8"),
    ],
    hidden=[
        T("flat", "prices = [3, 3, 3]", "max_profit(&[3, 3, 3])", "0"),
        T("two_days_up", "prices = [1, 2]", "max_profit(&[1, 2])", "1"),
        T("two_days_down", "prices = [2, 1]", "max_profit(&[2, 1])", "0"),
        T("zigzag", "prices = [2, 1, 2, 0, 1]", "max_profit(&[2, 1, 2, 0, 1])", "2"),
        T("drop_between_rises", "prices = [3, 2, 6, 5, 0, 3]", "max_profit(&[3, 2, 6, 5, 0, 3])", "7"),
        T("zero_to_max", "prices = [0, 4294967295]", "max_profit(&[0, u32::MAX])", "4_294_967_295"),
        T("past_u32", "prices = [0, 4294967295, 0, 4294967295]", "max_profit(&[0, u32::MAX, 0, u32::MAX])", "8_589_934_590"),
        T("plateau_then_rise", "prices = [1, 1, 1, 9]", "max_profit(&[1, 1, 1, 9])", "8"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Every choice of buy/sell/wait on every day.
            fn best(prices: &[u32], holding: Option<u32>) -> i64 {
                let Some((&p, rest)) = prices.split_first() else { return 0 };
                let wait = best(rest, holding);
                let act = match holding {
                    None => best(rest, Some(p)),
                    Some(bought) => p as i64 - bought as i64 + best(rest, None),
                };
                wait.max(act)
            }
            let mut rng = anneal_prelude::Rng::new(806);
            for _ in 0..300 {
                let n = rng.below(10);
                let prices: Vec<u32> = rng.vec(n, 0, 12);
                check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, None) as u64);
            }
        }

        #[test]
        fn scale_200k() {
            let prices: Vec<u32> = (0..200_000).map(|i| if i % 2 == 0 { 0 } else { u32::MAX }).collect();
            check!("prices = [0, 4294967295, …] (200000 days)", max_profit(&prices), 429_496_729_500_000);
        }
        """,
    ],
    wrong=dict(
        one_trade="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let mut low = u32::MAX;
                let mut best = 0u64;
                for &p in prices {
                    low = low.min(p);
                    best = best.max((p - low) as u64);
                }
                best
            }
        """,
        u32_total="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let mut total = 0u32;
                for w in prices.windows(2) {
                    total = total.wrapping_add(w[1].saturating_sub(w[0]));
                }
                total as u64
            }
        """,
    ),
    hints=[("approach", "Any trade from day i to day j earns the same as the sum of the day-to-day changes between them. Keep only the rises."),
           ("rust", "`prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()` is the whole solution.")],
    notes=("Summing every positive day-to-day change collects each upward move exactly once, which is the most any set of non-overlapping trades can collect.", "O(n)", "O(1)"),
    follow_up="What changes if each sale costs a fixed fee? (Hint: the greedy stops working; a two-state DP does.)",
    related=["D12", "D2"],
))

# ---------------------------------------------------------------- intervals

# Merges closed intervals on a small grid by marking 2·start..=2·end, so touching intervals join and
# (1, 2), (3, 4) stay apart. Used as the brute force in several hidden tests.
GRID_MERGE = """
    fn grid_merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
        let mut marked = vec![false; 64];
        for &(s, e) in intervals {
            for x in 2 * s..=2 * e {
                marked[x as usize] = true;
            }
        }
        let mut out = Vec::new();
        let mut x = 0;
        while x < marked.len() {
            if marked[x] {
                let start = x;
                while x + 1 < marked.len() && marked[x + 1] {
                    x += 1;
                }
                out.push((start as i32 / 2, x as i32 / 2));
            }
            x += 1;
        }
        out
    }
"""

P.append(dict(
    slug="merge-intervals", title="Merge intervals", level="medium", stage="intervals", tags=["intervals", "sorting", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Sort tuples, then fold into the output with `last_mut()`.", "A match guard `Some(last) if start <= last.1` merges in place."],
    statement="""
        Each `(start, end)` is a closed interval with `start ≤ end`. Merge every group of overlapping intervals
        and return the result sorted by start. Intervals that share an endpoint, like `(1, 4)` and `(4, 5)`, overlap.
    """,
    examples=[("intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]", "[(1, 6), (8, 10), (15, 18)]"), ("intervals = [(1, 4), (4, 5)]", "[(1, 5)]")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
            let mut sorted = intervals.to_vec();
            sorted.sort_unstable();
            let mut out: Vec<(i32, i32)> = Vec::with_capacity(sorted.len());
            for (start, end) in sorted {
                match out.last_mut() {
                    Some(last) if start <= last.1 => last.1 = last.1.max(end),
                    _ => out.push((start, end)),
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_four", "intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]", "merge(&[(1, 3), (2, 6), (8, 10), (15, 18)])", "vec![(1, 6), (8, 10), (15, 18)]"),
        T("leetcode_touching", "intervals = [(1, 4), (4, 5)]", "merge(&[(1, 4), (4, 5)])", "vec![(1, 5)]"),
        T("leetcode_unsorted", "intervals = [(4, 7), (1, 4)]", "merge(&[(4, 7), (1, 4)])", "vec![(1, 7)]"),
        T("empty", "intervals = []", "merge(&[])", "Vec::<(i32, i32)>::new()"),
        T("single", "intervals = [(2, 3)]", "merge(&[(2, 3)])", "vec![(2, 3)]"),
        T("contained", "intervals = [(1, 10), (2, 3)]", "merge(&[(1, 10), (2, 3)])", "vec![(1, 10)]"),
        T("output_sorted", "intervals = [(8, 10), (1, 3), (2, 6)]", "merge(&[(8, 10), (1, 3), (2, 6)])", "vec![(1, 6), (8, 10)]"),
    ],
    hidden=[
        T("points", "intervals = [(5, 5), (5, 5)]", "merge(&[(5, 5), (5, 5)])", "vec![(5, 5)]"),
        T("gap_of_one_stays_apart", "intervals = [(1, 2), (3, 4)]", "merge(&[(1, 2), (3, 4)])", "vec![(1, 2), (3, 4)]"),
        T("negatives", "intervals = [(-3, -1), (-2, 0)]", "merge(&[(-3, -1), (-2, 0)])", "vec![(-3, 0)]"),
        T("i32_extremes", "intervals = [(i32::MIN, 0), (0, i32::MAX)]", "merge(&[(i32::MIN, 0), (0, i32::MAX)])", "vec![(i32::MIN, i32::MAX)]"),
        T("contained_then_longer", "intervals = [(1, 10), (2, 3), (4, 11)]", "merge(&[(1, 10), (2, 3), (4, 11)])", "vec![(1, 11)]"),
        T("chain", "intervals = [(3, 4), (1, 2), (2, 3)]", "merge(&[(3, 4), (1, 2), (2, 3)])", "vec![(1, 4)]"),
        T("duplicates", "intervals = [(1, 3), (1, 3)]", "merge(&[(1, 3), (1, 3)])", "vec![(1, 3)]"),
        T("long_one_last", "intervals = [(2, 3), (5, 6), (1, 10)]", "merge(&[(2, 3), (5, 6), (1, 10)])", "vec![(1, 10)]"),
        GRID_MERGE,
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(807);
            for _ in 0..400 {
                let n = rng.below(8);
                let intervals: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(0, 25) as i32;
                        let len = rng.int(0, 5) as i32;
                        (s, s + len)
                    })
                    .collect();
                check!(format!("intervals = {intervals:?}"), merge(&intervals), grid_merge(&intervals));
            }
        }

        #[test]
        fn scale_200k() {
            // 199999 separate intervals in reverse order, plus one that joins the first two.
            let mut intervals: Vec<(i32, i32)> = (0..199_999).rev().map(|i| (3 * i, 3 * i + 1)).collect();
            intervals.push((1, 3));
            let out = merge(&intervals);
            check!("(3i, 3i + 1) for i in 0..199999, reversed, plus (1, 3)", (out.len(), out[0], out[1], out[out.len() - 1]), (199_998, (0, 4), (6, 7), (599_994, 599_995)));
        }
        """,
    ],
    wrong=dict(
        scan_all_output="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.iter_mut().find(|m| start <= m.1 && m.0 <= end) {
                        Some(m) => m.1 = m.1.max(end),
                        None => out.push((start, end)),
                    }
                }
                out
            }
        """,
        end_not_max="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.last_mut() {
                        Some(last) if start <= last.1 => last.1 = end,
                        _ => out.push((start, end)),
                    }
                }
                out
            }
        """,
        touching_apart="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.last_mut() {
                        Some(last) if start < last.1 => last.1 = last.1.max(end),
                        _ => out.push((start, end)),
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Sort by start. Each interval either overlaps the last merged one (extend it) or starts a new one."),
           ("rust", "`match out.last_mut() { Some(last) if start <= last.1 => last.1 = last.1.max(end), _ => out.push((start, end)) }`"),
           ("edge case", "Take the max of the ends: an interval can sit entirely inside the last merged one.")],
    notes=("After sorting by start, an interval can only overlap the most recent merged interval, so one pass with `last_mut()` merges everything.", "O(n log n)", "O(n)"),
    follow_up="How would you merge intervals arriving one at a time from a stream, keeping the merged set queryable? (Think `BTreeMap`.)",
    related=["S3", "S4"],
))

P.append(dict(
    slug="insert-interval", title="Insert interval", level="medium", stage="intervals", tags=["intervals", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn"],
    teaches=["Three phases in one pass: copy what ends before, absorb what overlaps, copy the rest.", "`extend_from_slice(&intervals[i..])` copies the tail at once."],
    statement="""
        `intervals` holds closed intervals sorted by start with no two overlapping or touching. Insert `new`,
        merging it with every interval it overlaps or touches, and return the list, still sorted and non-overlapping.
    """,
    examples=[("intervals = [(1, 3), (6, 9)], new = (2, 5)", "[(1, 5), (6, 9)]")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
            let mut out = Vec::with_capacity(intervals.len() + 1);
            let (mut lo, mut hi) = new;
            let mut i = 0;
            while i < intervals.len() && intervals[i].1 < lo {
                out.push(intervals[i]);
                i += 1;
            }
            while i < intervals.len() && intervals[i].0 <= hi {
                lo = lo.min(intervals[i].0);
                hi = hi.max(intervals[i].1);
                i += 1;
            }
            out.push((lo, hi));
            out.extend_from_slice(&intervals[i..]);
            out
        }
    """,
    visible=[
        T("leetcode_one_overlap", "intervals = [(1, 3), (6, 9)], new = (2, 5)", "insert(&[(1, 3), (6, 9)], (2, 5))", "vec![(1, 5), (6, 9)]"),
        T("leetcode_three_overlaps", "intervals = [(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], new = (4, 8)", "insert(&[(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8))", "vec![(1, 2), (3, 10), (12, 16)]"),
        T("into_empty", "intervals = [], new = (5, 7)", "insert(&[], (5, 7))", "vec![(5, 7)]"),
        T("goes_last", "intervals = [(1, 2)], new = (5, 6)", "insert(&[(1, 2)], (5, 6))", "vec![(1, 2), (5, 6)]"),
        T("goes_first", "intervals = [(5, 6)], new = (1, 2)", "insert(&[(5, 6)], (1, 2))", "vec![(1, 2), (5, 6)]"),
        T("touching_merges", "intervals = [(1, 3)], new = (3, 4)", "insert(&[(1, 3)], (3, 4))", "vec![(1, 4)]"),
    ],
    hidden=[
        T("covers_all", "intervals = [(1, 2), (4, 5), (7, 8)], new = (0, 10)", "insert(&[(1, 2), (4, 5), (7, 8)], (0, 10))", "vec![(0, 10)]"),
        T("inside_one", "intervals = [(1, 10)], new = (3, 4)", "insert(&[(1, 10)], (3, 4))", "vec![(1, 10)]"),
        T("in_a_gap", "intervals = [(1, 2), (8, 9)], new = (4, 5)", "insert(&[(1, 2), (8, 9)], (4, 5))", "vec![(1, 2), (4, 5), (8, 9)]"),
        T("touches_both_sides", "intervals = [(1, 3), (5, 7)], new = (3, 5)", "insert(&[(1, 3), (5, 7)], (3, 5))", "vec![(1, 7)]"),
        T("point_in_gap", "intervals = [(1, 3), (5, 7)], new = (4, 4)", "insert(&[(1, 3), (5, 7)], (4, 4))", "vec![(1, 3), (4, 4), (5, 7)]"),
        T("touches_left_neighbour", "intervals = [(1, 3), (8, 9)], new = (3, 5)", "insert(&[(1, 3), (8, 9)], (3, 5))", "vec![(1, 5), (8, 9)]"),
        T("i32_extremes_apart", "intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (0, 0)", "insert(&[(i32::MIN, -1), (1, i32::MAX)], (0, 0))", "vec![(i32::MIN, -1), (0, 0), (1, i32::MAX)]"),
        T("i32_extremes_join", "intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (-1, 1)", "insert(&[(i32::MIN, -1), (1, i32::MAX)], (-1, 1))", "vec![(i32::MIN, i32::MAX)]"),
        T("same_as_existing", "intervals = [(2, 4)], new = (2, 4)", "insert(&[(2, 4)], (2, 4))", "vec![(2, 4)]"),
        GRID_MERGE,
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(808);
            for _ in 0..400 {
                let n = rng.below(7);
                let raw: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(0, 25) as i32;
                        let len = rng.int(0, 3) as i32;
                        (s, s + len)
                    })
                    .collect();
                let intervals = grid_merge(&raw);
                let s = rng.int(0, 25) as i32;
                let len = rng.int(0, 5) as i32;
                let new = (s, s + len);
                let mut all = intervals.clone();
                all.push(new);
                check!(format!("intervals = {intervals:?}, new = {new:?}"), insert(&intervals, new), grid_merge(&all));
            }
        }

        #[test]
        fn scale_200k() {
            let intervals: Vec<(i32, i32)> = (0..200_000).map(|i| (3 * i, 3 * i + 1)).collect();
            let out = insert(&intervals, (1, 300_000));
            check!("(3i, 3i + 1) for i in 0..200000, new = (1, 300000)", (out.len(), out[0], out[1]), (100_000, (0, 300_001), (300_003, 300_004)));
        }
        """,
    ],
    wrong=dict(
        touching_stays_apart="""
            pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut lo, mut hi) = new;
                let mut i = 0;
                while i < intervals.len() && intervals[i].1 <= lo {
                    out.push(intervals[i]);
                    i += 1;
                }
                while i < intervals.len() && intervals[i].0 < hi {
                    lo = lo.min(intervals[i].0);
                    hi = hi.max(intervals[i].1);
                    i += 1;
                }
                out.push((lo, hi));
                out.extend_from_slice(&intervals[i..]);
                out
            }
        """,
        end_not_max="""
            pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut lo, mut hi) = new;
                let mut i = 0;
                while i < intervals.len() && intervals[i].1 < lo {
                    out.push(intervals[i]);
                    i += 1;
                }
                while i < intervals.len() && intervals[i].0 <= hi {
                    lo = lo.min(intervals[i].0);
                    hi = intervals[i].1;
                    i += 1;
                }
                out.push((lo, hi));
                out.extend_from_slice(&intervals[i..]);
                out
            }
        """,
    ),
    hints=[("approach", "The list is already sorted: copy intervals that end before `new` starts, absorb every interval that starts before `new` ends, then copy the rest."),
           ("rust", "Two `while` loops over one index `i`, then `out.extend_from_slice(&intervals[i..])`."),
           ("edge case", "Touching counts: `(1, 3)` and `(3, 4)` merge, so compare with `<` and `<=` carefully.")],
    notes=("Because the input is sorted and disjoint, the intervals that overlap `new` form one contiguous run; everything before and after is copied unchanged.", "O(n)", "O(n) for the output"),
    follow_up="If you had to insert many intervals one after another, what structure would keep each insert fast?",
    related=["S3", "D4"],
))

P.append(dict(
    slug="non-overlapping-intervals", title="Non-overlapping intervals", level="medium", stage="intervals", tags=["intervals", "greedy", "Blind 75"],
    companies=["Meta", "Amazon", "Google"],
    teaches=["Sort by end time: finishing early leaves the most room (the activity-selection argument).", "`Option<i32>` as \"nothing kept yet\" instead of a magic minimum."],
    statement="""
        Each `(start, end)` has `start < end` and covers the time from `start` up to but not including `end`, so
        intervals that only touch don't overlap. Return the fewest intervals to remove so the rest don't overlap.
    """,
    examples=[("intervals = [(1, 2), (2, 3), (3, 4), (1, 3)]", "1"), ("intervals = [(1, 2), (1, 2), (1, 2)]", "2")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
            let mut sorted = intervals.to_vec();
            sorted.sort_unstable_by_key(|iv| iv.1);
            let mut kept = 0;
            let mut last_end: Option<i32> = None;
            for (start, end) in sorted {
                if last_end.map_or(true, |e| start >= e) {
                    kept += 1;
                    last_end = Some(end);
                }
            }
            intervals.len() - kept
        }
    """,
    visible=[
        T("leetcode_one", "intervals = [(1, 2), (2, 3), (3, 4), (1, 3)]", "erase_overlap_intervals(&[(1, 2), (2, 3), (3, 4), (1, 3)])", "1"),
        T("leetcode_copies", "intervals = [(1, 2), (1, 2), (1, 2)]", "erase_overlap_intervals(&[(1, 2), (1, 2), (1, 2)])", "2"),
        T("leetcode_touching", "intervals = [(1, 2), (2, 3)]", "erase_overlap_intervals(&[(1, 2), (2, 3)])", "0"),
        T("empty", "intervals = []", "erase_overlap_intervals(&[])", "0"),
        T("single", "intervals = [(4, 9)]", "erase_overlap_intervals(&[(4, 9)])", "0"),
        T("drop_the_long_one", "intervals = [(1, 100), (1, 2), (3, 4), (5, 6)]", "erase_overlap_intervals(&[(1, 100), (1, 2), (3, 4), (5, 6)])", "1"),
    ],
    hidden=[
        T("nested", "intervals = [(1, 10), (2, 3)]", "erase_overlap_intervals(&[(1, 10), (2, 3)])", "1"),
        T("staircase", "intervals = [(0, 2), (1, 3), (2, 4), (3, 5)]", "erase_overlap_intervals(&[(0, 2), (1, 3), (2, 4), (3, 5)])", "2"),
        T("negatives", "intervals = [(-3, -1), (-2, 0), (-1, 1)]", "erase_overlap_intervals(&[(-3, -1), (-2, 0), (-1, 1)])", "1"),
        T("i32_extremes", "intervals = [(MIN, MAX), (MIN, 0), (0, MAX)]", "erase_overlap_intervals(&[(i32::MIN, i32::MAX), (i32::MIN, 0), (0, i32::MAX)])", "1"),
        T("earliest_start_is_a_trap", "intervals = [(1, 10), (2, 3), (4, 5)]", "erase_overlap_intervals(&[(1, 10), (2, 3), (4, 5)])", "1"),
        T("same_end", "intervals = [(1, 3), (2, 3), (0, 3)]", "erase_overlap_intervals(&[(1, 3), (2, 3), (0, 3)])", "2"),
        T("disjoint_unsorted", "intervals = [(5, 6), (1, 2), (3, 4)]", "erase_overlap_intervals(&[(5, 6), (1, 2), (3, 4)])", "0"),
        T("leetcode_mixed", "intervals = [(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)]", "erase_overlap_intervals(&[(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)])", "7"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(809);
            for _ in 0..300 {
                let n = rng.below(9);
                let intervals: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                let mut most = 0;
                for mask in 0u32..1 << n {
                    let kept: Vec<(i32, i32)> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| intervals[i]).collect();
                    let ok = (0..kept.len()).all(|i| (i + 1..kept.len()).all(|j| kept[i].1 <= kept[j].0 || kept[j].1 <= kept[i].0));
                    if ok {
                        most = most.max(kept.len());
                    }
                }
                check!(format!("intervals = {intervals:?}"), erase_overlap_intervals(&intervals), n - most);
            }
        }

        #[test]
        fn scale_200k() {
            // Pairs (2i, 2i + 2) and (2i + 1, 2i + 3): the (2i, 2i + 2) ones can all be kept.
            let intervals: Vec<(i32, i32)> = (0..100_000).rev().flat_map(|i| [(2 * i + 1, 2 * i + 3), (2 * i, 2 * i + 2)]).collect();
            check!("(2i, 2i + 2) and (2i + 1, 2i + 3) for i in 0..100000", erase_overlap_intervals(&intervals), 100_000);
        }
        """,
    ],
    wrong=dict(
        quadratic_dp="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let n = sorted.len();
                // best[i]: most intervals kept among 0..=i when interval i is kept.
                let mut best = vec![1usize; n];
                for i in 0..n {
                    for j in 0..i {
                        if sorted[j].1 <= sorted[i].0 {
                            best[i] = best[i].max(best[j] + 1);
                        }
                    }
                }
                n - best.into_iter().max().unwrap_or(0)
            }
        """,
        keep_earliest_start="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut kept = 0;
                let mut last_end: Option<i32> = None;
                for (start, end) in sorted {
                    if last_end.map_or(true, |e| start >= e) {
                        kept += 1;
                        last_end = Some(end);
                    }
                }
                intervals.len() - kept
            }
        """,
        touching_overlaps="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable_by_key(|iv| iv.1);
                let mut kept = 0;
                let mut last_end: Option<i32> = None;
                for (start, end) in sorted {
                    if last_end.map_or(true, |e| start > e) {
                        kept += 1;
                        last_end = Some(end);
                    }
                }
                intervals.len() - kept
            }
        """,
    ),
    hints=[("approach", "Flip it: keep as many intervals as possible. Of all intervals that could come first, keep the one that ends earliest."),
           ("rust", "`sort_unstable_by_key(|iv| iv.1)`, then keep an interval when its start is `>=` the last kept end."),
           ("edge case", "Sorting by start and keeping the first one fails on `[(1, 10), (2, 3), (4, 5)]`.")],
    notes=("Exchange argument: in any best solution, swapping the first kept interval for the one with the earliest end keeps it valid. So sort by end and keep greedily; the answer is n minus the number kept.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="If each interval had a weight and you wanted to keep the most total weight, does greedy still work? (No: weighted interval scheduling is a DP with binary search.)",
    related=["D12", "D4"],
))

P.append(dict(
    slug="minimum-number-of-arrows-to-burst-balloons", title="Minimum number of arrows to burst balloons", level="medium", stage="intervals", tags=["intervals", "greedy"],
    companies=["Meta", "Amazon"],
    teaches=["Sort by end and shoot at the end: the same activity-selection idea as non-overlapping intervals.", "Compare with `cmp`/`sort_by_key`, never by subtracting `i32`s (overflow)."],
    statement="""
        Each balloon spans the closed range `(start, end)` on the x-axis, `start ≤ end`. An arrow shot at `x`
        bursts every balloon with `start ≤ x ≤ end`. Return the fewest arrows that burst every balloon.
    """,
    examples=[("points = [(10, 16), (2, 8), (1, 6), (7, 12)]", "2"), ("points = [(1, 2), (2, 3), (3, 4), (4, 5)]", "2")],
    constraints=["0 ≤ points.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
            let mut sorted = points.to_vec();
            sorted.sort_unstable_by_key(|p| p.1);
            let mut arrows = 0;
            let mut last: Option<i32> = None;
            for (start, end) in sorted {
                if last.map_or(true, |x| start > x) {
                    arrows += 1;
                    last = Some(end);
                }
            }
            arrows
        }
    """,
    visible=[
        T("leetcode_two", "points = [(10, 16), (2, 8), (1, 6), (7, 12)]", "find_min_arrow_shots(&[(10, 16), (2, 8), (1, 6), (7, 12)])", "2"),
        T("leetcode_apart", "points = [(1, 2), (3, 4), (5, 6), (7, 8)]", "find_min_arrow_shots(&[(1, 2), (3, 4), (5, 6), (7, 8)])", "4"),
        T("leetcode_touching", "points = [(1, 2), (2, 3), (3, 4), (4, 5)]", "find_min_arrow_shots(&[(1, 2), (2, 3), (3, 4), (4, 5)])", "2"),
        T("no_balloons", "points = []", "find_min_arrow_shots(&[])", "0"),
        T("one_balloon", "points = [(3, 7)]", "find_min_arrow_shots(&[(3, 7)])", "1"),
        T("nested", "points = [(1, 10), (3, 4)]", "find_min_arrow_shots(&[(1, 10), (3, 4)])", "1"),
    ],
    hidden=[
        T("touch_once", "points = [(1, 2), (2, 3)]", "find_min_arrow_shots(&[(1, 2), (2, 3)])", "1"),
        T("points_only", "points = [(5, 5), (5, 5)]", "find_min_arrow_shots(&[(5, 5), (5, 5)])", "1"),
        T("i32_whole_line", "points = [(MIN, MAX), (MAX, MAX)]", "find_min_arrow_shots(&[(i32::MIN, i32::MAX), (i32::MAX, i32::MAX)])", "1"),
        T("i32_far_ends", "points = [(MIN, MIN), (MAX, MAX)]", "find_min_arrow_shots(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)])", "2"),
        T("leetcode_overflow", "points = [(-2147483646, -2147483645), (2147483646, 2147483647)]", "find_min_arrow_shots(&[(-2147483646, -2147483645), (2147483646, 2147483647)])", "2"),
        T("start_sort_trap", "points = [(1, 10), (2, 3), (4, 5)]", "find_min_arrow_shots(&[(1, 10), (2, 3), (4, 5)])", "2"),
        T("negatives", "points = [(-5, -3), (-4, 0), (1, 2)]", "find_min_arrow_shots(&[(-5, -3), (-4, 0), (1, 2)])", "2"),
        T("duplicates", "points = [(1, 3), (1, 3), (1, 3), (4, 4)]", "find_min_arrow_shots(&[(1, 3), (1, 3), (1, 3), (4, 4)])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(810);
            for _ in 0..300 {
                let n = rng.below(8);
                let points: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(0, 5) as i32;
                        (s, s + len)
                    })
                    .collect();
                // Some best set of arrows sits at balloon ends: try every subset of ends.
                let mut want = n;
                for mask in 0u32..1 << n {
                    let shots: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| points[i].1).collect();
                    if points.iter().all(|&(s, e)| shots.iter().any(|&x| s <= x && x <= e)) {
                        want = want.min(shots.len());
                    }
                }
                check!(format!("points = {points:?}"), find_min_arrow_shots(&points), want);
            }
        }

        #[test]
        fn scale_200k() {
            let points: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 1)).collect();
            check!("(2i, 2i + 1) for i in 0..200000, reversed", find_min_arrow_shots(&points), 200_000);
        }
        """,
    ],
    wrong=dict(
        retain_per_arrow="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut left = points.to_vec();
                left.sort_unstable_by_key(|p| p.1);
                let mut arrows = 0;
                while let Some(&(_, x)) = left.first() {
                    arrows += 1;
                    left.retain(|&(s, _)| s > x);
                }
                arrows
            }
        """,
        start_sort_no_shrink="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut sorted = points.to_vec();
                sorted.sort_unstable();
                let mut arrows = 0;
                let mut last: Option<i32> = None;
                for (start, end) in sorted {
                    if last.map_or(true, |x| start > x) {
                        arrows += 1;
                        last = Some(end);
                    }
                }
                arrows
            }
        """,
        touching_needs_two="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut sorted = points.to_vec();
                sorted.sort_unstable_by_key(|p| p.1);
                let mut arrows = 0;
                let mut last: Option<i32> = None;
                for (start, end) in sorted {
                    if last.map_or(true, |x| start >= x) {
                        arrows += 1;
                        last = Some(end);
                    }
                }
                arrows
            }
        """,
    ),
    hints=[("approach", "The balloon that ends first must be hit by some arrow; shooting at its end hits as many others as possible."),
           ("rust", "`sort_unstable_by_key(|p| p.1)` compares safely; a comparator like `a.1 - b.1` overflows at the `i32` extremes."),
           ("edge case", "Balloons are closed: one arrow at 2 bursts both `(1, 2)` and `(2, 3)`.")],
    notes=("Sorted by end, shoot at the first unburst balloon's end; every balloon starting at or before that point is burst too. It's the same greedy as non-overlapping intervals with closed ends.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="How does this relate to Non-overlapping intervals? Can you get one answer from the other?",
    related=["D12"],
))

P.append(dict(
    slug="meeting-rooms-ii", title="Meeting rooms II", level="medium", stage="intervals", tags=["intervals", "sweep line", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg", "Uber"],
    teaches=["Sweep line: sort the starts and the ends separately and walk them together.", "A min-heap of end times (`BinaryHeap<Reverse<i32>>`) is the other classic way."],
    statement="""
        Each meeting is `(start, end)` with `start < end`, covering the time from `start` up to but not including
        `end`. Return the fewest rooms needed to hold every meeting. A room freed at time `t` can host a meeting
        starting at `t`.
    """,
    examples=[("meetings = [(0, 30), (5, 10), (15, 20)]", "2"), ("meetings = [(7, 10), (2, 4)]", "1")],
    constraints=["0 ≤ meetings.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
            let mut starts: Vec<i32> = meetings.iter().map(|m| m.0).collect();
            let mut ends: Vec<i32> = meetings.iter().map(|m| m.1).collect();
            starts.sort_unstable();
            ends.sort_unstable();
            let (mut in_use, mut most, mut j) = (0usize, 0usize, 0usize);
            for &s in &starts {
                // Every meeting that ended by `s` has freed its room.
                while ends[j] <= s {
                    in_use -= 1;
                    j += 1;
                }
                in_use += 1;
                most = most.max(in_use);
            }
            most
        }
    """,
    visible=[
        T("leetcode_two", "meetings = [(0, 30), (5, 10), (15, 20)]", "min_meeting_rooms(&[(0, 30), (5, 10), (15, 20)])", "2"),
        T("leetcode_one", "meetings = [(7, 10), (2, 4)]", "min_meeting_rooms(&[(7, 10), (2, 4)])", "1"),
        T("no_meetings", "meetings = []", "min_meeting_rooms(&[])", "0"),
        T("single", "meetings = [(1, 2)]", "min_meeting_rooms(&[(1, 2)])", "1"),
        T("back_to_back_share", "meetings = [(1, 5), (5, 10)]", "min_meeting_rooms(&[(1, 5), (5, 10)])", "1"),
        T("all_at_once", "meetings = [(1, 5), (1, 5), (1, 5)]", "min_meeting_rooms(&[(1, 5), (1, 5), (1, 5)])", "3"),
    ],
    hidden=[
        T("nested", "meetings = [(1, 10), (2, 9), (3, 8)]", "min_meeting_rooms(&[(1, 10), (2, 9), (3, 8)])", "3"),
        T("chain", "meetings = [(1, 3), (2, 4), (3, 5)]", "min_meeting_rooms(&[(1, 3), (2, 4), (3, 5)])", "2"),
        T("negatives", "meetings = [(-10, -5), (-6, 0), (-5, 1)]", "min_meeting_rooms(&[(-10, -5), (-6, 0), (-5, 1)])", "2"),
        T("i32_extremes", "meetings = [(MIN, MAX), (0, 1), (1, 2)]", "min_meeting_rooms(&[(i32::MIN, i32::MAX), (0, 1), (1, 2)])", "2"),
        T("i32_touching", "meetings = [(MIN, 0), (0, MAX)]", "min_meeting_rooms(&[(i32::MIN, 0), (0, i32::MAX)])", "1"),
        T("leetcode_unsorted", "meetings = [(9, 10), (4, 9), (4, 17)]", "min_meeting_rooms(&[(9, 10), (4, 9), (4, 17)])", "2"),
        T("leetcode_shared_end", "meetings = [(2, 11), (6, 16), (11, 16)]", "min_meeting_rooms(&[(2, 11), (6, 16), (11, 16)])", "2"),
        T("classic_six", "meetings = [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]", "min_meeting_rooms(&[(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)])", "4"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(811);
            for _ in 0..400 {
                let n = rng.below(9);
                let meetings: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                // The busiest moment is always some meeting's start.
                let want = meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0);
                check!(format!("meetings = {meetings:?}"), min_meeting_rooms(&meetings), want);
            }
        }

        #[test]
        fn scale_200k() {
            let meetings: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (i, i + 1000)).collect();
            check!("(i, i + 1000) for i in 0..200000", min_meeting_rooms(&meetings), 1000);
        }
        """,
    ],
    wrong=dict(
        count_at_each_start="""
            pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
                meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0)
            }
        """,
        touching_needs_new_room="""
            pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
                let mut starts: Vec<i32> = meetings.iter().map(|m| m.0).collect();
                let mut ends: Vec<i32> = meetings.iter().map(|m| m.1).collect();
                starts.sort_unstable();
                ends.sort_unstable();
                let (mut in_use, mut most, mut j) = (0usize, 0usize, 0usize);
                for &s in &starts {
                    while ends[j] < s {
                        in_use -= 1;
                        j += 1;
                    }
                    in_use += 1;
                    most = most.max(in_use);
                }
                most
            }
        """,
    ),
    hints=[("approach", "Only the number of meetings running at once matters. Walk the start times in order and free a room for every meeting that has ended by then."),
           ("rust", "Collect and sort `starts` and `ends` separately; one index into `ends` follows the loop over `starts`. Or keep a `BinaryHeap<Reverse<i32>>` of end times."),
           ("edge case", "Free rooms with `end <= start`, so a meeting ending at 5 frees its room for one starting at 5.")],
    notes=("The rooms needed equal the most meetings running at any moment. Sorting starts and ends separately and sweeping counts that without tracking which meeting is in which room.", "O(n log n)", "O(n)"),
    follow_up="How would you also report which room each meeting goes to?",
    related=["D7", "S5"],
))

P.append(dict(
    slug="interval-list-intersections", title="Interval list intersections", level="medium", stage="intervals", tags=["intervals", "two pointers"],
    companies=["Meta", "Amazon", "Google"],
    teaches=["Two pointers over two sorted lists: always advance the interval that ends first.", "The overlap of two closed intervals is `(max of starts, min of ends)` when that's non-empty."],
    statement="""
        `a` and `b` are lists of closed intervals, each sorted by start with no two intervals in the same list
        overlapping. Return every intersection of an interval from `a` with one from `b`, sorted by start.
        A single shared point, like `(5, 5)`, counts.
    """,
    examples=[("a = [(0, 2), (5, 10), (13, 23), (24, 25)], b = [(1, 5), (8, 12), (15, 24), (25, 26)]", "[(1, 2), (5, 5), (8, 10), (15, 23), (24, 24), (25, 25)]")],
    constraints=["0 ≤ a.len(), b.len() ≤ 10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
            let mut out = Vec::new();
            let (mut i, mut j) = (0, 0);
            while i < a.len() && j < b.len() {
                let lo = a[i].0.max(b[j].0);
                let hi = a[i].1.min(b[j].1);
                if lo <= hi {
                    out.push((lo, hi));
                }
                if a[i].1 < b[j].1 {
                    i += 1;
                } else {
                    j += 1;
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_mixed", "a = [(0, 2), (5, 10), (13, 23), (24, 25)], b = [(1, 5), (8, 12), (15, 24), (25, 26)]", "interval_intersection(&[(0, 2), (5, 10), (13, 23), (24, 25)], &[(1, 5), (8, 12), (15, 24), (25, 26)])", "vec![(1, 2), (5, 5), (8, 10), (15, 23), (24, 24), (25, 25)]"),
        T("leetcode_one_empty", "a = [(1, 3), (5, 9)], b = []", "interval_intersection(&[(1, 3), (5, 9)], &[])", "Vec::<(i32, i32)>::new()"),
        T("both_empty", "a = [], b = []", "interval_intersection(&[], &[])", "Vec::<(i32, i32)>::new()"),
        T("shared_point", "a = [(1, 5)], b = [(5, 8)]", "interval_intersection(&[(1, 5)], &[(5, 8)])", "vec![(5, 5)]"),
        T("one_covers_many", "a = [(0, 10)], b = [(1, 2), (4, 5)]", "interval_intersection(&[(0, 10)], &[(1, 2), (4, 5)])", "vec![(1, 2), (4, 5)]"),
        T("no_overlap", "a = [(1, 2)], b = [(3, 4)]", "interval_intersection(&[(1, 2)], &[(3, 4)])", "Vec::<(i32, i32)>::new()"),
    ],
    hidden=[
        T("identical", "a = [(1, 2), (4, 6)], b = [(1, 2), (4, 6)]", "interval_intersection(&[(1, 2), (4, 6)], &[(1, 2), (4, 6)])", "vec![(1, 2), (4, 6)]"),
        T("negatives", "a = [(-5, -2), (0, 3)], b = [(-3, 1)]", "interval_intersection(&[(-5, -2), (0, 3)], &[(-3, 1)])", "vec![(-3, -2), (0, 1)]"),
        T("i32_extremes", "a = [(MIN, MAX)], b = [(MIN, MIN), (MAX, MAX)]", "interval_intersection(&[(i32::MIN, i32::MAX)], &[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)])", "vec![(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)]"),
        T("points_meet", "a = [(3, 3)], b = [(3, 3)]", "interval_intersection(&[(3, 3)], &[(3, 3)])", "vec![(3, 3)]"),
        T("interleaved", "a = [(1, 3), (5, 7), (9, 11)], b = [(2, 6), (8, 10)]", "interval_intersection(&[(1, 3), (5, 7), (9, 11)], &[(2, 6), (8, 10)])", "vec![(2, 3), (5, 6), (9, 10)]"),
        T("swapped_arguments", "a = [(2, 6), (8, 10)], b = [(1, 3), (5, 7), (9, 11)]", "interval_intersection(&[(2, 6), (8, 10)], &[(1, 3), (5, 7), (9, 11)])", "vec![(2, 3), (5, 6), (9, 10)]"),
        T("same_end", "a = [(1, 4), (6, 7)], b = [(2, 4), (5, 7)]", "interval_intersection(&[(1, 4), (6, 7)], &[(2, 4), (5, 7)])", "vec![(2, 4), (6, 7)]"),
        T("first_list_empty", "a = [], b = [(1, 2)]", "interval_intersection(&[], &[(1, 2)])", "Vec::<(i32, i32)>::new()"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn list(rng: &mut anneal_prelude::Rng) -> Vec<(i32, i32)> {
                let n = rng.below(6);
                let mut out = Vec::new();
                let mut pos = rng.int(-3, 3) as i32;
                for _ in 0..n {
                    let len = rng.int(0, 4) as i32;
                    out.push((pos, pos + len));
                    let gap = rng.int(1, 4) as i32;
                    pos += len + gap;
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(812);
            for _ in 0..400 {
                let a = list(&mut rng);
                let b = list(&mut rng);
                let mut want = Vec::new();
                for &(s1, e1) in &a {
                    for &(s2, e2) in &b {
                        if s1.max(s2) <= e1.min(e2) {
                            want.push((s1.max(s2), e1.min(e2)));
                        }
                    }
                }
                want.sort_unstable();
                check!(format!("a = {a:?}, b = {b:?}"), interval_intersection(&a, &b), want);
            }
        }

        #[test]
        fn scale_100k_each() {
            let a: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i, 4 * i + 2)).collect();
            let b: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i + 1, 4 * i + 3)).collect();
            let out = interval_intersection(&a, &b);
            check!("a = (4i, 4i + 2), b = (4i + 1, 4i + 3) for i in 0..100000", (out.len(), out[0], out[99_999]), (100_000, (1, 2), (399_997, 399_998)));
        }
        """,
    ],
    wrong=dict(
        all_pairs="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                for &(s1, e1) in a {
                    for &(s2, e2) in b {
                        if s1.max(s2) <= e1.min(e2) {
                            out.push((s1.max(s2), e1.min(e2)));
                        }
                    }
                }
                out.sort_unstable();
                out
            }
        """,
        drops_points="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut i, mut j) = (0, 0);
                while i < a.len() && j < b.len() {
                    let lo = a[i].0.max(b[j].0);
                    let hi = a[i].1.min(b[j].1);
                    if lo < hi {
                        out.push((lo, hi));
                    }
                    if a[i].1 < b[j].1 {
                        i += 1;
                    } else {
                        j += 1;
                    }
                }
                out
            }
        """,
        advance_later_end="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut i, mut j) = (0, 0);
                while i < a.len() && j < b.len() {
                    let lo = a[i].0.max(b[j].0);
                    let hi = a[i].1.min(b[j].1);
                    if lo <= hi {
                        out.push((lo, hi));
                    }
                    if a[i].0 < b[j].0 {
                        i += 1;
                    } else {
                        j += 1;
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Keep one index in each list. Record the overlap of the two current intervals, then move past whichever ends first: it can't meet anything later."),
           ("rust", "`let lo = a[i].0.max(b[j].0); let hi = a[i].1.min(b[j].1);` and push `(lo, hi)` when `lo <= hi`."),
           ("edge case", "Closed intervals: `(1, 5)` and `(5, 8)` intersect in `(5, 5)`.")],
    notes=("The interval that ends first can't overlap anything after the other list's current interval, so dropping it is safe. Each step advances one index.", "O(n + m)", "O(1) besides the output"),
    follow_up="How would you intersect k lists at once?",
    related=["D2", "D7"],
))

P.append(dict(
    slug="car-pooling", title="Car pooling", level="medium", stage="intervals", tags=["sweep line", "sorting"],
    companies=["Amazon", "Google"],
    teaches=["Turn intervals into `(position, change)` events and sort them.", "Sorting tuples puts drop-offs (negative change) before pick-ups at the same stop."],
    statement="""
        A car drives east with room for `capacity` passengers. Trip `(passengers, from, to)` picks up that many
        people at `from` and drops them at `to` (`from < to`). At any stop, passengers get off before new ones
        get on. Return `true` if every trip fits.
    """,
    examples=[("trips = [(2, 1, 5), (3, 3, 7)], capacity = 4", "false"), ("trips = [(2, 1, 5), (3, 3, 7)], capacity = 5", "true")],
    constraints=["0 ≤ trips.len() ≤ 10⁵", "1 ≤ passengers ≤ 1000", "0 ≤ from < to ≤ 2·10⁹", "0 ≤ capacity ≤ 10⁹"],
    starter="""
        pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
            let mut events: Vec<(u32, i64)> = Vec::with_capacity(2 * trips.len());
            for &(people, from, to) in trips {
                events.push((from, people as i64));
                events.push((to, -(people as i64)));
            }
            // At the same stop, the negative (drop-off) changes sort first.
            events.sort_unstable();
            let mut load = 0i64;
            for (_, change) in events {
                load += change;
                if load > capacity as i64 {
                    return false;
                }
            }
            true
        }
    """,
    visible=[
        T("leetcode_too_many", "trips = [(2, 1, 5), (3, 3, 7)], capacity = 4", "car_pooling(&[(2, 1, 5), (3, 3, 7)], 4)", "false"),
        T("leetcode_fits", "trips = [(2, 1, 5), (3, 3, 7)], capacity = 5", "car_pooling(&[(2, 1, 5), (3, 3, 7)], 5)", "true"),
        T("leetcode_three", "trips = [(3, 2, 7), (3, 7, 9), (8, 3, 9)], capacity = 11", "car_pooling(&[(3, 2, 7), (3, 7, 9), (8, 3, 9)], 11)", "true"),
        T("no_trips", "trips = [], capacity = 0", "car_pooling(&[], 0)", "true"),
        T("one_trip_too_big", "trips = [(5, 0, 1)], capacity = 4", "car_pooling(&[(5, 0, 1)], 4)", "false"),
        T("drop_off_first", "trips = [(3, 1, 5), (3, 5, 9)], capacity = 3", "car_pooling(&[(3, 1, 5), (3, 5, 9)], 3)", "true"),
    ],
    hidden=[
        T("exactly_full", "trips = [(4, 0, 10)], capacity = 4", "car_pooling(&[(4, 0, 10)], 4)", "true"),
        T("zero_capacity", "trips = [(1, 0, 1)], capacity = 0", "car_pooling(&[(1, 0, 1)], 0)", "false"),
        T("far_stops", "trips = [(1, 0, 1000000000), (1, 999999999, 1000000000)], capacity = 1", "car_pooling(&[(1, 0, 1_000_000_000), (1, 999_999_999, 1_000_000_000)], 1)", "false"),
        T("three_at_one_point", "trips = [(1, 0, 10), (1, 5, 6), (1, 5, 7)], capacity = 2", "car_pooling(&[(1, 0, 10), (1, 5, 6), (1, 5, 7)], 2)", "false"),
        T("relay", "trips = [(2, 0, 3), (2, 3, 6), (2, 6, 9)], capacity = 2", "car_pooling(&[(2, 0, 3), (2, 3, 6), (2, 6, 9)], 2)", "true"),
        T("unsorted_trips", "trips = [(2, 6, 9), (3, 0, 7)], capacity = 4", "car_pooling(&[(2, 6, 9), (3, 0, 7)], 4)", "false"),
        T("same_trip_twice", "trips = [(2, 1, 4), (2, 1, 4)], capacity = 4", "car_pooling(&[(2, 1, 4), (2, 1, 4)], 4)", "true"),
        T("big_capacity", "trips = [(1000, 0, 1); 1000], capacity = 1000000", "car_pooling(&vec![(1000, 0, 1); 1000], 1_000_000)", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(813);
            for _ in 0..400 {
                let n = rng.below(7);
                let trips: Vec<(u32, u32, u32)> = (0..n)
                    .map(|_| {
                        let people = rng.int(1, 5) as u32;
                        let from = rng.int(0, 10) as u32;
                        let len = rng.int(1, 5) as u32;
                        (people, from, from + len)
                    })
                    .collect();
                let capacity = rng.int(0, 12) as u32;
                let want = (0..=15u32).all(|x| trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0).sum::<u32>() <= capacity);
                check!(format!("trips = {trips:?}, capacity = {capacity}"), car_pooling(&trips, capacity), want);
            }
        }

        #[test]
        fn scale_100k() {
            let trips: Vec<(u32, u32, u32)> = (0..100_000u32).rev().map(|i| (1, i * 10_000, i * 10_000 + 5_000_000)).collect();
            check!("(1, 10000i, 10000i + 5000000) for i in 0..100000, capacity 500 and 499", (car_pooling(&trips, 500), car_pooling(&trips, 499)), (true, false));
        }
        """,
    ],
    wrong=dict(
        check_every_start="""
            pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
                trips.iter().all(|&(_, x, _)| {
                    trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0 as u64).sum::<u64>() <= capacity as u64
                })
            }
        """,
        pick_up_first="""
            pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
                let mut events: Vec<(u32, i64)> = Vec::new();
                for &(people, from, to) in trips {
                    events.push((from, people as i64));
                    events.push((to, -(people as i64)));
                }
                events.sort_unstable_by_key(|&(at, change)| (at, -change));
                let mut load = 0i64;
                for (_, change) in events {
                    load += change;
                    if load > capacity as i64 {
                        return false;
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "Only the load at each stop matters. Make an event `(from, +people)` and `(to, -people)` for each trip, sort them, and keep a running total."),
           ("rust", "A `Vec<(u32, i64)>` sorts by stop, then by change, so at the same stop the drop-offs (negative) come first for free."),
           ("edge case", "Stops go up to 2·10⁹, so a difference array indexed by stop would be too big here; sort the events instead.")],
    notes=("The load only changes at pick-ups and drop-offs. Sorting the 2n events and summing them checks the load at every stop.", "O(n log n)", "O(n)"),
    follow_up="If stops were at most 1000, how would a difference array make this O(n + 1000)?",
    related=["D1", "S3"],
))

# ---------------------------------------------------------------- greedy choices

P.append(dict(
    slug="jump-game", title="Jump game", level="medium", stage="greedy-choices", tags=["greedy", "arrays", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Keep one number, the farthest reachable index, instead of exploring every jump.", "`iter().enumerate()` with an early `return false` once `i` passes the frontier."],
    statement="""
        You start on index 0 of `nums`. From index `i` you may jump forward by any distance from 1 up to
        `nums[i]`, so `nums[i] = 0` means you're stuck there. Return `true` if you can reach the last index.
    """,
    examples=[("nums = [2, 3, 1, 1, 4]", "true"), ("nums = [3, 2, 1, 0, 4]", "false")],
    constraints=["1 ≤ nums.len() ≤ 2·10⁵", "0 ≤ nums[i] ≤ 10⁹"],
    starter="""
        pub fn can_jump(nums: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_jump(nums: &[u32]) -> bool {
            // Every index up to `reach` can be landed on.
            let mut reach = 0usize;
            for (i, &jump) in nums.iter().enumerate() {
                if i > reach {
                    return false;
                }
                reach = reach.max(i + jump as usize);
            }
            true
        }
    """,
    visible=[
        T("leetcode_reachable", "nums = [2, 3, 1, 1, 4]", "can_jump(&[2, 3, 1, 1, 4])", "true"),
        T("leetcode_stuck", "nums = [3, 2, 1, 0, 4]", "can_jump(&[3, 2, 1, 0, 4])", "false"),
        T("already_there", "nums = [0]", "can_jump(&[0])", "true"),
        T("stuck_at_start", "nums = [0, 1]", "can_jump(&[0, 1])", "false"),
        T("jump_over_a_zero", "nums = [2, 0, 1]", "can_jump(&[2, 0, 1])", "true"),
        T("shorter_jumps_allowed", "nums = [5, 0]", "can_jump(&[5, 0])", "true"),
    ],
    hidden=[
        T("two_ones", "nums = [1, 1]", "can_jump(&[1, 1])", "true"),
        T("zero_in_the_middle", "nums = [1, 0, 1]", "can_jump(&[1, 0, 1])", "false"),
        T("zero_at_the_end", "nums = [1, 1, 0]", "can_jump(&[1, 1, 0])", "true"),
        T("one_short", "nums = [3, 0, 0, 0, 1]", "can_jump(&[3, 0, 0, 0, 1])", "false"),
        T("just_enough", "nums = [4, 0, 0, 0, 1]", "can_jump(&[4, 0, 0, 0, 1])", "true"),
        T("later_index_reaches_further", "nums = [1, 2, 0, 0, 1]", "can_jump(&[1, 2, 0, 0, 1])", "false"),
        T("huge_jump", "nums = [1000000000, 0, 0, 0]", "can_jump(&[1_000_000_000, 0, 0, 0])", "true"),
        T("all_zeros", "nums = [0; 100]", "can_jump(&vec![0; 100])", "false"),
        T("relay", "nums = [2, 5, 0, 0, 0, 0, 1]", "can_jump(&[2, 5, 0, 0, 0, 0, 1])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(814);
            for _ in 0..400 {
                let n = 1 + rng.below(10);
                let nums: Vec<u32> = rng.vec(n, 0, 3);
                // Mark every index each reachable index can land on.
                let mut ok = vec![false; n];
                ok[0] = true;
                for i in 0..n {
                    if ok[i] {
                        for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                            ok[j] = true;
                        }
                    }
                }
                check!(format!("nums = {nums:?}"), can_jump(&nums), ok[n - 1]);
            }
        }

        #[test]
        fn scale_200k() {
            // nums[i] = 199998 - i: every jump lands at or before index 199998, which holds 0.
            let n = 200_000u32;
            let stuck: Vec<u32> = (0..n).map(|i| (n - 2).saturating_sub(i)).collect();
            let mut fixed = stuck.clone();
            fixed[0] = n - 1;
            check!("nums[i] = 199998 - i (then zeros); then with nums[0] = 199999", (can_jump(&stuck), can_jump(&fixed)), (false, true));
        }
        """,
    ],
    wrong=dict(
        mark_every_landing="""
            pub fn can_jump(nums: &[u32]) -> bool {
                let n = nums.len();
                let mut ok = vec![false; n];
                ok[0] = true;
                for i in 0..n {
                    if ok[i] {
                        for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                            ok[j] = true;
                        }
                    }
                }
                ok[n - 1]
            }
        """,
        no_frontier_check="""
            pub fn can_jump(nums: &[u32]) -> bool {
                let far = nums.iter().enumerate().map(|(i, &j)| i + j as usize).max().unwrap_or(0);
                far >= nums.len() - 1
            }
        """,
        zero_means_stuck="""
            pub fn can_jump(nums: &[u32]) -> bool {
                nums[..nums.len() - 1].iter().all(|&j| j > 0)
            }
        """,
    ),
    hints=[("approach", "Keep `reach`, the farthest index you can get to so far. Walk left to right; if you ever stand past `reach`, you're stuck."),
           ("rust", "`for (i, &jump) in nums.iter().enumerate()` and `reach = reach.max(i + jump as usize)`."),
           ("edge case", "A single index is already the last one, and a zero only matters if you can't jump over it.")],
    notes=("You can stop anywhere along a jump, so every index up to `reach` is reachable. One pass that extends `reach` and fails when `i > reach` decides it.", "O(n)", "O(1)"),
    follow_up="How would you return the fewest jumps instead? (That's Jump game II.)",
    related=["D12"],
))

P.append(dict(
    slug="jump-game-ii", title="Jump game II", level="medium", stage="greedy-choices", tags=["greedy", "BFS", "arrays"],
    companies=["Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["BFS by levels collapses into two numbers when each level is a contiguous window.", "`Option<usize>` for \"can't be reached\" instead of LeetCode's guarantee."],
    statement="""
        The moves are the same as in Jump game: from index `i` you may jump forward by 1 up to `nums[i]`
        places. Return the fewest jumps from index 0 to the last index, or `None` if it can't be reached.
    """,
    examples=[("nums = [2, 3, 1, 1, 4]", "Some(2)"), ("nums = [2, 3, 0, 1, 4]", "Some(2)")],
    constraints=["1 ≤ nums.len() ≤ 2·10⁵", "0 ≤ nums[i] ≤ 10⁹"],
    starter="""
        pub fn jump(nums: &[u32]) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn jump(nums: &[u32]) -> Option<usize> {
            let last = nums.len() - 1;
            // Indices up to `end` take `jumps` jumps; `far` is how far one more jump gets.
            let (mut jumps, mut end, mut far) = (0, 0, 0);
            for (i, &step) in nums[..last].iter().enumerate() {
                far = far.max(i + step as usize);
                if i == end {
                    if far <= i {
                        return None;
                    }
                    jumps += 1;
                    end = far;
                    if end >= last {
                        break;
                    }
                }
            }
            Some(jumps)
        }
    """,
    visible=[
        T("leetcode_two", "nums = [2, 3, 1, 1, 4]", "jump(&[2, 3, 1, 1, 4])", "Some(2)"),
        T("leetcode_zero_inside", "nums = [2, 3, 0, 1, 4]", "jump(&[2, 3, 0, 1, 4])", "Some(2)"),
        T("already_there", "nums = [0]", "jump(&[0])", "Some(0)"),
        T("unreachable", "nums = [1, 0, 1]", "jump(&[1, 0, 1])", "None"),
        T("one_step_at_a_time", "nums = [1, 1, 1, 1]", "jump(&[1, 1, 1, 1])", "Some(3)"),
        T("longest_jump_is_not_best", "nums = [3, 1, 4, 1, 1, 1, 1]", "jump(&[3, 1, 4, 1, 1, 1, 1])", "Some(2)"),
    ],
    hidden=[
        T("two_cells", "nums = [1, 0]", "jump(&[1, 0])", "Some(1)"),
        T("stuck_at_start", "nums = [0, 5]", "jump(&[0, 5])", "None"),
        T("overshoot", "nums = [10, 0]", "jump(&[10, 0])", "Some(1)"),
        T("stuck_after_a_level", "nums = [1, 1, 0, 1]", "jump(&[1, 1, 0, 1])", "None"),
        T("huge_jumps", "nums = [1000000000; 5]", "jump(&[1_000_000_000; 5])", "Some(1)"),
        T("window_edge", "nums = [2, 1, 1, 1]", "jump(&[2, 1, 1, 1])", "Some(2)"),
        T("three_levels", "nums = [1, 2, 1, 1, 1]", "jump(&[1, 2, 1, 1, 1])", "Some(3)"),
        T("exact_landing", "nums = [2, 0, 0]", "jump(&[2, 0, 0])", "Some(1)"),
        T("zero_on_the_last_index", "nums = [1, 1, 0]", "jump(&[1, 1, 0])", "Some(2)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(815);
            for _ in 0..400 {
                let n = 1 + rng.below(10);
                let nums: Vec<u32> = rng.vec(n, 0, 3);
                // dist[j]: fewest jumps to j, filled left to right.
                let mut dist: Vec<Option<usize>> = vec![None; n];
                dist[0] = Some(0);
                for i in 0..n {
                    let Some(d) = dist[i] else { continue };
                    for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                        dist[j] = Some(dist[j].map_or(d + 1, |x| x.min(d + 1)));
                    }
                }
                check!(format!("nums = {nums:?}"), jump(&nums), dist[n - 1]);
            }
        }

        #[test]
        fn scale_200k() {
            let ones = vec![1u32; 200_000];
            let big = vec![200_000u32; 200_000];
            let stuck: Vec<u32> = (0..200_000u32).map(|i| 199_998u32.saturating_sub(i)).collect();
            check!("200000 ones; 200000 × 200000; nums[i] = 199998 - i", (jump(&ones), jump(&big), jump(&stuck)), (Some(199_999), Some(1), None));
        }
        """,
    ],
    wrong=dict(
        quadratic_dp="""
            pub fn jump(nums: &[u32]) -> Option<usize> {
                let n = nums.len();
                let mut best: Vec<Option<usize>> = vec![None; n];
                best[0] = Some(0);
                for i in 0..n {
                    let Some(b) = best[i] else { continue };
                    for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                        if best[j].map_or(true, |x| b + 1 < x) {
                            best[j] = Some(b + 1);
                        }
                    }
                }
                best[n - 1]
            }
        """,
        longest_jump_each_time="""
            pub fn jump(nums: &[u32]) -> Option<usize> {
                let last = nums.len() - 1;
                let (mut i, mut jumps) = (0usize, 0usize);
                while i < last {
                    if nums[i] == 0 {
                        return None;
                    }
                    i += nums[i] as usize;
                    jumps += 1;
                }
                Some(jumps)
            }
        """,
        counts_the_last_index="""
            pub fn jump(nums: &[u32]) -> Option<usize> {
                let (mut jumps, mut end, mut far) = (0, 0, 0);
                for (i, &step) in nums.iter().enumerate() {
                    far = far.max(i + step as usize);
                    if i == end {
                        if far <= i {
                            return None;
                        }
                        jumps += 1;
                        end = far;
                    }
                }
                Some(jumps)
            }
        """,
    ),
    hints=[("approach", "Think in rounds, like BFS: the indices reachable in exactly j jumps form a window. Scanning the current window tells you how far the next window reaches."),
           ("rust", "Keep `end` (the edge of the current window) and `far`. When `i == end` you must jump: count it and set `end = far`."),
           ("edge case", "Don't jump from the last index: loop over `nums[..last]`. If `far` hasn't passed `i` when you must jump, return `None`.")],
    notes=("The indices reachable in j jumps form a contiguous window, so BFS needs only the window's end and the farthest index seen inside it. Each index is scanned once.", "O(n)", "O(1)"),
    follow_up="How would you return the actual indices you land on, not just the count?",
    related=["D9", "D12"],
))

P.append(dict(
    slug="gas-station", title="Gas station", level="medium", stage="greedy-choices", tags=["greedy", "prefix sums"],
    companies=["Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["One failure rules out a whole range of starts, so one pass finds the only candidate.", "`(total >= 0).then_some(start)` turns a condition into an `Option`."],
    statement="""
        Gas stations stand in a circle. Station `i` sells `gas[i]` fuel, and driving from it to the next station
        (the last one leads back to station 0) burns `cost[i]`. The tank is unlimited and starts empty. Return a
        station you can start from and drive once around the circle, or `None`. If several work, return the
        smallest index.
    """,
    examples=[("gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2]", "Some(3)"), ("gas = [2, 3, 4], cost = [3, 4, 3]", "None")],
    constraints=["1 ≤ gas.len() = cost.len() ≤ 2·10⁵", "0 ≤ gas[i], cost[i] ≤ 10⁹"],
    starter="""
        pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
            let (mut total, mut tank, mut start) = (0i64, 0i64, 0usize);
            for (i, (&g, &c)) in gas.iter().zip(cost).enumerate() {
                let diff = g as i64 - c as i64;
                total += diff;
                tank += diff;
                if tank < 0 {
                    // No start from `start` to `i` gets past `i`.
                    start = i + 1;
                    tank = 0;
                }
            }
            (total >= 0).then_some(start)
        }
    """,
    visible=[
        T("leetcode_start_three", "gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2]", "can_complete_circuit(&[1, 2, 3, 4, 5], &[3, 4, 5, 1, 2])", "Some(3)"),
        T("leetcode_none", "gas = [2, 3, 4], cost = [3, 4, 3]", "can_complete_circuit(&[2, 3, 4], &[3, 4, 3])", "None"),
        T("single_enough", "gas = [5], cost = [4]", "can_complete_circuit(&[5], &[4])", "Some(0)"),
        T("single_short", "gas = [1], cost = [2]", "can_complete_circuit(&[1], &[2])", "None"),
        T("exactly_enough", "gas = [1, 1], cost = [1, 1]", "can_complete_circuit(&[1, 1], &[1, 1])", "Some(0)"),
        T("several_work_take_smallest", "gas = [1, 0, 2, 0], cost = [0, 1, 0, 2]", "can_complete_circuit(&[1, 0, 2, 0], &[0, 1, 0, 2])", "Some(0)"),
    ],
    hidden=[
        T("all_zero", "gas = [0], cost = [0]", "can_complete_circuit(&[0], &[0])", "Some(0)"),
        T("start_at_the_last", "gas = [0, 0, 5], cost = [1, 1, 1]", "can_complete_circuit(&[0, 0, 5], &[1, 1, 1])", "Some(2)"),
        T("start_at_the_first", "gas = [3, 1, 1], cost = [1, 2, 2]", "can_complete_circuit(&[3, 1, 1], &[1, 2, 2])", "Some(0)"),
        T("short_by_one", "gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 3]", "can_complete_circuit(&[1, 2, 3, 4, 5], &[3, 4, 5, 1, 3])", "None"),
        T("tank_past_i32", "gas = [1000000000, 1000000000, 1000000000, 0, 0, 0], cost = [0, 0, 0, 1000000000, 1000000000, 1000000000]", "can_complete_circuit(&[1_000_000_000, 1_000_000_000, 1_000_000_000, 0, 0, 0], &[0, 0, 0, 1_000_000_000, 1_000_000_000, 1_000_000_000])", "Some(0)"),
        T("two_resets", "gas = [5, 1, 2, 3, 4], cost = [4, 4, 1, 5, 1]", "can_complete_circuit(&[5, 1, 2, 3, 4], &[4, 4, 1, 5, 1])", "Some(4)"),
        T("three_resets", "gas = [1, 1, 1, 10], cost = [2, 2, 2, 1]", "can_complete_circuit(&[1, 1, 1, 10], &[2, 2, 2, 1])", "Some(3)"),
        T("dips_to_zero", "gas = [2, 0, 1], cost = [1, 1, 1]", "can_complete_circuit(&[2, 0, 1], &[1, 1, 1])", "Some(0)"),
        T("total_short_by_one_at_scale", "gas = [999999999, 0], cost = [0, 1000000000]", "can_complete_circuit(&[999_999_999, 0], &[0, 1_000_000_000])", "None"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(816);
            for _ in 0..400 {
                let n = 1 + rng.below(7);
                let gas: Vec<u32> = rng.vec(n, 0, 4);
                let cost: Vec<u32> = rng.vec(n, 0, 4);
                // Drive around from every start.
                let want = (0..n).find(|&s| {
                    let mut tank = 0i64;
                    (0..n).all(|k| {
                        let i = (s + k) % n;
                        tank += gas[i] as i64 - cost[i] as i64;
                        tank >= 0
                    })
                });
                check!(format!("gas = {gas:?}, cost = {cost:?}"), can_complete_circuit(&gas, &cost), want);
            }
        }

        #[test]
        fn scale_200k() {
            // Every start before 199998 drives a long way, then runs dry at station 199998.
            let n = 200_000usize;
            let mut gas = vec![1u32; n];
            let mut cost = vec![0u32; n];
            gas[n - 2] = 0;
            cost[n - 2] = (n - 1) as u32;
            gas[n - 1] = (n - 1) as u32;
            let mut short = gas.clone();
            short[n - 1] = 0;
            check!(
                "gas = [1, …, 1, 0, 199999], cost = [0, …, 0, 199999, 0]; then gas[199999] = 0",
                (can_complete_circuit(&gas, &cost), can_complete_circuit(&short, &cost)),
                (Some(199_999), None)
            );
        }
        """,
    ],
    wrong=dict(
        try_every_start="""
            pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
                let n = gas.len();
                (0..n).find(|&s| {
                    let mut tank = 0i64;
                    (0..n).all(|k| {
                        let i = (s + k) % n;
                        tank += gas[i] as i64 - cost[i] as i64;
                        tank >= 0
                    })
                })
            }
        """,
        no_total_check="""
            pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
                let (mut tank, mut start) = (0i64, 0usize);
                for i in 0..gas.len() {
                    tank += gas[i] as i64 - cost[i] as i64;
                    if tank < 0 {
                        start = i + 1;
                        tank = 0;
                    }
                }
                (start < gas.len()).then_some(start)
            }
        """,
        i32_tank="""
            pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
                let (mut total, mut tank, mut start) = (0i32, 0i32, 0usize);
                for i in 0..gas.len() {
                    let diff = gas[i] as i32 - cost[i] as i32;
                    total += diff;
                    tank += diff;
                    if tank < 0 {
                        start = i + 1;
                        tank = 0;
                    }
                }
                (total >= 0).then_some(start)
            }
        """,
    ),
    hints=[("approach", "If total gas is less than total cost, nothing works. Otherwise drive once with a running tank; when it goes negative at station i, no start from the current one up to i can work, so try i + 1."),
           ("rust", "Work in `i64`: `g as i64 - c as i64` can be negative and the sums can pass `i32::MAX`. `(total >= 0).then_some(start)` builds the answer."),
           ("edge case", "When several stations work, the restart rule already lands on the smallest one.")],
    notes=("If the tank first goes negative at i when starting from s, every start between s and i fails too: each reaches i with no more fuel than the run from s had. So one pass leaves a single candidate, and the total decides if it works. The candidate is where the running sum first hits its minimum, which is the smallest working start.", "O(n)", "O(1)"),
    follow_up="If the tank held at most C units, does the same single pass still work?",
    related=["D1", "D2"],
))

P.append(dict(
    slug="partition-labels", title="Partition labels", level="medium", stage="greedy-choices", tags=["greedy", "strings", "two pointers"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["A `[usize; 26]` table of last positions beats a `HashMap` for lowercase ASCII.", "Grow the current piece's end to the furthest last-position seen; cut when you reach it."],
    statement="""
        Cut `s` into as many pieces as possible so that each letter appears in at most one piece. Return the
        lengths of the pieces, in order. `s` holds only lowercase ASCII letters.
    """,
    examples=[("s = \"ababcbacadefegdehijhklij\"", "[9, 7, 8]"), ("s = \"eccbbbbdec\"", "[10]")],
    constraints=["0 ≤ s.len() ≤ 2·10⁵", "s holds only b'a'..=b'z'"],
    starter="""
        pub fn partition_labels(s: &str) -> Vec<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn partition_labels(s: &str) -> Vec<usize> {
            let bytes = s.as_bytes();
            let mut last = [0usize; 26];
            for (i, &b) in bytes.iter().enumerate() {
                last[(b - b'a') as usize] = i;
            }
            let mut sizes = Vec::new();
            let (mut start, mut end) = (0, 0);
            for (i, &b) in bytes.iter().enumerate() {
                end = end.max(last[(b - b'a') as usize]);
                if i == end {
                    sizes.push(end - start + 1);
                    start = i + 1;
                }
            }
            sizes
        }
    """,
    visible=[
        T("leetcode_three_pieces", 's = "ababcbacadefegdehijhklij"', 'partition_labels("ababcbacadefegdehijhklij")', "vec![9, 7, 8]"),
        T("leetcode_one_piece", 's = "eccbbbbdec"', 'partition_labels("eccbbbbdec")', "vec![10]"),
        T("empty", 's = ""', 'partition_labels("")', "Vec::<usize>::new()"),
        T("single", 's = "a"', 'partition_labels("a")', "vec![1]"),
        T("all_distinct", 's = "abc"', 'partition_labels("abc")', "vec![1, 1, 1]"),
        T("repeat_joins_everything", 's = "abca"', 'partition_labels("abca")', "vec![4]"),
    ],
    hidden=[
        T("one_letter_repeated", 's = "aaaa"', 'partition_labels("aaaa")', "vec![4]"),
        T("two_blocks", 's = "aabb"', 'partition_labels("aabb")', "vec![2, 2]"),
        T("nested", 's = "abba"', 'partition_labels("abba")', "vec![4]"),
        T("crossing", 's = "abab"', 'partition_labels("abab")', "vec![4]"),
        T("tail_piece", 's = "abac"', 'partition_labels("abac")', "vec![3, 1]"),
        T("head_piece", 's = "caedbdedda"', 'partition_labels("caedbdedda")', "vec![1, 9]"),
        T("alphabet", 's = "abcdefghijklmnopqrstuvwxyz"', 'partition_labels("abcdefghijklmnopqrstuvwxyz")', "vec![1; 26]"),
        T("mixed", 's = "qiejxqfnqceocmy"', 'partition_labels("qiejxqfnqceocmy")', "vec![13, 1, 1]"),
        T("first_and_last", 's = "zaz"', 'partition_labels("zaz")', "vec![3]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(817);
            for _ in 0..400 {
                let len = rng.below(13);
                let s = rng.string(len, "abcd");
                // A cut after p is allowed when no letter appears on both sides.
                let b = s.as_bytes();
                let mut want = Vec::new();
                let mut start = 0;
                for p in 1..=b.len() {
                    if p == b.len() || b[..p].iter().all(|c| !b[p..].contains(c)) {
                        want.push(p - start);
                        start = p;
                    }
                }
                check!(format!("s = {s:?}"), partition_labels(&s), want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut s = "abcdefghijklmnopqrstuvwxy".repeat(4_000);
            s.push_str(&"z".repeat(100_000));
            let sizes = partition_labels(&s);
            check!("'abc…y' × 4000, then 100000 'z's", sizes, vec![100_000, 100_000]);
        }
        """,
    ],
    wrong=dict(
        rescan_for_last="""
            pub fn partition_labels(s: &str) -> Vec<usize> {
                let b = s.as_bytes();
                let mut sizes = Vec::new();
                let (mut start, mut end) = (0, 0);
                for i in 0..b.len() {
                    let mut last = i;
                    for j in (i..b.len()).rev() {
                        if b[j] == b[i] {
                            last = j;
                            break;
                        }
                    }
                    end = end.max(last);
                    if i == end {
                        sizes.push(end - start + 1);
                        start = i + 1;
                    }
                }
                sizes
            }
        """,
        end_not_max="""
            pub fn partition_labels(s: &str) -> Vec<usize> {
                let bytes = s.as_bytes();
                let mut last = [0usize; 26];
                for (i, &b) in bytes.iter().enumerate() {
                    last[(b - b'a') as usize] = i;
                }
                let mut sizes = Vec::new();
                let mut start = 0;
                for (i, &b) in bytes.iter().enumerate() {
                    if last[(b - b'a') as usize] == i {
                        sizes.push(i - start + 1);
                        start = i + 1;
                    }
                }
                sizes
            }
        """,
    ),
    hints=[("approach", "A piece can't end before the last occurrence of any letter inside it. Record each letter's last index, then grow the current piece's end as you scan."),
           ("rust", "`let mut last = [0usize; 26];` indexed by `(b - b'a') as usize`, filled from `s.as_bytes()`."),
           ("edge case", "Cut exactly when `i` equals the furthest last-index seen so far, and push `end - start + 1`.")],
    notes=("A cut after position i is allowed exactly when every letter seen so far has its last occurrence at or before i. The running max of last occurrences finds every allowed cut, and taking all of them gives the most pieces.", "O(n)", "O(1) besides the output"),
    follow_up="If `s` could hold any Unicode text, what would replace the `[usize; 26]` table, and would you report sizes in bytes or in chars?",
    related=["D1", "S2"],
))

P.append(dict(
    slug="boats-to-save-people", title="Boats to save people", level="medium", stage="greedy-choices", tags=["greedy", "sorting", "two pointers"],
    companies=["Amazon", "Google"],
    teaches=["Two pointers from both ends of a sorted copy pair the heaviest with the lightest.", "Add two `u32`s as `u64` before comparing: the sum can overflow."],
    statement="""
        `people[i]` is a person's weight. A boat carries at most two people, and their weights must add up to
        at most `limit`. Nobody weighs more than `limit`. Return the fewest boats that carry everyone.
    """,
    examples=[("people = [1, 2], limit = 3", "1"), ("people = [3, 2, 2, 1], limit = 3", "3"), ("people = [3, 5, 3, 4], limit = 5", "4")],
    constraints=["0 ≤ people.len() ≤ 2·10⁵", "1 ≤ people[i] ≤ limit ≤ 2³² − 1"],
    starter="""
        pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
            let mut w = people.to_vec();
            w.sort_unstable();
            let (mut lo, mut hi) = (0usize, w.len());
            let mut boats = 0;
            while lo < hi {
                // The heaviest left takes a boat, with the lightest if they fit together.
                hi -= 1;
                if lo < hi && w[lo] as u64 + w[hi] as u64 <= limit as u64 {
                    lo += 1;
                }
                boats += 1;
            }
            boats
        }
    """,
    visible=[
        T("leetcode_one_boat", "people = [1, 2], limit = 3", "num_rescue_boats(&[1, 2], 3)", "1"),
        T("leetcode_three", "people = [3, 2, 2, 1], limit = 3", "num_rescue_boats(&[3, 2, 2, 1], 3)", "3"),
        T("leetcode_four", "people = [3, 5, 3, 4], limit = 5", "num_rescue_boats(&[3, 5, 3, 4], 5)", "4"),
        T("nobody", "people = [], limit = 5", "num_rescue_boats(&[], 5)", "0"),
        T("one_person", "people = [5], limit = 5", "num_rescue_boats(&[5], 5)", "1"),
        T("at_most_two_per_boat", "people = [1, 1, 1], limit = 3", "num_rescue_boats(&[1, 1, 1], 3)", "2"),
    ],
    hidden=[
        T("exact_pairs", "people = [2, 2, 2, 2], limit = 4", "num_rescue_boats(&[2, 2, 2, 2], 4)", "2"),
        T("heaviest_alone", "people = [5, 1, 4, 2], limit = 5", "num_rescue_boats(&[5, 1, 4, 2], 5)", "3"),
        T("lightest_pair_trap", "people = [1, 1, 2, 2], limit = 3", "num_rescue_boats(&[1, 1, 2, 2], 3)", "2"),
        T("sum_past_u32", "people = [4294967295, 4294967295], limit = 4294967295", "num_rescue_boats(&[u32::MAX, u32::MAX], u32::MAX)", "2"),
        T("max_limit_pair", "people = [4294967294, 1], limit = 4294967295", "num_rescue_boats(&[u32::MAX - 1, 1], u32::MAX)", "1"),
        T("many_light", "people = [1; 1000], limit = 2", "num_rescue_boats(&vec![1; 1000], 2)", "500"),
        T("all_heavy", "people = [3, 3, 3], limit = 5", "num_rescue_boats(&[3, 3, 3], 5)", "3"),
        T("mixed", "people = [2, 49, 50, 51, 98], limit = 100", "num_rescue_boats(&[2, 49, 50, 51, 98], 100)", "3"),
        T("odd_one_out", "people = [1, 2, 3, 4, 5], limit = 6", "num_rescue_boats(&[1, 2, 3, 4, 5], 6)", "3"),
        """
        #[test]
        fn random_vs_brute_force() {
            // The last person rides alone or with any partner that fits.
            fn fewest(left: &mut Vec<u32>, limit: u32) -> usize {
                let Some(first) = left.pop() else { return 0 };
                let mut out = 1 + fewest(left, limit);
                for j in 0..left.len() {
                    if first + left[j] <= limit {
                        let other = left.remove(j);
                        out = out.min(1 + fewest(left, limit));
                        left.insert(j, other);
                    }
                }
                left.push(first);
                out
            }
            let mut rng = anneal_prelude::Rng::new(818);
            for _ in 0..300 {
                let n = rng.below(8);
                let limit = rng.int(1, 8) as u32;
                let people: Vec<u32> = rng.vec(n, 1, limit as i64);
                let want = fewest(&mut people.clone(), limit);
                check!(format!("people = {people:?}, limit = {limit}"), num_rescue_boats(&people, limit), want);
            }
        }

        #[test]
        fn scale_200k() {
            let people: Vec<u32> = (1..=200_000).rev().collect();
            check!("people = 200000 down to 1, limit = 200001", num_rescue_boats(&people, 200_001), 100_000);
        }
        """,
    ],
    wrong=dict(
        search_best_partner="""
            pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
                let mut w = people.to_vec();
                w.sort_unstable();
                let mut used = vec![false; w.len()];
                let mut boats = 0;
                for i in (0..w.len()).rev() {
                    if used[i] {
                        continue;
                    }
                    used[i] = true;
                    boats += 1;
                    if let Some(j) = (0..i).rev().find(|&j| !used[j] && w[i] as u64 + w[j] as u64 <= limit as u64) {
                        used[j] = true;
                    }
                }
                boats
            }
        """,
        pair_lightest_two="""
            pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
                let mut w = people.to_vec();
                w.sort_unstable();
                let (mut i, mut boats) = (0, 0);
                while i < w.len() {
                    if i + 1 < w.len() && w[i] as u64 + w[i + 1] as u64 <= limit as u64 {
                        i += 2;
                    } else {
                        i += 1;
                    }
                    boats += 1;
                }
                boats
            }
        """,
        u32_sum="""
            pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
                let mut w = people.to_vec();
                w.sort_unstable();
                let (mut lo, mut hi) = (0usize, w.len());
                let mut boats = 0;
                while lo < hi {
                    hi -= 1;
                    if lo < hi && w[lo] + w[hi] <= limit {
                        lo += 1;
                    }
                    boats += 1;
                }
                boats
            }
        """,
    ),
    hints=[("approach", "The heaviest person must ride with someone or alone. If the lightest person fits with them, pair them; if not, nobody fits with them."),
           ("rust", "Sort a copy, then move `lo` and `hi` inward. Add as `u64`: two `u32` weights can overflow."),
           ("edge case", "Check `lo < hi` before pairing: when one person is left, they need their own boat.")],
    notes=("If the heaviest can't share with the lightest, they can't share with anyone, so they go alone. If they can, swapping any other partner for the lightest never hurts (exchange argument).", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="What if a boat could carry any number of people up to the limit? (That's bin packing, which is NP-hard.)",
    related=["D2", "S3"],
))

P.append(dict(
    slug="two-city-scheduling", title="Two city scheduling", level="medium", stage="greedy-choices", tags=["greedy", "sorting"],
    companies=["Amazon", "Bloomberg"],
    teaches=["Sort by the cost difference `a - b`: only the difference decides who goes where.", "Compute `a as i64 - b as i64` in the sort key; `u32` subtraction underflows."],
    statement="""
        `costs[i] = (a, b)`: flying person `i` to city A costs `a`, to city B costs `b`. There is an even number
        of people, and exactly half must go to each city. Return the lowest total cost.
    """,
    examples=[("costs = [(10, 20), (30, 200), (400, 50), (30, 20)]", "110")],
    constraints=["0 ≤ costs.len() ≤ 2·10⁵, even", "a and b are any u32"],
    starter="""
        pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
            let mut by_gain = costs.to_vec();
            // Most money saved by choosing A first.
            by_gain.sort_unstable_by_key(|&(a, b)| a as i64 - b as i64);
            let (to_a, to_b) = by_gain.split_at(costs.len() / 2);
            to_a.iter().map(|&(a, _)| a as u64).sum::<u64>() + to_b.iter().map(|&(_, b)| b as u64).sum::<u64>()
        }
    """,
    visible=[
        T("leetcode_four", "costs = [(10, 20), (30, 200), (400, 50), (30, 20)]", "two_city_sched_cost(&[(10, 20), (30, 200), (400, 50), (30, 20)])", "110"),
        T("leetcode_six", "costs = [(259, 770), (448, 54), (926, 667), (184, 139), (840, 118), (577, 469)]", "two_city_sched_cost(&[(259, 770), (448, 54), (926, 667), (184, 139), (840, 118), (577, 469)])", "1859"),
        T("leetcode_eight", "costs = [(515, 563), (451, 713), (537, 709), (343, 819), (855, 779), (457, 60), (650, 359), (631, 42)]", "two_city_sched_cost(&[(515, 563), (451, 713), (537, 709), (343, 819), (855, 779), (457, 60), (650, 359), (631, 42)])", "3086"),
        T("nobody", "costs = []", "two_city_sched_cost(&[])", "0"),
        T("half_must_go_to_each", "costs = [(1, 100), (1, 100)]", "two_city_sched_cost(&[(1, 100), (1, 100)])", "101"),
    ],
    hidden=[
        T("swap_pair", "costs = [(5, 1), (1, 5)]", "two_city_sched_cost(&[(5, 1), (1, 5)])", "2"),
        T("all_equal", "costs = [(3, 3); 4]", "two_city_sched_cost(&[(3, 3); 4])", "12"),
        T("a_cheaper_for_all", "costs = [(1, 10), (2, 20), (3, 30), (4, 40)]", "two_city_sched_cost(&[(1, 10), (2, 20), (3, 30), (4, 40)])", "37"),
        T("u32_extremes", "costs = [(4294967295, 0), (0, 4294967295)]", "two_city_sched_cost(&[(u32::MAX, 0), (0, u32::MAX)])", "0"),
        T("total_past_u32", "costs = [(4294967295, 4294967295); 4]", "two_city_sched_cost(&[(u32::MAX, u32::MAX); 4])", "17_179_869_180"),
        T("sort_by_a_trap", "costs = [(1, 2), (2, 100)]", "two_city_sched_cost(&[(1, 2), (2, 100)])", "4"),
        T("zeros", "costs = [(0, 0), (0, 0)]", "two_city_sched_cost(&[(0, 0), (0, 0)])", "0"),
        T("six_with_ties", "costs = [(10, 20), (30, 200), (400, 50), (30, 20), (1, 1), (1, 1)]", "two_city_sched_cost(&[(10, 20), (30, 200), (400, 50), (30, 20), (1, 1), (1, 1)])", "112"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(819);
            for _ in 0..300 {
                let n = 2 * rng.below(6);
                let costs: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(0, 20) as u32, rng.int(0, 20) as u32)).collect();
                // Every way to send exactly half to A.
                let mut want = u64::MAX;
                for mask in 0u32..1 << n {
                    if mask.count_ones() as usize == n / 2 {
                        let total: u64 = (0..n).map(|i| (if mask >> i & 1 == 1 { costs[i].0 } else { costs[i].1 }) as u64).sum();
                        want = want.min(total);
                    }
                }
                check!(format!("costs = {costs:?}"), two_city_sched_cost(&costs), want);
            }
        }

        #[test]
        fn scale_200k() {
            let costs: Vec<(u32, u32)> = (0..200_000u32).rev().map(|i| (i, 200_000 - i)).collect();
            check!("costs[i] = (i, 200000 - i) for i in 0..200000, reversed", two_city_sched_cost(&costs), 10_000_000_000);
        }
        """,
    ],
    wrong=dict(
        quadratic_dp="""
            pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
                let half = costs.len() / 2;
                // best[j]: lowest cost so far with j people sent to A.
                let mut best = vec![u64::MAX; half + 1];
                best[0] = 0;
                for (i, &(a, b)) in costs.iter().enumerate() {
                    for j in (0..=half.min(i + 1)).rev() {
                        let via_b = if best[j] == u64::MAX { u64::MAX } else { best[j] + b as u64 };
                        let via_a = if j > 0 && best[j - 1] != u64::MAX { best[j - 1] + a as u64 } else { u64::MAX };
                        best[j] = via_a.min(via_b);
                    }
                }
                best[half]
            }
        """,
        cheaper_city_each="""
            pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
                costs.iter().map(|&(a, b)| a.min(b) as u64).sum()
            }
        """,
        sort_by_a="""
            pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
                let mut sorted = costs.to_vec();
                sorted.sort_unstable();
                let (to_a, to_b) = sorted.split_at(costs.len() / 2);
                to_a.iter().map(|&(a, _)| a as u64).sum::<u64>() + to_b.iter().map(|&(_, b)| b as u64).sum::<u64>()
            }
        """,
    ),
    hints=[("approach", "Imagine everyone flies to B, then choose half of them to switch to A. Switching person i changes the total by `a - b`, so switch the half with the smallest `a - b`."),
           ("rust", "`sort_unstable_by_key(|&(a, b)| a as i64 - b as i64)`, then `split_at(n / 2)` and sum each side as `u64`."),
           ("edge case", "Sending each person to their cheaper city ignores the half-and-half rule.")],
    notes=("Only the difference a - b matters once half must go each way: sort by it, send the first half to A and the rest to B. Any other split swaps some pair and can only cost more.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="With three cities and a third of the people each, does sorting still work? (No: it needs DP or min-cost flow.)",
    related=["D12", "S3"],
))

P.append(dict(
    slug="minimum-add-to-make-parentheses-valid", title="Minimum add to make parentheses valid", level="medium", stage="greedy-choices", tags=["greedy", "strings", "stack"],
    companies=["Meta", "Amazon", "Google"],
    teaches=["With one bracket type, a counter replaces the stack.", "Count two different failures: closes with nothing to match, and opens left at the end."],
    statement="""
        `s` holds only `(` and `)`. One move inserts a single parenthesis anywhere in `s`. Return the fewest moves
        that make `s` balanced, meaning every `)` closes an earlier `(` and none stays open.
    """,
    examples=[("s = \"())\"", "1"), ("s = \"(((\"", "3")],
    constraints=["0 ≤ s.len() ≤ 2·10⁵", "s holds only '(' and ')'"],
    starter="""
        pub fn min_add_to_make_valid(s: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn min_add_to_make_valid(s: &str) -> usize {
            let (mut open, mut added) = (0usize, 0usize);
            for b in s.bytes() {
                if b == b'(' {
                    open += 1;
                } else if open > 0 {
                    open -= 1;
                } else {
                    // A ')' with nothing to close needs a new '(' before it.
                    added += 1;
                }
            }
            open + added
        }
    """,
    visible=[
        T("leetcode_one_close", 's = "())"', 'min_add_to_make_valid("())")', "1"),
        T("leetcode_three_open", 's = "((("', 'min_add_to_make_valid("(((")', "3"),
        T("empty", 's = ""', 'min_add_to_make_valid("")', "0"),
        T("balanced", 's = "()()"', 'min_add_to_make_valid("()()")', "0"),
        T("counts_match_order_wrong", 's = ")("', 'min_add_to_make_valid(")(")', "2"),
        T("both_kinds", 's = "()))(("', 'min_add_to_make_valid("()))((")', "4"),
    ],
    hidden=[
        T("single_open", 's = "("', 'min_add_to_make_valid("(")', "1"),
        T("single_close", 's = ")"', 'min_add_to_make_valid(")")', "1"),
        T("nested", 's = "((()))"', 'min_add_to_make_valid("((()))")', "0"),
        T("only_closes", 's = ")))"', 'min_add_to_make_valid(")))")', "3"),
        T("close_then_open", 's = "())("', 'min_add_to_make_valid("())(")', "2"),
        T("extra_in_the_middle", 's = "(()))("', 'min_add_to_make_valid("(()))(")', "2"),
        T("alternating", 's = "(()())"', 'min_add_to_make_valid("(()())")', "0"),
        T("wrapped_backwards", 's = ")()("', 'min_add_to_make_valid(")()(")', "2"),
        T("closes_then_opens", 's = ")))((("', 'min_add_to_make_valid(")))(((")', "6"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(820);
            for _ in 0..400 {
                let len = rng.below(15);
                let s = rng.string(len, "()");
                // Strip matched pairs until none are left; what's left needs a partner each.
                let mut rest = s.clone();
                while rest.contains("()") {
                    rest = rest.replace("()", "");
                }
                check!(format!("s = {s:?}"), min_add_to_make_valid(&s), rest.len());
            }
        }

        #[test]
        fn scale_200k() {
            let nested = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));
            let backwards = format!("{}{}", ")".repeat(100_000), "(".repeat(100_000));
            check!("'(' × 100000 then ')' × 100000; then the reverse", (min_add_to_make_valid(&nested), min_add_to_make_valid(&backwards)), (0, 200_000));
        }
        """,
    ],
    wrong=dict(
        strip_pairs="""
            pub fn min_add_to_make_valid(s: &str) -> usize {
                let mut rest: Vec<u8> = s.bytes().collect();
                while let Some(i) = rest.windows(2).position(|w| w[0] == b'(' && w[1] == b')') {
                    rest.drain(i..i + 2);
                }
                rest.len()
            }
        """,
        count_difference="""
            pub fn min_add_to_make_valid(s: &str) -> usize {
                let open = s.bytes().filter(|&b| b == b'(').count();
                let close = s.len() - open;
                open.abs_diff(close)
            }
        """,
        forgets_open_left="""
            pub fn min_add_to_make_valid(s: &str) -> usize {
                let (mut open, mut added) = (0usize, 0usize);
                for b in s.bytes() {
                    if b == b'(' {
                        open += 1;
                    } else if open > 0 {
                        open -= 1;
                    } else {
                        added += 1;
                    }
                }
                added
            }
        """,
    ),
    hints=[("approach", "Scan left to right counting unmatched `(`. A `)` with nothing to match needs an inserted `(`; each `(` still open at the end needs a `)`."),
           ("rust", "`s.bytes()` and two `usize` counters; with one bracket type you don't need a stack."),
           ("edge case", "`)(` needs 2 moves even though the counts match.")],
    notes=("Every `)` that arrives with no open `(` forces an insertion before it, and every `(` still open at the end forces one after it. Those two counts are also enough, so their sum is the answer.", "O(n)", "O(1)"),
    follow_up="How would you return one shortest balanced string, not just the count?",
    related=["D3"],
))

P.append(dict(
    slug="valid-parenthesis-string", title="Valid parenthesis string", level="medium", stage="greedy-choices", tags=["greedy", "strings"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Track a range of possible states (`lo..=hi` open counts) instead of branching on each `*`.", "`saturating_sub` keeps the low end of a `usize` range at 0."],
    statement="""
        `s` holds `(`, `)` and `*`. Each `*` can stand for `(`, for `)`, or for nothing. Return `true` if some
        choice makes `s` balanced: every `)` closes an earlier `(` and none stays open.
    """,
    examples=[("s = \"()\"", "true"), ("s = \"(*)\"", "true"), ("s = \"(*))\"", "true")],
    constraints=["0 ≤ s.len() ≤ 2·10⁵", "s holds only '(', ')' and '*'"],
    starter="""
        pub fn check_valid_string(s: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn check_valid_string(s: &str) -> bool {
            // lo..=hi: the open counts some choice of stars can reach.
            let (mut lo, mut hi) = (0usize, 0usize);
            for b in s.bytes() {
                match b {
                    b'(' => {
                        lo += 1;
                        hi += 1;
                    }
                    b')' => {
                        if hi == 0 {
                            return false;
                        }
                        lo = lo.saturating_sub(1);
                        hi -= 1;
                    }
                    _ => {
                        lo = lo.saturating_sub(1);
                        hi += 1;
                    }
                }
            }
            lo == 0
        }
    """,
    visible=[
        T("leetcode_pair", 's = "()"', 'check_valid_string("()")', "true"),
        T("leetcode_star_as_nothing", 's = "(*)"', 'check_valid_string("(*)")', "true"),
        T("leetcode_star_as_open", 's = "(*))"', 'check_valid_string("(*))")', "true"),
        T("empty", 's = ""', 'check_valid_string("")', "true"),
        T("star_cannot_close_a_later_open", 's = "*("', 'check_valid_string("*(")', "false"),
        T("not_enough_stars", 's = "((*"', 'check_valid_string("((*")', "false"),
    ],
    hidden=[
        T("lone_star", 's = "*"', 'check_valid_string("*")', "true"),
        T("lone_open", 's = "("', 'check_valid_string("(")', "false"),
        T("lone_close", 's = ")"', 'check_valid_string(")")', "false"),
        T("stars_only", 's = "**"', 'check_valid_string("**")', "true"),
        T("three_stars_close", 's = "(((***"', 'check_valid_string("(((***")', "true"),
        T("two_stars_short", 's = "(((**"', 'check_valid_string("(((**")', "false"),
        T("open_left_at_end", 's = "(*)("', 'check_valid_string("(*)(")', "false"),
        T("star_as_open_first", 's = "*)"', 'check_valid_string("*)")', "true"),
        T("leetcode_long_false", 's = "((*)(*))((*"', 'check_valid_string("((*)(*))((*")', "false"),
        T("leetcode_long_mixed", 's = "*()(())*()(()()((()(()()*)(*(())((((((((()*)(()(*)"', 'check_valid_string("*()(())*()(()()((()(()()*)(*(())((((((((()*)(()(*)")', "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every reading of every star.
            fn ok(s: &[u8], open: usize) -> bool {
                let Some((&b, rest)) = s.split_first() else { return open == 0 };
                match b {
                    b'(' => ok(rest, open + 1),
                    b')' => open > 0 && ok(rest, open - 1),
                    _ => ok(rest, open + 1) || ok(rest, open) || (open > 0 && ok(rest, open - 1)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(821);
            for _ in 0..400 {
                let len = rng.below(9);
                let s = rng.string(len, "(*)");
                check!(format!("s = {s:?}"), check_valid_string(&s), ok(s.as_bytes(), 0));
            }
        }

        #[test]
        fn scale_200k() {
            let fine = format!("{}{}", "(".repeat(100_000), "*".repeat(100_000));
            let extra_open = format!("({fine}");
            let extra_close = format!("{}{}", "*".repeat(100_000), ")".repeat(100_001));
            check!(
                "'(' × 100000 then '*' × 100000; with one more '(' in front; '*' × 100000 then ')' × 100001",
                (check_valid_string(&fine), check_valid_string(&extra_open), check_valid_string(&extra_close)),
                (true, false, false)
            );
        }
        """,
    ],
    wrong=dict(
        set_of_counts="""
            pub fn check_valid_string(s: &str) -> bool {
                // possible[k]: some choice leaves k open after this prefix.
                let mut possible = vec![true];
                for b in s.bytes() {
                    let mut next = vec![false; possible.len() + 1];
                    for (k, &ok) in possible.iter().enumerate() {
                        if !ok {
                            continue;
                        }
                        if b != b')' {
                            next[k + 1] = true;
                        }
                        if b != b'(' && k > 0 {
                            next[k - 1] = true;
                        }
                        if b == b'*' {
                            next[k] = true;
                        }
                    }
                    possible = next;
                }
                possible[0]
            }
        """,
        low_not_clamped="""
            pub fn check_valid_string(s: &str) -> bool {
                let (mut lo, mut hi) = (0i64, 0i64);
                for b in s.bytes() {
                    match b {
                        b'(' => {
                            lo += 1;
                            hi += 1;
                        }
                        b')' => {
                            lo -= 1;
                            hi -= 1;
                        }
                        _ => {
                            lo -= 1;
                            hi += 1;
                        }
                    }
                    if hi < 0 {
                        return false;
                    }
                }
                lo <= 0
            }
        """,
        stars_only_open="""
            pub fn check_valid_string(s: &str) -> bool {
                let mut open = 0i64;
                for b in s.bytes() {
                    if b == b')' {
                        open -= 1;
                    } else {
                        open += 1;
                    }
                    if open < 0 {
                        return false;
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "Don't branch on each `*`. Track the lowest and highest number of open `(` any choice could give: `(` raises both, `)` lowers both, `*` lowers the low end and raises the high end."),
           ("rust", "Two `usize` counters; `lo.saturating_sub(1)` keeps the low end at 0, since no valid choice goes negative."),
           ("edge case", "Fail as soon as `hi` would drop below 0; at the end the answer is `lo == 0`. Order matters: `*(` is not balanced.")],
    notes=("Every open count between lo and hi is reachable by some choice of stars, and clamping lo at 0 drops choices that would close too much. If even the most-open choice goes negative, nothing works; at the end, some choice lands on 0 exactly when lo is 0.", "O(n)", "O(1)"),
    follow_up="How would you produce one concrete replacement for the stars that balances `s`?",
    related=["D3", "D12"],
))

P.append(dict(
    slug="queue-reconstruction-by-height", title="Queue reconstruction by height", level="medium", stage="greedy-choices", tags=["greedy", "sorting"],
    companies=["Amazon", "Google"],
    teaches=["`sort_unstable_by_key(|&(h, k)| (Reverse(h), k))` sorts one field descending and another ascending.", "`Vec::insert(k, x)` shifts the tail: O(n) per insert, fine here and worth saying out loud."],
    statement="""
        Each person is `(h, k)`: height `h`, and exactly `k` people in front of them who are at least as tall.
        `people` lists everyone in scrambled order. Rebuild the queue and return it front to back. The input
        always describes a real queue.
    """,
    examples=[("people = [(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]", "[(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]")],
    constraints=["0 ≤ people.len() ≤ 10⁴", "h is any u32", "the input describes a real queue"],
    starter="""
        pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;

        pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
            let mut sorted = people.to_vec();
            // Tallest first; among equal heights, the one with fewer people in front first.
            sorted.sort_unstable_by_key(|&(h, k)| (Reverse(h), k));
            let mut queue = Vec::with_capacity(sorted.len());
            for person in sorted {
                // Everyone placed so far is at least as tall, so index k is exactly right.
                queue.insert(person.1, person);
            }
            queue
        }
    """,
    visible=[
        T("leetcode_six", "people = [(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]", "reconstruct_queue(&[(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)])", "vec![(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]"),
        T("leetcode_six_more", "people = [(6, 0), (5, 0), (4, 0), (3, 2), (2, 2), (1, 4)]", "reconstruct_queue(&[(6, 0), (5, 0), (4, 0), (3, 2), (2, 2), (1, 4)])", "vec![(4, 0), (5, 0), (2, 2), (3, 2), (1, 4), (6, 0)]"),
        T("nobody", "people = []", "reconstruct_queue(&[])", "Vec::<(u32, usize)>::new()"),
        T("one_person", "people = [(5, 0)]", "reconstruct_queue(&[(5, 0)])", "vec![(5, 0)]"),
        T("equal_height_counts", "people = [(5, 1), (5, 0)]", "reconstruct_queue(&[(5, 1), (5, 0)])", "vec![(5, 0), (5, 1)]"),
        T("all_zero_means_rising", "people = [(3, 0), (1, 0), (2, 0)]", "reconstruct_queue(&[(3, 0), (1, 0), (2, 0)])", "vec![(1, 0), (2, 0), (3, 0)]"),
    ],
    hidden=[
        T("falling", "people = [(1, 2), (2, 1), (3, 0)]", "reconstruct_queue(&[(1, 2), (2, 1), (3, 0)])", "vec![(3, 0), (2, 1), (1, 2)]"),
        T("all_same_height", "people = [(4, 2), (4, 1), (4, 0)]", "reconstruct_queue(&[(4, 2), (4, 1), (4, 0)])", "vec![(4, 0), (4, 1), (4, 2)]"),
        T("short_one_first", "people = [(9, 0), (1, 0)]", "reconstruct_queue(&[(9, 0), (1, 0)])", "vec![(1, 0), (9, 0)]"),
        T("u32_heights", "people = [(0, 2), (4294967295, 1), (4294967295, 0)]", "reconstruct_queue(&[(0, 2), (u32::MAX, 1), (u32::MAX, 0)])", "vec![(u32::MAX, 0), (u32::MAX, 1), (0, 2)]"),
        T("zero_height", "people = [(0, 0), (0, 1)]", "reconstruct_queue(&[(0, 0), (0, 1)])", "vec![(0, 0), (0, 1)]"),
        T("six_mixed", "people = [(4, 2), (1, 4), (5, 1), (3, 1), (5, 0), (2, 0)]", "reconstruct_queue(&[(4, 2), (1, 4), (5, 1), (3, 1), (5, 0), (2, 0)])", "vec![(2, 0), (5, 0), (3, 1), (5, 1), (1, 4), (4, 2)]"),
        T("seven_mixed", "people = [(1, 6), (7, 0), (2, 4), (3, 2), (6, 1), (2, 1), (6, 0)]", "reconstruct_queue(&[(1, 6), (7, 0), (2, 4), (3, 2), (6, 1), (2, 1), (6, 0)])", "vec![(6, 0), (2, 1), (6, 1), (3, 2), (2, 4), (7, 0), (1, 6)]"),
        T("equal_heights_then_short", "people = [(2, 1), (2, 0), (1, 2)]", "reconstruct_queue(&[(2, 1), (2, 0), (1, 2)])", "vec![(2, 0), (2, 1), (1, 2)]"),
        """
        /// The (h, k) pairs of a queue given front to back.
        fn describe(heights: &[u32]) -> Vec<(u32, usize)> {
            (0..heights.len()).map(|i| (heights[i], heights[..i].iter().filter(|&&h| h >= heights[i]).count())).collect()
        }

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(822);
            for _ in 0..400 {
                let n = rng.below(9);
                let heights: Vec<u32> = rng.vec(n, 1, 5);
                let queue = describe(&heights);
                let mut people = queue.clone();
                rng.shuffle(&mut people);
                check!(format!("people = {people:?}"), reconstruct_queue(&people), queue);
            }
        }

        #[test]
        fn scale_10k() {
            let heights: Vec<u32> = (0..10_000u32).map(|i| i * 7919 % 10_007 % 500).collect();
            let queue = describe(&heights);
            let people: Vec<(u32, usize)> = queue.iter().rev().copied().collect();
            check!("10000 people, heights (7919 i mod 10007) mod 500, given back to front", reconstruct_queue(&people) == queue, true);
        }
        """,
    ],
    wrong=dict(
        pick_front_each_time="""
            pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
                // Front to back: the next person is the shortest whose k matches who's already placed.
                let mut left = people.to_vec();
                let mut queue: Vec<(u32, usize)> = Vec::new();
                while !left.is_empty() {
                    let mut pick: Option<usize> = None;
                    for (i, &(h, k)) in left.iter().enumerate() {
                        let taller = queue.iter().filter(|q| q.0 >= h).count();
                        if taller == k && pick.map_or(true, |j| h < left[j].0) {
                            pick = Some(i);
                        }
                    }
                    queue.push(left.remove(pick.unwrap()));
                }
                queue
            }
        """,
        ties_larger_k_first="""
            use std::cmp::Reverse;

            pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
                let mut sorted = people.to_vec();
                sorted.sort_unstable_by_key(|&(h, k)| (Reverse(h), Reverse(k)));
                let mut queue = Vec::new();
                for person in sorted {
                    queue.insert(person.1.min(queue.len()), person);
                }
                queue
            }
        """,
        shortest_first="""
            pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
                let mut sorted = people.to_vec();
                sorted.sort_unstable();
                let mut queue = Vec::new();
                for person in sorted {
                    queue.insert(person.1.min(queue.len()), person);
                }
                queue
            }
        """,
    ),
    hints=[("approach", "Place the tallest people first. Shorter people are invisible to them, so a tall person's position depends only on people at least as tall."),
           ("rust", "`sort_unstable_by_key(|&(h, k)| (Reverse(h), k))`, then `queue.insert(k, person)` for each person in that order."),
           ("edge case", "Equal heights count as 'at least as tall', so among equal heights insert the smaller `k` first.")],
    notes=("After sorting tallest first, everyone already placed is at least as tall as the current person, so inserting at index k puts exactly k of them in front. Later insertions are shorter and don't change anyone's count.", "O(n²) for the inserts (O(n log n) for the sort)", "O(n)"),
    follow_up="How would a Fenwick tree over empty slots, filled shortest first, make this O(n log n)?",
    related=["S3", "D13"],
))

# ---------------------------------------------------------------- hard greedy

P.append(dict(
    slug="hand-of-straights", title="Hand of straights", level="medium", stage="hard-greedy", tags=["greedy", "BTreeMap", "sorting"],
    companies=["Amazon", "Google"],
    teaches=["A `BTreeMap<_, usize>` is a sorted multiset: `first_key_value()` gives the smallest card left.", "`card + 1` can overflow at `i32::MAX`; widen the key to `i64`."],
    statement="""
        Split the cards in `hand` into groups of exactly `group_size` cards, where each group is a run of
        consecutive values such as 3, 4, 5. Every card must be used. Return `true` if that's possible.
        Card values are any `i32`.
    """,
    examples=[("hand = [1, 2, 3, 6, 2, 3, 4, 7, 8], group_size = 3", "true"), ("hand = [1, 2, 3, 4, 5], group_size = 4", "false")],
    constraints=["0 ≤ hand.len() ≤ 2·10⁵", "hand[i] is any i32", "1 ≤ group_size ≤ 2·10⁵"],
    starter="""
        pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
            todo!()
        }
    """,
    solution="""
        use std::collections::BTreeMap;

        pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
            if hand.len() % group_size != 0 {
                return false;
            }
            let mut counts: BTreeMap<i64, usize> = BTreeMap::new();
            for &card in hand {
                *counts.entry(card as i64).or_insert(0) += 1;
            }
            // The smallest card left must start a run; all `n` copies of it start `n` runs.
            while let Some((&first, &n)) = counts.first_key_value() {
                for card in first..first + group_size as i64 {
                    match counts.get_mut(&card) {
                        Some(c) if *c >= n => {
                            *c -= n;
                            if *c == 0 {
                                counts.remove(&card);
                            }
                        }
                        _ => return false,
                    }
                }
            }
            true
        }
    """,
    visible=[
        T("leetcode_three_runs", "hand = [1, 2, 3, 6, 2, 3, 4, 7, 8], group_size = 3", "is_n_straight_hand(&[1, 2, 3, 6, 2, 3, 4, 7, 8], 3)", "true"),
        T("leetcode_wrong_size", "hand = [1, 2, 3, 4, 5], group_size = 4", "is_n_straight_hand(&[1, 2, 3, 4, 5], 4)", "false"),
        T("empty_hand", "hand = [], group_size = 3", "is_n_straight_hand(&[], 3)", "true"),
        T("groups_of_one", "hand = [5, 5, 1], group_size = 1", "is_n_straight_hand(&[5, 5, 1], 1)", "true"),
        T("duplicates_make_two_runs", "hand = [1, 1, 2, 2, 3, 3], group_size = 3", "is_n_straight_hand(&[1, 1, 2, 2, 3, 3], 3)", "true"),
        T("gap_breaks_the_run", "hand = [1, 2, 4], group_size = 3", "is_n_straight_hand(&[1, 2, 4], 3)", "false"),
    ],
    hidden=[
        T("not_divisible", "hand = [1, 2, 3, 4], group_size = 3", "is_n_straight_hand(&[1, 2, 3, 4], 3)", "false"),
        T("top_of_i32", "hand = [2147483646, 2147483647], group_size = 2", "is_n_straight_hand(&[i32::MAX - 1, i32::MAX], 2)", "true"),
        T("run_past_i32_max", "hand = [2147483647, 2147483647], group_size = 2", "is_n_straight_hand(&[i32::MAX, i32::MAX], 2)", "false"),
        T("bottom_of_i32", "hand = [-2147483648, -2147483647], group_size = 2", "is_n_straight_hand(&[i32::MIN, i32::MIN + 1], 2)", "true"),
        T("negatives", "hand = [0, -1, -3, -2], group_size = 2", "is_n_straight_hand(&[0, -1, -3, -2], 2)", "true"),
        T("duplicate_start_short", "hand = [1, 1, 2, 2, 3, 4], group_size = 3", "is_n_straight_hand(&[1, 1, 2, 2, 3, 4], 3)", "false"),
        T("spaced_out", "hand = [8, 10, 12], group_size = 3", "is_n_straight_hand(&[8, 10, 12], 3)", "false"),
        T("group_bigger_than_hand", "hand = [1, 2], group_size = 3", "is_n_straight_hand(&[1, 2], 3)", "false"),
        T("one_group_of_all", "hand = [3, 1, 2], group_size = 3", "is_n_straight_hand(&[3, 1, 2], 3)", "true"),
        T("three_runs_of_four", "hand = [5, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], group_size = 4", "is_n_straight_hand(&[5, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], 4)", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(823);
            for _ in 0..400 {
                let size = 1 + rng.below(4);
                let groups = rng.below(4);
                let mut hand: Vec<i32> = Vec::new();
                for _ in 0..groups {
                    let start = rng.int(-3, 5) as i32;
                    hand.extend(start..start + size as i32);
                }
                if rng.bool() && !hand.is_empty() {
                    let i = rng.below(hand.len());
                    hand[i] = rng.int(-3, 8) as i32;
                }
                rng.shuffle(&mut hand);
                // Remove the smallest card's run one card at a time from a sorted Vec.
                let mut left = hand.clone();
                left.sort_unstable();
                let mut want = left.len() % size == 0;
                while want && !left.is_empty() {
                    let first = left[0];
                    for card in first..first + size as i32 {
                        match left.iter().position(|&c| c == card) {
                            Some(i) => {
                                left.remove(i);
                            }
                            None => {
                                want = false;
                                break;
                            }
                        }
                    }
                }
                check!(format!("hand = {hand:?}, group_size = {size}"), is_n_straight_hand(&hand, size), want);
            }
        }

        #[test]
        fn scale_200k() {
            let distinct: Vec<i32> = (0..200_000).rev().collect();
            let mut broken = distinct.clone();
            broken[0] = 0;
            let stacked: Vec<i32> = (0..200_000).map(|i| i % 1000).collect();
            check!(
                "199999 down to 0 in runs of 1000; the same with 199999 swapped for 0; 0..1000 two hundred times in runs of 1000",
                (is_n_straight_hand(&distinct, 1000), is_n_straight_hand(&broken, 1000), is_n_straight_hand(&stacked, 1000)),
                (true, false, true)
            );
        }
        """,
    ],
    wrong=dict(
        sorted_vec_search="""
            pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
                let mut cards = hand.to_vec();
                cards.sort_unstable();
                while let Some(&first) = cards.first() {
                    for k in 0..group_size as i64 {
                        match cards.iter().position(|&c| c as i64 == first as i64 + k) {
                            Some(i) => {
                                cards.remove(i);
                            }
                            None => return false,
                        }
                    }
                }
                true
            }
        """,
        i32_keys="""
            use std::collections::BTreeMap;

            pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
                if hand.len() % group_size != 0 {
                    return false;
                }
                let mut counts: BTreeMap<i32, usize> = BTreeMap::new();
                for &card in hand {
                    *counts.entry(card).or_insert(0) += 1;
                }
                while let Some((&first, &n)) = counts.first_key_value() {
                    for card in first..first + group_size as i32 {
                        match counts.get_mut(&card) {
                            Some(c) if *c >= n => {
                                *c -= n;
                                if *c == 0 {
                                    counts.remove(&card);
                                }
                            }
                            _ => return false,
                        }
                    }
                }
                true
            }
        """,
        ignores_copies="""
            use std::collections::BTreeSet;

            pub fn is_n_straight_hand(hand: &[i32], group_size: usize) -> bool {
                if hand.len() % group_size != 0 {
                    return false;
                }
                let cards: BTreeSet<i64> = hand.iter().map(|&c| c as i64).collect();
                cards.iter().all(|&c| cards.contains(&(c + 1)) || cards.contains(&(c - 1)) || group_size == 1)
            }
        """,
    ),
    hints=[("approach", "The smallest card left can only be the start of a run, so that run is forced: it needs the next `group_size - 1` values too. Take it and repeat."),
           ("rust", "Count cards in a `BTreeMap<i64, usize>`. If the smallest key has count `n`, subtract `n` from each of the next `group_size` keys at once, removing keys that reach 0."),
           ("edge case", "A run starting near `i32::MAX` needs values past it; `i32` arithmetic overflows there, `i64` keys don't.")],
    notes=("The smallest remaining card can't be in the middle of a run, so the run it starts is forced. With counts in a BTreeMap, each successful lookup removes at least one card, so the work is O(n log n).", "O(n log n)", "O(n)"),
    follow_up="Can you avoid the sorted map, starting runs only from values whose predecessor is missing from a `HashMap`?",
    related=["S4", "D7"],
))

P.append(dict(
    slug="remove-k-digits", title="Remove K digits", level="medium", stage="hard-greedy", tags=["greedy", "monotonic stack", "strings"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["A monotonic stack drops each digit the moment a smaller one follows it.", "`Vec<u8>` as the stack, `truncate` for leftover removals, and a byte slice back to `&str`."],
    statement="""
        `num` is a non-negative integer written in decimal, with no leading zeros unless it is `"0"`. Remove
        exactly `k` digits so the number left is as small as possible, and return it without leading zeros.
        If no digits are left, return `"0"`.
    """,
    examples=[("num = \"1432219\", k = 3", "\"1219\""), ("num = \"10200\", k = 1", "\"200\""), ("num = \"10\", k = 2", "\"0\"")],
    constraints=["1 ≤ num.len() ≤ 2·10⁵", "0 ≤ k ≤ num.len()", "num holds only ASCII digits"],
    starter="""
        pub fn remove_kdigits(num: &str, k: usize) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn remove_kdigits(num: &str, k: usize) -> String {
            let mut k = k;
            let mut stack: Vec<u8> = Vec::with_capacity(num.len());
            for b in num.bytes() {
                // A bigger digit before a smaller one should go.
                while k > 0 && stack.last().is_some_and(|&top| top > b) {
                    stack.pop();
                    k -= 1;
                }
                stack.push(b);
            }
            // What's left is non-decreasing: drop any remaining removals from the end.
            stack.truncate(stack.len() - k);
            let start = stack.iter().position(|&b| b != b'0').unwrap_or(stack.len());
            match std::str::from_utf8(&stack[start..]).unwrap() {
                "" => "0".to_string(),
                digits => digits.to_string(),
            }
        }
    """,
    visible=[
        T("leetcode_1219", 'num = "1432219", k = 3', 'remove_kdigits("1432219", 3)', '"1219"'),
        T("leetcode_leading_zero", 'num = "10200", k = 1', 'remove_kdigits("10200", 1)', '"200"'),
        T("leetcode_nothing_left", 'num = "10", k = 2', 'remove_kdigits("10", 2)', '"0"'),
        T("remove_none", 'num = "123", k = 0', 'remove_kdigits("123", 0)', '"123"'),
        T("rising_drops_the_end", 'num = "12345", k = 2', 'remove_kdigits("12345", 2)', '"123"'),
        T("single_digit_removed", 'num = "9", k = 1', 'remove_kdigits("9", 1)', '"0"'),
    ],
    hidden=[
        T("repeat_then_rise", 'num = "112", k = 1', 'remove_kdigits("112", 1)', '"11"'),
        T("falling", 'num = "54321", k = 2', 'remove_kdigits("54321", 2)', '"321"'),
        T("only_zeros_left", 'num = "100", k = 1', 'remove_kdigits("100", 1)', '"0"'),
        T("all_but_one", 'num = "1234567890", k = 9', 'remove_kdigits("1234567890", 9)', '"0"'),
        T("all_same", 'num = "1111", k = 2', 'remove_kdigits("1111", 2)', '"11"'),
        T("zeros_inside", 'num = "10001", k = 1', 'remove_kdigits("10001", 1)', '"1"'),
        T("two_peaks", 'num = "43214321", k = 4', 'remove_kdigits("43214321", 4)', '"1321"'),
        T("zero_alone", 'num = "0", k = 0', 'remove_kdigits("0", 0)', '"0"'),
        T("equal_digits_stay", 'num = "5337", k = 2', 'remove_kdigits("5337", 2)', '"33"'),
        T("peak_later", 'num = "1173", k = 2', 'remove_kdigits("1173", 2)', '"11"'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(824);
            for _ in 0..400 {
                let len = 1 + rng.below(9);
                let mut num = rng.string(len, "0012349");
                if len > 1 && num.starts_with('0') {
                    num.replace_range(0..1, "1");
                }
                let k = rng.below(len + 1);
                // Try every set of kept positions and keep the smallest value.
                let b = num.as_bytes();
                let mut want: Option<String> = None;
                for mask in 0u32..1 << len {
                    if mask.count_ones() as usize != len - k {
                        continue;
                    }
                    let kept: String = (0..len).filter(|&i| mask >> i & 1 == 1).map(|i| b[i] as char).collect();
                    let trimmed = kept.trim_start_matches('0');
                    let value = if trimmed.is_empty() { "0".to_string() } else { trimmed.to_string() };
                    if want.as_ref().map_or(true, |w| (value.len(), &value) < (w.len(), w)) {
                        want = Some(value);
                    }
                }
                check!(format!("num = {num:?}, k = {k}"), remove_kdigits(&num, k), want.unwrap());
            }
        }

        #[test]
        fn scale_200k() {
            let rising = format!("{}{}", "1".repeat(100_000), "9".repeat(100_000));
            let zeros = format!("1{}", "0".repeat(199_999));
            check!(
                "'1' × 100000 then '9' × 100000, k = 100000; '1' then '0' × 199999, k = 1",
                (remove_kdigits(&rising, 100_000) == "1".repeat(100_000), remove_kdigits(&zeros, 1)),
                (true, "0".to_string())
            );
        }
        """,
    ],
    wrong=dict(
        remove_first_peak_k_times="""
            pub fn remove_kdigits(num: &str, k: usize) -> String {
                let mut digits: Vec<u8> = num.bytes().collect();
                for _ in 0..k {
                    let i = (0..digits.len() - 1).find(|&i| digits[i] > digits[i + 1]).unwrap_or(digits.len() - 1);
                    digits.remove(i);
                }
                let s: String = digits.iter().map(|&b| b as char).collect();
                let s = s.trim_start_matches('0');
                if s.is_empty() { "0".to_string() } else { s.to_string() }
            }
        """,
        keeps_leading_zeros="""
            pub fn remove_kdigits(num: &str, k: usize) -> String {
                let mut k = k;
                let mut stack: Vec<u8> = Vec::new();
                for b in num.bytes() {
                    while k > 0 && stack.last().is_some_and(|&top| top > b) {
                        stack.pop();
                        k -= 1;
                    }
                    stack.push(b);
                }
                stack.truncate(stack.len() - k);
                if stack.is_empty() { "0".to_string() } else { String::from_utf8(stack).unwrap() }
            }
        """,
        forgets_leftover_k="""
            pub fn remove_kdigits(num: &str, k: usize) -> String {
                let mut k = k;
                let mut stack: Vec<u8> = Vec::new();
                for b in num.bytes() {
                    while k > 0 && stack.last().is_some_and(|&top| top > b) {
                        stack.pop();
                        k -= 1;
                    }
                    stack.push(b);
                }
                let start = stack.iter().position(|&b| b != b'0').unwrap_or(stack.len());
                match std::str::from_utf8(&stack[start..]).unwrap() {
                    "" => "0".to_string(),
                    digits => digits.to_string(),
                }
            }
        """,
    ),
    hints=[("approach", "The leftmost digits matter most. Scanning left to right, a digit followed by a smaller one should be removed. Keep a stack and pop while the top is bigger than the incoming digit and removals remain."),
           ("rust", "A `Vec<u8>` stack with `stack.last().is_some_and(|&top| top > b)`; `truncate(len - k)` for leftovers; start the answer at the first byte that isn't `b'0'`."),
           ("edge case", "Strip leading zeros, and return `\"0\"` when nothing is left. If removals remain after the scan, the stack is non-decreasing, so take them from the end.")],
    notes=("To make the number smallest, make the first digit as small as possible, then the second, and so on. The stack removes each digit the first time a smaller digit follows it, so what stays is the smallest prefix available; leftover removals come off the non-decreasing tail. Each digit is pushed and popped at most once.", "O(n)", "O(n)"),
    follow_up="How would you keep exactly m digits to make the largest number instead, or merge the best picks from two numbers (Create maximum number)?",
    related=["D3", "S2"],
))

P.append(dict(
    slug="candy", title="Candy", level="hard", stage="hard-greedy", tags=["greedy", "arrays"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["Two one-sided passes, combined with `max`, satisfy a rule that looks both ways.", "`(0..n.saturating_sub(1)).rev()` walks backwards without underflow on an empty slice."],
    statement="""
        Children stand in a row and `ratings[i]` is child `i`'s rating. Give every child at least one candy, and
        give each child more candy than any neighbour with a lower rating. Neighbours with equal ratings have
        no rule between them. Return the fewest candies in total.
    """,
    examples=[("ratings = [1, 0, 2]", "5"), ("ratings = [1, 2, 2]", "4")],
    constraints=["0 ≤ ratings.len() ≤ 2·10⁵", "ratings[i] is any i32"],
    starter="""
        pub fn candy(ratings: &[i32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn candy(ratings: &[i32]) -> u64 {
            let n = ratings.len();
            let mut give = vec![1u64; n];
            // More than a lower-rated left neighbour...
            for i in 1..n {
                if ratings[i] > ratings[i - 1] {
                    give[i] = give[i - 1] + 1;
                }
            }
            // ...and more than a lower-rated right neighbour, keeping the first rule.
            for i in (0..n.saturating_sub(1)).rev() {
                if ratings[i] > ratings[i + 1] {
                    give[i] = give[i].max(give[i + 1] + 1);
                }
            }
            give.iter().sum()
        }
    """,
    visible=[
        T("leetcode_valley", "ratings = [1, 0, 2]", "candy(&[1, 0, 2])", "5"),
        T("leetcode_equal_neighbours", "ratings = [1, 2, 2]", "candy(&[1, 2, 2])", "4"),
        T("nobody", "ratings = []", "candy(&[])", "0"),
        T("one_child", "ratings = [7]", "candy(&[7])", "1"),
        T("falling", "ratings = [3, 2, 1]", "candy(&[3, 2, 1])", "6"),
        T("all_equal", "ratings = [2, 2, 2]", "candy(&[2, 2, 2])", "3"),
    ],
    hidden=[
        T("peak_then_plateau", "ratings = [1, 3, 2, 2, 1]", "candy(&[1, 3, 2, 2, 1])", "7"),
        T("mountain", "ratings = [1, 2, 3, 2, 1]", "candy(&[1, 2, 3, 2, 1])", "9"),
        T("long_rise_short_fall", "ratings = [1, 3, 4, 5, 2]", "candy(&[1, 3, 4, 5, 2])", "11"),
        T("fall_rise_fall", "ratings = [5, 4, 3, 5, 6, 2]", "candy(&[5, 4, 3, 5, 6, 2])", "12"),
        T("short_rise_long_fall", "ratings = [1, 6, 10, 8, 7, 3, 2]", "candy(&[1, 6, 10, 8, 7, 3, 2])", "18"),
        T("plateau_top", "ratings = [1, 2, 87, 87, 87, 2, 1]", "candy(&[1, 2, 87, 87, 87, 2, 1])", "13"),
        T("negatives", "ratings = [-5, -10, -10, 3]", "candy(&[-5, -10, -10, 3])", "6"),
        T("i32_extremes", "ratings = [-2147483648, 2147483647, -2147483648]", "candy(&[i32::MIN, i32::MAX, i32::MIN])", "4"),
        T("two_rising", "ratings = [1, 2]", "candy(&[1, 2])", "3"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(825);
            for _ in 0..400 {
                let n = rng.below(10);
                let ratings: Vec<i32> = rng.vec(n, -2, 3);
                // Raise any child that breaks a rule until nobody does.
                let mut give = vec![1u64; n];
                loop {
                    let mut changed = false;
                    for i in 0..n {
                        for j in [i.wrapping_sub(1), i + 1] {
                            if j < n && ratings[i] > ratings[j] && give[i] <= give[j] {
                                give[i] = give[j] + 1;
                                changed = true;
                            }
                        }
                    }
                    if !changed {
                        break;
                    }
                }
                check!(format!("ratings = {ratings:?}"), candy(&ratings), give.iter().sum::<u64>());
            }
        }

        #[test]
        fn scale_200k() {
            let falling: Vec<i32> = (0..200_000).rev().collect();
            let rising: Vec<i32> = (0..200_000).collect();
            check!("199999 down to 0; 0 up to 199999", (candy(&falling), candy(&rising)), (20_000_100_000, 20_000_100_000));
        }
        """,
    ],
    wrong=dict(
        relax_until_stable="""
            pub fn candy(ratings: &[i32]) -> u64 {
                let n = ratings.len();
                let mut give = vec![1u64; n];
                let mut changed = true;
                while changed {
                    changed = false;
                    for i in 0..n {
                        if i > 0 && ratings[i] > ratings[i - 1] && give[i] <= give[i - 1] {
                            give[i] = give[i - 1] + 1;
                            changed = true;
                        }
                        if i + 1 < n && ratings[i] > ratings[i + 1] && give[i] <= give[i + 1] {
                            give[i] = give[i + 1] + 1;
                            changed = true;
                        }
                    }
                }
                give.iter().sum()
            }
        """,
        left_pass_only="""
            pub fn candy(ratings: &[i32]) -> u64 {
                let n = ratings.len();
                let mut give = vec![1u64; n];
                for i in 1..n {
                    if ratings[i] > ratings[i - 1] {
                        give[i] = give[i - 1] + 1;
                    }
                }
                give.iter().sum()
            }
        """,
        u32_total="""
            pub fn candy(ratings: &[i32]) -> u64 {
                let n = ratings.len();
                let mut give = vec![1u32; n];
                for i in 1..n {
                    if ratings[i] > ratings[i - 1] {
                        give[i] = give[i - 1] + 1;
                    }
                }
                for i in (0..n.saturating_sub(1)).rev() {
                    if ratings[i] > ratings[i + 1] {
                        give[i] = give[i].max(give[i + 1] + 1);
                    }
                }
                give.iter().sum::<u32>() as u64
            }
        """,
    ),
    hints=[("approach", "Split the rule in two. A left-to-right pass makes each child beat a lower-rated left neighbour; a right-to-left pass does the same for the right neighbour."),
           ("rust", "`vec![1u64; n]`; in the second pass use `give[i].max(give[i + 1] + 1)` so the first pass's result survives."),
           ("edge case", "A sorted row of 2·10⁵ children needs about 2·10¹⁰ candies, more than a `u32` holds.")],
    notes=("After both passes, each child's count is the longer of the strictly rising runs reaching it from the left and from the right. Any valid assignment needs at least that much, so the total is the minimum.", "O(n)", "O(n)"),
    follow_up="Can you do it in O(1) extra space by counting the lengths of rising and falling slopes as you go?",
    related=["D12", "D1"],
))

P.append(dict(
    slug="minimum-interval-to-include-each-query", title="Minimum interval to include each query", level="hard", stage="hard-greedy", tags=["intervals", "heap", "sorting", "offline queries"],
    companies=["Amazon", "Google"],
    teaches=["Offline queries: sort query indices, answer in sorted order, write answers back by index.", "Lazy deletion from a `BinaryHeap<Reverse<_>>`: only discard stale tops when you look at them."],
    statement="""
        Each interval `(left, right)` is closed and has size `right - left + 1`. For each query `q`, find the
        size of the smallest interval containing `q`, or `None` if no interval does. Return the answers in the
        same order as `queries`.
    """,
    examples=[("intervals = [(1, 4), (2, 4), (3, 6), (4, 4)], queries = [2, 3, 4, 5]", "[Some(3), Some(3), Some(1), Some(4)]"),
              ("intervals = [(2, 3), (2, 5), (1, 8), (20, 25)], queries = [2, 19, 5, 22]", "[Some(2), None, Some(4), Some(6)]")],
    constraints=["0 ≤ intervals.len(), queries.len() ≤ 10⁵", "left ≤ right, both any i32", "queries[i] is any i32"],
    starter="""
        pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
            let mut sorted = intervals.to_vec();
            sorted.sort_unstable();
            let mut order: Vec<usize> = (0..queries.len()).collect();
            order.sort_unstable_by_key(|&i| queries[i]);
            // (size, right) of every interval that starts at or before the current query.
            let mut open: BinaryHeap<Reverse<(u64, i32)>> = BinaryHeap::new();
            let mut answers = vec![None; queries.len()];
            let mut next = 0;
            for i in order {
                let q = queries[i];
                while next < sorted.len() && sorted[next].0 <= q {
                    let (left, right) = sorted[next];
                    open.push(Reverse(((right as i64 - left as i64 + 1) as u64, right)));
                    next += 1;
                }
                // An interval that ended before q ended before every later query too.
                while open.peek().is_some_and(|Reverse((_, right))| *right < q) {
                    open.pop();
                }
                answers[i] = open.peek().map(|Reverse((size, _))| *size);
            }
            answers
        }
    """,
    visible=[
        T("leetcode_four", "intervals = [(1, 4), (2, 4), (3, 6), (4, 4)], queries = [2, 3, 4, 5]", "min_interval(&[(1, 4), (2, 4), (3, 6), (4, 4)], &[2, 3, 4, 5])", "vec![Some(3), Some(3), Some(1), Some(4)]"),
        T("leetcode_with_miss", "intervals = [(2, 3), (2, 5), (1, 8), (20, 25)], queries = [2, 19, 5, 22]", "min_interval(&[(2, 3), (2, 5), (1, 8), (20, 25)], &[2, 19, 5, 22])", "vec![Some(2), None, Some(4), Some(6)]"),
        T("no_intervals", "intervals = [], queries = [1]", "min_interval(&[], &[1])", "vec![None]"),
        T("no_queries", "intervals = [(1, 2)], queries = []", "min_interval(&[(1, 2)], &[])", "Vec::<Option<u64>>::new()"),
        T("ends_are_included", "intervals = [(1, 1)], queries = [1]", "min_interval(&[(1, 1)], &[1])", "vec![Some(1)]"),
        T("answers_in_query_order", "intervals = [(0, 10), (5, 6)], queries = [6, 0, 20]", "min_interval(&[(0, 10), (5, 6)], &[6, 0, 20])", "vec![Some(2), Some(11), None]"),
    ],
    hidden=[
        T("whole_i32", "intervals = [(-2147483648, 2147483647)], queries = [0]", "min_interval(&[(i32::MIN, i32::MAX)], &[0])", "vec![Some(4_294_967_296)]"),
        T("query_at_i32_edges", "intervals = [(-2147483648, -2147483648), (2147483647, 2147483647)], queries = [2147483647, -2147483648, 0]", "min_interval(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)], &[i32::MAX, i32::MIN, 0])", "vec![Some(1), Some(1), None]"),
        T("negatives", "intervals = [(-5, -1), (-3, 3), (0, 0)], queries = [-4, -3, 0, 1, 4]", "min_interval(&[(-5, -1), (-3, 3), (0, 0)], &[-4, -3, 0, 1, 4])", "vec![Some(5), Some(5), Some(1), Some(7), None]"),
        T("nested", "intervals = [(1, 10), (2, 9), (3, 8), (4, 7)], queries = [5, 1, 9, 11]", "min_interval(&[(1, 10), (2, 9), (3, 8), (4, 7)], &[5, 1, 9, 11])", "vec![Some(4), Some(10), Some(8), None]"),
        T("repeated_queries", "intervals = [(1, 3)], queries = [2, 2, 2]", "min_interval(&[(1, 3)], &[2, 2, 2])", "vec![Some(3); 3]"),
        T("small_one_ends_first", "intervals = [(1, 2), (1, 100)], queries = [3, 2]", "min_interval(&[(1, 2), (1, 100)], &[3, 2])", "vec![Some(100), Some(2)]"),
        T("same_interval_twice", "intervals = [(4, 6), (4, 6)], queries = [5, 7]", "min_interval(&[(4, 6), (4, 6)], &[5, 7])", "vec![Some(3), None]"),
        T("before_everything", "intervals = [(10, 20)], queries = [9, 10, 20, 21]", "min_interval(&[(10, 20)], &[9, 10, 20, 21])", "vec![None, Some(11), Some(11), None]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(826);
            for _ in 0..400 {
                let n = rng.below(7);
                let intervals: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let left = rng.int(-5, 10) as i32;
                        let len = rng.int(0, 5) as i32;
                        (left, left + len)
                    })
                    .collect();
                let m = rng.below(7);
                let queries: Vec<i32> = rng.vec(m, -6, 16);
                let want: Vec<Option<u64>> = queries
                    .iter()
                    .map(|&q| intervals.iter().filter(|&&(l, r)| l <= q && q <= r).map(|&(l, r)| (r - l + 1) as u64).min())
                    .collect();
                check!(format!("intervals = {intervals:?}, queries = {queries:?}"), min_interval(&intervals, &queries), want);
            }
        }

        #[test]
        fn scale_100k() {
            let mut intervals: Vec<(i32, i32)> = (0..99_999).rev().map(|i| (2 * i, 2 * i + 1)).collect();
            intervals.push((0, 200_005));
            let queries: Vec<i32> = (0..100_000).rev().map(|j| 3 * j).collect();
            let out = min_interval(&intervals, &queries);
            let count = |v: Option<u64>| out.iter().filter(|&&x| x == v).count();
            check!(
                "(2i, 2i + 1) for i in 0..99999 plus (0, 200005); queries 3j for j from 99999 down to 0",
                (count(Some(2)), count(Some(200_006)), count(None), out[0], out[99_999]),
                (66_666, 3, 33_331, None, Some(2))
            );
        }
        """,
    ],
    wrong=dict(
        every_pair="""
            pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
                queries
                    .iter()
                    .map(|&q| intervals.iter().filter(|&&(l, r)| l <= q && q <= r).map(|&(l, r)| (r as i64 - l as i64 + 1) as u64).min())
                    .collect()
            }
        """,
        size_off_by_one="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut order: Vec<usize> = (0..queries.len()).collect();
                order.sort_unstable_by_key(|&i| queries[i]);
                let mut open: BinaryHeap<Reverse<(u64, i32)>> = BinaryHeap::new();
                let mut answers = vec![None; queries.len()];
                let mut next = 0;
                for i in order {
                    let q = queries[i];
                    while next < sorted.len() && sorted[next].0 <= q {
                        let (left, right) = sorted[next];
                        open.push(Reverse(((right as i64 - left as i64) as u64, right)));
                        next += 1;
                    }
                    while open.peek().is_some_and(|Reverse((_, right))| *right < q) {
                        open.pop();
                    }
                    answers[i] = open.peek().map(|Reverse((size, _))| *size);
                }
                answers
            }
        """,
        answers_in_sorted_order="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut qs = queries.to_vec();
                qs.sort_unstable();
                let mut open: BinaryHeap<Reverse<(u64, i32)>> = BinaryHeap::new();
                let mut answers = Vec::new();
                let mut next = 0;
                for q in qs {
                    while next < sorted.len() && sorted[next].0 <= q {
                        let (left, right) = sorted[next];
                        open.push(Reverse(((right as i64 - left as i64 + 1) as u64, right)));
                        next += 1;
                    }
                    while open.peek().is_some_and(|Reverse((_, right))| *right < q) {
                        open.pop();
                    }
                    answers.push(open.peek().map(|Reverse((size, _))| *size));
                }
                answers
            }
        """,
    ),
    hints=[("approach", "Answer the queries from smallest to largest. Add each interval once its left end is at or before the query, keep them in a min-heap by size, and pop from the top any interval whose right end is already behind the query."),
           ("rust", "Sort indices with `order.sort_unstable_by_key(|&i| queries[i])` so answers go back to `answers[i]`; `BinaryHeap<Reverse<(u64, i32)>>` is a min-heap by size."),
           ("edge case", "`(i32::MIN, i32::MAX)` has size 2³², which doesn't fit a `u32`: compute `right as i64 - left as i64 + 1`.")],
    notes=("Offline processing: with queries sorted, an interval whose right end is behind the current query is behind every later one, so dropping it from the heap top is safe; intervals buried lower are dropped when they surface. Each interval is pushed and popped at most once.", "O(n log n + q log q)", "O(n + q)"),
    follow_up="How would you answer the queries online, one at a time as they arrive?",
    related=["D7", "S5", "D4"],
))

P.append(dict(
    slug="employee-free-time", title="Employee free time", level="hard", stage="hard-greedy", tags=["intervals", "heap", "k-way merge"],
    companies=["Amazon", "Google", "Airbnb", "Uber"],
    teaches=["k-way merge of sorted lists with a `BinaryHeap<Reverse<(start, list, index)>>`.", "Merge intervals, but keep the gaps instead of the merged blocks."],
    statement="""
        `schedule[e]` lists employee `e`'s working intervals `(start, end)`, sorted and not overlapping; each
        covers the time from `start` up to but not including `end`. Return the free time every employee shares:
        the gaps of positive length between the first start and the last end, sorted.
    """,
    examples=[("schedule = [[(1, 2), (5, 6)], [(1, 3)], [(4, 10)]]", "[(3, 4)]"), ("schedule = [[(1, 3), (6, 7)], [(2, 4)], [(2, 5), (9, 12)]]", "[(5, 6), (7, 9)]")],
    constraints=["0 ≤ total number of intervals ≤ 2·10⁵", "start < end, both any i32", "each employee's list is sorted and non-overlapping"],
    starter="""
        pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
            // One entry per employee: (start, employee, index) of their next interval.
            let mut heap = BinaryHeap::new();
            for (e, list) in schedule.iter().enumerate() {
                if let Some(&(start, _)) = list.first() {
                    heap.push(Reverse((start, e, 0usize)));
                }
            }
            let mut free = Vec::new();
            let mut busy_until: Option<i32> = None;
            while let Some(Reverse((start, e, i))) = heap.pop() {
                let end = schedule[e][i].1;
                busy_until = Some(match busy_until {
                    Some(b) if start > b => {
                        free.push((b, start));
                        end
                    }
                    Some(b) => b.max(end),
                    None => end,
                });
                if let Some(&(next, _)) = schedule[e].get(i + 1) {
                    heap.push(Reverse((next, e, i + 1)));
                }
            }
            free
        }
    """,
    visible=[
        T("leetcode_one_gap", "schedule = [[(1, 2), (5, 6)], [(1, 3)], [(4, 10)]]", "employee_free_time(&[vec![(1, 2), (5, 6)], vec![(1, 3)], vec![(4, 10)]])", "vec![(3, 4)]"),
        T("leetcode_two_gaps", "schedule = [[(1, 3), (6, 7)], [(2, 4)], [(2, 5), (9, 12)]]", "employee_free_time(&[vec![(1, 3), (6, 7)], vec![(2, 4)], vec![(2, 5), (9, 12)]])", "vec![(5, 6), (7, 9)]"),
        T("no_employees", "schedule = []", "employee_free_time(&[])", "Vec::<(i32, i32)>::new()"),
        T("one_employee", "schedule = [[(1, 2), (3, 4)]]", "employee_free_time(&[vec![(1, 2), (3, 4)]])", "vec![(2, 3)]"),
        T("touching_is_not_free", "schedule = [[(1, 2)], [(2, 3)]]", "employee_free_time(&[vec![(1, 2)], vec![(2, 3)]])", "Vec::<(i32, i32)>::new()"),
        T("employee_with_no_work", "schedule = [[], [(1, 2), (4, 5)]]", "employee_free_time(&[vec![], vec![(1, 2), (4, 5)]])", "vec![(2, 4)]"),
    ],
    hidden=[
        T("nested", "schedule = [[(1, 10)], [(2, 3), (5, 6)]]", "employee_free_time(&[vec![(1, 10)], vec![(2, 3), (5, 6)]])", "Vec::<(i32, i32)>::new()"),
        T("long_then_short", "schedule = [[(1, 5), (20, 30)], [(2, 3), (6, 7)]]", "employee_free_time(&[vec![(1, 5), (20, 30)], vec![(2, 3), (6, 7)]])", "vec![(5, 6), (7, 20)]"),
        T("negatives", "schedule = [[(-10, -5), (0, 2)], [(-7, -6), (3, 4)]]", "employee_free_time(&[vec![(-10, -5), (0, 2)], vec![(-7, -6), (3, 4)]])", "vec![(-5, 0), (2, 3)]"),
        T("i32_extremes", "schedule = [[(-2147483648, -1)], [(1, 2147483647)]]", "employee_free_time(&[vec![(i32::MIN, -1)], vec![(1, i32::MAX)]])", "vec![(-1, 1)]"),
        T("all_lists_empty", "schedule = [[], []]", "employee_free_time(&[vec![], vec![]])", "Vec::<(i32, i32)>::new()"),
        T("single_interval", "schedule = [[(0, 1)]]", "employee_free_time(&[vec![(0, 1)]])", "Vec::<(i32, i32)>::new()"),
        T("same_hours_for_all", "schedule = [[(1, 3), (5, 6)], [(1, 3), (5, 6)], [(1, 3), (5, 6)]]", "employee_free_time(&[vec![(1, 3), (5, 6)], vec![(1, 3), (5, 6)], vec![(1, 3), (5, 6)]])", "vec![(3, 5)]"),
        T("relay_across_employees", "schedule = [[(1, 2), (3, 4), (5, 6)], [(2, 3)], [(6, 8), (10, 11)]]", "employee_free_time(&[vec![(1, 2), (3, 4), (5, 6)], vec![(2, 3)], vec![(6, 8), (10, 11)]])", "vec![(4, 5), (8, 10)]"),
        T("touching_within_one_list", "schedule = [[(1, 2), (2, 3), (5, 6)]]", "employee_free_time(&[vec![(1, 2), (2, 3), (5, 6)]])", "vec![(3, 5)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(827);
            for _ in 0..400 {
                let k = rng.below(4);
                let mut schedule: Vec<Vec<(i32, i32)>> = Vec::new();
                for _ in 0..k {
                    let count = rng.below(4);
                    let mut list = Vec::new();
                    let mut t = rng.int(0, 4) as i32;
                    for _ in 0..count {
                        let len = rng.int(1, 4) as i32;
                        list.push((t, t + len));
                        let gap = rng.int(0, 4) as i32;
                        t += len + gap;
                    }
                    schedule.push(list);
                }
                // Mark each busy unit [t, t + 1) on a small grid and read off the gaps.
                let mut busy = vec![false; 64];
                for &(s, e) in schedule.iter().flatten() {
                    for t in s..e {
                        busy[t as usize] = true;
                    }
                }
                let mut want = Vec::new();
                if let (Some(first), Some(last)) = (busy.iter().position(|&b| b), busy.iter().rposition(|&b| b)) {
                    let mut t = first;
                    while t <= last {
                        if busy[t] {
                            t += 1;
                        } else {
                            let start = t;
                            while !busy[t] {
                                t += 1;
                            }
                            want.push((start as i32, t as i32));
                        }
                    }
                }
                check!(format!("schedule = {schedule:?}"), employee_free_time(&schedule), want);
            }
        }

        #[test]
        fn scale_200k() {
            // Employee e works (e + 2000k, e + 2000k + 1): together busy 2000k..2000k + 1000, free after.
            let schedule: Vec<Vec<(i32, i32)>> = (0..1000).map(|e| (0..200).map(|k| (e + 2000 * k, e + 2000 * k + 1)).collect()).collect();
            let free = employee_free_time(&schedule);
            check!("1000 employees; employee e works (e + 2000k, e + 2000k + 1) for k in 0..200", (free.len(), free[0], free[198]), (199, (1000, 2000), (397_000, 398_000)));
        }
        """,
    ],
    wrong=dict(
        check_each_end="""
            pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
                let all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
                let mut free = Vec::new();
                for &(_, end) in &all {
                    // Free from `end` if nobody works at `end` and somebody starts later.
                    if all.iter().any(|&(s, e)| s <= end && end < e) {
                        continue;
                    }
                    if let Some(next) = all.iter().map(|&(s, _)| s).filter(|&s| s > end).min() {
                        free.push((end, next));
                    }
                }
                free.sort_unstable();
                free.dedup();
                free
            }
        """,
        keeps_empty_gaps="""
            pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
                let mut all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
                all.sort_unstable();
                let mut free = Vec::new();
                let mut busy_until: Option<i32> = None;
                for (start, end) in all {
                    busy_until = Some(match busy_until {
                        Some(b) if start >= b => {
                            free.push((b, start));
                            end
                        }
                        Some(b) => b.max(end),
                        None => end,
                    });
                }
                free
            }
        """,
        end_not_max="""
            pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
                let mut all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
                all.sort_unstable();
                let mut free = Vec::new();
                for w in all.windows(2) {
                    if w[1].0 > w[0].1 {
                        free.push((w[0].1, w[1].0));
                    }
                }
                free
            }
        """,
    ),
    hints=[("approach", "Treat all intervals as one stream sorted by start, tracking the latest end seen so far. A start after that end opens a free gap."),
           ("rust", "Each list is already sorted, so merge them with a `BinaryHeap<Reverse<(i32, usize, usize)>>` holding each employee's next interval. Flattening and sorting also works in O(N log N)."),
           ("edge case", "Keep the max end: one long interval can cover several later ones. A gap must have positive length, so `(1, 2)` then `(2, 3)` leaves no free time.")],
    notes=("This is merge intervals across every employee, keeping the gaps between merged blocks. The heap holds one interval per employee, so N intervals from k employees cost O(N log k).", "O(N log k)", "O(k) for the heap, plus the output"),
    follow_up="If each calendar were a live stream of new meetings, how would you report shared free time as soon as it is certain?",
    related=["D7", "S5"],
))

P.append(dict(
    slug="minimum-number-of-refueling-stops", title="Minimum number of refueling stops", level="hard", stage="hard-greedy", tags=["greedy", "heap"],
    companies=["Amazon", "Google"],
    teaches=["Defer the decision: remember every station you passed and take the best one only when you must.", "`passed.pop()?` in a function returning `Option` exits with `None` when the heap is empty."],
    statement="""
        A car drives east from position 0 to `target`, using one unit of fuel per unit of distance. It starts with
        `start_fuel` and its tank has no limit. `stations[i] = (position, fuel)`, sorted by position; stopping
        there adds all of that fuel. Return the fewest stops needed to reach `target`, or `None`. Arriving
        anywhere with exactly 0 fuel left still counts.
    """,
    examples=[("target = 1, start_fuel = 1, stations = []", "Some(0)"), ("target = 100, start_fuel = 1, stations = [(10, 100)]", "None"),
              ("target = 100, start_fuel = 10, stations = [(10, 60), (20, 30), (30, 30), (60, 40)]", "Some(2)")],
    constraints=["1 ≤ target ≤ 10¹²", "0 ≤ start_fuel ≤ 10¹²", "0 ≤ stations.len() ≤ 2·10⁵", "0 < position < target, strictly increasing", "1 ≤ fuel ≤ 10⁹"],
    starter="""
        pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BinaryHeap;

        pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
            // Fuel of every station passed but not used yet; a max-heap.
            let mut passed = BinaryHeap::new();
            let mut reach = start_fuel;
            let (mut stops, mut next) = (0, 0);
            while reach < target {
                while next < stations.len() && stations[next].0 <= reach {
                    passed.push(stations[next].1);
                    next += 1;
                }
                // Out of fuel: we should have stopped at the richest station behind us.
                reach += passed.pop()?;
                stops += 1;
            }
            Some(stops)
        }
    """,
    visible=[
        T("leetcode_already_there", "target = 1, start_fuel = 1, stations = []", "min_refuel_stops(1, 1, &[])", "Some(0)"),
        T("leetcode_cannot_reach", "target = 100, start_fuel = 1, stations = [(10, 100)]", "min_refuel_stops(100, 1, &[(10, 100)])", "None"),
        T("leetcode_two_stops", "target = 100, start_fuel = 10, stations = [(10, 60), (20, 30), (30, 30), (60, 40)]", "min_refuel_stops(100, 10, &[(10, 60), (20, 30), (30, 30), (60, 40)])", "Some(2)"),
        T("exact_fuel_no_stations", "target = 10, start_fuel = 10, stations = []", "min_refuel_stops(10, 10, &[])", "Some(0)"),
        T("arrive_empty_at_a_station", "target = 100, start_fuel = 50, stations = [(50, 50)]", "min_refuel_stops(100, 50, &[(50, 50)])", "Some(1)"),
        T("richest_not_farthest", "target = 100, start_fuel = 50, stations = [(10, 50), (50, 10)]", "min_refuel_stops(100, 50, &[(10, 50), (50, 10)])", "Some(1)"),
    ],
    hidden=[
        T("no_fuel_no_stations", "target = 5, start_fuel = 0, stations = []", "min_refuel_stops(5, 0, &[])", "None"),
        T("no_fuel_to_first_station", "target = 5, start_fuel = 0, stations = [(1, 10)]", "min_refuel_stops(5, 0, &[(1, 10)])", "None"),
        T("station_out_of_reach", "target = 10, start_fuel = 1, stations = [(2, 100)]", "min_refuel_stops(10, 1, &[(2, 100)])", "None"),
        T("forced_every_stop", "target = 100, start_fuel = 25, stations = [(25, 25), (50, 50)]", "min_refuel_stops(100, 25, &[(25, 25), (50, 50)])", "Some(2)"),
        T("leetcode_ten_none", "target = 1000, start_fuel = 83, stations = [(25, 27), (36, 187), (140, 186), (378, 6), (492, 202), (517, 89), (579, 234), (673, 86), (808, 53), (954, 49)]", "min_refuel_stops(1000, 83, &[(25, 27), (36, 187), (140, 186), (378, 6), (492, 202), (517, 89), (579, 234), (673, 86), (808, 53), (954, 49)])", "None"),
        T("leetcode_ten_four", "target = 1000, start_fuel = 299, stations = [(13, 21), (26, 115), (100, 47), (225, 99), (299, 141), (444, 198), (608, 190), (636, 157), (647, 255), (841, 123)]", "min_refuel_stops(1000, 299, &[(13, 21), (26, 115), (100, 47), (225, 99), (299, 141), (444, 198), (608, 190), (636, 157), (647, 255), (841, 123)])", "Some(4)"),
        T("reach_past_u32", "target = 10¹², start_fuel = 10⁹, stations = (k·10⁹, 10⁹) for k in 1..1000", "min_refuel_stops(1_000_000_000_000, 1_000_000_000, &(1..1000u64).map(|k| (k * 1_000_000_000, 1_000_000_000)).collect::<Vec<_>>())", "Some(999)"),
        T("plenty_of_fuel", "target = 50, start_fuel = 100, stations = [(10, 5), (20, 5)]", "min_refuel_stops(50, 100, &[(10, 5), (20, 5)])", "Some(0)"),
        T("one_short", "target = 100, start_fuel = 50, stations = [(50, 49)]", "min_refuel_stops(100, 50, &[(50, 49)])", "None"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(828);
            for _ in 0..400 {
                let target = rng.int(1, 30) as u64;
                let start_fuel = rng.int(0, 12) as u64;
                let n = rng.below(8);
                let mut stations = Vec::new();
                let mut pos = 0u64;
                for _ in 0..n {
                    pos += rng.int(1, 5) as u64;
                    if pos >= target {
                        break;
                    }
                    let fuel = rng.int(1, 10) as u64;
                    stations.push((pos, fuel));
                }
                // Every set of stops, driven in order.
                let mut want: Option<usize> = None;
                for mask in 0u32..1 << stations.len() {
                    let mut reach = start_fuel;
                    for (i, &(pos, fuel)) in stations.iter().enumerate() {
                        if pos > reach {
                            break;
                        }
                        if mask >> i & 1 == 1 {
                            reach += fuel;
                        }
                    }
                    if reach >= target {
                        let c = mask.count_ones() as usize;
                        want = Some(want.map_or(c, |w| w.min(c)));
                    }
                }
                check!(format!("target = {target}, start_fuel = {start_fuel}, stations = {stations:?}"), min_refuel_stops(target, start_fuel, &stations), want);
            }
        }

        #[test]
        fn scale_200k() {
            let stations: Vec<(u64, u64)> = (1..=200_000).map(|p| (p, 1)).collect();
            check!(
                "stations (p, 1) for p in 1..=200000, start_fuel = 1, target = 200001 and 200002",
                (min_refuel_stops(200_001, 1, &stations), min_refuel_stops(200_002, 1, &stations)),
                (Some(200_000), None)
            );
        }
        """,
    ],
    wrong=dict(
        quadratic_dp="""
            pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
                let n = stations.len();
                // far[t]: the farthest position reachable with t stops.
                let mut far = vec![0u64; n + 1];
                far[0] = start_fuel;
                for (i, &(pos, fuel)) in stations.iter().enumerate() {
                    for t in (0..=i).rev() {
                        if far[t] >= pos {
                            far[t + 1] = far[t + 1].max(far[t] + fuel);
                        }
                    }
                }
                (0..=n).find(|&t| far[t] >= target)
            }
        """,
        stop_at_farthest="""
            pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
                let mut used = vec![false; stations.len()];
                let mut reach = start_fuel;
                let mut stops = 0;
                while reach < target {
                    let pick = (0..stations.len()).rev().find(|&i| !used[i] && stations[i].0 <= reach)?;
                    used[pick] = true;
                    reach += stations[pick].1;
                    stops += 1;
                }
                Some(stops)
            }
        """,
        needs_fuel_left="""
            use std::collections::BinaryHeap;

            pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
                let mut passed = BinaryHeap::new();
                let mut reach = start_fuel;
                let (mut stops, mut next) = (0, 0);
                while reach < target {
                    while next < stations.len() && stations[next].0 < reach {
                        passed.push(stations[next].1);
                        next += 1;
                    }
                    reach += passed.pop()?;
                    stops += 1;
                }
                Some(stops)
            }
        """,
    ),
    hints=[("approach", "Drive as far as your fuel allows, remembering the fuel of every station you pass. When you can't reach the target, pretend you had stopped at the passed station with the most fuel."),
           ("rust", "`BinaryHeap<u64>` is already a max-heap; `reach += passed.pop()?;` returns `None` from the function when no passed station is left."),
           ("edge case", "Reaching a station or the target with exactly 0 fuel is fine, so compare positions with `<=`.")],
    notes=("When fuel runs out, any passed station could have been a stop, and the one with the most fuel reaches at least as far as any other single choice. Deferring each choice until it's needed never uses more stops. Each station enters and leaves the heap once.", "O(n log n)", "O(n)"),
    follow_up="If each stop also took time proportional to the fuel pumped, how would you minimise total travel time instead?",
    related=["D7", "D12", "S5"],
))

P.append(dict(
    slug="course-schedule-iii", title="Course schedule III", level="hard", stage="hard-greedy", tags=["greedy", "heap", "sorting"],
    companies=["Amazon", "Google"],
    teaches=["Sort by deadline, keep a max-heap of what you've taken, and swap out the longest when you run late.", "Track the running total in `u64`: two `u32` durations can overflow."],
    statement="""
        Course `(duration, last_day)` takes `duration` days and must be finished by day `last_day`. Courses run
        one at a time, back to back, starting on day 1, so a course that starts after `t` days of earlier courses
        finishes on day `t + duration`. Return the most courses you can finish.
    """,
    examples=[("courses = [(100, 200), (200, 1300), (1000, 1250), (2000, 3200)]", "3"), ("courses = [(1, 2)]", "1"), ("courses = [(3, 2), (4, 3)]", "0")],
    constraints=["0 ≤ courses.len() ≤ 2·10⁵", "1 ≤ duration, last_day ≤ 2³² − 1"],
    starter="""
        pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::BinaryHeap;

        pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
            let mut by_deadline = courses.to_vec();
            by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
            // Durations of the courses taken so far; a max-heap.
            let mut taken = BinaryHeap::new();
            let mut time = 0u64;
            for (duration, last_day) in by_deadline {
                taken.push(duration);
                time += duration as u64;
                if time > last_day as u64 {
                    // Too late: drop the longest course (maybe this one).
                    if let Some(longest) = taken.pop() {
                        time -= longest as u64;
                    }
                }
            }
            taken.len()
        }
    """,
    visible=[
        T("leetcode_three", "courses = [(100, 200), (200, 1300), (1000, 1250), (2000, 3200)]", "schedule_course(&[(100, 200), (200, 1300), (1000, 1250), (2000, 3200)])", "3"),
        T("leetcode_one", "courses = [(1, 2)]", "schedule_course(&[(1, 2)])", "1"),
        T("leetcode_none_fit", "courses = [(3, 2), (4, 3)]", "schedule_course(&[(3, 2), (4, 3)])", "0"),
        T("no_courses", "courses = []", "schedule_course(&[])", "0"),
        T("finish_on_the_last_day", "courses = [(5, 5)]", "schedule_course(&[(5, 5)])", "1"),
        T("swap_long_for_short", "courses = [(4, 4), (1, 5), (1, 5), (1, 5)]", "schedule_course(&[(4, 4), (1, 5), (1, 5), (1, 5)])", "3"),
    ],
    hidden=[
        T("too_long_alone", "courses = [(6, 5)]", "schedule_course(&[(6, 5)])", "0"),
        T("same_deadline", "courses = [(2, 2), (2, 2)]", "schedule_course(&[(2, 2), (2, 2)])", "1"),
        T("back_to_back", "courses = [(1, 2), (2, 3)]", "schedule_course(&[(1, 2), (2, 3)])", "2"),
        T("shorter_pair_wins", "courses = [(5, 5), (4, 6), (2, 6)]", "schedule_course(&[(5, 5), (4, 6), (2, 6)])", "2"),
        T("leetcode_eight", "courses = [(5, 15), (3, 19), (6, 7), (2, 10), (5, 16), (8, 14), (10, 11), (2, 19)]", "schedule_course(&[(5, 15), (3, 19), (6, 7), (2, 10), (5, 16), (8, 14), (10, 11), (2, 19)])", "5"),
        T("leetcode_seven", "courses = [(7, 17), (3, 12), (10, 20), (9, 10), (5, 20), (10, 19), (4, 18)]", "schedule_course(&[(7, 17), (3, 12), (10, 20), (9, 10), (5, 20), (10, 19), (4, 18)])", "4"),
        T("time_past_u32", "courses = [(4294967295, 4294967295), (4294967295, 4294967295)]", "schedule_course(&[(u32::MAX, u32::MAX), (u32::MAX, u32::MAX)])", "1"),
        T("unsorted_input", "courses = [(2, 10), (9, 9)]", "schedule_course(&[(2, 10), (9, 9)])", "1"),
        T("duration_order_trap", "courses = [(1, 100), (99, 99), (1, 2)]", "schedule_course(&[(1, 100), (99, 99), (1, 2)])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(829);
            for _ in 0..300 {
                let n = rng.below(9);
                let courses: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(1, 6) as u32, rng.int(1, 15) as u32)).collect();
                // A set fits exactly when it fits in deadline order.
                let mut want = 0;
                for mask in 0u32..1 << n {
                    let mut chosen: Vec<(u32, u32)> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| courses[i]).collect();
                    chosen.sort_unstable_by_key(|c| c.1);
                    let mut t = 0;
                    if chosen.iter().all(|&(d, last)| {
                        t += d;
                        t <= last
                    }) {
                        want = want.max(chosen.len());
                    }
                }
                check!(format!("courses = {courses:?}"), schedule_course(&courses), want);
            }
        }

        #[test]
        fn scale_200k() {
            let same = vec![(1u32, 100_000u32); 200_000];
            let spread: Vec<(u32, u32)> = (0..200_000u32).rev().map(|i| (2, 2 * i + 2)).collect();
            check!("(1, 100000) × 200000; (2, 2i + 2) for i in 0..200000", (schedule_course(&same), schedule_course(&spread)), (100_000, 200_000));
        }
        """,
    ],
    wrong=dict(
        scan_for_longest="""
            pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
                let mut by_deadline = courses.to_vec();
                by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
                let mut taken: Vec<u32> = Vec::new();
                let mut time = 0u64;
                for (duration, last_day) in by_deadline {
                    taken.push(duration);
                    time += duration as u64;
                    if time > last_day as u64 {
                        let longest = (0..taken.len()).max_by_key(|&i| taken[i]).unwrap();
                        time -= taken.swap_remove(longest) as u64;
                    }
                }
                taken.len()
            }
        """,
        skip_when_late="""
            pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
                let mut by_deadline = courses.to_vec();
                by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
                let (mut time, mut count) = (0u64, 0);
                for (duration, last_day) in by_deadline {
                    if time + duration as u64 <= last_day as u64 {
                        time += duration as u64;
                        count += 1;
                    }
                }
                count
            }
        """,
        u32_time="""
            use std::collections::BinaryHeap;

            pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
                let mut by_deadline = courses.to_vec();
                by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
                let mut taken = BinaryHeap::new();
                let mut time = 0u32;
                for (duration, last_day) in by_deadline {
                    taken.push(duration);
                    time += duration;
                    if time > last_day {
                        if let Some(longest) = taken.pop() {
                            time -= longest;
                        }
                    }
                }
                taken.len()
            }
        """,
    ),
    hints=[("approach", "Take courses in order of deadline. If adding one makes you late, drop the longest course taken so far (possibly the new one): the count stays the same and the finish time drops as far as it can."),
           ("rust", "A `BinaryHeap<u32>` of the durations taken, with the running total in `u64`."),
           ("edge case", "Dropping a course never makes an earlier one late: everything taken so far has a deadline no later than the current course's.")],
    notes=("In deadline order, the heap always holds a largest set of courses that fits, and among those the one with the smallest total time. Swapping the longest course out for the new one keeps the count and lowers the total, which only helps later courses.", "O(n log n)", "O(n)"),
    follow_up="If each course had a value and you wanted the most total value, would the heap still work? (No: that needs a knapsack-style DP.)",
    related=["D7", "D12", "D9"],
))

STAGES = [
    ("first-greedy", "First greedy", "easy"),
    ("intervals", "Intervals", "medium"),
    ("greedy-choices", "Greedy choices", "medium"),
    ("hard-greedy", "Hard greedy", "hard"),
]

if __name__ == "__main__":
    n = write_track("d8-intervals-greedy", "D8", "Intervals & greedy", "D", "core", 9,
                    "Sort, sweep and choose: merging intervals, sweep lines and greedy exchange arguments, with tuples, sort keys and heaps.",
                    STAGES, P)
    print("D8", n)
