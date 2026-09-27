// The planned curriculum (docs/CURRICULUM.md), so section pages can show tracks
// that aren't written yet. Generated from the mockup's track data.
import type { Section, Tier } from "./api";

export interface PlannedTrack {
  code: string;
  name: string;
  /** Planned problem count. */
  planned: number;
  tier: Tier;
}

export const PLANNED: PlannedTrack[] = [
  { code: "D1", name: "Arrays & hashing", planned: 24, tier: "core" },
  { code: "D2", name: "Two pointers & windows", planned: 18, tier: "core" },
  { code: "D3", name: "Stacks & queues", planned: 14, tier: "core" },
  { code: "D4", name: "Binary search", planned: 14, tier: "core" },
  { code: "D5", name: "Linked lists", planned: 15, tier: "core" },
  { code: "D6", name: "Trees & BSTs", planned: 44, tier: "core" },
  { code: "D7", name: "Heaps & priority queues", planned: 13, tier: "core" },
  { code: "D8", name: "Intervals & greedy", planned: 29, tier: "core" },
  { code: "D9", name: "Graphs", planned: 58, tier: "core" },
  { code: "D10", name: "Tries & strings", planned: 25, tier: "core" },
  { code: "D11", name: "Recursion & backtracking", planned: 28, tier: "core" },
  { code: "D12", name: "Dynamic programming", planned: 57, tier: "core" },
  { code: "D13", name: "Matrix, bits & math", planned: 16, tier: "core" },
  { code: "D14", name: "Data-structure design", planned: 20, tier: "core" },
  { code: "L1", name: "Ownership & moves", planned: 18, tier: "core" },
  { code: "L2", name: "Borrowing", planned: 35, tier: "core" },
  { code: "L3", name: "Lifetimes", planned: 20, tier: "core" },
  { code: "L4", name: "Traits & dispatch", planned: 22, tier: "core" },
  { code: "L5", name: "Generics & associated types", planned: 16, tier: "core" },
  { code: "L6", name: "Closures", planned: 14, tier: "core" },
  { code: "L7", name: "Enums & patterns", planned: 14, tier: "core" },
  { code: "L8", name: "Error design", planned: 16, tier: "core" },
  { code: "L9", name: "Modules & Cargo", planned: 10, tier: "light" },
  { code: "L10", name: "Macros", planned: 12, tier: "sde3" },
  { code: "S1", name: "Option & Result", planned: 16, tier: "core" },
  { code: "S2", name: "Strings & text", planned: 18, tier: "core" },
  { code: "S3", name: "Vec & slices", planned: 20, tier: "core" },
  { code: "S4", name: "Maps & sets", planned: 18, tier: "core" },
  { code: "S5", name: "Queues & heaps", planned: 14, tier: "core" },
  { code: "S6", name: "Iterators", planned: 22, tier: "core" },
  { code: "S7", name: "Smart pointers", planned: 20, tier: "core" },
  { code: "S8", name: "Core traits", planned: 16, tier: "core" },
  { code: "S9", name: "I/O & filesystem", planned: 14, tier: "core" },
  { code: "S10", name: "Time & processes", planned: 8, tier: "light" },
  { code: "S11", name: "mem, ptr & alloc", planned: 12, tier: "sde3" },
  { code: "C1", name: "Threads & shared state", planned: 22, tier: "core" },
  { code: "C2", name: "Message passing", planned: 16, tier: "core" },
  { code: "C3", name: "Atomics & lock-free", planned: 14, tier: "sde3" },
  { code: "C4", name: "Async & Tokio", planned: 26, tier: "core" },
  { code: "C5", name: "Async internals", planned: 12, tier: "sde3" },
  { code: "C6", name: "Data parallelism", planned: 8, tier: "light" },
  { code: "Y1", name: "Memory & layout", planned: 14, tier: "sde3" },
  { code: "Y2", name: "Unsafe Rust", planned: 16, tier: "sde3" },
  { code: "Y3", name: "FFI", planned: 10, tier: "sde3" },
  { code: "Y4", name: "Performance", planned: 14, tier: "sde3" },
  { code: "Y5", name: "Testing & verification", planned: 14, tier: "sde3" },
  { code: "B1", name: "HTTP with axum", planned: 16, tier: "core" },
  { code: "B2", name: "Tower & middleware", planned: 12, tier: "core" },
  { code: "B3", name: "Databases with sqlx", planned: 14, tier: "core" },
  { code: "B4", name: "Networking & protocols", planned: 14, tier: "core" },
  { code: "B5", name: "Resilience", planned: 12, tier: "core" },
  { code: "B6", name: "Observability", planned: 12, tier: "core" },
  { code: "M1", name: "Idioms & patterns", planned: 12, tier: "core" },
  { code: "M2", name: "Machine coding", planned: 12, tier: "core" },
];

export const SECTION_NAMES: Record<Section, string> = {
  D: "Data Structures & Algorithms",
  L: "Rust Language",
  S: "Rust Standard Library",
  C: "Concurrency & Async",
  Y: "Systems Rust",
  B: "Backend Rust",
  M: "Design in Rust",
};

