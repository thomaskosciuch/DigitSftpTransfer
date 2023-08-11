from paramiko import SFTPAttributes
from pysftp import Connection

from constants import DESTINATION_DIRECTORY, IDENTIFIER, SOURCE_DIRECTORY

def older_than(source_time:int , destination_time:int) -> bool:
    return source_time <= destination_time

def get_files_absent_from_destination(source_connection: Connection, destination_connection: Connection) -> list[str]:
    source_files: list[SFTPAttributes] = source_connection.listdir_attr(SOURCE_DIRECTORY)
    source_files: list[SFTPAttributes] = list(filter(lambda file: IDENTIFIER in file.filename, source_files))
    source_file_array: list[str] = [file.filename for file in source_files]
    source_file_times: dict[str, int] = {file.filename: file.st_mtime for file in source_files}
    destination_files: list[SFTPAttributes] = destination_connection.listdir_attr(DESTINATION_DIRECTORY)
    destination_files: list[SFTPAttributes] = list(filter(lambda file: file.filename in source_file_array, destination_files))
    destination_file_times: dict[str, int] = {file.filename: file.st_mtime for file in destination_files}
    files_to_add: list[str] = []

    for source_file, source_time in source_file_times.items():
        if source_file in destination_file_times:
            if older_than(source_time, destination_file_times[source_file]):
                continue
            files_to_add.append(source_file)
        else:
            files_to_add.append(source_file)
    return files_to_add
