Nodes are `Rc<RefCell<Node>>` and edges are undirected (each side lists the other). Return a deep copy of
the connected graph containing `start`: every copied node is new, and the copy has the same shape,
cycles and self-loops included.

```rust
pub struct Node { pub val: i32, pub neighbors: Vec<NodeRef> }
pub type NodeRef = Rc<RefCell<Node>>;
```
