# mgit - Multi-Repository Git Tool

**Parallel execution for multi-repo workflows. 4-6x faster than sequential operations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/vnesic/mgit)

Multi-repository Git operations tool with parallel execution support. Perfect for AOSP development, microservices, and managing multiple independent Git repositories.

**Author:** Vladimir Nesic  
**Email:** vladimirs.nesic@gmail.com  
**GitHub:** https://github.com/vnesic/mgit

---

## Features

- 🚀 **Parallel execution** - 4-6x faster with `-j` flag
- 📦 **Multi-repo commits** - Same message across all repositories
- 🔗 **Chain commits** - Daisy-chain commits with clickable URLs (NEW in v1.2.0)
- 🔍 **Smart discovery** - Automatic Git repository detection
- 📝 **Change tracking** - Link files for reproducible builds
- 🛡️ **Thread-safe** - Proper locking and grouped output
- ⚡ **Zero dependencies** - Just Python 3.6+ and Git

---

## Quick Start

### Installation

**Option 1: Install from this repository**

```bash
# Clone the repository
git clone https://github.com/vnesic/mgit.git
cd mgit

# Install the Debian package
sudo dpkg -i mgit_1.2.0_all.deb

# Verify installation
mgit --help
```

**Option 2: Direct download**

```bash
# Download the package directly
wget https://github.com/vnesic/mgit/raw/main/mgit_1.2.0_all.deb

# Install
sudo dpkg -i mgit_1.2.0_all.deb
```

**Option 3: Manual installation (script only)**

```bash
# Download just the script
wget https://github.com/vnesic/mgit/raw/main/raw/main/mgit
sudo cp mgit /usr/local/bin/
sudo chmod +x /usr/local/bin/mgit
```

### First Commands

```bash
# Navigate to your multi-repo workspace
cd ~/your-project

# Show status with parallel execution
mgit status --dirty -j8

# Fetch all repositories in parallel
mgit exec -- fetch --all -j16

# Commit all changes
mgit commit -m "Update dependencies" --add --push

# NEW: Chain commits with URLs (v1.2.0)
mgit commit -m "Implement feature X" --add --chain
```

---

## Performance

**With 50 repositories on an 8-core machine:**

| Command | Sequential | Parallel (-j8) | Speedup |
|---------|------------|----------------|---------|
| `status` | 12.3s | 2.1s | **5.9x** ⚡ |
| `exec -- fetch` | 124.8s | 18.9s | **6.6x** ⚡ |
| `log -n 5` | 18.7s | 2.9s | **6.4x** ⚡ |
| `diff` | 15.4s | 2.5s | **6.2x** ⚡ |

---

## Usage

### Basic Commands

```bash
# Status - show repository status
mgit status -j8                    # All repos
mgit status --dirty -j8            # Only dirty repos
mgit status --dirty --no-untracked -j8  # Ignore untracked

# Log - show commit history
mgit -j12 log -- -n 5 --oneline    # Last 5 commits
mgit -j8 log --since="yesterday"   # Recent commits

# Diff - show changes
mgit diff -j8                      # Unstaged changes
mgit diff --cached -j8             # Staged changes
mgit diff origin/main -j12         # Compare with branch

# Checkout - switch branches
mgit checkout develop -j8          # Checkout branch
mgit checkout v2.1.0 -j8          # Checkout tag

# Exec - run any git command
mgit exec -- fetch --all -j16      # Fetch all repos
mgit exec -- branch -vv -j8        # Show branches
mgit exec -- remote -v -j8         # Show remotes

# Commit - multi-repo commit
mgit commit -m "Fix bugs" --add --push
mgit commit -m "Release v2.1.0" --add \
  --link-file releases/v2.1.0.txt \
  --meta-repo .releases
```

### Choosing -j Value

```bash
< 20 repos:    mgit status -j4
20-100 repos:  mgit status -j8    # Good starting point
100-200 repos: mgit status -j16
200+ repos:    mgit status -j32

# Auto-detect CPU cores
mgit status -j$(nproc)
```

