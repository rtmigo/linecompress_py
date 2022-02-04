import subprocess
import sys


def lint():
    print("Running pylint...")
    package_dir_path = 'linecompress'
    r = subprocess.call([sys.executable, '-m', 'pylint', package_dir_path,
                         '--disable=invalid-name',
                         '--disable=missing-module-docstring',
                         '--disable=missing-class-docstring',
                         '--disable=missing-function-docstring', ])
    if r & 1 or r & 2 or r & 32:
        exit(r)

    print("Running mypy...")
    subprocess.check_call([sys.executable, '-m', 'mypy', package_dir_path,
                           '--ignore-missing-imports'])


if __name__ == "__main__":
    lint()
