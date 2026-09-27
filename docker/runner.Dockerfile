# Sandbox image for anneal-runner: stable rustc + clippy, nothing else.
# Runs are started with --network none, a read-only root filesystem and an
# unprivileged user, so cargo's home lives on a tmpfs.
FROM rust:1.98-slim

RUN rustup component add clippy \
    && rm -rf /usr/local/rustup/downloads /usr/local/rustup/tmp

ENV CARGO_HOME=/tmp/cargo-home \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=1 \
    RUSTC_BOOTSTRAP=1

WORKDIR /work
