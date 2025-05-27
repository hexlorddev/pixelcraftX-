import os
import json
import inspect
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PluginDocumentation:
    def __init__(self, output_dir: str = "docs/plugins"):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure the documentation output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_docs(self, plugin_name: str, plugin_module: Any, metadata: Dict = None) -> bool:
        """Generate documentation for a specific plugin."""
        try:
            doc_data = {
                'name': plugin_name,
                'metadata': metadata or {},
                'generated_at': datetime.now().isoformat(),
                'functions': self._extract_functions(plugin_module),
                'classes': self._extract_classes(plugin_module),
                'attributes': self._extract_attributes(plugin_module)
            }
            
            # Generate markdown
            markdown = self._generate_markdown(doc_data)
            
            # Save documentation
            output_path = os.path.join(self.output_dir, f"{plugin_name}.md")
            with open(output_path, 'w') as f:
                f.write(markdown)
            
            # Save raw data
            json_path = os.path.join(self.output_dir, f"{plugin_name}.json")
            with open(json_path, 'w') as f:
                json.dump(doc_data, f, indent=4)
            
            logger.info(f"Generated documentation for plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error generating documentation for {plugin_name}: {e}")
            return False
    
    def _extract_functions(self, module: Any) -> List[Dict]:
        """Extract function information from a module."""
        functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                functions.append({
                    'name': name,
                    'doc': inspect.getdoc(obj) or '',
                    'signature': str(inspect.signature(obj)),
                    'args': self._get_function_args(obj)
                })
        return functions
    
    def _extract_classes(self, module: Any) -> List[Dict]:
        """Extract class information from a module."""
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                classes.append({
                    'name': name,
                    'doc': inspect.getdoc(obj) or '',
                    'methods': self._extract_methods(obj),
                    'attributes': self._extract_class_attributes(obj)
                })
        return classes
    
    def _extract_methods(self, cls: type) -> List[Dict]:
        """Extract method information from a class."""
        methods = []
        for name, obj in inspect.getmembers(cls):
            if inspect.isfunction(obj):
                methods.append({
                    'name': name,
                    'doc': inspect.getdoc(obj) or '',
                    'signature': str(inspect.signature(obj)),
                    'args': self._get_function_args(obj)
                })
        return methods
    
    def _extract_class_attributes(self, cls: type) -> List[Dict]:
        """Extract attribute information from a class."""
        attributes = []
        for name, obj in inspect.getmembers(cls):
            if not name.startswith('_') and not inspect.isfunction(obj):
                attributes.append({
                    'name': name,
                    'type': type(obj).__name__,
                    'value': str(obj)
                })
        return attributes
    
    def _extract_attributes(self, module: Any) -> List[Dict]:
        """Extract module-level attributes."""
        attributes = []
        for name, obj in inspect.getmembers(module):
            if not name.startswith('_') and not inspect.isfunction(obj) and not inspect.isclass(obj):
                attributes.append({
                    'name': name,
                    'type': type(obj).__name__,
                    'value': str(obj)
                })
        return attributes
    
    def _get_function_args(self, func: callable) -> List[Dict]:
        """Get function argument information."""
        args = []
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            args.append({
                'name': name,
                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                'default': str(param.default) if param.default != inspect.Parameter.empty else None
            })
        return args
    
    def _generate_markdown(self, doc_data: Dict) -> str:
        """Generate markdown documentation from plugin data."""
        md = f"# {doc_data['name']}\n\n"
        
        # Metadata
        if doc_data['metadata']:
            md += "## Metadata\n\n"
            for key, value in doc_data['metadata'].items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        # Functions
        if doc_data['functions']:
            md += "## Functions\n\n"
            for func in doc_data['functions']:
                md += f"### {func['name']}\n\n"
                if func['doc']:
                    md += f"{func['doc']}\n\n"
                md += f"```python\n{func['name']}{func['signature']}\n```\n\n"
                if func['args']:
                    md += "**Arguments:**\n\n"
                    for arg in func['args']:
                        md += f"- `{arg['name']}`: {arg['type']}"
                        if arg['default']:
                            md += f" (default: {arg['default']})"
                        md += "\n"
                md += "\n"
        
        # Classes
        if doc_data['classes']:
            md += "## Classes\n\n"
            for cls in doc_data['classes']:
                md += f"### {cls['name']}\n\n"
                if cls['doc']:
                    md += f"{cls['doc']}\n\n"
                
                if cls['methods']:
                    md += "#### Methods\n\n"
                    for method in cls['methods']:
                        md += f"##### {method['name']}\n\n"
                        if method['doc']:
                            md += f"{method['doc']}\n\n"
                        md += f"```python\n{method['name']}{method['signature']}\n```\n\n"
                
                if cls['attributes']:
                    md += "#### Attributes\n\n"
                    for attr in cls['attributes']:
                        md += f"- `{attr['name']}`: {attr['type']} = {attr['value']}\n"
                md += "\n"
        
        # Module Attributes
        if doc_data['attributes']:
            md += "## Module Attributes\n\n"
            for attr in doc_data['attributes']:
                md += f"- `{attr['name']}`: {attr['type']} = {attr['value']}\n"
        
        return md 