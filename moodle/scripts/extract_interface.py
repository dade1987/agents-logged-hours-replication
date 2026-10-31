"""Usage: python3 extract_interface.py <commit A> <commit B>
Condition "iface": lists classes, functions and web services that are new or changed
in the fix (A^..B, non-test files) and are used by the developers' tests.
Prints only names and signatures, never test code or function bodies."""
import re, subprocess, sys, os
G = os.environ.get('MOODLE', '/home/user/moodle')
A, B = sys.argv[1], sys.argv[2]
def git(*a): return subprocess.run(['git', '-C', G, *a], capture_output=True, text=True).stdout
files = git('diff', '--name-only', A + '^', B).split()
tests = [f for f in files if f.endswith('_test.php')]
srcs = [f for f in files if '/tests/' not in f and f.endswith('.php')]
testtxt = ''.join(l[1:] for f in tests for l in git('diff', A + '^', B, '--', f).splitlines() if l.startswith('+'))
out = []
for f in srcs:
    ns = re.search(r'^namespace\s+([\w\\]+);', git('show', f'{B}:{f}'), re.M)
    lines = git('diff', A + '^', B, '--', f).splitlines()
    for i, l in enumerate(lines):
        if not l.startswith('+'): continue
        m = re.match(r'\+\s*((?:final |abstract )?(?:class|interface|trait|enum)\s+(\w+).*)', l) or \
            re.match(r'\+\s*((?:public |protected |private |static |final |abstract )*function\s+(\w+)\s*\(.*)', l) or \
            re.match(r"\+\s*'((\w+_\w+))'\s*=>\s*\[", l)
        if m and re.search(r'\b' + re.escape(m.group(2)) + r'\b', testtxt):
            sig = m.group(1).rstrip('{ ').strip()
            j = i
            while sig.count('(') > sig.count(')') and j + 1 < len(lines) and j < i + 15:
                j += 1; sig += ' ' + lines[j][1:].strip()
            sig = re.sub(r'\s*\{\s*$', '', sig)
            out.append(f"- {f}{' (namespace ' + ns.group(1) + ')' if ns else ''}: {sig}")
print('\n'.join(dict.fromkeys(out)) if out else '(no new interface used by the tests)')
