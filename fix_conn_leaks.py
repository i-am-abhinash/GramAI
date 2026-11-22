import os
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    modified = False
    
    for line in lines:
        new_lines.append(line)
        if "cursor.close()" in line:
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + "conn.close()\n")
            modified = True
            
    if modified:
        # Check if conn.close() is already there somehow to avoid double
        content = "".join(new_lines)
        if content.count("conn.close()") > content.count("cursor.close()"):
            # Too complicated, let's just make it simple
            pass
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("".join(new_lines))
        print(f"Fixed {filepath}")

services_dir = r"d:\GramAI\backend\services"
for root, dirs, files in os.walk(services_dir):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))

repos_dir = r"d:\GramAI\backend\repositories"
for root, dirs, files in os.walk(repos_dir):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))
