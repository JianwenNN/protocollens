#!/usr/bin/env python3
"""
Quick Setup Test Script for ProtocolLens

This script verifies that your environment is correctly configured.
Run this before starting the main application.
"""

import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"      {details}")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 9
    print_result(
        "Python Version",
        passed,
        f"Found: {version.major}.{version.minor}.{version.micro} (Required: 3.9+)"
    )
    return passed

def check_dependencies():
    """Check required packages"""
    print_header("Checking Dependencies")
    
    required_packages = [
        "streamlit",
        "pydantic",
        "dotenv",
        "genai",
        "pdfplumber"
    ]
    
    all_passed = True
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "genai":
                __import__("google.genai")
            else:
                __import__(package)
            print_result(f"{package}", True, "Installed")
        except ImportError:
            print_result(f"{package}", False, "Not found - run: pip install -r requirements.txt")
            all_passed = False
    
    return all_passed

def check_env_file():
    """Check .env file exists and has API key"""
    print_header("Checking Environment Configuration")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_result(
            ".env file",
            False,
            "File not found - copy .env.example to .env and add your API key"
        )
        return False
    
    print_result(".env file", True, "Found")
    
    # Check for API key
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print_result(
            "GEMINI_API_KEY",
            False,
            "Not set in .env file"
        )
        return False
    
    if api_key == "your_api_key_here":
        print_result(
            "GEMINI_API_KEY",
            False,
            "Please replace with your actual API key"
        )
        return False
    
    print_result(
        "GEMINI_API_KEY",
        True,
        f"Set (length: {len(api_key)} chars)"
    )
    return True

def check_project_structure():
    """Check project structure"""
    print_header("Checking Project Structure")
    
    required_paths = [
        "app/main.py",
        "app/orchestrator.py",
        "app/schemas/trial.py",
        "app/utils/gemini_client.py",
        "app/utils/pdf_parser.py",
        "app/prompts/extract_trial_object.txt",
        "config.py"
    ]
    
    all_passed = True
    for path in required_paths:
        exists = Path(path).exists()
        print_result(path, exists, "Found" if exists else "Missing")
        all_passed = all_passed and exists
    
    return all_passed

def test_gemini_api():
    """Test Gemini API connection"""
    print_header("Testing Gemini API Connection")
    
    try:
        from app.utils.gemini_client import GeminiClient
        
        client = GeminiClient()
        print_result("Client initialization", True, "Success")
        
        # Try a simple API call
        print("      Testing API call (this may take a few seconds)...")
        response = client.generate("Hello", model="gemini-3-flash-preview")
        
        if response and len(response) > 0:
            print_result(
                "API call",
                True,
                f"Success - received {len(response)} chars"
            )
            return True
        else:
            print_result("API call", False, "Empty response")
            return False
            
    except ValueError as e:
        print_result("Client initialization", False, str(e))
        return False
    except Exception as e:
        print_result("API call", False, str(e))
        return False

def test_pdf_parser():
    """Test PDF parser"""
    print_header("Testing PDF Parser")
    
    try:
        from app.utils.pdf_parser import PDFParser
        
        parser = PDFParser()
        print_result("PDF Parser initialization", True, "Success")
        return True
    except Exception as e:
        print_result("PDF Parser initialization", False, str(e))
        return False

def test_orchestrator():
    """Test orchestrator initialization"""
    print_header("Testing Orchestrator")
    
    try:
        from app.orchestrator import ProtocolOrchestrator
        
        orchestrator = ProtocolOrchestrator()
        print_result("Orchestrator initialization", True, "Success")
        
        # Check prompts are readable
        from pathlib import Path
        prompts_dir = Path("app/prompts")
        prompt_files = list(prompts_dir.glob("*.txt"))
        
        print_result(
            "Prompt files",
            len(prompt_files) > 0,
            f"Found {len(prompt_files)} prompt files"
        )
        
        return True
    except Exception as e:
        print_result("Orchestrator initialization", False, str(e))
        return False

def print_summary(results):
    """Print final summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! You're ready to run ProtocolLens.")
        print("\nTo start the application, run:")
        print("  streamlit run app/main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the application.")
        print("\nFor help, see:")
        print("  - README.md")
        print("  - TROUBLESHOOTING.md")
    
    return failed == 0

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  ProtocolLens Setup Verification")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['python_version'] = check_python_version()
    results['dependencies'] = check_dependencies()
    results['env_file'] = check_env_file()
    results['project_structure'] = check_project_structure()
    results['pdf_parser'] = test_pdf_parser()
    results['orchestrator'] = test_orchestrator()
    
    # Only test API if env is configured
    if results['env_file']:
        results['gemini_api'] = test_gemini_api()
    
    # Print summary
    success = print_summary(results)
    
    # Exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()