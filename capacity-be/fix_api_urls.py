#!/usr/bin/env python3
"""
Script to fix API endpoint URLs in test files
"""
import os
import re

def fix_api_urls_in_file(filepath):
    """Fix API URLs in a single test file"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Add API_BASE constant if not present
    if 'API_BASE = "/api/v1"' not in content:
        # Find the imports section and add API_BASE
        imports_end = content.find('\n\nclass')
        if imports_end == -1:
            imports_end = content.find('\nclient = TestClient(app)')
            if imports_end != -1:
                imports_end = content.find('\n', imports_end + 1)

        if imports_end != -1:
            before = content[:imports_end]
            after = content[imports_end:]
            content = before + '\n\n# API Base URL\nAPI_BASE = "/api/v1"' + after

    # Replace hardcoded URLs with API_BASE
    patterns = [
        (r'"/sprints/', '"{API_BASE}/sprints/'),
        (r'"/members/', '"{API_BASE}/members/'),
        (r'"/pto/', '"{API_BASE}/pto/'),
        # Already prefixed URLs
        (r'"/api/v1/sprints/', '"{API_BASE}/sprints/'),
        (r'"/api/v1/members/', '"{API_BASE}/members/'),
        (r'"/api/v1/pto/', '"{API_BASE}/pto/'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Remove duplicate API_BASE definitions
    lines = content.split('\n')
    api_base_lines = [i for i, line in enumerate(lines) if 'API_BASE = "/api/v1"' in line]
    if len(api_base_lines) > 1:
        # Keep only the first one
        for i in sorted(api_base_lines[1:], reverse=True):
            del lines[i]
        content = '\n'.join(lines)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Fixed URLs in {filepath}")

def main():
    test_files = [
        "/app/tests/api/test_availability_endpoints.py",
        "/app/tests/api/test_sprints_endpoints.py",
        "/app/tests/api/test_members_endpoints.py"
    ]

    for filepath in test_files:
        if os.path.exists(filepath):
            fix_api_urls_in_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()
