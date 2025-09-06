# project_manager.py
import subprocess
import json
import os
import glob
from pathlib import Path
from datetime import datetime

class ProjectManager:
    def __init__(self, base_path):
        self.base_path = base_path
        if base_path.startswith("~"):
            self.base_path = os.path.expanduser(base_path)
        
        # Get the path to the semgrep executable in the virtual environment
        self.semgrep_path = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'semgrep.exe')
        
    def detect_languages(self):
        """Automatically detect programming languages used in the project."""
        print(f"[ProjectManager] Detecting languages in {self.base_path}...")
        
        language_extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby',
            '.go': 'Go', '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.xml': 'XML',
            '.json': 'JSON', '.yml': 'YAML', '.yaml': 'YAML'
        }
        
        language_counts = {}
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext in language_extensions:
                        language = language_extensions[ext]
                        language_counts[language] = language_counts.get(language, 0) + 1
                        file_count += 1
            
            return {"languages": language_counts, "total_files": file_count}
        except Exception as e:
            print(f"[ProjectManager] Language detection failed: {e}")
            return {"error": str(e)}
    
    def get_file_structure(self):
        """Get the project's file structure."""
        structure = {"files": [], "directories": []}
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Skip virtual environments and hidden directories
                if any(part.startswith('.') or part in ['venv', '.venv', 'node_modules'] 
                      for part in root.split(os.path.sep)):
                    continue
                
                for file in files:
                    if not file.startswith('.'):
                        structure["files"].append(os.path.join(root, file))
                
                for dir in dirs:
                    if not dir.startswith('.'):
                        structure["directories"].append(os.path.join(root, dir))
            
            return structure
        except Exception as e:
            print(f"[ProjectManager] File structure analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_file_contents(self):
        """Automatically read and analyze project files."""
        print(f"[ProjectManager] Analyzing file contents in {self.base_path}...")
        
        code_content = {}
        important_files = ['main.py', 'example.py', 'app.py', 'index.py', 'requirements.txt', 
                          'package.json', 'dockerfile', 'docker-compose.yml']
        
        for file in important_files:
            file_path = os.path.join(self.base_path, file)
            if os.path.exists(file_path):
                try:
                    # Try UTF-8 first
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_content[file] = f.read()
                except UnicodeDecodeError:
                    try:
                        # Fallback to UTF-16 (common Windows issue)
                        with open(file_path, 'r', encoding='utf-16') as f:
                            code_content[file] = f.read()
                    except Exception as e:
                        code_content[file] = f"Error reading {file}: {str(e)}"
                except Exception as e:
                    code_content[file] = f"Error reading {file}: {str(e)}"
        
        return code_content
    
    def detect_frameworks(self, code_content):
        """Automatically detect which web framework is actually used."""
        framework_indicators = {
            'flask': ['from flask', 'import Flask', '@app.route', 'flask.Flask'],
            'django': ['from django', 'DJANGO_SETTINGS', 'django.db', 'django.contrib'],
            'fastapi': ['from fastapi', 'import FastAPI', 'fastapi.FastAPI'],
            'express': ['require("express")', 'const express =', 'express()'],
            'react': ['import React', 'react-dom', 'JSX', 'useState'],
            'vue': ['import Vue', 'new Vue', 'vue-create'],
            'angular': ['@angular', 'import { Component }', 'angular.module']
        }
        
        detected_frameworks = set()
        for file_name, content in code_content.items():
            if isinstance(content, str):
                for framework, indicators in framework_indicators.items():
                    if any(indicator.lower() in content.lower() for indicator in indicators):
                        detected_frameworks.add(framework)
        
        return list(detected_frameworks)
    
    def run_scan(self):
        """Run comprehensive code analysis with enhanced error handling."""
        print(f"[ProjectManager] Running comprehensive scan on {self.base_path}...")
        
        results = {
            "languages": self.detect_languages(),
            "structure": self.get_file_structure(),
            "file_contents": self.analyze_file_contents(),
            "semgrep_scan": self._run_semgrep_with_fallback(),
            "potential_issues": self._identify_potential_issues()
        }
        
        # Detect frameworks from file contents
        if "file_contents" in results:
            results["detected_frameworks"] = self.detect_frameworks(results["file_contents"])
        
        return results
    
    def _run_semgrep_with_fallback(self):
        """Run Semgrep with multiple fallback strategies."""
        print("[ProjectManager] Running Semgrep analysis...")
        
        # Try multiple Semgrep strategies
        strategies = [
            self._run_semgrep_basic,
            self._run_semgrep_security,
            self._run_semgrep_auto
        ]
        
        for strategy in strategies:
            result = strategy()
            if result and not result.get("error"):
                return result
        
        # If all strategies failed
        return {"error": "All Semgrep scanning strategies failed", "suggested_fix": "Check Semgrep installation: pip install semgrep"}
    
    def _run_semgrep_basic(self):
        """Basic Semgrep pattern matching."""
        try:
            cmd = [self.semgrep_path, '--pattern', 'def $F(...): ...', '--json', self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr, "returncode": result.returncode}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_semgrep_security(self):
        """Semgrep with security rules."""
        try:
            cmd = [self.semgrep_path, '--config', 'p/security-audit', '--json', self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_semgrep_auto(self):
        """Semgrep with auto-configuration."""
        try:
            cmd = [self.semgrep_path, '--config', 'auto', '--json', self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _identify_potential_issues(self):
        """Identify potential issues through basic file analysis."""
        issues = []
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check for common problematic files
                    if file in ['.env', 'config.json', 'secrets.txt', 'credentials.json']:
                        issues.append(f"Potential sensitive file: {file_path}")
                    
                    # Check file permissions (Unix-like systems)
                    if hasattr(os, 'stat'):
                        try:
                            stat_info = os.stat(file_path)
                            if stat_info.st_mode & 0o777 == 0o777:  # World-writable
                                issues.append(f"World-writable file: {file_path}")
                        except:
                            pass
            
            return issues
        except Exception as e:
            return [f"Error in issue identification: {str(e)}"]
    
    def run_audit(self):
        """Run comprehensive dependency audit with enhanced error handling."""
        print(f"[ProjectManager] Auditing dependencies in {self.base_path}...")
        
        results = {
            "osv_scanner": self._run_osv_audit_with_fallback(),
            "dependency_files": self._find_dependency_files(),
            "manual_checks": self._manual_dependency_checks()
        }
        
        return results
    
    def _run_osv_audit_with_fallback(self):
        """Run OSV-Scanner with multiple fallback strategies."""
        print("[ProjectManager] Running OSV-Scanner analysis...")
        
        # Try multiple OSV-Scanner strategies
        strategies = [
            self._run_osv_audit_standard,
            self._run_osv_audit_recursive,
            self._run_osv_audit_lockfile
        ]
        
        for strategy in strategies:
            result = strategy()
            if result and not result.get("error"):
                return result
        
        # If all strategies failed
        return {"error": "All OSV-Scanner strategies failed", "suggested_fix": "Install OSV-Scanner: winget install Google.OSVScanner"}
    
    def _run_osv_audit_standard(self):
        """Standard OSV-Scanner execution."""
        try:
            cmd = ['osv-scanner', '--json', self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr, "returncode": result.returncode}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_osv_audit_recursive(self):
        """OSV-Scanner with recursive flag."""
        try:
            cmd = ['osv-scanner', '--recursive', '--json', self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_osv_audit_lockfile(self):
        """OSV-Scanner targeting lock files."""
        try:
            cmd = ['osv-scanner', '--lockfile', self.base_path, '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _find_dependency_files(self):
        """Find and analyze dependency files."""
        dependency_files = {
            'requirements.txt': None,
            'package.json': None,
            'pom.xml': None,
            'build.gradle': None,
            'go.mod': None,
            'Cargo.toml': None,
            'composer.json': None,
            'Gemfile': None
        }
        
        for dep_file in dependency_files.keys():
            file_path = os.path.join(self.base_path, dep_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # First 1000 chars
                        dependency_files[dep_file] = {
                            'exists': True,
                            'content': content,
                            'encoding': 'utf-8'
                        }
                except UnicodeDecodeError:
                    try:
                        # Try UTF-16 encoding (common Windows issue)
                        with open(file_path, 'r', encoding='utf-16') as f:
                            content = f.read(1000)
                            dependency_files[dep_file] = {
                                'exists': True,
                                'content': content,
                                'encoding': 'utf-16',
                                'warning': 'UTF-16 encoding may cause issues with some tools'
                            }
                    except Exception as e:
                        dependency_files[dep_file] = {'exists': True, 'error': str(e)}
                except Exception as e:
                    dependency_files[dep_file] = {'exists': True, 'error': str(e)}
        
        return dependency_files
    
    def _manual_dependency_checks(self):
        """Perform manual checks for common dependency issues."""
        checks = []
        
        # Check for common problematic patterns
        requirements_path = os.path.join(self.base_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    content = f.read()
                    
                    # Check version pinning
                    if '==' not in content and '>=' not in content:
                        checks.append("requirements.txt might not have version pinning")
                    
                    # Check for outdated packages
                    outdated_indicators = ['requests==2.25', 'flask==1.1', 'django==3.1', 'numpy==1.19']
                    for indicator in outdated_indicators:
                        if indicator in content:
                            checks.append(f"Outdated package detected: {indicator}")
                            
            except Exception as e:
                checks.append(f"Error reading requirements.txt: {str(e)}")
        
        return checks
    
    def generate_requirements_fix(self, current_content):
        """Generate updated requirements.txt content with secure versions."""
        version_updates = {
            'requests': '>=2.31.0',
            'flask': '>=2.3.3', 
            'django': '>=4.2.4',
            'numpy': '>=1.24.0',
            'setuptools': '>=68.0.0'
        }
        
        if not current_content:
            return "# No requirements.txt content available for fixing"
        
        updated_lines = []
        for line in current_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                updated_lines.append(line)
                continue
                
            updated = False
            for pkg, new_version in version_updates.items():
                if line.startswith(pkg + '=='):
                    updated_lines.append(f"{pkg}{new_version}")
                    updated = True
                    break
            
            if not updated:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def get_summary(self):
        """Generate a comprehensive project summary."""
        scan_results = self.run_scan()
        audit_results = self.run_audit()
        
        # Generate fixes if requirements.txt content is available
        requirements_fix = None
        if ('dependency_files' in audit_results and 
            'requirements.txt' in audit_results['dependency_files'] and
            audit_results['dependency_files']['requirements.txt'] and
            'content' in audit_results['dependency_files']['requirements.txt']):
            
            req_content = audit_results['dependency_files']['requirements.txt']['content']
            requirements_fix = self.generate_requirements_fix(req_content)
        
        return {
            "code_analysis": scan_results,
            "dependency_analysis": audit_results,
            "generated_fixes": {
                "requirements_txt": requirements_fix
            },
            "path": self.base_path,
            "timestamp": str(datetime.now())
        }