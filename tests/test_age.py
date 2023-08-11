from os import stat

from compare_files import older_than

old_filepath: str = 'tests/test_age.py'
new_filepath: str = 'tests/test_file'

with open('tests/test_file', 'w') as test_file:
    test_file.write('')

old_mtime: int = stat(old_filepath).st_mtime
new_mtime: int = stat(new_filepath).st_mtime


def test_newer_file_age():
    assert older_than(new_mtime, old_mtime) == False

# def test_same_file_age(new_mtime, new_mtime):
#     == False

