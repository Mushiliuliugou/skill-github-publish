#!/usr/bin/env python3
"""Read-only Skill preflight. Reports locations/categories, never secret values."""
import json
import re
import sys
from pathlib import Path


def check(root):
    findings = []
    def add(level, code, path, message):
        findings.append(dict(level=level, code=code, path=str(path), message=message))
    if not root.is_dir():
        add('error', 'directory_missing', root, '目标文件夹不存在')
        return findings
    entry = root / 'SKILL.md'
    if not entry.is_file() or entry.is_symlink():
        add('error', 'entry_missing', 'SKILL.md', '缺少普通文件 SKILL.md，或入口是符号链接')
        return findings
    try:
        body = entry.read_text(encoding='utf-8')
    except (UnicodeError, OSError):
        add('error', 'entry_unreadable', 'SKILL.md', '入口无法按 UTF-8 读取')
        return findings
    front = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', body, re.S)
    if not front:
        add('error', 'frontmatter_missing', 'SKILL.md', '需要 YAML 元数据块')
    else:
        # Deliberately a lightweight check, not a complete YAML parser.
        for field in ('name', 'description'):
            m = re.search(r'^' + field + r':\s*(.+)$', front[1], re.M)
            if not m or m[1].strip() in ('', '""', "''"):
                add('error', 'metadata_missing', 'SKILL.md', '缺少非空 ' + field)
            elif field == 'name':
                name = m[1].strip().strip('\'"')
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) >= 64:
                    add('error', 'invalid_name', 'SKILL.md', '名称应为小写字母、数字、连字符且少于64字符')
                if name != root.name:
                    add('review', 'folder_name', 'SKILL.md', '名称与文件夹不一致，请核对发布布局')
        if not body[front.end():].strip():
            add('error', 'body_empty', 'SKILL.md', '缺少正文')
    inventory = []
    secret_patterns = [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                       r'\bgh[pousr]_[A-Za-z0-9]{20,}', r'\bgithub_pat_[A-Za-z0-9_]{20,}',
                       r'\bsk-[A-Za-z0-9_-]{20,}',
                       r'(?im)^\s*(?:api_key|password|secret|access_token)\s*[:=]\s*[\'\"]?[^\s\'\"]{8,}']
    for file in sorted(root.rglob('*')):
        rel = file.relative_to(root)
        if '.git' in rel.parts:
            continue
        if file.is_symlink():
            add('review', 'symlink', rel, '符号链接需确认可移植性与发布范围')
            continue
        if not file.is_file():
            continue
        inventory.append(str(rel))
        try:
            size = file.stat().st_size
            if size > 25 * 1024 * 1024:
                add('review', 'large_file', rel, '超过25 MiB；采用网页上传前核实限制')
            if file.name == '.env' or (file.name.startswith('.env.') and file.name != '.env.example'):
                add('review', 'environment_config', rel, '真实环境配置需排除并检查凭据')
            if any(x in rel.parts for x in ('__pycache__', 'node_modules')) or file.name == '.DS_Store':
                add('review', 'generated_file', rel, '疑似缓存或依赖，确认是否需要发布')
            if size > 2 * 1024 * 1024:
                add('review', 'content_not_scanned', rel, '大文件未扫描正文，需单独检查')
                continue
            content = file.read_text(encoding='utf-8')
        except UnicodeError:
            add('review', 'binary_not_scanned', rel, '二进制文件需检查内容及素材来源')
            continue
        except OSError:
            add('review', 'unreadable', rel, '文件读取失败，需人工检查')
            continue
        if any(re.search(pattern, content) for pattern in secret_patterns):
            add('review', 'possible_secret', rel, '可能含凭据或示例匹配；检查时不要回显值')
        if file.suffix.lower() == '.md':
            if re.search(r'\bTODO\b|\bTBD\b|\[待填写\]', content):
                add('review', 'placeholder', rel, '可能存在未完成占位符')
            if re.search(r'/Users/[^\s]+|[A-Z]:\\Users\\', content):
                add('review', 'absolute_path', rel, '可能依赖作者本地路径，结合示例上下文审核')
            for link in re.findall(r'\]\(([^)]+)\)', content):
                link = link.strip('<>').split('#', 1)[0]
                if not link or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', link) or link.startswith('/'):
                    continue
                target = (file.parent / link).resolve()
                if not target.is_relative_to(root.resolve()):
                    add('review', 'external_local_reference', rel, '相对链接指向 Skill 文件夹之外')
                elif not target.exists():
                    add('review', 'missing_reference', rel, '存在无法解析的相对链接，检查路径及占位符')
    return findings, inventory


def main():
    if len(sys.argv) != 2:
        print('Usage: python3 check_skill.py <skill-directory>', file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    result = check(root)
    findings, inventory = result if isinstance(result, tuple) else (result, [])
    errors = sum(x['level'] == 'error' for x in findings)
    print(json.dumps(dict(target=str(root), static_status='needs_fix' if errors else 'ready_for_review',
                         findings=findings, files=inventory,
                         manual_gates=['用途与兼容性', '实际行为试用', 'README与安装说明', '隐私及历史审核',
                                       '公开范围与许可决定', '上传授权', '远程内容验收'],
                         limitation='轻量静态检查，不解析完整YAML，不证明无密钥或行为正确。'), ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
