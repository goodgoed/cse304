import unittest, sys, os, glob, decaf_checker
from unittest.mock import patch
from io import StringIO
class DecafTest(unittest.TestCase):
    def run_test(self, input_file, expected_output_file):
        
        # Uncomment below line of code to see what is different between expected output and actual output 
        # self.maxDiff = None
        test_args = ['test.py',input_file]
        with open(expected_output_file, 'r') as f:
            expected_output = f.read().strip()

        with patch('sys.stdout', new_callable=lambda: StringIO()) as mock_stdout:
            with patch.object(sys, 'argv', test_args):
                decaf_checker.main()
                actual_output = mock_stdout.getvalue().strip()
        
        self.assertEqual(expected_output, actual_output)

def create_test_method(input_file, expected_output_file):
    def do_test_expected_output(self):
        self.run_test(input_file, expected_output_file)
    return do_test_expected_output

if __name__ == '__main__':
    test_folder = "tests"
    for input_file in glob.glob(os.path.join(test_folder, "input", "*.decaf")):
        base_name = os.path.basename(input_file)[:-6]
        expected_output_file = os.path.join(test_folder, "expected", f"{base_name}.txt")

        print(f"Found test file: {input_file}", file=sys.stderr)
        print(f"Found expected output file: {expected_output_file}", file=sys.stderr)

        if os.path.isfile(expected_output_file):
            print("Creating test method", file=sys.stderr)
            test_method = create_test_method(input_file, expected_output_file)
            test_method.__name__ = f"test_{base_name}"
            setattr(DecafTest, test_method.__name__, test_method)
        else:
            print("Expected output file not found", file=sys.stderr)

    unittest.main()