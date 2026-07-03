import unittest
import os
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
from audit import audit_file

class TestAudit(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.rubric_path = os.path.join(self.test_dir, "rubric.yaml")
        self.target_path = os.path.join(self.test_dir, "target.md")
        
        # Create dummy rubric
        with open(self.rubric_path, 'w') as f:
            f.write("sections:\n  test:\n    weight: 100")
            
        # Create dummy target
        with open(self.target_path, 'w') as f:
            f.write("# Test Prompt\nThis is a test.")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_audit_generation(self):
        result = audit_file(self.target_path, self.rubric_path)
        self.assertIn("Audit Context Prepared", result)
        self.assertIn("Test Prompt", result)
        self.assertIn("sections:", result)
        self.assertIn("Instructions for Auditor", result)

    def test_missing_file(self):
        result = audit_file("nonexistent.md", self.rubric_path)
        self.assertIn("Error: Target file not found", result)

if __name__ == '__main__':
    unittest.main()
