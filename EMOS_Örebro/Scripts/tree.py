import os
from pathlib import Path

def generate_tree(directory, ignore=None, max_depth=None):
    if ignore is None:
        ignore = {'.git', '__pycache__', 'node_modules', '.idea'}
    
    directory = Path(directory)
    tree = []
    
    def walk(path, depth=0):
        if max_depth and depth > max_depth:
            return
            
        entries = sorted(
            [entry for entry in path.iterdir() if entry.name not in ignore],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
        
        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            prefix = "└── " if is_last else "├── "
            connector = "    " if is_last else "│   "
            
            tree.append(f"{'│   ' * (depth-1)}{prefix}{entry.name}")
            
            if entry.is_dir():
                walk(entry, depth + 1)
    
    tree.append(f"{directory.name}/")
    walk(directory, 1)
    return '\n'.join(tree)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", default=".")
    args = parser.parse_args()
    print(generate_tree(args.dir))
