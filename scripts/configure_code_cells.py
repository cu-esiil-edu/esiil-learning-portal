import os
import re
import shutil

import yaml

def load_yaml(file):
    with open(file, 'r') as stream:
        return yaml.safe_load(stream)

def replace_params(content, params):
    # Replace quoted parameters in code
    # Note that you can't format quarto parameters and leave the
    # string as a format string for later
    quoted_params = {f'__param_{key}': value for key, value in params.items()}
    format_pattern = re.compile("f[\'\"][^\'\"]*__param_[^\'\"]*[\'\"]")
    format_strings = format_pattern.findall(content)
    if format_strings:
        for format_string in format_strings:
            content = content.replace(
                format_string, format_string.format(**quoted_params)[1:])

    # Replace unquoted parameters in code
    for key, value in params.items():
        placeholder = f"__param_{key}"
        content = content.replace(placeholder, f'"{value}"')
    return content

def replace_exec_options(content, code_block_templates):
    # Find template params
    option_pattern = re.compile(r"(#\| template: (\w+))")
    option_groups = option_pattern.findall(content)
    if option_groups:
        for (option_string, code_block_type) in option_groups:
            code_block_template = code_block_templates[code_block_type]
            options = [
                f'#| {key}: {value}'
                for key, value
                in code_block_template.items()]
            content = content.replace(
                option_string, 
                '\n'.join(options))

    return content

def process_file(input_file, params, code_block_templates):
    # Make a copy of the original
    shutil.copy2(input_file, f"{ input_file }.original")

    # Read the input file
    with open(input_file, 'r') as file:
        content = file.read()

    # Remove test parameter cell
    param_pattern = re.compile(r'\#\| tags: \[parameters\][^`]*```')
    param_cell = param_pattern.search(content)
    if param_cell:
        content = content.replace(f'```{{python}}\n{param_cell[0]}', '')

    # Replace placeholders with parameter values
    content = replace_params(content, params)
    content = replace_exec_options(content, code_block_templates)

    # Write the modified content back to the file
    with open(input_file, 'w') as file:
        file.write(content)

def main():
    print('Inserting code parameters')
    
    # Get the profile from environment variable
    profiles = os.getenv('QUARTO_PROFILE').split(',')

    # Load the _quarto.yml file
    quarto_filenames = ['_quarto.yml']
    quarto_filenames += [
        f'_quarto-{ profile }.yml' 
        for profile in profiles
        if profile
    ]
    config = {}
    for quarto_filename in quarto_filenames:
        config = config | load_yaml(quarto_filename)

    # Get code block templates
    code_block_templates = config.get('code-block-templates')
    if code_block_templates is None:
        code_block_templates = {}

    # Process all .qmd files in the render list
    input_files = os.getenv('QUARTO_PROJECT_INPUT_FILES')
    if not input_files:
        print('No files to render')
        return
    input_file_list = input_files.split('\n')
    
    for input_file in input_file_list:
        print(f'  Pre-rendering { input_file }')
        notebook = os.path.basename(os.path.dirname(input_file))
        params = {}
        if 'params' in config:
            if notebook in config['params']:
                params = config['params'][notebook]
                print('    Parameters:', params)
        process_file(input_file, params, code_block_templates)

if __name__ == "__main__":
    main()