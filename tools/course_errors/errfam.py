# Error families: id -> dict(code, title, bad, good, meaning, fixes)
FAM = {}
def fam(id_, code, title, bad, good, meaning, fixes):
    FAM[id_] = dict(code=code, title=title, bad=bad.strip("\n"), good=good.strip("\n"), meaning=meaning, fixes=fixes)

fam("moved","E0382","Use of a moved value",
'''struct Frame { data: Vec<u8> }

fn main() {
    let frame = Frame { data: vec![0; 4096] };
    let handle = std::thread::spawn(move || frame.data.len());
    println!("{}", frame.data.len());
    handle.join().unwrap();
}''',
'''use std::sync::Arc;

struct Frame { data: Vec<u8> }

fn main() {
    let frame = Arc::new(Frame { data: vec![0; 4096] });
    let mine = Arc::clone(&frame);
    let handle = std::thread::spawn(move || mine.data.len());
    println!("{}", frame.data.len());
    handle.join().unwrap();
}''',
"A value has one owner. Passing it somewhere by value (a function call, a `move` closure, an assignment) gives the ownership away, and the old name is no longer usable.",
["Borrow instead of moving: pass `&frame` where the callee only reads.","Share ownership when two places really need it: `Arc` across threads, `Rc` on one thread, and clone the `Arc`, not the data.","Clone the value if a copy is what you mean (and cheap enough)."])

fam("two_mut","E0499","Two mutable borrows at once",
'''fn main() {
    let mut pages = vec![1u32, 2, 3];
    let first = &mut pages[0];
    let second = &mut pages[1];
    *first += *second;
}''',
'''fn main() {
    let mut pages = vec![1u32, 2, 3];
    let (left, right) = pages.split_at_mut(1);
    left[0] += right[0];
}''',
"At any moment there can be many readers or exactly one writer of a value. Two `&mut` into the same `Vec` (even to different elements) break that, because the compiler cannot see that the indexes differ.",
["Split the data: `split_at_mut`, `iter_mut`, `swap`, or separate fields instead of one big struct.","Finish with the first borrow before you start the second.","Keep indexes or ids instead of references, and look them up when you need them."])

fam("read_while_write","E0502","Mutating something you are reading",
'''use std::collections::HashMap;

fn main() {
    let mut frames: HashMap<u32, u32> = HashMap::new();
    frames.insert(1, 10);
    for (page, _frame) in frames.iter() {
        frames.remove(page);
    }
}''',
'''use std::collections::HashMap;

fn main() {
    let mut frames: HashMap<u32, u32> = HashMap::new();
    frames.insert(1, 10);
    let pages: Vec<u32> = frames.keys().copied().collect();
    for page in pages {
        frames.remove(&page);
    }
}''',
"A loop over a collection holds a shared borrow of it until the loop ends; changing the collection inside the loop needs a mutable borrow at the same time.",
["Collect what you need first (keys, ids), end the borrow, then change the collection.","Use `retain` or `drain` when the loop is really 'remove what matches'.","Mark what to change in the loop and apply it after."])

fam("move_out_of_borrow","E0507","Cannot move out of a borrowed place",
'''struct Node { next: Option<Box<Node>> }
struct List { head: Option<Box<Node>> }

impl List {
    fn pop_node(&mut self) -> Option<Box<Node>> {
        let head = self.head;
        head
    }
}

fn main() {}''',
'''struct Node { next: Option<Box<Node>> }
struct List { head: Option<Box<Node>> }

impl List {
    fn pop_node(&mut self) -> Option<Box<Node>> {
        let mut head = self.head.take()?;
        self.head = head.next.take();
        Some(head)
    }
}

fn main() {}''',
"You only have `&mut self`, not ownership of `self`, so you cannot take a field out and leave a hole. The compiler will not let a struct be half-empty.",
["`Option::take()` swaps `None` in and gives you the old value.","`std::mem::replace(&mut self.x, new)` and `mem::take` do the same for any type.","Borrow the field (`as_ref`, `as_mut`) when you only need to look."])

