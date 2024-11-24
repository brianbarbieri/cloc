import os
from gitignore_parser import parse_gitignore # type: ignore
import argparse

def list_files_with_extensions(directory, git_ignore_path):    
    # Parse .gitignore if it exists
    is_ignored = parse_gitignore(git_ignore_path) if os.path.exists(git_ignore_path) else lambda x: False

    files_with_info = []
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
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
    # Sort the dictionary and store the result in a list of tuples
    sorted_info = sorted(
        info_dict.items(),
        key=lambda x: x[1]["line_count"],
        reverse=True
    )

    # Calculate totals
    total_line_count = sum(info["line_count"] for info in info_dict.values())
    total_empty_lines = sum(info["empty_lines"] for info in info_dict.values())
    total_files = sum(info["# of files"] for info in info_dict.values())

    print("-------------------------------------------------------------------------------")
    for ext, data in sorted_info:
        print(f"{ext:20} {data['# of files']:10} {data['empty_lines']:10} {data['line_count']:10}")
    print("-------------------------------------------------------------------------------")
    print(f"{'Sum:':20} {total_files:10} {total_empty_lines:10} {total_line_count:10}")
    print("-------------------------------------------------------------------------------")
    
def show_empty_lines(directory, git_ignore_path):    
    # Parse .gitignore if it exists
    is_ignored = parse_gitignore(git_ignore_path) if os.path.exists(git_ignore_path) else lambda x: False
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
                    empty_lines = [i for i, line in enumerate(lines) if line.strip() == '' or line.strip() == '\n']
            except Exception as e:
                pass
            if empty_lines:
                print(f'File: {file_path}')
                print(f'On lines: {empty_lines}')


def main(directory, git_ignore_path):
    info_dict = list_files_with_extensions(directory, git_ignore_path)
    visualize_info(info_dict)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory to scan")
    parser.add_argument("--git-coount", help="The .gitcount file to use", default=None)
    args = parser.parse_args()
    