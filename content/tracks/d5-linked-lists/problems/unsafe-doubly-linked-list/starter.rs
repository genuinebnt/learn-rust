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

    pub fn push_front(&mut self, val: i32) {
        todo!()
    }

    pub fn push_back(&mut self, val: i32) {
        todo!()
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        todo!()
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
        todo!()
    }
}
