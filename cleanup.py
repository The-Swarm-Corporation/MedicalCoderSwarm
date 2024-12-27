#!/usr/bin/env python3

import subprocess
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def uninstall_packages(python_version):
    """Uninstall all packages for a specific Python version"""
    python_path = f"/usr/local/bin/python{python_version}"
    
    if not os.path.exists(python_path):
        logger.error(f"{python_path} not found")
        return
        
    logger.info(f"\nProcessing Python {python_version}")
    logger.info("=" * 50)
    
    try:
        # Get list of installed packages
        result = subprocess.check_output(
            [python_path, "-m", "pip", "list", "--format=freeze"],
            stderr=subprocess.DEVNULL
        ).decode()
        
        packages = [
            line.split('==')[0] 
            for line in result.split('\n') 
            if line and not line.startswith('pip') and not line.startswith('setuptools')
        ]
        
        if not packages:
            logger.info("No packages to remove")
            return
            
        logger.info(f"Found {len(packages)} packages")
        
        # Uninstall packages
        for package in packages:
            logger.info(f"Removing {package}...")
            try:
                subprocess.check_call(
                    [python_path, "-m", "pip", "uninstall", "-y", package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                logger.error(f"Failed to remove {package}")
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def clean_pip_cache():
    """Clean pip cache"""
    cache_dir = Path.home() / "Library/Caches/pip"
    if cache_dir.exists():
        logger.info("\nCleaning pip cache...")
        try:
            subprocess.run(["rm", "-rf", str(cache_dir)])
            logger.info("Cache cleaned")
        except Exception as e:
            logger.error(f"Failed to clean cache: {str(e)}")

def main():
    logger.info("Starting package cleanup...")
    
    # Target Python versions
    versions = ["3.9", "3.11", "3.12"]
    
    # Clean packages for each version
    for version in versions:
        uninstall_packages(version)
    
    # Clean pip cache
    clean_pip_cache()
    
    logger.info("\nCleanup complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")