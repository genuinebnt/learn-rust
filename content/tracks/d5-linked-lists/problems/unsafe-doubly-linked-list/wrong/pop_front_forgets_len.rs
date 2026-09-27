use std::marker::PhantomData;
use std::ptr::NonNull;

struct Node {
    val: i32,
    prev: Option<NonNull<Node>>,
    next: Option<NonNull<Node>>,
}

/// A doubly linked list that owns its nodes through raw pointers.
pub struct LinkedList {
    head: Option<NonNull<Node>>,
    tail: Option<NonNull<Node>>,
    len: usize,
    /// Tells the compiler (and drop check) that we own `Box<Node>`s.
    _owns: PhantomData<Box<Node>>,
}

pub struct Iter<'a> {
    next: Option<NonNull<Node>>,
    _list: PhantomData<&'a Node>,
}

impl Default for LinkedList {
    fn default() -> Self {
        LinkedList { head: None, tail: None, len: 0, _owns: PhantomData }
    }
}

impl LinkedList {
    pub fn new() -> Self {
        Self::default()
    }

    fn alloc(val: i32, prev: Option<NonNull<Node>>, next: Option<NonNull<Node>>) -> NonNull<Node> {
        NonNull::from(Box::leak(Box::new(Node { val, prev, next })))
    }

    pub fn push_front(&mut self, val: i32) {
        let node = Self::alloc(val, None, self.head);
        match self.head {
            // SAFETY: `h` came from `alloc` and is owned by this list until popped; `&mut self` means no other access.
            Some(mut h) => unsafe { h.as_mut().prev = Some(node) },
            None => self.tail = Some(node),
        }
        self.head = Some(node);
        self.len += 1;
    }

    pub fn push_back(&mut self, val: i32) {
        let node = Self::alloc(val, self.tail, None);
        match self.tail {
            // SAFETY: as in push_front: a live node we own, accessed through `&mut self`.
            Some(mut t) => unsafe { t.as_mut().next = Some(node) },
            None => self.head = Some(node),
        }
        self.tail = Some(node);
        self.len += 1;
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        self.head.map(|h| {
            // SAFETY: `h` was created by `Box::leak` in `alloc` and is unlinked below, so it's freed exactly once.
            let node = unsafe { Box::from_raw(h.as_ptr()) };
            self.head = node.next;
            match self.head {
                // SAFETY: the new head is a live node we own.
                Some(mut n) => unsafe { n.as_mut().prev = None },
                None => self.tail = None,
            }
            node.val
        })
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        self.tail.map(|t| {
            // SAFETY: as in pop_front, mirrored.
            let node = unsafe { Box::from_raw(t.as_ptr()) };
            self.tail = node.prev;
            match self.tail {
                // SAFETY: the new tail is a live node we own.
                Some(mut p) => unsafe { p.as_mut().next = None },
                None => self.head = None,
            }
            self.len -= 1;
            node.val
        })
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn iter(&self) -> Iter<'_> {
        Iter { next: self.head, _list: PhantomData }
    }
}

impl<'a> Iterator for Iter<'a> {
    type Item = &'a i32;

    fn next(&mut self) -> Option<&'a i32> {
        self.next.map(|n| {
            // SAFETY: the list is borrowed for 'a, so no node can be popped or freed while this reference lives.
            let node = unsafe { &*n.as_ptr() };
            self.next = node.next;
            &node.val
        })
    }
}

impl Drop for LinkedList {
    fn drop(&mut self) {
        while self.pop_front().is_some() {}
    }
}
