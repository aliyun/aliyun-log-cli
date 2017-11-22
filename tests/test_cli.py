from util import run_test
import sys


def test_main():
    files = sys.argv[1:]
    if not files:
        files = ['cmd_list.txt']
    for file_path in files:
        run_test(file_path)


if __name__ == '__main__':
    test_main()


