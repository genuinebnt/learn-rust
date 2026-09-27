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
  { code: "D6", name: "Trees & BSTs", planned: 24, tier: "core" },
  { code: "D7", name: "Heaps & priority queues", planned: 13, tier: "core" },
  { code: "D8", name: "Intervals & greedy", planned: 16, tier: "core" },
  { code: "D9", name: "Graphs", planned: 35, tier: "core" },
  { code: "D10", name: "Tries & strings", planned: 15, tier: "core" },
  { code: "D11", name: "Backtracking", planned: 16, tier: "core" },
  { code: "D12", name: "Dynamic programming", planned: 35, tier: "core" },
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
