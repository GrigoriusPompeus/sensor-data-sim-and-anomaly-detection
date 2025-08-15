#!/usr/bin/env python3
"""
Comprehensive Test Runner

Runs all available test scripts and provides a summary.
"""

import subprocess
import sys

def run_test(script_name, description):
    """Run a test script and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              timeout=30)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out")
        return False
    except Exception as e:
        print(f"❌ {script_name} failed: {e}")
        return False

def main():
    """Run all tests and provide summary."""
    print("🚀 COMPREHENSIVE SENSOR SIMULATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("test_imports.py", "Import and Dependency Test"),
        ("test_sensor.py", "Individual Sensor Creation Test"),
        ("test_all_sensors.py", "All Sensor Implementations Test"),
        ("test_active_rules.py", "Anomaly Detection Rules Test"),
        ("test_extreme_temp.py", "Extreme Temperature Scenarios Test"),
        ("test_extreme_values.py", "Extreme Values Threshold Test"),
    ]
    
    results = []
    
    for script, description in tests:
        success = run_test(script, description)
        results.append((script, description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for script, description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:<10} | {description}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