---

## Real-World Examples

### Daily Development Workflow

```bash
# Morning check
cd ~/your-project
mgit status --dirty -j8
mgit -j8 log --since="yesterday" --oneline

# Fetch updates
mgit exec -- fetch origin -j16

# End of day commit
mgit commit -m "WIP: Feature implementation" --add
```

### AOSP Development

```bash
cd ~/aosp

# Quick status (47 repos in ~2 seconds)
mgit status --dirty -j8

# Sync all repos
mgit exec -- pull --rebase -j12

# Create snapshot
mgit commit -m "AOSP sync $(date +%F)" --add \
  --link-file snapshots/aosp-$(date +%F).txt
```

### Release Management

```bash
# Create release with tracking
mgit commit -m "Release v2.1.0" --add \
  --link-file releases/v2.1.0-manifest.txt \
  --meta-repo .releases \
  --push

# Tag all repos
mgit exec -- tag -a v2.1.0 -m "Release v2.1.0" -j8
mgit exec -- push origin v2.1.0 -j16
```

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started guide
- **[CHEATSHEET.md](CHEATSHEET.md)** - Quick reference for all commands
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[MULTI_COMMIT_GUIDE.md](MULTI_COMMIT_GUIDE.md)** - Complete multi-repository commit guide
- **[CHAIN_COMMITS.md](CHAIN_COMMITS.md)** - Chain commits feature (NEW in v1.2.0)
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **Man page:** `man mgit` (after installation)
- **Full documentation:** `/usr/share/doc/mgit/` (after installation)

---

## Command Reference

### Global Options

```
-j, --jobs N        Number of parallel jobs (default: 4)
--skip-dir DIR      Additional directory to skip (repeatable)
--dry-run           Show what would be done without executing
-h, --help          Show help message
```

### Commands

```
status              Show repository status
  --dirty             Show only repositories with changes
  --no-untracked      Don't consider untracked files as dirty

log [args...]       Show commit logs (args passed to git log)
diff [args...]      Show differences (args passed to git diff)
checkout <ref>      Checkout a branch, tag, or commit
exec -- <cmd>       Execute arbitrary git command

commit              Commit changes in all dirty repositories
  -m MSG              Commit message (required)
  --add               Stage all changes before committing
  --amend             Amend the previous commit
  --no-verify         Bypass hooks
  --push              Push after commit
  --link-file PATH    Write repo→SHA mappings
  --meta-repo DIR     Maintain meta repository
```

---

## Tips & Tricks

### Create Shell Aliases

Add to `~/.bashrc`:

```bash
alias ms='mgit status --dirty -j8'
alias mf='mgit exec -- fetch --all -j16'
alias ml='mgit -j8 log -- -n 5 --oneline'
```

### Find Optimal -j Value

```bash
for j in 1 4 8 16; do
  echo "Testing -j$j:"
  time mgit status --dirty -j$j
done
```

---

## Troubleshooting

### Command not found

```bash
which mgit
export PATH="/usr/local/bin:$PATH"
```

### No repositories found

```bash
pwd  # Check directory
find . -name .git -type d
```

### -j flag not recognized

```bash
mgit --help | grep jobs
sudo dpkg -i mgit_1.1.0_all.deb  # Reinstall
```

---

## Support

- **GitHub Issues:** https://github.com/vnesic/mgit/issues
- **Email:** vladimirs.nesic@gmail.com

---

## License

MIT License - Copyright © 2026 Vladimir Nesic

See full license text in the repository.

---

## Changelog

### v1.1.0 (2026-01-10)

- ✨ Add parallel execution with `-j` flag
- ⚡ 4-6x performance improvement
- 📊 Progress indicators
- 🔒 Thread-safe implementation

### v1.0.0 (2026-01-10)

- 🎉 Initial release

---

**Get started:**

```bash
git clone https://github.com/vnesic/mgit.git
cd mgit
sudo dpkg -i mgit_1.1.0_all.deb
cd ~/your-project
mgit status --dirty -j8
```

🚀 **Happy coding!**
