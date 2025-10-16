# Code for Python to Shell script translator
import re

def convert_assignment(line):
    var, value = line.split('=', 1)
    return f'{var.strip()}={value.strip()}'

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
            shell_parts.append(part.strip('"\''))
        elif re.match(r'^\d+$', part):
            shell_parts.append(part)
        else:
            shell_parts.append(f'${part}')
    return f'echo {" ".join(shell_parts)}'

def convert_if(line):
    condition = re.match(r'if (.+):', line).group(1).strip()
    return f'if {convert_condition(condition)}; then'

def convert_elif(line):
    condition = re.match(r'elif (.+):', line).group(1).strip()
    return f'elif {convert_condition(condition)}; then'

def convert_else(_):
    return 'else'

def convert_condition(cond):
    # Handle string or numeric equality
    # Handle both: var == "string" and var == number
    cond = cond.strip()

    # Support multiple comparison patterns
    # string comparison: [ "$var" = "value" ]
    str_eq = re.match(r'(\w+)\s*==\s*["\'](.*?)["\']', cond)
    num_eq = re.match(r'(\w+)\s*==\s*(\d+)', cond)

    if str_eq:
        var, val = str_eq.groups()
        return f'[ "${var}" = "{val}" ]'
    elif num_eq:
        var, val = num_eq.groups()
        return f'[ ${var} -eq {val} ]'
    else:
        return f'# Unsupported condition: {cond}'

def convert_for_range(line):
    match = re.match(r'for (\w+) in range\((\w+)\):', line)
    if match:
        var, end = match.groups()
        return f'for {var} in $(seq 0 $((${end} - 1))); do'
    match = re.match(r'for (\w+) in range\((\d+)\):', line)
    if match:
        var, end = match.groups()
        return f'for {var} in $(seq 0 {int(end)-1}); do'
    return "# Unsupported range"

def convert_for_list(line):
    match = re.match(r'for (\w+) in \[(.*?)\]:', line)
    if match:
        var, items = match.groups()
        items = items.replace('"', '').replace("'", "").strip()
        items_list = items.split(',')
        items_str = ' '.join(i.strip() for i in items_list)
        return f'for {var} in {items_str}; do'
    return "# Unsupported for loop"

def convert_line(line, indent_level):
    stripped = line.strip()
    indent = '  ' * indent_level

    if not stripped:
        return ""

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
        stripped = line.strip()

        # Close blocks when indent decreases
        while indent_stack and indent_stack[-1] > indent_level:
            block = block_keywords.pop()
            closing = 'done' if block == 'for' else 'fi'
            shell_lines.append('  ' * (indent_stack[-1] - 1) + closing)
            indent_stack.pop()

        shell_line = convert_line(line, indent_level)
        shell_lines.append(shell_line)

        if stripped.startswith(('for ', 'if ', 'elif ', 'else:')):
            indent_stack.append(indent_level + 1)
            if stripped.startswith('for '):
                block_keywords.append('for')
            else:
                block_keywords.append('if')

    # Close any remaining blocks
    while indent_stack:
        block = block_keywords.pop()
        closing = 'done' if block == 'for' else 'fi'
        shell_lines.append('  ' * (indent_stack.pop() - 1) + closing)

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
