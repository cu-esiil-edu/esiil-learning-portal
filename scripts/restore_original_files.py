import os
import shutil
from glob import glob

def main():
    print('Restoring original .qmd files')

    # Process all .qmd files in the render list
    original_file_list = glob(os.path.join('**', '*.original'), recursive=True)
    print(original_file_list)
    for original_file in original_file_list:
        input_file = original_file.replace('.original', '')
        os.remove(input_file)
        shutil.move(original_file, input_file)

if __name__ == "__main__":
    main()