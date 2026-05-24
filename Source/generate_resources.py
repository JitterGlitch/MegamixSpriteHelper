import os
import subprocess
import sys
import html
import argparse
from pathlib import Path


def create_qrc_file(folder_path, qrc_path, prefix="icon"):
    folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: The directory '{folder_path}' does not exist.")
        sys.exit(1)

    print(f"Scanning '{folder_path}' for files...")

    qrc_lines = [
        '<RCC>',
        f'  <qresource prefix="{prefix}">'
    ]

    file_count = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = Path(root) / file
            relative_path = full_path.relative_to(Path.cwd()) if full_path.is_absolute() else full_path

            normalized_path = str(relative_path).replace('\\', '/')

            escaped_path = html.escape(normalized_path)

            qrc_lines.append(f'    <file>{escaped_path}</file>')
            file_count += 1

    qrc_lines.append('  </qresource>')
    qrc_lines.append('</RCC>\n')

    with open(qrc_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(qrc_lines))

    print(f"Success: '{qrc_path}' created with {file_count} files.")


def compile_qrc_to_py(qrc_path, py_path):
    print(f"Compiling '{qrc_path}' to '{py_path}'...")

    try:
        subprocess.run(
            ["pyside6-rcc", qrc_path, "-o", py_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Success: Resource file compiled to '{py_path}'.")
        print(f"You can now import it in your code using: import {Path(py_path).stem}")

    except FileNotFoundError:
        print("Error: 'pyside6-rcc' command not found.")
        print("Make sure PySide6 is installed (pip install PySide6) and in your system PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling QRC file:\n{e.stderr}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate and compile a PySide6 QRC file from a folder.")
    parser.add_argument("folder", help="Path to the folder containing your resources (e.g., Images/)")
    parser.add_argument("-o", "--output", default="resources", help="Base name for the output files (default: 'resources')")
    parser.add_argument("-p", "--prefix", default="icon", help="Resource prefix used in the QRC file (default: 'icon')")

    args = parser.parse_args()

    qrc_file = f"{args.output}.qrc"
    py_file = f"{args.output}_rc.py"

    create_qrc_file(args.folder, qrc_file, args.prefix)
    compile_qrc_to_py(qrc_file, py_file)

if __name__ == "__main__":
    main()