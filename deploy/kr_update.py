"""Update the checked-out KR release without replacing local work."""
import subprocess


def fast_forward(git, branch, repository):
    def run(*args):
        return subprocess.check_output([git, *args], stderr=subprocess.STDOUT).decode('utf-8', 'replace').strip()

    if run('symbolic-ref', '--short', 'HEAD') != branch:
        raise RuntimeError('KR updater: checkout and configured branch differ')
    if run('remote', 'get-url', 'origin') != repository:
        raise RuntimeError('KR updater: configured repository differs from origin')
    if run('status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('KR updater: tracked local changes; update skipped')
    run('fetch', 'origin', 'refs/heads/' + branch)
    target = run('rev-parse', '--verify', 'FETCH_HEAD^{commit}')
    run('merge-base', '--is-ancestor', 'HEAD', target)
    run('merge', '--ff-only', '--no-overwrite-ignore', target)
