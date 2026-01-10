# mgit Quick Start Guide

Get up and running with `mgit` in 5 minutes.

---

## 1. Install

```bash
sudo dpkg -i mgit_1.1.0_all.deb
```

**Verify:**
```bash
mgit --help
```

---

## 2. Navigate to Your Workspace

```bash
# AOSP
cd ~/aosp

# Microservices
cd ~/services

# Any multi-repo folder
cd ~/your-project
```

---

## 3. First Commands

### Check Status

```bash
# All repos (parallel with 8 jobs)
mgit status -j8
```

**Output:**
```
Scanning for Git repositories from /home/user/project...
Found 47 repositories.
Using 8 parallel jobs for execution.

project: frameworks/base
M  core/java/android/app/Activity.java

project: vendor/hardware
?? new_feature.cpp

[Processed 47 repos in 2.14s using 8 jobs]
```

### Show Only Dirty Repos

```bash
mgit status --dirty -j8
```

---

## 4. Common Operations

### Fetch All Repos

```bash
mgit exec -- fetch --all -j16
```

**Time:** ~18s for 50 repos (vs ~125s sequential)

### Show Recent Commits

```bash
mgit log --since="yesterday" --oneline -j8
```

### Show Changes

```bash
mgit diff -j8
```

---

## 5. Commit Across All Repos

```bash
# Commit all changes with same message
mgit commit -m "Update dependencies" --add --push
```

**What happens:**
1. Stages all changes in dirty repos
2. Creates commit with same message
3. Pushes to remote
4. Shows commit SHA for each repo

**Output:**
```
Found 3 repositories with changes.

project: frameworks/base
  ✓ Committed: a1b2c3d4
  ✓ Pushed

project: vendor/hardware
  ✓ Committed: e5f6g7h8
  ✓ Pushed

============================================================
Committed: 2 repositories
```

---

## 6. Performance Comparison

Try it yourself:

```bash
# Sequential (slow)
time mgit status --dirty -j1

# Parallel (fast)
time mgit status --dirty -j8
```

**Result:** 4-6x faster with `-j8`!

---

## Quick Reference

### Essential Commands

```bash
# Status
mgit status --dirty -j8

# Fetch
mgit exec -- fetch --all -j16

# Log
mgit log -n 5 --oneline -j8

# Diff
mgit diff -j8

# Commit
mgit commit -m "Message" --add --push

# Checkout
mgit checkout develop -j8

# Any git command
mgit exec -- branch -vv -j8
```

### Choosing -j Value

```bash
< 20 repos:    -j4
20-100 repos:  -j8   ← Start here
100-200 repos: -j16
200+ repos:    -j32
```

---

## Typical Workflows

### Morning Check

```bash
cd ~/project
mgit status --dirty -j8
mgit log --since="yesterday" --oneline -j8
```

### Sync All Repos

```bash
mgit exec -- fetch origin -j16
mgit exec -- pull --rebase -j12
```

### Release Snapshot

```bash
mgit commit -m "Release v2.1.0" --add \
  --link-file releases/v2.1.0.txt \
  --push
```

---

## Tips

### 1. Create Aliases

Add to `~/.bashrc`:

```bash
alias ms='mgit status --dirty -j8'
alias mf='mgit exec -- fetch --all -j16'
alias ml='mgit log -n 5 --oneline -j8'
```

Usage:
```bash
ms   # Quick status
mf   # Quick fetch
ml   # Quick log
```

### 2. Use Dry Run

Before destructive operations:

```bash
mgit --dry-run commit -m "Test" --add --push
```

### 3. Check Before Commit

```bash
mgit status --dirty -j8
mgit diff -j8
mgit commit -m "Update" --add
```

---

## Next Steps

### Read Full Documentation

```bash
man mgit
cat /usr/share/doc/mgit/README.md
```

### Learn Advanced Features

- **Link files:** Track multi-repo changes
- **Meta repos:** Maintain release history
- **Custom skip dirs:** Filter discovery
- **Performance tuning:** Optimize -j values

See: `/usr/share/doc/mgit/USAGE_EXAMPLES.md`

---

## Troubleshooting

### Command not found

```bash
which mgit
export PATH="/usr/local/bin:$PATH"
```

### No repos found

```bash
pwd  # Check you're in the right directory
find . -name .git -type d  # List git repos
```

### -j flag not working

```bash
mgit --help | grep jobs  # Verify v1.1.0
sudo dpkg -i mgit_1.1.0_all.deb  # Reinstall if needed
```

---

## Help

- **GitHub:** https://github.com/vnesic/mgit
- **Issues:** https://github.com/vnesic/mgit/issues
- **Email:** vladimirs.nesic@gmail.com

---

## Summary

1. **Install:** `sudo dpkg -i mgit_1.1.0_all.deb`
2. **Navigate:** `cd ~/your-project`
3. **Run:** `mgit status --dirty -j8`
4. **Enjoy:** 4-6x faster operations!

🚀 **You're ready to go!**
