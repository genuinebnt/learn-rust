#!/bin/sh
# Installs the anneal CLI for this computer:  curl -fsSL __BASE__/install.sh | sh
set -eu

base="__BASE__"
os=$(uname -s)
arch=$(uname -m)
case "$os" in
    Darwin) os=macos ;;
    Linux) os=linux ;;
    *) echo "anneal: there is no build for $os (macOS and Linux only)" >&2; exit 1 ;;
esac
case "$arch" in
    arm64 | aarch64) arch=arm64 ;;
    x86_64 | amd64) arch=x64 ;;
    *) echo "anneal: there is no build for $arch" >&2; exit 1 ;;
esac

dir="${ANNEAL_INSTALL_DIR:-$HOME/.local/bin}"
mkdir -p "$dir"
tmp=$(mktemp "$dir/.anneal.XXXXXX")
trap 'rm -f "$tmp"' EXIT
if ! curl -fsSL "$base/downloads/anneal-$os-$arch" -o "$tmp"; then
    echo "anneal: could not download $base/downloads/anneal-$os-$arch" >&2
    exit 1
fi
chmod +x "$tmp"
mv "$tmp" "$dir/anneal"
trap - EXIT

echo "Installed $dir/anneal"
case ":$PATH:" in
    *":$dir:"*) ;;
    *) echo "Add it to your PATH:  export PATH=\"$dir:\$PATH\"" ;;
esac
cat <<MSG

Needs git, curl and a Rust toolchain (https://rustup.rs). Then:
  anneal course login $base
  anneal course restore        # your committed work, if you ran 'anneal course remote' on another laptop
  anneal course init bustub    # or start fresh
MSG