fam("not_mut","E0596","Cannot borrow as mutable",
'''struct Pool { free: Vec<u32> }

impl Pool {
    fn release(&self, frame: u32) {
        self.free.push(frame);
    }
}

fn main() {}''',
'''use std::sync::Mutex;

struct Pool { free: Mutex<Vec<u32>> }

impl Pool {
    fn release(&self, frame: u32) {
        self.free.lock().unwrap().push(frame);
    }
}

fn main() {}''',
"A method that takes `&self` promises not to change the value. Changing a field needs `&mut self`, or a type that allows change through a shared reference.",
["Take `&mut self` if the caller can hold the only reference.","When many threads must share the value (`&self` everywhere), put the changing part behind a `Mutex`, an `RwLock` or an atomic: that is interior mutability.","Declare the variable `let mut` if the error is about a local."])

fam("not_send","E0277","Cannot be sent between threads safely",
'''use std::rc::Rc;

fn main() {
    let shared = Rc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}''',
'''use std::sync::Arc;

fn main() {
    let shared = Arc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}''',
"A value that goes to another thread must be `Send`; a value shared by reference between threads must be `Sync`. `Rc`, `RefCell` and raw pointers are neither, because their bookkeeping is not thread safe.",
["Use `Arc` for shared ownership across threads and `Mutex`/`RwLock` for shared changes.","Read the *last* lines of the message: they say which field or type inside your struct is the one that is not `Send`.","A `MutexGuard` is not `Send` either: finish with it before the thread boundary."])

fam("closure_outlives","E0373","The closure may outlive the current function",
'''fn main() {
    let name = String::from("worker");
    let h = std::thread::spawn(|| println!("{}", name));
    h.join().unwrap();
}''',
'''fn main() {
    let name = String::from("worker");
    let h = std::thread::spawn(move || println!("{}", name));
    h.join().unwrap();
}''',
"`thread::spawn` may keep the closure running after the function that created it has returned, so the closure may not borrow from the function's variables.",
["Add `move` so the closure owns what it uses (clone an `Arc` first if you need it elsewhere too).","If the threads are all joined before the function ends, use `thread::scope`: its threads may borrow.","Pass the data in through a channel instead of capturing it."])

fam("missing_lifetime","E0106","Missing lifetime specifier",
'''struct Page { data: [u8; 8] }

struct Guard {
    page: &Page,
}

fn main() {}''',
'''struct Page { data: [u8; 8] }

struct Guard<'a> {
    page: &'a Page,
}

fn main() {}''',
"A struct that holds a reference has to say how long the reference is valid, so the compiler can check that the struct never outlives what it points at. The name `'a` ties the two together.",
["Add the lifetime parameter to the struct and every `impl` that mentions it.","Own the data instead (`Arc<Page>`, an id) when the borrow makes the type hard to use: a guard that must be stored in a `Vec` or sent to a thread usually wants ownership.","Remember: the lifetime is a promise you must keep, not a way to make the compiler stop."])

fam("short_lived","E0597","Borrowed value does not live long enough",
'''struct Pool { pages: Vec<u8> }
struct Guard<'a> { pool: &'a Pool }

fn main() {
    let guard;
    {
        let pool = Pool { pages: vec![0; 8] };
        guard = Guard { pool: &pool };
    }
    println!("{}", guard.pool.pages.len());
}''',
'''struct Pool { pages: Vec<u8> }
struct Guard<'a> { pool: &'a Pool }

fn main() {
    let pool = Pool { pages: vec![0; 8] };
    let guard = Guard { pool: &pool };
    println!("{}", guard.pool.pages.len());
}''',
"A reference cannot outlive the thing it points to. Here the pool is dropped at the end of the inner block, while the guard that points at it is used after.",
["Declare the owner first (earlier = lives longer) and the borrower after it.","Return owned data (a clone, an `Arc`) instead of a reference to a local.","If a guard must outlive its creator's scope, make it own what it needs."])

fam("mismatched","E0308","Mismatched types",
'''struct PageId(i32);

fn offset(page: PageId, page_size: usize) -> u64 {
    page.0 * page_size
}

fn main() {}''',
'''struct PageId(i32);

fn offset(page: PageId, page_size: usize) -> u64 {
    page.0 as u64 * page_size as u64
}

fn main() {}''',
"Rust never converts between integer types behind your back: `i32`, `usize` and `u64` are three different types, and so is a newtype around one of them.",
["Convert on purpose: `as` for a plain cast, `u64::from(x)` when it cannot fail, `usize::try_from(x)?` when it can.","Decide one type per quantity (an offset is `u64`, a length is `usize`) and convert at the edges.","Check for a sign: converting a negative `i32` with `as u64` gives a huge number."])

