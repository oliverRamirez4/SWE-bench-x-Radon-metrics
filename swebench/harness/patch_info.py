import re
import sys
from collections import defaultdict

def parse_git_patch(patch_text):
    stats = {
        "files_modified": [],
        "files_added": [],
        "functions_modified": [],
        "functions_added": [],
        "functions_deleted": [],
        "lines_modified": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "hunks_modified": 0,
        "test_files_modified": []
    }
    
    file_pattern = re.compile(r'\+\+\+ b/(\S+)')
    func_pattern = re.compile(r'^\s*(def|class)\s+(\w+)')
    added_file_pattern = re.compile(r'new file mode')
    
    current_file = None
    function_scope = None
    inside_new_file = False
    
    for line in patch_text.split("\n"):
        if line.startswith('+++ b/'):
            current_file = file_pattern.search(line).group(1)
            if current_file not in stats["files_modified"]:
                stats["files_modified"].append(current_file)
            inside_new_file = False  # Reset new file flag
            
            # Detect modified test files
            if "test" in current_file.lower() and current_file not in stats["test_files_modified"]:
                stats["test_files_modified"].append(current_file)
                
        elif added_file_pattern.search(line):
            inside_new_file = True  # Mark that a new file is being added
        elif inside_new_file and line.startswith('+++ b/'):
            new_file = file_pattern.search(line).group(1)
            if new_file not in stats["files_added"]:
                stats["files_added"].append(new_file)
        elif line.startswith('@@'):
            stats["hunks_modified"] += 1  # Count modified hunks
            function_scope = None  # Reset function scope when entering a new chunk
        elif line.startswith('+') and not line.startswith('+++'):
            stats["lines_modified"] += 1  # Count added lines
            stats["lines_added"] += 1
            match = func_pattern.search(line)
            if match:
                func_name = match.group(2)
                if current_file and func_name not in stats["functions_added"]:
                    stats["functions_added"].append(func_name)
        elif line.startswith('-') and not line.startswith('---'):
            stats["lines_modified"] += 1  # Count deleted lines
            stats["lines_deleted"] += 1
            match = func_pattern.search(line)
            if match:
                func_name = match.group(2)
                if current_file and func_name not in stats["functions_deleted"]:
                    stats["functions_deleted"].append(func_name)
        elif not line.startswith('-') and func_pattern.match(line):
            function_scope = func_pattern.match(line).group(2)
            if function_scope not in stats["functions_modified"]:
                stats["functions_modified"].append(function_scope)
    
    return stats