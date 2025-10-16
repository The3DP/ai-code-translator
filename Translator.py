#Code for translator
import re

def convert_assignment(line):
    return line.strip()

def convert_input(line):
    match = re.match(r'(\w+)\s*=\s*input\(["\'](.*?)["\']\)', line)
    if match:
        var, prompt = match.groups()
        return f'read -p "{prompt} " {var}'
    return "# Unsupported input"

def convert_print(line):
    content = line[6:-1].strip()
    parts = [p.strip() for p in content.split(',')]
    shell_parts = []
    for part in parts:
        if re.match(r'^["\'].*["\']$', part):
            shell_parts.append(part)
        elif re.match(r'\d+$', part):
            shell_parts.append(part)
        else:
            shell_parts.append(f'${part}')
    return f'echo {" ".join(shell_parts)}'

def convert_if(line):
    condition = re.match(r'if (.+):', line).group(1).strip()
    return 'if ' + convert_condition(condition) + '; then'

def convert_elif(line):
    condition = re.match(r'elif (.+):', line).group(1).strip()
    return 'elif ' + convert_condition(condition) + '; then'

def convert_else(_):
    return 'else'

def convert_condition(cond):
    # Support only equality for now
    cond = re.sub(r'(\w+)\s*==\s*["\'](.*?)["\']', r'[ "$\1" = "\2" ]', cond)
    return cond

def convert_for_range(line):
    match = re.match(r'for (\w+) in range\((\w+)\):', line)
    if match:
        var, end = match.groups()
        return f'for {var} in $(seq 0 $(({end} - 1))); do'
    match = re.match(r'for (\w+) in range\((\d+)\):', line)
    if match:
        var, end = match.groups()
        return f'for {var} in $(seq 0 {int(end)-1}); do'
    return "# Unsupported range"

def convert_for_list(line):
    match = re.match(r'for (\w+) in \[(.*?)\]:', line)
    if match:
        var, items = match.groups()
        items = items.strip().replace('"', '').replace("'", "")
        return f'for {var} in {items}; do'
    return "# Unsupported for loop"

def convert_line(line, indent_level):
    stripped = line.strip()

    if not stripped:
        return ""

    indent = '  ' * indent_level

    if stripped.startswith('#'):
        return indent + stripped

    if 'input(' in stripped:
        return indent + convert_input(stripped)

    if re.match(r'^\w+\s*=\s*["\']?.+["\']?$', stripped):
        return indent + convert_assignment(stripped)

    if stripped.startswith('print('):
        return indent + convert_print(stripped)

    if stripped.startswith('if '):
        return indent + convert_if(stripped)

    if stripped.startswith('elif '):
        return indent + convert_elif(stripped)

    if stripped.startswith('else:'):
        return indent + convert_else(stripped)

    if stripped.startswith('for ') and 'range' in stripped:
        return indent + convert_for_range(stripped)

    if stripped.startswith('for ') and '[' in stripped:
        return indent + convert_for_list(stripped)

    return indent + f'# Unsupported: {stripped}'

def convert_python_to_shell(py_code):
    lines = py_code.strip().split('\n')
    shell_lines = []
    indent_stack = []
    block_keywords = []

    for i, line in enumerate(lines):
        current_indent = len(line) - len(line.lstrip())
        indent_level = current_indent // 4

        # Close blocks if indentation decreased
        while indent_stack and indent_stack[-1] > indent_level:
            block = block_keywords.pop()
            end = 'done' if block == 'for' else 'fi'
            shell_lines.append('  ' * (indent_stack[-1] - 1) + end)
            indent_stack.pop()

        stripped = line.strip()

        shell_line = convert_line(line, indent_level)
        shell_lines.append(shell_line)

        # Check if line starts a block
        if stripped.startswith(('for ', 'if ', 'elif ', 'else:')):
            indent_stack.append(indent_level + 1)
            if stripped.startswith('for '):
                block_keywords.append('for')
            else:
                block_keywords.append('if')

    # Close remaining blocks
    while indent_stack:
        block = block_keywords.pop()
        end = 'done' if block == 'for' else 'fi'
        shell_lines.append('  ' * (indent_stack.pop() - 1) + end)

    return '\n'.join(shell_lines)


# Run the converter with an example
if __name__ == "__main__":
    python_code = '''
# Greet a user multiple times
name = input("Enter your name: ")
count = 3

for i in range(count):
    print("Hello", name, i)

if name == "Alice":
    print("Welcome back!")
elif name == "Bob":
    print("Hey Bob!")
else:
    print("Who are you?")
'''
    shell_script = convert_python_to_shell(python_code)
    print("Converted shell script:\n")
    print(shell_script)