fam("no_method","E0599","No method named … found",
'''use std::fs::File;

fn main() {
    let f = File::open("db").unwrap();
    let mut buf = [0u8; 8];
    f.read_at(&mut buf, 0).unwrap();
}''',
'''use std::fs::File;
use std::os::unix::fs::FileExt;

fn main() {
    let f = File::open("db").unwrap();
    let mut buf = [0u8; 8];
    f.read_at(&mut buf, 0).unwrap();
}''',
"The method exists, but it belongs to a trait, and a trait's methods can only be called when the trait is in scope. The message usually says which `use` to add.",
["Read the `help:` line: it names the trait to import.","If the method really does not exist for your type, check the type: you may be calling it on an `Option`, a `&&T` or a wrapper.","Check the feature or platform: `FileExt` is in `std::os::unix`."])

fam("no_eq","E0369","Binary operation cannot be applied",
'''struct Rid { page: u32, slot: u32 }

fn main() {
    let a = Rid { page: 1, slot: 2 };
    let b = Rid { page: 1, slot: 2 };
    println!("{}", a == b);
}''',
'''#[derive(PartialEq)]
struct Rid { page: u32, slot: u32 }

fn main() {
    let a = Rid { page: 1, slot: 2 };
    let b = Rid { page: 1, slot: 2 };
    println!("{}", a == b);
}''',
"`==`, `<`, `+` and the like are methods of traits (`PartialEq`, `PartialOrd`, `Add`). A type has them only if it implements them; a struct starts with none.",
["`#[derive(PartialEq, Eq, Hash, Clone, Copy, Debug)]` for the usual set; add `PartialOrd, Ord` for ordering.","Floats are `PartialOrd` but not `Ord` (NaN): sort with `total_cmp` or a wrapper.","Implement the trait by hand when equality means something other than 'all fields equal'."])

fam("non_exhaustive","E0004","Non-exhaustive patterns",
'''enum Mode { IntentionShared, Shared, Exclusive }

fn is_write(m: Mode) -> bool {
    match m {
        Mode::Exclusive => true,
        Mode::Shared => false,
    }
}

fn main() {}''',
'''enum Mode { IntentionShared, Shared, Exclusive }

fn is_write(m: Mode) -> bool {
    match m {
        Mode::Exclusive => true,
        Mode::Shared | Mode::IntentionShared => false,
    }
}

fn main() {}''',
"A `match` must cover every possible value. The message names the one you forgot, which is exactly why enums are good for states: add a variant and the compiler lists every `match` to update.",
["Add the arm the message names.","A catch-all `_ =>` silences the error now and hides the next forgotten variant: prefer it only when 'everything else' really is one case.","Combine arms with `|` when they do the same thing."])

fam("type_annot","E0282","Type annotations needed",
'''fn main() {
    let ids = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
    println!("{}", ids.len());
}''',
'''fn main() {
    let ids: Vec<u32> = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
    println!("{}", ids.len());
}''',
"`collect`, `parse`, `into` and `Default::default()` can produce many types, and nothing says which one you want.",
["Annotate the variable (`let ids: Vec<u32> = …`).","Or use the turbofish: `.collect::<Vec<u32>>()`, `.parse::<u32>()`.","The annotation is often the best documentation of what you meant."])

fam("temp_dropped","E0716","Temporary value dropped while borrowed",
'''use std::sync::Mutex;

fn main() {
    let state = Mutex::new(vec![1, 2, 3]);
    let first = state.lock().unwrap().first().unwrap();
    println!("{}", first);
}''',
'''use std::sync::Mutex;

fn main() {
    let state = Mutex::new(vec![1, 2, 3]);
    let first = *state.lock().unwrap().first().unwrap();
    println!("{}", first);
}''',
"`state.lock().unwrap()` creates a guard that lives only until the end of the statement, and you kept a reference into it. The reference would point into a lock that was already released.",
["Copy or clone the value out inside the statement (`let first = *state.lock().unwrap().first().unwrap();`).","Or give the guard a name (`let guard = state.lock().unwrap();`) so it lives as long as you need it.","This error is the compiler protecting you from reading data without the lock."])

fam("immutable_twice","E0384","Cannot assign twice to an immutable variable",
'''fn main() {
    let pins = 0;
    pins += 1;
    println!("{}", pins);
}''',
'''fn main() {
    let mut pins = 0;
    pins += 1;
    println!("{}", pins);
}''',
"Variables are immutable unless declared `mut`. It is a feature: when you see `let mut`, you know to look for the change.",
["Add `mut` if the variable is meant to change.","Often a new binding is clearer: `let pins = pins + 1;`.","If a struct field must change, the method needs `&mut self` (see the 'cannot borrow as mutable' error)."])

