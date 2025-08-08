#!/usr/bin/env python3
"""
SuperClaude内容提取器 / SuperClaude Content Extractor
从SuperClaude框架中提取所有需要翻译的交互内容 / Extracts all interactive content that needs translation from the SuperClaude framework
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ExtractedContent:
    """提取的内容项 / Extracted content item"""
    key: str
    text: str
    content_type: str  # commands, personas, ui, errors, help
    context: str
    file_source: Optional[str] = None


class SuperClaudeContentExtractor:
    """SuperClaude内容提取器 / SuperClaude content extractor"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def extract_all_content(self) -> Dict[str, Dict[str, str]]:
        """提取所有需要翻译的内容"""
        
        content = {
            "commands": {},
            "personas": {},
            "ui": {},
            "errors": {},
            "help": {}
        }
        
        # 1. 从Commands目录提取命令描述
        content["commands"].update(self._extract_from_commands())
        
        # 2. 从PERSONAS.md提取角色描述
        content["personas"].update(self._extract_from_personas())
        
        # 3. 从各种源文件提取UI文本
        content["ui"].update(self._extract_ui_texts())
        
        # 4. 提取错误消息
        content["errors"].update(self._extract_error_messages())
        
        # 5. 提取帮助文本
        content["help"].update(self._extract_help_texts())
        
        return content
    
    def _extract_from_commands(self) -> Dict[str, str]:
        """从Commands目录提取命令描述"""
        commands = {}
        commands_dir = self.project_root / "SuperClaude" / "Commands"
        
        if not commands_dir.exists():
            # 如果文件不存在，使用预定义的命令描述
            return self._get_default_command_descriptions()
        
        # 扫描.md文件获取命令描述
        for cmd_file in commands_dir.glob("*.md"):
            cmd_name = cmd_file.stem
            try:
                content = cmd_file.read_text(encoding="utf-8")
                
                # 提取Purpose部分
                purpose_match = re.search(r"## Purpose\s*\n(.*?)(?=\n##|\n```|\Z)", content, re.DOTALL)
                if purpose_match:
                    purpose = purpose_match.group(1).strip()
                    commands[cmd_name] = purpose
                else:
                    # 如果找不到Purpose，使用文件的第一段描述
                    lines = content.split('\n')
                    for line in lines[1:10]:  # 跳过标题，检查前几行
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('```'):
                            commands[cmd_name] = line
                            break
                
            except Exception as e:
                print(f"Warning: Could not extract from {cmd_file}: {e}")
        
        # 如果提取结果为空，使用默认描述
        if not commands:
            commands = self._get_default_command_descriptions()
            
        return commands
    
    def _extract_from_personas(self) -> Dict[str, str]:
        """从PERSONAS.md提取角色描述"""
        personas = {}
        personas_file = self.project_root / "SuperClaude" / "Core" / "PERSONAS.md"
        
        if not personas_file.exists():
            return self._get_default_persona_descriptions()
        
        try:
            content = personas_file.read_text(encoding="utf-8")
            
            # 匹配persona定义模式
            persona_pattern = r"##\s*`--persona-(\w+)`\s*\n.*?\*\*Identity\*\*:\s*([^*\n]+)"
            matches = re.finditer(persona_pattern, content, re.DOTALL)
            
            for match in matches:
                persona_name = match.group(1)
                identity = match.group(2).strip()
                personas[persona_name] = identity
                
        except Exception as e:
            print(f"Warning: Could not extract personas: {e}")
            personas = self._get_default_persona_descriptions()
            
        return personas
    
    def _extract_ui_texts(self) -> Dict[str, str]:
        """提取UI相关文本"""
        ui_texts = {}
        
        # 1. 从安装程序提取UI文本
        setup_ui_file = self.project_root / "setup" / "utils" / "ui.py"
        if setup_ui_file.exists():
            try:
                content = setup_ui_file.read_text(encoding="utf-8")
                
                # 提取字符串字面量
                string_pattern = r'["\']([^"\']{10,})["\']'
                matches = re.findall(string_pattern, content)
                
                for i, text in enumerate(matches):
                    if self._is_ui_text(text):
                        ui_texts[f"ui_extracted_{i}"] = text
                        
            except Exception as e:
                print(f"Warning: Could not extract UI texts: {e}")
        
        # 2. 添加预定义的UI文本
        ui_texts.update(self._get_default_ui_texts())
        
        return ui_texts
    
    def _extract_error_messages(self) -> Dict[str, str]:
        """提取错误消息"""
        errors = {}
        
        # 扫描Python文件中的错误消息
        python_files = list(self.project_root.rglob("*.py"))[:20]  # 限制文件数量避免过度扫描
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # 查找常见的错误模式
                error_patterns = [
                    r'raise\s+\w+Error\(["\']([^"\']+)["\']',
                    r'print\(["\'](?:Error|ERROR)[^"\']*?([^"\']{10,})["\']',
                    r'logger\.error\(["\']([^"\']+)["\']'
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for i, text in enumerate(matches):
                        if self._is_error_message(text):
                            key = f"error_{py_file.stem}_{i}"
                            errors[key] = text
                            
            except Exception:
                continue  # 忽略读取错误
        
        # 添加预定义的错误消息
        errors.update(self._get_default_error_messages())
        
        return errors
    
    def _extract_help_texts(self) -> Dict[str, str]:
        """提取帮助文本"""
        help_texts = {}
        
        # 从README和文档提取帮助信息
        doc_files = [
            self.project_root / "README.md",
            self.project_root / "Docs" / "superclaude-user-guide.md"
        ]
        
        for doc_file in doc_files:
            if doc_file.exists():
                try:
                    content = doc_file.read_text(encoding="utf-8")
                    
                    # 提取使用示例和说明
                    usage_pattern = r"Usage[:\s]*\n(.*?)(?=\n##|\n\n|\Z)"
                    matches = re.findall(usage_pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    for i, text in enumerate(matches):
                        text = text.strip()
                        if len(text) > 10 and len(text) < 200:
                            help_texts[f"help_{doc_file.stem}_{i}"] = text
                            
                except Exception:
                    continue
        
        # 添加预定义的帮助文本
        help_texts.update(self._get_default_help_texts())
        
        return help_texts
    
    def _is_ui_text(self, text: str) -> bool:
        """判断是否为UI相关文本"""
        ui_indicators = [
            "install", "setup", "config", "welcome", "success", "complete",
            "loading", "progress", "please", "click", "select", "choose"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in ui_indicators)
    
    def _is_error_message(self, text: str) -> bool:
        """判断是否为错误消息"""
        error_indicators = [
            "error", "failed", "cannot", "unable", "not found", "invalid",
            "missing", "denied", "timeout", "exception"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in error_indicators)
    
    # === 默认内容定义 ===
    
    def _get_default_command_descriptions(self) -> Dict[str, str]:
        """获取默认的命令描述"""
        return {
            "analyze": "Multi-dimensional code and system analysis",
            "implement": "Feature and code implementation with intelligent persona activation",
            "build": "Project builder with framework detection", 
            "improve": "Evidence-based code enhancement",
            "design": "Design orchestration",
            "troubleshoot": "Problem investigation",
            "explain": "Educational explanations",
            "cleanup": "Project cleanup and technical debt reduction",
            "document": "Documentation generation",
            "estimate": "Evidence-based estimation", 
            "task": "Long-term project management",
            "test": "Testing workflows",
            "git": "Git workflow assistant",
            "index": "Command catalog browsing",
            "load": "Project context loading",
            "spawn": "Task orchestration",
            "workflow": "Workflow generation and management"
        }
    
    def _get_default_persona_descriptions(self) -> Dict[str, str]:
        """获取默认的Persona描述"""
        return {
            "architect": "Systems architecture specialist, long-term thinking focus, scalability expert",
            "frontend": "UX specialist, accessibility advocate, performance-conscious developer",
            "backend": "Reliability engineer, API specialist, data integrity focus",
            "analyzer": "Root cause specialist, evidence-based investigator, systematic analyst", 
            "security": "Threat modeler, vulnerability specialist",
            "mentor": "Knowledge transfer specialist",
            "refactorer": "Code quality specialist",
            "performance": "Optimization specialist",
            "qa": "Quality advocate, testing specialist",
            "devops": "Infrastructure specialist", 
            "scribe": "Professional writer, documentation specialist, localization expert"
        }
    
    def _get_default_ui_texts(self) -> Dict[str, str]:
        """获取默认的UI文本"""
        return {
            "welcome": "Welcome to SuperClaude installation wizard",
            "installation_success": "Installation completed successfully!",
            "installation_failed": "Installation failed. Please check the logs.",
            "select_components": "Please select components to install:",
            "config_saved": "Configuration saved successfully",
            "loading": "Loading...",
            "processing": "Processing request...",
            "analyzing": "Analyzing code...",
            "building": "Building project...",
            "completed": "Operation completed successfully",
            "cancelled": "Operation cancelled by user",
            "please_wait": "Please wait while we process your request",
            "choose_option": "Please choose an option:",
            "confirm_action": "Are you sure you want to continue?",
            "click_continue": "Click to continue",
            "ready": "Ready",
            "busy": "Busy",
            "connected": "Connected",
            "disconnected": "Disconnected"
        }
    
    def _get_default_error_messages(self) -> Dict[str, str]:
        """获取默认的错误消息"""
        return {
            "file_not_found": "File not found: {filename}",
            "permission_denied": "Permission denied. Please check file permissions",
            "file_already_exists": "File already exists: {filename}", 
            "directory_not_found": "Directory not found: {dirname}",
            "connection_failed": "Connection failed. Please check your network",
            "connection_timeout": "Connection timeout. Please try again",
            "api_error": "API request failed with error: {error}",
            "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
            "invalid_config": "Invalid configuration format",
            "missing_config": "Configuration file not found",
            "config_parse_error": "Error parsing configuration file",
            "component_not_found": "Component not found: {component}",
            "component_load_failed": "Failed to load component: {component}",
            "dependency_missing": "Missing dependency: {dependency}",
            "command_failed": "Command execution failed",
            "invalid_arguments": "Invalid arguments provided",
            "unauthorized_operation": "Unauthorized operation"
        }
    
    def _get_default_help_texts(self) -> Dict[str, str]:
        """获取默认的帮助文本"""
        return {
            "usage_analyze": "Usage: /sc:analyze [target] --focus [domain]",
            "usage_build": "Usage: /sc:build [target] [options]", 
            "usage_improve": "Usage: /sc:improve [target] --focus [quality|performance|security]",
            "feature_personas": "SuperClaude uses intelligent personas to provide specialized expertise",
            "feature_wave_mode": "Wave mode enables multi-stage orchestration for complex operations",
            "feature_mcp_servers": "MCP servers provide enhanced capabilities for specific domains",
            "getting_started": "Getting started with SuperClaude",
            "best_practices": "Best practices for using SuperClaude effectively",
            "troubleshooting": "Common issues and solutions",
            "example_basic": "Basic usage example",
            "example_advanced": "Advanced usage example",
            "see_documentation": "See documentation for more details",
            "refer_to_guide": "Refer to the user guide"
        }
    
    def get_content_statistics(self) -> Dict[str, int]:
        """获取内容统计信息"""
        content = self.extract_all_content()
        
        stats = {}
        total = 0
        for category, items in content.items():
            count = len(items)
            stats[category] = count
            total += count
        
        stats["total"] = total
        return stats
    
    def extract_detailed_content(self) -> List[ExtractedContent]:
        """提取详细的内容信息，包含上下文"""
        detailed_content = []
        content = self.extract_all_content()
        
        for category, items in content.items():
            for key, text in items.items():
                detailed_content.append(ExtractedContent(
                    key=key,
                    text=text,
                    content_type=category,
                    context=self._get_content_context(category, key),
                    file_source=self._get_file_source(category, key)
                ))
        
        return detailed_content
    
    def _get_content_context(self, category: str, key: str) -> str:
        """获取内容的上下文信息"""
        context_map = {
            "commands": "SuperClaude command functionality",
            "personas": "AI expert role characteristics", 
            "ui": "User interface interaction",
            "errors": "Error handling and troubleshooting",
            "help": "User guidance and documentation"
        }
        return context_map.get(category, "General content")
    
    def _get_file_source(self, category: str, key: str) -> Optional[str]:
        """获取内容的源文件"""
        # 这里可以扩展来跟踪具体的源文件
        source_map = {
            "commands": "SuperClaude/Commands/",
            "personas": "SuperClaude/Core/PERSONAS.md",
            "ui": "setup/utils/ui.py",
            "errors": "Various Python files",
            "help": "README.md, Docs/"
        }
        return source_map.get(category)


if __name__ == "__main__":
    # 测试内容提取器
    extractor = SuperClaudeContentExtractor()
    content = extractor.extract_all_content()
    stats = extractor.get_content_statistics()
    
    print("SuperClaude Content Statistics:")
    for category, count in stats.items():
        print(f"  {category}: {count} items")
    
    print("\nSample content:")
    for category, items in content.items():
        print(f"\n{category.upper()}:")
        for key, text in list(items.items())[:2]:
            print(f"  {key}: {text[:60]}...")