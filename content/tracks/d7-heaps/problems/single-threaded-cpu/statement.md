`tasks[i] = (enqueue_time, processing_time)`. A single CPU runs tasks one at a time, to completion:

- when it's free and tasks are waiting, it starts the one with the shortest processing time, breaking ties by
  smaller index;
- when it's free and nothing is waiting, it idles until the next task arrives;
- a task whose enqueue time equals the moment the CPU becomes free is already waiting.

Return the indices in the order the CPU runs them.
