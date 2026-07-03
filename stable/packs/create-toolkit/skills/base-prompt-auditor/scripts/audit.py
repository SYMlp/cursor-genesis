import argparse
import sys
import os
import yaml

def load_rubric(rubric_path):
    try:
        with open(rubric_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading rubric from {rubric_path}: {e}")
        sys.exit(1)

def audit_file(target_path, rubric_path):
    if not os.path.exists(target_path):
        return f"Error: Target file not found: {target_path}"
    
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading target file: {e}"
        
    rubric = load_rubric(rubric_path)
    
    # Format output for the LLM
    output = []
    output.append("# 📋 Audit Context Prepared")
    output.append(f"**Target File**: `{target_path}`")
    output.append("\n## 📄 File Content")
    output.append("```")
    output.append(content)
    output.append("```")
    
    output.append("\n## 📏 Engineering Rubric (V2.1)")
    output.append("```yaml")
    output.append(yaml.dump(rubric, default_flow_style=False, allow_unicode=True))
    output.append("```")
    
    output.append("\n## 🤖 Instructions for Auditor")
    output.append("1. Analyze the `File Content`.")
    output.append("2. Evaluate strictly against the `Engineering Rubric`.")
    output.append("3. Produce the **Audit Report** as defined in the Skill definition.")
    
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit a prompt file.")
    parser.add_argument("file_path", help="Path to the file to audit")
    
    # Determine absolute path to assets relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_rubric = os.path.join(script_dir, "../assets/rubric.yaml")
    
    parser.add_argument("--rubric", default=default_rubric, help="Path to rubric file")
    
    args = parser.parse_args()
    
    try:
        result = audit_file(args.file_path, args.rubric)
        # Use UTF-8 encoding for output to handle potential unicode in files
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(result.encode('utf-8'))
        else:
            print(result)
    except Exception as e:
        print(f"Error during audit preparation: {str(e)}")
        sys.exit(1)