fam("unresolved","E0432","Unresolved import",
'''use bustub::storage::disk::disk_scheduler::DiskScheduler;

fn main() {}''',
'''use std::collections::HashMap;

fn main() {
    let _m: HashMap<u32, u32> = HashMap::new();
}''',
"The path in a `use` does not exist. In this course the usual cause is a file that is not there yet: later modules' files appear in your repo when you reach them.",
["Check the spelling and the module path against the files under `src/`.","If it belongs to a later module, you do not need it yet: the stage you are on does not use it.","After `anneal course update`, new files appear; a stale `target/` rarely matters, but `cargo clean` rules it out."])

fam("borrow_moved","E0505","Cannot move out while borrowed",
'''fn consume(v: Vec<u8>) -> usize { v.len() }

fn main() {
    let page = vec![0u8; 8];
    let first = &page[0];
    let n = consume(page);
    println!("{} {}", first, n);
}''',
'''fn consume(v: Vec<u8>) -> usize { v.len() }

fn main() {
    let page = vec![0u8; 8];
    let first = page[0];
    let n = consume(page);
    println!("{} {}", first, n);
}''',
"You gave away a value while a reference to it was still going to be used. The reference would be left pointing at something that no longer belongs to you.",
["Finish using the reference before you move the value.","Copy the small thing you need (`page[0]`) instead of holding a reference.","Pass a reference to the function if it only needs to read."])

fam("static_needed","E0521","Borrowed data escapes outside of the function",
'''struct Disk { name: String }

impl Disk {
    fn start(&self) {
        std::thread::spawn(move || println!("{}", self.name));
    }
}

fn main() {}''',
'''use std::sync::Arc;

struct Disk { name: String }

impl Disk {
    fn start(self: &Arc<Self>) {
        let me = Arc::clone(self);
        std::thread::spawn(move || println!("{}", me.name));
    }
}

fn main() {}''',
"A spawned thread may run for ever, so everything it uses must be owned or `'static`. A `&self` is a borrow that ends when the caller says so.",
["Make the object shared (`Arc<Self>`) and clone the `Arc` into the thread.","Move what the thread needs into it (clone the name, take the channel).","Use `thread::scope` if the thread is joined before the method returns."])

fam("not_hash","E0599","The method exists, but its trait bounds were not satisfied",
'''use std::collections::HashMap;

#[derive(PartialEq)]
struct Key(f64);

fn main() {
    let mut m: HashMap<Key, u32> = HashMap::new();
    m.insert(Key(1.0), 1);
}''',
'''use std::collections::HashMap;

#[derive(PartialEq, Eq, Hash)]
struct Key(u64);

fn main() {
    let mut m: HashMap<Key, u32> = HashMap::new();
    m.insert(Key(1), 1);
}''',
"A generic function or type needs a capability (`Hash + Eq` for a `HashMap` key, `Ord` for a `BTreeMap` key or `sort`) and your type does not have it. The message ends with a `help:` naming the missing trait.",
["Derive or implement the trait. Floats have no `Eq`/`Hash`: store bits (`f64::to_bits`) or a fixed-point integer.","If you cannot change the type, wrap it in a newtype that has the trait.","Read the `required by a bound in …` note: it points at the exact generic that asked."])

fam("guard_across","E0382","A lock guard moved by `wait`",
'''use std::sync::{Condvar, Mutex};

fn main() {
    let m = Mutex::new(false);
    let cv = Condvar::new();
    let guard = m.lock().unwrap();
    let _ = cv.wait(guard);
    println!("{}", *guard);
}''',
'''use std::sync::{Condvar, Mutex};

fn main() {
    let m = Mutex::new(true);
    let cv = Condvar::new();
    let mut guard = m.lock().unwrap();
    while !*guard {
        guard = cv.wait(guard).unwrap();
    }
    println!("{}", *guard);
}''',
"`Condvar::wait` takes the guard by value (it releases the lock while sleeping) and gives a new guard back. The old guard variable was moved into the call.",
["Assign the result back: `guard = cv.wait(guard).unwrap();`.","Wait in a loop that re-checks the condition: wake-ups can be spurious.","`wait_while(guard, |state| …)` does the loop for you."])
