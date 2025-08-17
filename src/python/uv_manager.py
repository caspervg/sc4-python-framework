"""
UV Package Manager Integration for SC4 Python Framework

This module provides integration with the uv package manager for handling
Python dependencies in SC4 plugins.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union

class UVManager:
    """
    Manager for uv package operations in SC4 Python environment.
    """
    
    def __init__(self, uv_path: Optional[str] = None):
        """
        Initialize UV manager.
        
        Args:
            uv_path: Path to uv executable. If None, will try to find it.
        """
        self.logger = logging.getLogger(__name__)
        self.uv_path = uv_path or self._find_uv_executable()
        self.python_path = None
        self.venv_path = None
        
        if not self.uv_path:
            self.logger.warning("UV executable not found. Package management will be limited.")
    
    def _find_uv_executable(self) -> Optional[str]:
        """
        Find the uv executable.
        
        Returns:
            Path to uv executable or None if not found
        """
        # Check common locations
        possible_paths = [
            "uv.exe",  # In PATH
            "./vendor/uv/uv.exe",  # Local vendor directory
            os.path.join(os.path.dirname(__file__), "..", "..", "vendor", "uv", "uv.exe"),
        ]
        
        for path in possible_paths:
            if self._check_uv_executable(path):
                self.logger.info(f"Found uv executable at: {path}")
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(["where", "uv"], capture_output=True, text=True)
            if result.returncode == 0:
                uv_path = result.stdout.strip().split('\n')[0]
                if self._check_uv_executable(uv_path):
                    return uv_path
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return None
    
    def _check_uv_executable(self, path: str) -> bool:
        """
        Check if a path is a valid uv executable.
        
        Args:
            path: Path to check
            
        Returns:
            True if valid uv executable
        """
        try:
            if not os.path.exists(path):
                return False
            
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and "uv" in result.stdout.lower()
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def create_venv(self, venv_path: str, python_version: str = "3.11") -> bool:
        """
        Create a virtual environment using uv.
        
        Args:
            venv_path: Path where to create the virtual environment
            python_version: Python version to use
            
        Returns:
            True if successful
        """
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return False
        
        try:
            cmd = [self.uv_path, "venv", venv_path, "--python", python_version]
            
            self.logger.info(f"Creating virtual environment at: {venv_path}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.venv_path = venv_path
                self.python_path = self._get_venv_python_path(venv_path)
                self.logger.info("Virtual environment created successfully")
                return True
            else:
                self.logger.error(f"Failed to create venv: {result.stderr}")
                return False
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error creating virtual environment: {e}")
            return False
    
    def _get_venv_python_path(self, venv_path: str) -> str:
        """
        Get the Python executable path in a virtual environment.
        
        Args:
            venv_path: Path to virtual environment
            
        Returns:
            Path to Python executable
        """
        if os.name == 'nt':  # Windows
            return os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix-like
            return os.path.join(venv_path, "bin", "python")
    
    def install_package(self, package: str, venv_path: Optional[str] = None) -> bool:
        """
        Install a package using uv.
        
        Args:
            package: Package to install (can include version specification)
            venv_path: Virtual environment path (uses default if None)
            
        Returns:
            True if successful
        """
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return False
        
        target_venv = venv_path or self.venv_path
        if not target_venv:
            self.logger.error("No virtual environment specified")
            return False
        
        try:
            cmd = [self.uv_path, "pip", "install", package]
            
            # Set environment to use the virtual environment
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = target_venv
            
            self.logger.info(f"Installing package: {package}")
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=300, env=env)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully installed: {package}")
                return True
            else:
                self.logger.error(f"Failed to install {package}: {result.stderr}")
                return False
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error installing package {package}: {e}")
            return False
    
    def install_requirements(self, requirements_file: str, venv_path: Optional[str] = None) -> bool:
        """
        Install packages from a requirements file.
        
        Args:
            requirements_file: Path to requirements.txt file
            venv_path: Virtual environment path (uses default if None)
            
        Returns:
            True if successful
        """
        if not os.path.exists(requirements_file):
            self.logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return False
        
        target_venv = venv_path or self.venv_path
        if not target_venv:
            self.logger.error("No virtual environment specified")
            return False
        
        try:
            cmd = [self.uv_path, "pip", "install", "-r", requirements_file]
            
            # Set environment to use the virtual environment
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = target_venv
            
            self.logger.info(f"Installing requirements from: {requirements_file}")
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=600, env=env)
            
            if result.returncode == 0:
                self.logger.info("Successfully installed all requirements")
                return True
            else:
                self.logger.error(f"Failed to install requirements: {result.stderr}")
                return False
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error installing requirements: {e}")
            return False
    
    def list_packages(self, venv_path: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List installed packages in the virtual environment.
        
        Args:
            venv_path: Virtual environment path (uses default if None)
            
        Returns:
            List of package dictionaries with name and version
        """
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return []
        
        target_venv = venv_path or self.venv_path
        if not target_venv:
            self.logger.error("No virtual environment specified")
            return []
        
        try:
            cmd = [self.uv_path, "pip", "list", "--format", "json"]
            
            # Set environment to use the virtual environment
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = target_venv
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=60, env=env)
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return packages
            else:
                self.logger.error(f"Failed to list packages: {result.stderr}")
                return []
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            self.logger.error(f"Error listing packages: {e}")
            return []
    
    def uninstall_package(self, package: str, venv_path: Optional[str] = None) -> bool:
        """
        Uninstall a package.
        
        Args:
            package: Package name to uninstall
            venv_path: Virtual environment path (uses default if None)
            
        Returns:
            True if successful
        """
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return False
        
        target_venv = venv_path or self.venv_path
        if not target_venv:
            self.logger.error("No virtual environment specified")
            return False
        
        try:
            cmd = [self.uv_path, "pip", "uninstall", package, "-y"]
            
            # Set environment to use the virtual environment
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = target_venv
            
            self.logger.info(f"Uninstalling package: {package}")
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=120, env=env)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully uninstalled: {package}")
                return True
            else:
                self.logger.error(f"Failed to uninstall {package}: {result.stderr}")
                return False
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error uninstalling package {package}: {e}")
            return False
    
    def sync_dependencies(self, requirements_file: str, venv_path: Optional[str] = None) -> bool:
        """
        Sync dependencies to match exactly what's in requirements file.
        
        Args:
            requirements_file: Path to requirements.txt file
            venv_path: Virtual environment path (uses default if None)
            
        Returns:
            True if successful
        """
        if not self.uv_path:
            self.logger.error("UV executable not available")
            return False
        
        target_venv = venv_path or self.venv_path
        if not target_venv:
            self.logger.error("No virtual environment specified")
            return False
        
        try:
            cmd = [self.uv_path, "pip", "sync", requirements_file]
            
            # Set environment to use the virtual environment
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = target_venv
            
            self.logger.info(f"Syncing dependencies from: {requirements_file}")
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=600, env=env)
            
            if result.returncode == 0:
                self.logger.info("Successfully synced dependencies")
                return True
            else:
                self.logger.error(f"Failed to sync dependencies: {result.stderr}")
                return False
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Error syncing dependencies: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if uv is available for use.
        
        Returns:
            True if uv executable is available
        """
        return self.uv_path is not None
    
    def get_uv_version(self) -> Optional[str]:
        """
        Get the version of the uv executable.
        
        Returns:
            Version string or None if not available
        """
        if not self.uv_path:
            return None
        
        try:
            result = subprocess.run([self.uv_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extract version from output like "uv 0.1.0"
                return result.stdout.strip().split()[-1]
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        
        return None