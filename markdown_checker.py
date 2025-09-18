#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown格式检查工具
支持标准MD语法检查，包括标题、列表、代码块等基本元素
"""

import re
import sys
from pathlib import Path

class MarkdownChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def check_file(self, file_path):
        """检查Markdown文件格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.check_content(content, str(file_path))
            
        except Exception as e:
            return [f"文件读取错误: {str(e)}"], []
    
    def check_content(self, content, filename="content"):
        """检查Markdown内容格式"""
        self.errors = []
        self.warnings = []
        
        # 检查基本元素
        self._check_headings(content)
        self._check_lists(content)
        self._check_code_blocks(content)
        self._check_links(content)
        self._check_images(content)
        self._check_format_consistency(content)
        
        return self.errors, self.warnings
    
    def _check_headings(self, content):
        """检查标题格式"""
        lines = content.split('\n')
        heading_pattern = re.compile(r'^#{1,6}\s+.+$')
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#') and not heading_pattern.match(line):
                self.errors.append(f"第{i}行: 标题格式错误 - '{line.strip()}'")
    
    def _check_lists(self, content):
        """检查列表格式"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 忽略分隔线 (---)
            if stripped == '---':
                continue
                
            # 忽略加粗文本 (**text**)
            if re.match(r'^\*\*.+\*\*$', stripped):
                continue
                
            if stripped and (stripped.startswith('-') or stripped.startswith('*') or stripped.startswith('+')):
                if not re.match(r'^[-*+]\s+.+$', stripped):
                    self.errors.append(f"第{i}行: 无序列表格式错误 - '{stripped}'")
            
            elif stripped and re.match(r'^\d+\.', stripped):
                if not re.match(r'^\d+\.\s+.+$', stripped):
                    self.errors.append(f"第{i}行: 有序列表格式错误 - '{stripped}'")
    
    def _check_code_blocks(self, content):
        """检查代码块格式"""
        lines = content.split('\n')
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if in_code_block:
                # 代码块内不检查格式
                continue
                
            # 检查行内代码
            if '`' in line:
                # 简单的行内代码检查
                backticks = line.count('`')
                if backticks % 2 != 0:
                    self.warnings.append(f"第{i}行: 可能缺少闭合反引号")
    
    def _check_links(self, content):
        """检查链接格式"""
        # 检查标准链接格式 [text](url)
        link_pattern = re.compile(r'\[.*?\]\(.*?\)')
        matches = link_pattern.findall(content)
        
        for match in matches:
            if not re.match(r'\[[^\]]+\]\([^)]+\)', match):
                self.errors.append(f"链接格式错误: '{match}'")
    
    def _check_images(self, content):
        """检查图片格式"""
        # 检查标准图片格式 ![alt](url)
        img_pattern = re.compile(r'!\[.*?\]\(.*?\)')
        matches = img_pattern.findall(content)
        
        for match in matches:
            if not re.match(r'!\[[^\]]+\]\([^)]+\)', match):
                self.errors.append(f"图片格式错误: '{match}'")
    
    def _check_format_consistency(self, content):
        """检查格式一致性"""
        lines = content.split('\n')
        
        # 检查中英文混排的空格一致性
        for i, line in enumerate(lines, 1):
            if re.search(r'[a-zA-Z][\u4e00-\u9fff]|[\u4e00-\u9fff][a-zA-Z]', line):
                self.warnings.append(f"第{i}行: 中英文混排，建议添加空格分隔")
        
        # 检查标题层级一致性
        heading_levels = []
        for line in lines:
            if line.strip().startswith('#'):
                level = len(line.strip().split(' ')[0])
                heading_levels.append(level)
        
        if heading_levels:
            # 检查标题层级是否合理（如不应该从##直接跳到####）
            for i in range(1, len(heading_levels)):
                if heading_levels[i] > heading_levels[i-1] + 1:
                    self.warnings.append("标题层级跳跃过大，建议保持层级连续性")

def main():
    """命令行入口"""
    if len(sys.argv) != 2:
        print("用法: python markdown_checker.py <markdown文件>")
        sys.exit(1)
    
    checker = MarkdownChecker()
    errors, warnings = checker.check_file(sys.argv[1])
    
    print("=" * 50)
    print(f"Markdown格式检查报告: {sys.argv[1]}")
    print("=" * 50)
    
    if errors:
        print("\n❌ 错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ 无格式错误")
    
    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✅ 无格式警告")
    
    print(f"\n总计: {len(errors)}个错误, {len(warnings)}个警告")

if __name__ == "__main__":
    main()