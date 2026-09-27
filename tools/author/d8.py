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
