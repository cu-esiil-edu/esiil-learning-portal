import os
import re
import shutil

import yaml

def load_yaml(file):
    with open(file, 'r') as stream:
        return yaml.safe_load(stream)

def get_frontmatter_params(file_path):
    """
    Extracts parameters from YAML front matter
    
    The function assumes the YAML front matter is at the very beginning of the file
    and is delimited by lines containing only '---'.
    
    :param file_path: Path to the Quarto markdown file.
    :return: A dictionary containing the YAML data, or an empty dict if not found.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use a regular expression to extract the YAML block.
    # This regex matches text between two '---' delimiters at the very beginning.
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    
    if match:
        yaml_str = match.group(1)
        try:
            yaml_data = yaml.safe_load(yaml_str)
            if isinstance(yaml_data, dict):
                if 'params' in yaml_data:
                    return yaml_data['params'] 
                
        except yaml.YAMLError as e:
            print("Error parsing YAML:", e)
            return {}
        
    # No parameters found
    return {}

def get_included_files(file_path):
    """
    Extracts the list of file names included via templating syntax from a markdown file.
    
    The function searches for directives in the form:
        {{< include filename >}}
    
    :param file_path: Path to the Quarto markdown file.
    :return: A list of filenames included in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex pattern to match the include directive.
    # It looks for the keyword "include" and then captures the filename.
    pattern = r'{{<\s*include\s+([^ >]+)\s*>}}'
    included_files = re.findall(pattern, content)
    return included_files

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

def replace_params(content, params):
    # Replace parameters in code
    for key, value in params.items():
        placeholder = f"__param_{key}"
        content = content.replace(placeholder, f'{value}')
    return content

def process_file(input_file, code_block_templates, params):
    # Make a copy of the original
    shutil.copy2(input_file, f"{ input_file }.original")

    # Read the input file
    with open(input_file, 'r') as file:
        content = file.read()

    # Replace code block execution parameters
    content = replace_exec_options(content, code_block_templates)

    # Insert code parameters
    content = replace_params(content, params)
    
    # Write the modified content back to the file
    with open(input_file, 'w') as file:
        file.write(content)

def main():
    print('Configuring code cells')
    # Load the _quarto.yml file
    config = load_yaml("_quarto.yml")

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
        # Get parameters
        params = get_frontmatter_params(input_file)
        print('    Parameters:', params)
                
        print(f'  Pre-rendering { input_file }')
        included_files = get_included_files(input_file)
        for included_file in included_files:
            included_file_path = os.path.join(
                os.path.dirname(input_file),
                included_file)
            print(f'Configuring included file { included_file_path }')
            process_file(included_file_path, code_block_templates, params)
            
        process_file(input_file, code_block_templates, params)

if __name__ == "__main__":
    main()
