A challenge: no walkthrough, no hints, no solution. Solve it with what module 1a taught. It is extra practice and does not count towards the course.

## What to build

`MirroredDisk` in `src/storage/disk/mirrored_disk.rs`: a disk made of two other disks that keeps the same pages on both, so that one of them failing does not lose anything. It is a `DiskIo` like the others, so anything that takes a disk can take a mirror.

## Why

Real storage engines do not trust one device. Mirroring (RAID 1) is the simplest answer, and it is a good test of whether you understand what a disk promises: when a disk fails for a while and comes back, it has *missed* writes, and a naive mirror will happily read the old page from it. Getting that right is most of the exercise, and it uses the `DiskIo` seam from stage 1a-04.

## The contract

- Writes go to both disks. A write succeeds if at least one disk took it, and fails only if both failed.
- Reads return the latest successful write of the page (zeros if the page was never written or has been deleted), even while one disk is down and even if one disk missed some writes while it was down.
- At most one disk is down at any moment. When a disk comes back, the reads that follow are what bring it up to date.
- Deleting a page deletes it from both.

## What the tests check

- A mirror with both disks healthy behaves like one disk, and both copies hold every write.
- Reads work with either disk down; writes work with one disk down.
- A disk that missed a write never serves the old page after it comes back.
- A property over random sequences of writes, reads, deletes and disks going down and up, compared with a plain map of pages.

## Done when

All the `s1a_c1` tests pass.
