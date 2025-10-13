"""
wembed_core/chunker/dependency_analyzer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Analyzes Python project dependencies and builds a usage graph.
This module provides the DependencyAnalyzer class which scans Python files
for import statements, determines the source of each dependency (standard library,
third-party packages, or local modules), and builds a graph of dependencies
between modules.
"""

import ast
import importlib
import json
import os
from dataclasses import asdict
from typing import Dict, List, Optional, Set

from wembed_core.constants.stdlib_modules import STD_LIB_MODULES
from wembed_core.schemas import DependencyNode, ImportStatement


class DependencyAnalyzer:
    """Analyzes Python dependencies and creates usage graphs"""

    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.dependencies: Dict[str, DependencyNode] = {}
        self.imports: List[ImportStatement] = []
        self.local_modules: Set[str] = set()
        self.stdlib_modules = STD_LIB_MODULES

    def discover_local_modules(self) -> Set[str]:
        """Discover all local Python modules in the project"""
        local_modules = set()

        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common non-code directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)

                    # Convert file path to module name
                    module_name = rel_path.replace(os.sep, ".").replace(".py", "")
                    local_modules.add(module_name)

                    # Also add package names
                    parts = module_name.split(".")
                    for i in range(1, len(parts)):
                        package_name = ".".join(parts[:i])
                        local_modules.add(package_name)

        self.local_modules = local_modules
        return local_modules

    def analyze_file(self, file_path: str) -> List[ImportStatement]:
        """Analyze imports in a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_stmt = ImportStatement(
                        module=alias.name,
                        names=[alias.name],
                        alias=alias.asname,
                        file_path=file_path,
                        line_number=node.lineno,
                        is_from_import=False,
                    )
                    imports.append(import_stmt)

            elif isinstance(node, ast.ImportFrom):
                if node.module:  # Handle "from module import ..."
                    names = [alias.name for alias in node.names]
                    import_stmt = ImportStatement(
                        module=node.module,
                        names=names,
                        alias=None,
                        file_path=file_path,
                        line_number=node.lineno,
                        is_from_import=True,
                    )
                    imports.append(import_stmt)

        self.imports.extend(imports)
        return imports

    def analyze_project(self) -> Dict[str, DependencyNode]:
        """Analyze all dependencies in the project"""
        self.discover_local_modules()

        # Analyze all Python files
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d for d in dirs if not d.startswith(".") and d not in ["__pycache__"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)

        # Process all imports to build dependency graph
        for import_stmt in self.imports:
            self._process_import(import_stmt)

        # Load external dependencies from requirements files
        self._load_requirements()

        return self.dependencies

    def _process_import(self, import_stmt: ImportStatement):
        """Process a single import statement"""
        module = import_stmt.module

        # Determine dependency source
        source = self._determine_source(module)

        # Get or create dependency node
        if module not in self.dependencies:
            version = None
            if source == "external":
                version = self._get_package_version(module)

            self.dependencies[module] = DependencyNode(
                name=module,
                version=version,
                source=source,
                file_path=(
                    self._get_module_file_path(module) if source == "local" else None
                ),
                used_by=set(),
                imports=set(),
            )

        # Add usage relationship
        self.dependencies[module].used_by.add(import_stmt.file_path)
        self.dependencies[module].imports.update(import_stmt.names)
        self.dependencies[module].is_used = True

    def _determine_source(self, module: str) -> str:
        """Determine if a module is stdlib, local, or external"""
        # Check if it's a local module
        if any(module.startswith(local) for local in self.local_modules):
            return "local"

        # Check if it's stdlib
        root_module = module.split(".")[0]
        if root_module in self.stdlib_modules:
            return "stdlib"

        # Otherwise, it's external
        return "external"

    def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get the version of an installed package using importlib.metadata"""
        try:
            # Try the root module name first
            root_module = package_name.split(".")[0]
            return importlib.metadata.version(root_module)
        except importlib.metadata.PackageNotFoundError:
            try:
                # Fallback to the full package name
                return importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                return None

    def _get_module_file_path(self, module: str) -> Optional[str]:
        """Get the file path for a local module"""
        # Convert module name to file path
        parts = module.split(".")
        potential_paths = [
            os.path.join(self.project_root, *parts) + ".py",
            os.path.join(self.project_root, *parts, "__init__.py"),
        ]

        for path in potential_paths:
            if os.path.exists(path):
                return path

        return None

    def _load_requirements(self):
        """Load dependencies from requirements.txt and similar files"""
        req_files = [
            "requirements.txt",
            "requirements.in",
            "setup.py",
            "pyproject.toml",
        ]

        for req_file in req_files:
            req_path = os.path.join(self.project_root, req_file)
            if os.path.exists(req_path):
                if req_file.endswith(".txt") or req_file.endswith(".in"):
                    self._parse_requirements_txt(req_path)
                elif req_file == "setup.py":
                    self._parse_setup_py(req_path)
                elif req_file == "pyproject.toml":
                    self._parse_pyproject_toml(req_path)

    def _parse_requirements_txt(self, file_path: str):
        """Parse requirements.txt file"""
        # This is a placeholder for actual parsing logic
        pass

    def _parse_setup_py(self, file_path: str):
        """Parse setup.py file"""
        # This is a placeholder for actual parsing logic
        pass

    def _parse_pyproject_toml(self, file_path: str):
        """Parse pyproject.toml file"""
        # This is a placeholder for actual parsing logic
        pass

    def get_unused_dependencies(self) -> List[DependencyNode]:
        """Get a list of dependencies that are loaded but not used"""
        return [dep for dep in self.dependencies.values() if not dep.is_used]

    def export_analysis(self, output_path: str):
        """Export the dependency analysis to a JSON file"""
        export_data = {
            "project_root": self.project_root,
            "dependencies": {name: asdict(d) for name, d in self.dependencies.items()},
            "imports": [asdict(i) for i in self.imports],
        }

        # Convert sets to lists for JSON serialization
        for dep in export_data["dependencies"].values():
            dep["used_by"] = list(dep["used_by"])
            dep["imports"] = list(dep["imports"])

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
            print(f"Dependency analysis exported to {output_path}")
        except Exception as e:
            print(f"Error exporting dependency analysis: {e}")

    def print_summary(self):
        """Print a summary of the dependency analysis"""
        if not self.dependencies:
            print("\nDependency Analysis Summary: No dependencies found.")
            return

        external_deps = [
            d for d in self.dependencies.values() if d.source == "external"
        ]
        local_deps = [d for d in self.dependencies.values() if d.source == "local"]
        stdlib_deps = [d for d in self.dependencies.values() if d.source == "stdlib"]

        print("\nDependency Analysis Summary:")
        print(f"  Total unique dependencies: {len(self.dependencies)}")
        print(f"  External dependencies: {len(external_deps)}")
        print(f"  Local modules: {len(local_deps)}")
        print(f"  Standard library modules: {len(stdlib_deps)}")

        if external_deps:
            print("\nTop 5 external dependencies (by usage):")
            # Sort by the number of files using the dependency
            sorted_deps = sorted(
                external_deps, key=lambda d: len(d.used_by), reverse=True
            )
            for dep in sorted_deps[:5]:
                print(f"  - {dep.name} (used in {len(dep.used_by)} files)")
