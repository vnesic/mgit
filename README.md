# mgit - Multi-Repository Git Tool

**Parallel execution for multi-repo workflows. 4-6x faster than sequential operations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/vnesic/mgit)

**Author:** Vladimir Nesic  
**Email:** vladimirs.nesic@gmail.com  
**GitHub:** https://github.com/vnesic/mgit

---

## What is mgit?

`mgit` is a powerful command-line tool designed to manage multiple independent Git repositories simultaneously. It's perfect for AOSP development, microservices architectures, and any workflow involving many repos.

**Key Features:**
- 🚀 **Parallel execution** with `-j` flag - 4-6x faster!
- 📦 **Multi-repo commits** - Same message across all repos
- 🔍 **Smart discovery** - Automatically finds all Git repositories
- 🔗 **Change tracking** - Link files and meta-repos for releases
- 🛡️ **Thread-safe** - Proper locking and grouped output
- ⚡ **No dependencies** - Just Python 3.6+ and Git

---

## Quick Start

### Installation

```bash
# Download and install
sudo dpkg -i mgit_1.1.0_all.deb

# Verify installation
mgit --help
```

### First Commands

```bash
# Navigate to your multi-repo workspace
cd ~/your-project

# Show status of all repos (parallel)
mgit status -j8

# Show only dirty repos
mgit status --dirty -j8

# Commit all changes with same message
mgit commit -m "Update dependencies" --add --push
```

**That's it!** You're now running git operations across all repos in parallel.

---

## Performance

**With 50 repositories:**

| Command | Sequential | Parallel (-j8) | Speedup |
|---------|------------|----------------|---------|
| `status` | 12.3s | 2.1s | **5.9x** ⚡ |
| `exec -- fetch` | 124.8s | 18.9s | **6.6x** ⚡ |
| `log -n 5` | 18.7s | 2.9s | **6.4x** ⚡ |
| `diff` | 15.4s | 2.5s | **6.2x** ⚡ |

---

## Installation Methods

### Method 1: Debian Package (Recommended)

```bash
sudo dpkg -i mgit_1.1.0_all.deb
mgit --help
```

### Method 2: Manual

```bash
sudo cp mgit /usr/local/bin/
sudo chmod +x /usr/local/bin/mgit
```

### Method 3: User-Local (No sudo)

```bash
mkdir -p ~/.local/bin
cp mgit ~/.local/bin/
chmod +x ~/.local/bin/mgit
export PATH="$HOME/.local/bin:$PATH"
```

**Requirements:** Python 3.6+, Git 2.0+

---

## Usage

### Basic Commands

```bash
# Status
mgit status -j8                    # All repos
mgit status --dirty -j8            # Only dirty repos

# Log
mgit log -n 5 --oneline -j12       # Last 5 commits
mgit log --since="yesterday" -j8   # Recent commits

# Diff
mgit diff -j8                      # Show changes
mgit diff origin/main -j12         # Compare with branch

# Exec
mgit exec -- fetch --all -j16      # Fetch all repos
mgit exec -- branch -vv -j8        # Show branches

# Commit
mgit commit -m "Fix bugs" --add --push
```

### Choosing -j Value

```bash
< 20 repos:    mgit status -j4
20-100 repos:  mgit status -j8
100-200 repos: mgit status -j16
200+ repos:    mgit status -j32
```

---

## Real-World Examples

### Daily Workflow

```bash
# Morning check
mgit status --dirty -j8
mgit log --since="yesterday" --oneline -j8

# Fetch updates
mgit exec -- fetch origin -j16

# End of day commit
mgit commit -m "WIP: Feature" --add
```

### AOSP Development

```bash
cd ~/aosp

# Quick status (47 repos in ~2 seconds)
mgit status --dirty -j8

# Sync all repos
mgit exec -- pull --rebase -j12

# Create snapshot
mgit commit -m "AOSP sync" --add \
  --link-file snapshots/2026-01-10.txt
```

### Release Management

```bash
# Create release
mgit commit -m "Release v2.1.0" --add \
  --link-file releases/v2.1.0.txt \
  --meta-repo .releases \
  --push

# Tag all repos
mgit exec -- tag -a v2.1.0 -m "Release" -j8
mgit exec -- push origin v2.1.0 -j16
```

---

## Advanced Features

### Link Files - Track Multi-Repo Changes

```bash
mgit commit -m "Update HALs" --add \
  --link-file changes/hal-update.txt

# Creates: changes/hal-update.txt
# frameworks/base a1b2c3d4...
# vendor/hardware e5f6g7h8...
```

### Meta Repositories

```bash
mgit commit -m "Release v2.1.0" --add \
  --link-file releases/v2.1.0.txt \
  --meta-repo .releases

# .releases/ is now a git repo tracking all releases
```

### Dry Run

```bash
mgit --dry-run commit -m "Test" --add --push
# Shows what would happen without executing
```

---

## Command Reference

### Global Flags

```
-j, --jobs N        Number of parallel jobs (default: 4)
--skip-dir DIR      Skip directory (repeatable)
--dry-run           Preview without executing
-h, --help          Show help
```

### Commands

```
status              Show repository status
  --dirty             Only dirty repos
  --no-untracked      Ignore untracked files

log [args]          Show commit logs
diff [args]         Show differences  
checkout REF        Checkout branch/tag/commit
exec -- CMD         Run arbitrary git command

commit              Commit to all dirty repos
  -m MSG              Commit message (required)
  --add               Stage all changes
  --amend             Amend previous commit
  --no-verify         Skip hooks
  --push              Push after commit
  --link-file FILE    Track changes
  --meta-repo DIR     Meta repository
```

---

## Documentation

Included in package:

- **README.md** - This file
- **QUICKREF.md** - Quick reference
- **USAGE_EXAMPLES.md** - Real scenarios
- **PARALLEL_PERFORMANCE.md** - Performance guide
- **EDGE_CASES.md** - Edge case handling

```bash
man mgit
ls /usr/share/doc/mgit/
```

---

## Troubleshooting

### Command not found

```bash
which mgit
export PATH="/usr/local/bin:$PATH"
```

### Performance not improving

```bash
# Benchmark
for j in 1 4 8 16; do
  time mgit status -j$j
done
```

### No repos found

```bash
pwd  # Check directory
find . -name .git -type d
```

---

## Support

- **GitHub:** https://github.com/vnesic/mgit
- **Issues:** https://github.com/vnesic/mgit/issues  
- **Email:** vladimirs.nesic@gmail.com

---

## License

MIT License - Copyright © 2026 Vladimir Nesic

See LICENSE file for full text.

---

## Changelog

### v1.1.0 (2026-01-10)

- ✨ Parallel execution with `-j`
- ⚡ 4-6x faster
- 📊 Progress indicators
- 🔒 Thread-safe

### v1.0.0 (2026-01-10)

- 🎉 Initial release

---

**Get started now:**

```bash
sudo dpkg -i mgit_1.1.0_all.deb
cd ~/your-project
mgit status --dirty -j8
```

🚀 **Happy coding!**
