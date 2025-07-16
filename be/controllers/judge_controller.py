import subprocess
import tempfile
import os

def judge_code(source_code, input_data, expected_output):
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as temp_file:
            temp_file.write(source_code)
            temp_file_path = temp_file.name

        completed = subprocess.run(
            ["python", temp_file_path],
            input=input_data.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        output = completed.stdout.decode().strip()
        error = completed.stderr.decode().strip()

        # So sánh kết quả
        passed = output == expected_output.strip()

        return {
            "passed": passed,
            "output": output,
            "error": error,
            "expected": expected_output.strip()
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Chạy quá thời gian giới hạn!"}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
