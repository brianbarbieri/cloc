import os
from typing import Callable, List
import argparse

from gitignore_parser import parse_gitignore # type: ignore


def list_files_with_extensions(directory : str, git_ignore_path: str):    
    """
    Scans the given directory and returns a dictionary of file types and their
    corresponding line counts.

    Ignores directories and files specified in the given .gitignore file.

    :param directory: The directory to scan
    :param git_ignore_path: The path to the .gitignore file
    :return: A dictionary of file types and their corresponding line counts
    """
    is_ignored: Callable[[str], bool]  = parse_gitignore(git_ignore_path) if os.path.exists(git_ignore_path) else lambda x: False

    files_with_info = []
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        for file in files:
            file_path: str = os.path.join(root, file)
            
            # Skip ignored files
            if is_ignored(file_path):
                continue

            file_name, file_extension = os.path.splitext(file)
            try:
                # Count the lines in the file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    empty_lines = sum(1 for line in lines if line.strip() == '' or line.strip() == '\n')
                    line_count -= empty_lines
            except Exception as e:
                line_count = 0  # Handle unreadable files gracefully
                empty_lines = 0

            files_with_info.append((file_path, file_extension, line_count, empty_lines))
    
    info_dict = {}
    for file_path, ext, linecount, empty_lines in files_with_info:    
        if ext not in info_dict:
            if ext == "":
                ext = "no_ext"
            info_dict[ext] = {"line_count": 0, "empty_lines": 0, "# of files" : 0}
        info_dict[ext]["line_count"] += linecount
        info_dict[ext]["empty_lines"] += empty_lines
        info_dict[ext]["empty_lines"] += empty_lines
        info_dict[ext]["# of files"] += 1

    return info_dict

def visualize_info(info_dict):
    """
    Sort the dictionary of file extensions and their corresponding line counts,
    empty line counts, and number of files, and print the results in a nicely
    formatted table.

    :param info_dict: A dictionary where the keys are file extensions and the
                      values are dictionaries with the keys "line_count",
                      "empty_lines", and "# of files".
    """
    sorted_info = sorted(
        info_dict.items(),
        key=lambda x: x[1]["line_count"],
        reverse=True
    )

    # Calculate totals
    total_line_count: int = sum(info["line_count"] for info in info_dict.values())
    total_empty_lines: int = sum(info["empty_lines"] for info in info_dict.values())
    total_files: int = sum(info["# of files"] for info in info_dict.values())

    print("-------------------------------------------------------------------------------")
    print(f"{'Extension':20} {'# of files':20} {'# of empty lines':20} {'line count':20}")
    print("-------------------------------------------------------------------------------")
    for ext, data in sorted_info:
        print(f"{ext:20} {data['# of files']:<20} {data['empty_lines']:<20} {data['line_count']:<20}")
    print("-------------------------------------------------------------------------------")
    print(f"{'Sum:':20} {total_files:<20} {total_empty_lines:<20} {total_line_count:<20}")
    print("-------------------------------------------------------------------------------")
    
def show_empty_lines(directory, git_ignore_path):    
    """
    Scans the given directory and prints out all empty lines in the files found.

    Ignores directories and files specified in the given .gitignore file.
    """
    is_ignored: Callable[[str], bool] = parse_gitignore(git_ignore_path) if os.path.exists(git_ignore_path) else lambda x: False
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip ignored files
            if is_ignored(file_path):
                continue

            file_name, file_extension = os.path.splitext(file)
            empty_lines = []
            try:
                # Count the lines in the file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    empty_lines: List[int] = [i for i, line in enumerate(lines) if line.strip() == '' or line.strip() == '\n']
            except Exception as e:
                pass
            if empty_lines:
                print(f'File: {file_path}')
                print(f'On lines: {empty_lines}')


def main(directory, git_ignore_path):
    """
    Main function for the cloc script.

    Scans the given directory and prints out a table of file types and their
    corresponding line counts.

    :param directory: The directory to scan
    :param git_ignore_path: The path to the .gitignore file
    """
    
    info_dict = list_files_with_extensions(directory, git_ignore_path)
    visualize_info(info_dict)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory to scan")
    parser.add_argument("--git-coount", help="The .gitcount file to use", default=None)
    args = parser.parse_args()
    