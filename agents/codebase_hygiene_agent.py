#!/usr/bin/env python3
"""
Codebase Hygiene Agent - Keeps Repository Clean and Organized
Prevents accumulation of unused/broken files and maintains code quality
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timedelta

class CodebaseHygieneAgent:
    """Maintains codebase cleanliness and prevents technical debt accumulation"""

    def __init__(self, repo_path: str = "/Users/chungty/Projects/vdg-clean/abm-research"):
        self.repo_path = Path(repo_path)
        self.cleanup_log = []
        self.file_patterns = {
            'temporary': ['*temp*', '*tmp*', '*test*', '*mock*', '*debug*'],
            'backup': ['*.backup', '*.bak', '*.old'],
            'generated': ['*generated*', '*auto*'],
            'duplicate': []  # Will be identified by analysis
        }

        print("🧹 Codebase Hygiene Agent initialized")
        print(f"🎯 Monitoring: {repo_path}")

    def analyze_codebase_health(self) -> Dict:
        """Analyze codebase for cleanliness issues"""

        print("\n🔍 ANALYZING CODEBASE HEALTH...")

        analysis = {
            'total_files': 0,
            'issues_found': {
                'unused_files': [],
                'duplicate_files': [],
                'temporary_files': [],
                'large_files': [],
                'broken_imports': []
            },
            'recommendations': []
        }

        # Scan all Python files
        python_files = list(self.repo_path.glob('**/*.py'))
        analysis['total_files'] = len(python_files)

        print(f"📊 Found {len(python_files)} Python files")

        # Check for unused files
        unused = self._find_unused_files(python_files)
        analysis['issues_found']['unused_files'] = unused

        # Check for duplicates
        duplicates = self._find_duplicate_files(python_files)
        analysis['issues_found']['duplicate_files'] = duplicates

        # Check for temporary files
        temp_files = self._find_temporary_files()
        analysis['issues_found']['temporary_files'] = temp_files

        # Check for large files
        large_files = self._find_large_files()
        analysis['issues_found']['large_files'] = large_files

        # Generate recommendations
        analysis['recommendations'] = self._generate_cleanup_recommendations(analysis)

        self._print_analysis_summary(analysis)
        return analysis

    def _find_unused_files(self, python_files: List[Path]) -> List[str]:
        """Find Python files that are never imported or executed"""

        print("   🔍 Checking for unused files...")

        # Get all import statements across codebase
        imported_modules = set()
        executed_files = set()

        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Check if file has if __name__ == "__main__"
                if 'if __name__ == "__main__"' in content:
                    executed_files.add(file_path.name.replace('.py', ''))

                # Extract import statements
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('from ') and ' import ' in line:
                        module = line.split(' import ')[0].replace('from ', '').strip()
                        if not module.startswith('.'):  # Ignore relative imports for now
                            imported_modules.add(module)
                    elif line.startswith('import '):
                        module = line.replace('import ', '').split(',')[0].split(' as ')[0].strip()
                        imported_modules.add(module)

            except Exception as e:
                print(f"      ⚠️ Error reading {file_path}: {e}")
                continue

        # Find files that are never imported or executed
        unused = []
        for file_path in python_files:
            filename = file_path.name.replace('.py', '')

            # Skip if it's a main execution file
            if filename in executed_files:
                continue

            # Skip if it's imported
            if filename in imported_modules:
                continue

            # Skip special files
            if filename.startswith('__') or filename in ['setup', 'config']:
                continue

            unused.append(str(file_path.relative_to(self.repo_path)))

        print(f"      📋 Found {len(unused)} potentially unused files")
        return unused

    def _find_duplicate_files(self, python_files: List[Path]) -> List[Dict]:
        """Find files with similar names or identical content"""

        print("   🔍 Checking for duplicate files...")

        duplicates = []

        # Group by similar names
        name_groups = {}
        for file_path in python_files:
            base_name = file_path.name.replace('.py', '')

            # Look for naming patterns that suggest duplicates
            for existing_name in name_groups:
                if (base_name in existing_name or existing_name in base_name or
                    base_name.replace('_', '') == existing_name.replace('_', '') or
                    base_name.endswith('_v2') or base_name.endswith('_new') or
                    existing_name.endswith('_v2') or existing_name.endswith('_new')):

                    if existing_name not in name_groups:
                        name_groups[existing_name] = []
                    name_groups[existing_name].append(str(file_path.relative_to(self.repo_path)))
                    break
            else:
                name_groups[base_name] = [str(file_path.relative_to(self.repo_path))]

        # Filter groups with more than 1 file
        for name, files in name_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'pattern': name,
                    'files': files
                })

        print(f"      📋 Found {len(duplicates)} duplicate file groups")
        return duplicates

    def _find_temporary_files(self) -> List[str]:
        """Find temporary, test, or debug files"""

        print("   🔍 Checking for temporary files...")

        temp_files = []

        for pattern in self.file_patterns['temporary'] + self.file_patterns['backup']:
            matches = list(self.repo_path.glob(f'**/{pattern}'))
            for match in matches:
                if match.is_file():
                    temp_files.append(str(match.relative_to(self.repo_path)))

        print(f"      📋 Found {len(temp_files)} temporary files")
        return temp_files

    def _find_large_files(self, size_limit_mb: int = 5) -> List[Dict]:
        """Find unusually large files that might need attention"""

        print(f"   🔍 Checking for files larger than {size_limit_mb}MB...")

        large_files = []

        for file_path in self.repo_path.glob('**/*'):
            if file_path.is_file():
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > size_limit_mb:
                        large_files.append({
                            'file': str(file_path.relative_to(self.repo_path)),
                            'size_mb': round(size_mb, 2)
                        })
                except Exception:
                    continue

        print(f"      📋 Found {len(large_files)} large files")
        return large_files

    def _generate_cleanup_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable cleanup recommendations"""

        recommendations = []

        if analysis['issues_found']['unused_files']:
            recommendations.append(f"🗑️ REMOVE {len(analysis['issues_found']['unused_files'])} unused files")

        if analysis['issues_found']['duplicate_files']:
            recommendations.append(f"🔄 CONSOLIDATE {len(analysis['issues_found']['duplicate_files'])} duplicate file groups")

        if analysis['issues_found']['temporary_files']:
            recommendations.append(f"🧹 CLEAN {len(analysis['issues_found']['temporary_files'])} temporary files")

        if analysis['issues_found']['large_files']:
            recommendations.append(f"📦 REVIEW {len(analysis['issues_found']['large_files'])} large files")

        # Repository structure recommendations
        if analysis['total_files'] > 20:
            recommendations.append("📁 ORGANIZE into logical subdirectories (agents/, core/, dashboard/)")

        recommendations.append("📋 CREATE agents/README.md documenting each agent's purpose")
        recommendations.append("🔧 STANDARDIZE naming convention (snake_case for all modules)")

        return recommendations

    def _print_analysis_summary(self, analysis: Dict):
        """Print comprehensive analysis summary"""

        print(f"\n📋 CODEBASE HEALTH ANALYSIS")
        print("=" * 50)
        print(f"Total Files: {analysis['total_files']}")

        total_issues = sum(
            len(issues) if isinstance(issues, list) else len(issues)
            for issues in analysis['issues_found'].values()
        )

        print(f"Issues Found: {total_issues}")

        for issue_type, issues in analysis['issues_found'].items():
            if issues:
                print(f"   • {issue_type.replace('_', ' ').title()}: {len(issues)}")

        print(f"\n🎯 CLEANUP RECOMMENDATIONS:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"   {i}. {rec}")

        health_score = max(0, 100 - (total_issues * 5))
        print(f"\n📊 HEALTH SCORE: {health_score}/100")

    def execute_safe_cleanup(self, analysis: Dict, confirm_destructive: bool = False) -> Dict:
        """Execute safe cleanup operations (non-destructive by default)"""

        print(f"\n🧹 EXECUTING SAFE CLEANUP...")

        cleanup_results = {
            'files_moved': [],
            'files_removed': [],
            'directories_created': [],
            'warnings': []
        }

        # Create organized directory structure
        agent_dir = self.repo_path / 'agents'
        if not agent_dir.exists():
            agent_dir.mkdir()
            cleanup_results['directories_created'].append('agents/')
            print("   📁 Created agents/ directory")

        core_dir = self.repo_path / 'core'
        if not core_dir.exists():
            core_dir.mkdir()
            cleanup_results['directories_created'].append('core/')
            print("   📁 Created core/ directory")

        dashboard_dir = self.repo_path / 'dashboard'
        if not dashboard_dir.exists():
            dashboard_dir.mkdir()
            cleanup_results['directories_created'].append('dashboard/')
            print("   📁 Created dashboard/ directory")

        # Move files to appropriate directories (safe operation)
        python_files = list(self.repo_path.glob('*.py'))
        for file_path in python_files:
            filename = file_path.name.lower()

            if 'agent' in filename:
                target = agent_dir / file_path.name
                if not target.exists():
                    file_path.rename(target)
                    cleanup_results['files_moved'].append(f"{file_path.name} → agents/")
                    print(f"   📦 Moved {file_path.name} to agents/")

            elif 'dashboard' in filename or 'server' in filename:
                target = dashboard_dir / file_path.name
                if not target.exists():
                    file_path.rename(target)
                    cleanup_results['files_moved'].append(f"{file_path.name} → dashboard/")
                    print(f"   📦 Moved {file_path.name} to dashboard/")

            elif 'comprehensive' in filename or 'system' in filename:
                target = core_dir / file_path.name
                if not target.exists():
                    file_path.rename(target)
                    cleanup_results['files_moved'].append(f"{file_path.name} → core/")
                    print(f"   📦 Moved {file_path.name} to core/")

        # Remove temporary files (destructive - requires confirmation)
        if confirm_destructive and analysis['issues_found']['temporary_files']:
            for temp_file in analysis['issues_found']['temporary_files']:
                file_path = self.repo_path / temp_file
                if file_path.exists():
                    file_path.unlink()
                    cleanup_results['files_removed'].append(temp_file)
                    print(f"   🗑️ Removed {temp_file}")

        print(f"\n✅ Cleanup completed:")
        print(f"   📦 Files moved: {len(cleanup_results['files_moved'])}")
        print(f"   🗑️ Files removed: {len(cleanup_results['files_removed'])}")
        print(f"   📁 Directories created: {len(cleanup_results['directories_created'])}")

        return cleanup_results

    def create_agent_documentation(self):
        """Create documentation for agent architecture"""

        agents_readme = self.repo_path / 'agents' / 'README.md'

        readme_content = """# ABM Research Agents

This directory contains the agent architecture for the Verdigris ABM research system.

## Agent Architecture

### 1. QA Verification Agent (`qa_verification_agent.py`)
**Purpose**: Tests every claim before marking tasks complete
- Verifies Notion databases exist and are accessible
- Confirms data population in all databases
- Validates 5-phase workflow completeness
- Prevents false success reporting

### 2. Product Design Agent (`product_design_agent.py`)
**Purpose**: Holds process accountable to skill specification
- Reviews implementations against SKILL.md
- Ensures 5-phase workflow compliance
- Validates salesperson persona requirements

### 3. Data Pipeline Agent (`data_pipeline_agent.py`)
**Purpose**: Owns research-to-Notion data flow
- Executes complete 5-phase ABM research
- Populates all 4 Notion databases correctly
- Handles API errors and retries

### 4. Codebase Hygiene Agent (`codebase_hygiene_agent.py`)
**Purpose**: Maintains repository cleanliness
- Identifies unused/duplicate files
- Organizes code into logical directories
- Prevents technical debt accumulation

### 5. System Integration Agent (`system_integration_agent.py`)
**Purpose**: End-to-end workflow orchestration
- Coordinates all agents in proper sequence
- Ensures dependencies are met
- Maintains system state

## Usage

Each agent can be run independently or orchestrated through the System Integration Agent.

```python
# Run QA verification
python agents/qa_verification_agent.py

# Execute full workflow
python agents/system_integration_agent.py
```

## Sequential Gates

Agents must pass QA verification before proceeding:
1. Product Design approves requirements
2. Data Pipeline completes research + Notion population
3. QA Verification confirms accessibility
4. Dashboard Integration builds on verified foundation
5. System Integration tests complete workflow
"""

        with open(agents_readme, 'w') as f:
            f.write(readme_content)

        print(f"   📋 Created agents/README.md")


if __name__ == "__main__":
    hygiene_agent = CodebaseHygieneAgent()

    # Analyze codebase health
    analysis = hygiene_agent.analyze_codebase_health()

    # Execute safe cleanup
    cleanup_results = hygiene_agent.execute_safe_cleanup(analysis, confirm_destructive=False)

    # Create agent documentation
    hygiene_agent.create_agent_documentation()