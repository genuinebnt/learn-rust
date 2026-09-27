Implement a deque as a doubly linked list: `next` links are `Rc`, `prev` links are `Weak`, so nodes don't
keep each other alive. Popping must give back the value without cloning the node.
