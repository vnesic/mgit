#!/bin/bash
# Integration test script for mgit
# Tests mgit commands in a real multi-repo environment

# Don't exit on error - we want to run all tests
set +e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MGIT="python3 $SCRIPT_DIR/raw/main/mgit"
TEST_DIR=$(mktemp -d -t mgit-integration-test-XXXXXX)
PASSED=0
FAILED=0

echo "=========================================="
echo "mgit Integration Test Suite"
echo "=========================================="
echo "Test directory: $TEST_DIR"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up test directory..."
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Test result helpers
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Setup test repositories
setup_repos() {
    info "Setting up test repositories..."
    cd "$TEST_DIR"

    for i in 1 2 3; do
        mkdir -p "repo$i"
        cd "repo$i"
        git init -q
        git config user.name "Test User"
        git config user.email "test@example.com"
        echo "# Repo $i" > README.md
        git add README.md
        git commit -q -m "Initial commit"
        cd ..
    done

    pass "Setup 3 test repositories"
}

# Test 1: Repository Discovery
test_discovery() {
    info "Testing repository discovery..."
    cd "$TEST_DIR"

    output=$($MGIT status 2>&1)

    if echo "$output" | grep -q "Found 3 repositories"; then
        pass "Discovered all 3 repositories"
    else
        fail "Repository discovery (expected 3 repos)"
        echo "$output"
        return
    fi

    if echo "$output" | grep -q "project: repo1" && \
       echo "$output" | grep -q "project: repo2" && \
       echo "$output" | grep -q "project: repo3"; then
        pass "All repositories listed in status"
    else
        fail "Repository listing in status"
    fi
}

# Test 2: Status Command
test_status() {
    info "Testing status command..."
    cd "$TEST_DIR"

    # Test clean status
    output=$($MGIT status 2>&1)
    if echo "$output" | grep -q "(clean)"; then
        pass "Status shows clean repositories"
    else
        fail "Clean status detection"
    fi

    # Make repo1 dirty
    echo "new content" > repo1/test.txt

    # Test dirty status
    output=$($MGIT status --dirty 2>&1)
    if echo "$output" | grep -q "project: repo1"; then
        pass "Status --dirty detects modified repository"
    else
        fail "Dirty status detection"
    fi

    # Clean up
    rm repo1/test.txt
}

# Test 3: Log Command
test_log() {
    info "Testing log command..."
    cd "$TEST_DIR"

    output=$($MGIT log -- -n 1 --oneline 2>&1)

    if echo "$output" | grep -q "Initial commit"; then
        pass "Log command shows commits"
    else
        fail "Log command"
        echo "$output"
    fi
}

# Test 4: Diff Command
test_diff() {
    info "Testing diff command..."
    cd "$TEST_DIR"

    # Make a change
    echo "Modified content" >> repo1/README.md

    output=$($MGIT diff 2>&1)

    if echo "$output" | grep -q "Modified content"; then
        pass "Diff command shows changes"
    else
        fail "Diff command"
    fi

    # Revert change
    cd repo1
    git checkout README.md
    cd ..
}

# Test 5: Commit Command
test_commit() {
    info "Testing commit command..."
    cd "$TEST_DIR"

    # Make changes in all repos
    for i in 1 2 3; do
        echo "test content" > "repo$i/test.txt"
    done

    # Commit with --add
    output=$($MGIT commit -m "Test commit" --add 2>&1)

    if echo "$output" | grep -q "Committed: 3 repositories"; then
        pass "Commit command commits to all repos"
    else
        fail "Commit command"
        echo "$output"
        return
    fi

    # Verify commits
    cd repo1
    if git log -1 --oneline | grep -q "Test commit"; then
        pass "Commit message is correct"
    else
        fail "Commit message verification"
    fi
    cd ..
}

