#!/usr/bin/env python3
"""
Test suite for mgit - Multi-repository Git operations tool

Run with:
    python3 test_mgit.py
    python3 -m pytest test_mgit.py -v
"""

import os
import sys
import shutil
import tempfile
import subprocess
import unittest
from pathlib import Path


class TestMGitSetup(unittest.TestCase):
    """Setup and teardown for test repositories."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary directory with test git repositories."""
        cls.test_dir = tempfile.mkdtemp(prefix='mgit_test_')
        cls.mgit_script = Path(__file__).parent / 'raw' / 'main' / 'mgit'

        # Create test repository structure
        cls.repo_names = ['repo1', 'repo2', 'repo3']
        cls.repos = []

        for repo_name in cls.repo_names:
            repo_path = Path(cls.test_dir) / repo_name
            repo_path.mkdir()

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)

            # Create initial commit
            test_file = repo_path / 'README.md'
            test_file.write_text(f'# {repo_name}\n\nTest repository\n')
            subprocess.run(['git', 'add', 'README.md'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, check=True, capture_output=True)

            cls.repos.append(repo_path)

        print(f"\nTest directory: {cls.test_dir}")
        print(f"Test repos: {', '.join(cls.repo_names)}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test directory."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
            print(f"\nCleaned up: {cls.test_dir}")

    def run_mgit(self, *args, check=False):
        """Helper to run mgit command."""
        cmd = ['python3', str(self.mgit_script)] + list(args)
        result = subprocess.run(
            cmd,
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        if check and result.returncode != 0:
            print(f"STDERR: {result.stderr}")
        return result


class TestMGitDiscovery(TestMGitSetup):
    """Test repository discovery functionality."""

    def test_discovers_all_repos(self):
        """Test that mgit discovers all git repositories."""
        result = self.run_mgit('status')
        self.assertEqual(result.returncode, 0, f"mgit status failed: {result.stderr}")

        # Check that all repos are discovered
        for repo_name in self.repo_names:
            self.assertIn(f'project: {repo_name}', result.stdout,
                         f"Repository {repo_name} not discovered")

    def test_skip_directories(self):
        """Test that skip directories are honored."""
        # Create a directory that should be skipped
        skip_dir = Path(self.test_dir) / 'node_modules' / 'test_repo'
        skip_dir.mkdir(parents=True)
        subprocess.run(['git', 'init'], cwd=skip_dir, check=True, capture_output=True)

        result = self.run_mgit('status')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('node_modules/test_repo', result.stdout,
                        "Skip directory not honored")

        # Clean up
        shutil.rmtree(Path(self.test_dir) / 'node_modules')

    def test_custom_skip_directory(self):
        """Test custom skip directory option."""
        custom_dir = Path(self.test_dir) / 'custom' / 'test_repo'
        custom_dir.mkdir(parents=True)
        subprocess.run(['git', 'init'], cwd=custom_dir, check=True, capture_output=True)

        result = self.run_mgit('--skip-dir', 'custom', 'status')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('custom/test_repo', result.stdout)

        # Clean up
        shutil.rmtree(Path(self.test_dir) / 'custom')


class TestMGitStatus(TestMGitSetup):
    """Test status command."""

    def test_status_clean_repos(self):
        """Test status on clean repositories."""
        result = self.run_mgit('status')
        self.assertEqual(result.returncode, 0)

        for repo_name in self.repo_names:
            self.assertIn(f'project: {repo_name}', result.stdout)

    def test_status_dirty_only(self):
        """Test status --dirty flag."""
        # Make one repo dirty
        test_file = self.repos[0] / 'test.txt'
        test_file.write_text('new content')

        result = self.run_mgit('status', '--dirty')
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.repo_names[0], result.stdout)

        # Clean up
        test_file.unlink()

    def test_status_parallel_execution(self):
        """Test status with parallel execution."""
        result = self.run_mgit('-j8', 'status')
        self.assertEqual(result.returncode, 0)

        # Should mention using parallel jobs
        self.assertIn('8 parallel jobs', result.stderr)


class TestMGitLog(TestMGitSetup):
    """Test log command."""

    def test_log_basic(self):
        """Test basic log command."""
        result = self.run_mgit('log', '--', '-n', '1', '--oneline')
        self.assertEqual(result.returncode, 0)

        # Each repo should show its log
        for repo_name in self.repo_names:
            self.assertIn(f'project: {repo_name}', result.stdout)
            self.assertIn('Initial commit', result.stdout)

    def test_log_parallel(self):
        """Test log with parallel execution."""
        result = self.run_mgit('-j10', 'log', '--', '-n', '1', '--oneline')
        self.assertEqual(result.returncode, 0)
        self.assertIn('10 parallel jobs', result.stderr)


class TestMGitDiff(TestMGitSetup):
    """Test diff command."""

    def test_diff_no_changes(self):
        """Test diff with no changes."""
        result = self.run_mgit('diff')
        self.assertEqual(result.returncode, 0)

    def test_diff_with_changes(self):
        """Test diff with actual changes."""
        # Make changes in a repo
        test_file = self.repos[0] / 'README.md'
        original_content = test_file.read_text()
        test_file.write_text(original_content + '\nNew line\n')

        result = self.run_mgit('diff')
        self.assertEqual(result.returncode, 0)
        self.assertIn('New line', result.stdout)

        # Clean up
        test_file.write_text(original_content)


class TestMGitCommit(TestMGitSetup):
    """Test commit command."""

    def test_commit_with_changes(self):
        """Test committing changes."""
        # Make changes in all repos
        for repo in self.repos:
            test_file = repo / 'test.txt'
            test_file.write_text('test content')

        # Commit with --add
        result = self.run_mgit('commit', '-m', 'Test commit', '--add')
        self.assertEqual(result.returncode, 0, f"Commit failed: {result.stderr}")

        # Verify commits were made
        for repo in self.repos:
            log_result = subprocess.run(
                ['git', 'log', '-n', '1', '--oneline'],
                cwd=repo,
                capture_output=True,
                text=True
            )
            self.assertIn('Test commit', log_result.stdout)

    def test_commit_no_changes(self):
        """Test commit with no changes."""
        result = self.run_mgit('commit', '-m', 'No changes')
        self.assertEqual(result.returncode, 0)
        self.assertIn('No repositories with changes', result.stdout)

    def test_commit_chain(self):
        """Test chain commit functionality."""
        # Make changes in all repos
        for repo in self.repos:
            test_file = repo / f'chain_test_{repo.name}.txt'
            test_file.write_text('chain test')

        # Commit with chain
        result = self.run_mgit('commit', '-m', 'Chain test', '--add', '--chain')
        self.assertEqual(result.returncode, 0, f"Chain commit failed: {result.stderr}")

        # Verify chain info in commits
        # First repo should be chain start
        log_result = subprocess.run(
            ['git', 'log', '-n', '1', '--format=%B'],
            cwd=self.repos[0],
            capture_output=True,
            text=True
        )
        self.assertIn('Chain test', log_result.stdout)

        # Second repo should have chain info
        log_result = subprocess.run(
            ['git', 'log', '-n', '1', '--format=%B'],
            cwd=self.repos[1],
            capture_output=True,
            text=True
        )
        self.assertIn('Chain test', log_result.stdout)
        self.assertIn('Chained-From:', log_result.stdout)

    def test_commit_amend(self):
        """Test commit --amend."""
        # Make initial commit
        test_file = self.repos[0] / 'amend_test.txt'
        test_file.write_text('initial')
        subprocess.run(['git', 'add', '.'], cwd=self.repos[0], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=self.repos[0], check=True, capture_output=True)

        # Make another change and amend
        test_file.write_text('amended')
        result = self.run_mgit('commit', '-m', 'Amended', '--add', '--amend')
        self.assertEqual(result.returncode, 0)


class TestMGitExec(TestMGitSetup):
    """Test exec command."""

    def test_exec_basic_command(self):
        """Test executing a basic git command."""
        result = self.run_mgit('exec', '--', 'branch')
        self.assertEqual(result.returncode, 0)

        # Each repo should show branch info
        for repo_name in self.repo_names:
            self.assertIn(f'project: {repo_name}', result.stdout)

    def test_exec_with_output(self):
        """Test exec command with output."""
        result = self.run_mgit('exec', '--', 'log', '-n', '1', '--oneline')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Initial commit', result.stdout)

    def test_exec_parallel(self):
        """Test exec with parallel execution."""
        result = self.run_mgit('-j8', 'exec', '--', 'status')
        self.assertEqual(result.returncode, 0)
        self.assertIn('8 parallel jobs', result.stderr)


class TestMGitCheckout(TestMGitSetup):
    """Test checkout command."""

    def test_checkout_branch(self):
        """Test checking out a branch."""
        # Create a branch in all repos
        for repo in self.repos:
            subprocess.run(['git', 'branch', 'test-branch'], cwd=repo, check=True, capture_output=True)

        # Checkout the branch
        result = self.run_mgit('checkout', 'test-branch')
        self.assertEqual(result.returncode, 0)

        # Verify all repos are on test-branch
        for repo in self.repos:
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo,
                capture_output=True,
                text=True
            )
            self.assertEqual(branch_result.stdout.strip(), 'test-branch')

        # Checkout back to main/master
        for repo in self.repos:
            subprocess.run(['git', 'checkout', '-'], cwd=repo, check=True, capture_output=True)


class TestMGitDryRun(TestMGitSetup):
    """Test dry-run mode."""

    def test_dry_run_commit(self):
        """Test dry-run with commit."""
        # Make changes
        test_file = self.repos[0] / 'dry_run_test.txt'
        test_file.write_text('dry run test')

        result = self.run_mgit('--dry-run', 'commit', '-m', 'Dry run', '--add')
        self.assertEqual(result.returncode, 0)
        self.assertIn('DRY RUN', result.stdout)

        # Verify no actual commit was made
        log_result = subprocess.run(
            ['git', 'log', '-n', '1', '--oneline'],
            cwd=self.repos[0],
            capture_output=True,
            text=True
        )
        self.assertNotIn('Dry run', log_result.stdout)

        # Clean up
        test_file.unlink()


class TestMGitLinkFile(TestMGitSetup):
    """Test link file functionality."""

    def test_link_file_creation(self):
        """Test that link file is created correctly."""
        # Make changes and commit
        for repo in self.repos:
            test_file = repo / 'link_test.txt'
            test_file.write_text('link test')

        link_file = Path(self.test_dir) / 'commits.txt'
        result = self.run_mgit(
            'commit', '-m', 'Link test', '--add',
            '--link-file', str(link_file)
        )
        self.assertEqual(result.returncode, 0)

        # Verify link file exists and contains SHAs
        self.assertTrue(link_file.exists(), "Link file not created")
        content = link_file.read_text()

        for repo_name in self.repo_names:
            self.assertIn(repo_name, content)

        # Verify SHA format (40 hex chars)
        import re
        sha_pattern = re.compile(r'[0-9a-f]{40}')
        self.assertTrue(sha_pattern.search(content), "No valid SHA found in link file")


class TestMGitParallelExecution(TestMGitSetup):
    """Test parallel execution features."""

    def test_various_job_counts(self):
        """Test different parallel job counts."""
        for jobs in [1, 4, 8, 16]:
            result = self.run_mgit(f'-j{jobs}', 'status')
            self.assertEqual(result.returncode, 0)

            if jobs > 1:
                self.assertIn(f'{jobs} parallel jobs', result.stderr)


class TestMGitErrors(TestMGitSetup):
    """Test error handling."""

    def test_invalid_command(self):
        """Test handling of invalid command."""
        result = self.run_mgit('invalid-command')
        self.assertNotEqual(result.returncode, 0)

    def test_missing_commit_message(self):
        """Test commit without message."""
        result = self.run_mgit('commit')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('required', result.stderr.lower())

    def test_invalid_checkout_ref(self):
        """Test checkout with invalid ref."""
        result = self.run_mgit('checkout', 'nonexistent-branch')
        # Should complete but report errors
        self.assertEqual(result.returncode, 0)  # Soft failure
        self.assertIn('ERROR', result.stderr)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMGitDiscovery))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitLog))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitDiff))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitCommit))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitExec))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitCheckout))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitDryRun))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitLinkFile))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitParallelExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestMGitErrors))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
