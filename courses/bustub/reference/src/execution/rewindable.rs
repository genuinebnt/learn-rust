//! An iterator that can go back to a marked position.

use std::collections::VecDeque;

pub struct Rewindable<I: Iterator> {
    // @begin 3e-c5
    inner: I,
    /// Items read from `inner` since the mark, kept for replay.
    since_mark: Vec<I::Item>,
    /// Items waiting to be replayed (front first) after a reset.
    replay: VecDeque<I::Item>,
    marked: bool,
    //~ _rewind: std::marker::PhantomData<I>,
    // @end
}

impl<I: Iterator> Rewindable<I>
where
    I::Item: Clone,
{
    pub fn new(inner: I) -> Rewindable<I> {
        // @begin 3e-c5
        Rewindable { inner, since_mark: Vec::new(), replay: VecDeque::new(), marked: false }
        //~ todo!("3e-c5: wrap the iterator, nothing marked")
        // @end
    }

    pub fn mark(&mut self) {
        // @begin 3e-c5
        // what is still waiting to be replayed is "after the mark" too: it stays buffered
        self.since_mark = self.replay.iter().cloned().collect();
        self.marked = true;
        //~ todo!("3e-c5: forget what was read before this point, keep what is yet to be replayed")
        // @end
    }

    pub fn reset(&mut self) {
        // @begin 3e-c5
        if self.marked {
            self.replay = self.since_mark.iter().cloned().collect();
        }
        //~ todo!("3e-c5: replay everything since the mark")
        // @end
    }

    /// How many items are being held for a possible reset.
    pub fn buffered(&self) -> usize {
        // @begin 3e-c5
        self.since_mark.len()
        //~ todo!("3e-c5: how many items are kept")
        // @end
    }
}

impl<I: Iterator> Iterator for Rewindable<I>
where
    I::Item: Clone,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        // @begin 3e-c5
        let item = match self.replay.pop_front() {
            Some(x) => x,
            None => {
                let x = self.inner.next()?;
                if self.marked {
                    self.since_mark.push(x.clone());
                }
                return Some(x);
            }
        };
        Some(item)
        //~ todo!("3e-c5: replayed items first, then the underlying iterator (keeping what is read since the mark)")
        // @end
    }
}