# Test 6: Chain Commits
test_chain_commits() {
    info "Testing chain commits..."
    cd "$TEST_DIR"

    # Make changes
    for i in 1 2 3; do
        echo "chain test" > "repo$i/chain.txt"
    done

    # Commit with chain
    output=$($MGIT commit -m "Chain test" --add --chain 2>&1)

    if echo "$output" | grep -q "chain start"; then
        pass "Chain commit creates chain start"
    else
        fail "Chain commit start"
        echo "$output"
        return
    fi

    if echo "$output" | grep -q "chained from"; then
        pass "Chain commit links repositories"
    else
        fail "Chain commit linking"
    fi

    # Verify chain info in commit message
    cd repo2
    if git log -1 --format=%B | grep -q "Chained-From:"; then
        pass "Chain info in commit message"
    else
        fail "Chain info verification"
    fi
    cd ..
}

# Test 7: Exec Command
test_exec() {
    info "Testing exec command..."
    cd "$TEST_DIR"

    output=$($MGIT exec -- branch 2>&1)

    if echo "$output" | grep -q "project: repo1" && \
       echo "$output" | grep -q "project: repo2"; then
        pass "Exec command runs in all repos"
    else
        fail "Exec command"
    fi
}

# Test 8: Parallel Execution
test_parallel() {
    info "Testing parallel execution..."
    cd "$TEST_DIR"

    output=$($MGIT -j8 status 2>&1)

    if echo "$output" | grep -q "Using 8 parallel jobs"; then
        pass "Parallel execution with -j flag"
    else
        fail "Parallel execution"
    fi
}

# Test 9: Dry Run
test_dry_run() {
    info "Testing dry run mode..."
    cd "$TEST_DIR"

    # Make a change
    echo "dry run test" > repo1/dryrun.txt

    output=$($MGIT --dry-run commit -m "Dry run" --add 2>&1)

    if echo "$output" | grep -q "DRY RUN"; then
        pass "Dry run mode doesn't execute"
    else
        fail "Dry run mode"
        return
    fi

    # Verify no commit was made
    cd repo1
    if ! git log -1 --oneline | grep -q "Dry run"; then
        pass "Dry run doesn't create commits"
    else
        fail "Dry run verification (commit was made)"
    fi
    cd ..

    # Clean up
    rm repo1/dryrun.txt
}

# Test 10: Link File
test_link_file() {
    info "Testing link file creation..."
    cd "$TEST_DIR"

    # Make changes
    for i in 1 2 3; do
        echo "link test" > "repo$i/link.txt"
    done

    # Commit with link file
    $MGIT commit -m "Link test" --add --link-file commits.txt >/dev/null 2>&1

    if [ -f commits.txt ]; then
        pass "Link file created"
    else
        fail "Link file creation"
        return
    fi

    if grep -q "repo1" commits.txt && \
       grep -q "repo2" commits.txt && \
       grep -E -q "[0-9a-f]{40}" commits.txt; then
        pass "Link file contains correct info"
    else
        fail "Link file content"
    fi
}

# Test 11: Checkout Command
test_checkout() {
    info "Testing checkout command..."
    cd "$TEST_DIR"

    # Create branches
    for i in 1 2 3; do
        cd "repo$i"
        git branch test-branch
        cd ..
    done

    # Checkout branch
    $MGIT checkout test-branch >/dev/null 2>&1

    # Verify
    cd repo1
    current_branch=$(git branch --show-current)
    cd ..

    if [ "$current_branch" = "test-branch" ]; then
        pass "Checkout switches branches"
    else
        fail "Checkout command"
    fi

    # Switch back
    $MGIT checkout - >/dev/null 2>&1
}

# Test 12: Error Handling
test_error_handling() {
    info "Testing error handling..."
    cd "$TEST_DIR"

    # Test invalid command
    if ! $MGIT invalid-command >/dev/null 2>&1; then
        pass "Invalid command returns error"
    else
        fail "Invalid command handling"
    fi

    # Test missing required argument
    if ! $MGIT commit >/dev/null 2>&1; then
        pass "Missing required argument returns error"
    else
        fail "Missing argument handling"
    fi
}

# Run all tests
echo "Running tests..."
echo ""

setup_repos
echo ""

test_discovery
test_status
test_log
test_diff
test_commit
test_chain_commits
test_exec
test_parallel
test_dry_run
test_link_file
test_checkout
test_error_handling

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