/** Which nav area each section belongs to. */
export const NAV_SECTIONS = {
  dsa: ["D"],
  rust: ["L", "S", "C", "Y"],
  build: ["B", "M"],
} as const satisfies Record<string, Section[]>;

export type NavArea = keyof typeof NAV_SECTIONS;

export const sectionOf = (code: string) => code[0] as Section;

/** One line per track: what interviewers probe. Written tracks show their own summary instead. */
export const BLURB: Record<string, string> = {
  D1: "entry API \u00b7 [u8; 26] counts \u00b7 get() vs [] \u00b7 total_cmp",
  D2: "bytes() \u00b7 checked_sub on usize \u00b7 monotonic VecDeque",
  D3: "Vec as a stack \u00b7 Option + ? on malformed input",
  D4: "partition_point \u00b7 binary_search_by \u00b7 BTreeMap::range",
  D5: "Option<Box<Node>> \u00b7 take() \u00b7 cursors \u00b7 index arenas",
  D6: "Rc<RefCell<TreeNode>> vs arenas \u00b7 iterators with lifetimes",
  D7: "BinaryHeap is a max-heap: Reverse<T>, Ord newtypes",
  D8: "sort_unstable_by_key \u00b7 sweep lines \u00b7 BTreeMap counts",
  D9: "index-based graphs \u00b7 union-find \u00b7 BinaryHeap",
  D10: "[Option<Box<Node>>; 26] \u00b7 get_or_insert_with \u00b7 bytes vs chars",
  D11: "&mut Vec push / recurse / pop \u00b7 bitmask pruning",
  D12: "rolling arrays \u00b7 owned memo keys \u00b7 recursive-closure pitfalls",
  D13: "count_ones \u00b7 wrapping_* and checked_* \u00b7 overflow in debug vs release",
  D14: "slab + index-linked lists \u00b7 injected clocks \u00b7 no Rc<RefCell> on hot paths",
  L1: "Whether you think in moves and drops, or reach for .clone() to make errors go away.",
  L2: "Whether you reason in aliasing and mutation rules instead of fighting the compiler.",
  L3: "Whether you can say why the compiler rejects code, not just add 'a until it compiles.",
  L4: "API taste: static vs dynamic dispatch, object safety, and when dyn is the right cost.",
  L5: "Bounds that say exactly what you need, and knowing what monomorphization costs.",
  L6: "Which Fn trait a closure gets, and returning closures without boxing by reflex.",
  L7: "Enums as state machines, let-else, and bindings that don't move by accident.",
  L8: "thiserror for libraries, anyhow for apps, and no unwrap on input you don't control.",
  L9: "Crate boundaries, features and semver: which changes break your users.",
  L10: "When a macro is warranted, hygiene, and reading someone else's macro_rules!.",
  S1: "Combinators over match, and keeping sentinels out of your APIs.",
  S2: "String vs &str, UTF-8 boundaries, and allocating only when you must.",
  S3: "The cost model: capacity, reallocation, and slices as views.",
  S4: "The entry API, BTreeMap ranges, and Hash + Eq consistency.",
  S5: "BinaryHeap ordering, Reverse<T>, and VecDeque's ring buffer.",
  S6: "Lazy chains, IntoIterator for references, and writing your own adapters.",
  S7: "Picking the cheapest correct tool: &T, Box, Rc, Arc, Arc<Mutex<T>>.",
  S8: "Which traits to derive, which to write by hand, and what Borrow is for.",
  S9: "Generic Read / Write code you can test without files.",
  S10: "Instant vs SystemTime, and making time injectable for tests.",
  S11: "size_of, niche optimisation, MaybeUninit: what std does under the hood.",
  C1: "Which primitive and which lock scope, not just 'add a Mutex'.",
  C2: "Channels, actors and shutdown without losing work.",
  C3: "Which Ordering and why, and when lock-free is not worth it.",
  C4: "The executor model: cooperative scheduling, why blocking is catastrophic, cancellation at .await.",
  C5: "Future, Waker and Pin: what .await compiles into.",
  C6: "When parallelism helps, and when false sharing eats the gain.",
  Y1: "Layout, padding and allocation costs you can reason about without a profiler.",
  Y2: "Stating the safety contract you opt into, and writing // SAFETY: unprompted.",
  Y3: "Ownership across the C boundary: who allocates and who frees.",
  Y4: "Measure first, then fix: allocation, locality, inlining.",
  Y5: "Tests that find bugs: property tests, Miri, loom.",
  B1: "Extractors, state and error mapping in axum.",
  B2: "Service and Layer: how every middleware in the ecosystem works.",
  B3: "Transactions, pools, and turning database errors into status codes.",
  B4: "Framing, timeouts and parsers that survive hostile input.",
  B5: "Retries, idempotency and circuit breakers that don't make outages worse.",
  B6: "Tracing across .await, metrics, and shutting down cleanly.",
  M1: "Rust-shaped patterns: builders, newtypes, RAII, typestate.",
  M2: "A working, tested design in 60 to 90 minutes, then the follow-ups.",
};

/** DSA tracks in the order CURRICULUM.md recommends (graphs before heaps and greedy). */
export const DSA_ORDER = ["D1", "D2", "D3", "D4", "D5", "D6", "D9", "D7", "D8", "D12", "D10", "D11", "D13", "D14"];
