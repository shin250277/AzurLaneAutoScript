"""Update the checked-out KR release without replacing local work."""
import subprocess


def fast_forward(git, branch, repository):
    def run(*args):
        return subprocess.check_output([git, *args], stderr=subprocess.STDOUT).decode('utf-8', 'replace').strip()

    if run('symbolic-ref', '--short', 'HEAD') != branch:
        raise RuntimeError('KR updater: checkout and configured branch differ')
    if run('remote', 'get-url', 'origin') != repository:
        raise RuntimeError('KR updater: configured repository differs from origin')
    run('fetch', 'origin', 'refs/heads/' + branch)
    target = run('rev-parse', '--verify', 'FETCH_HEAD^{commit}')
    run('merge-base', '--is-ancestor', 'HEAD', target)
    def paths(*args):
        output = subprocess.check_output(
            [git, 'diff', '--no-renames', '--name-only', '-z', *args, '--'],
            stderr=subprocess.STDOUT)
        return set(output.split(b'\0')) - {b''}

    incoming = paths('HEAD', target)
    if not incoming and run('rev-parse', 'HEAD') == target:
        return
    conflicts = incoming & (paths('--cached') | paths())
    if conflicts:
        names = ', '.join(p.decode('utf-8', 'replace') for p in sorted(conflicts))
        raise RuntimeError('KR updater: local edits overlap incoming update; '
                           'no files changed: ' + names)
    run('merge', '--ff-only', '--no-overwrite-ignore', target)
