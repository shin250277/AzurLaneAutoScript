"""Convert remaining pre-upstream color-count similarity literals to distances."""
import ast
from pathlib import Path


if __name__ == '__main__':
    count = 0
    for path in Path('module').rglob('*.py'):
        text = path.read_text(encoding='utf-8-sig')
        lines = text.splitlines(keepends=True)
        edits = []
        for node in ast.walk(ast.parse(text)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != 'image_color_count':
                continue
            for keyword in node.keywords:
                value = keyword.value
                if keyword.arg == 'threshold' and isinstance(value, ast.Num) and value.n > 127:
                    edits.append((value.lineno - 1, value.col_offset, str(value.n), str(255 - value.n)))
        for row, col, old, new in sorted(edits, reverse=True):
            encoded = lines[row].encode('utf-8')
            assert encoded[col:col + len(old)].decode() == old
            lines[row] = (encoded[:col] + new.encode() + encoded[col + len(old):]).decode('utf-8')
        if edits:
            path.write_text(''.join(lines), encoding='utf-8')
            count += len(edits)
    print('Converted explicit thresholds:', count)
