import janus_swi as janus
import pandas as pd
import re
import os
import time

def get_predicate_info(rule_file_path):
    with open(rule_file_path, "r", encoding='utf-8') as f:
        content = f.read()

    # Regex: หาบรรทัดที่เป็นกฎหลัก เช่น label_pm_risk(...) :- ...
    # จับกลุ่ม 1: ชื่อ Predicate
    # จับกลุ่ม 2: ไส้ในวงเล็บทั้งหมด (Arguments)

    # main_rule = content.splitlines()[-1]
    pattern = re.compile(r"^(\w+)\((.+)\)\s*:-", re.MULTILINE)
    
    match = pattern.search(content)
    if match:
        pred_name = match.group(1)
        args_raw = match.group(2)
        
        # เทคนิค: นับจำนวนลูกน้ำ (,) เพื่อหาจำนวน Arguments (Arity)
        # วิธีนี้ดีกว่า split(',') เพราะถ้าใน text มีลูกน้ำ (เช่น 'Hello, World') มันจะไม่พัง
        # เราสมมติง่ายๆ ว่า Arguments ขั้นด้วย , และเราสนใจแค่จำนวน
        # (ถ้า Logic ซับซ้อนกว่านี้อาจต้องใช้ module shlex ช่วย parse)
        arg_count = args_raw.count(',') + 1
        
        print(f"Detected Predicate: {pred_name}")
        print(f"Arity (Arg Count): {arg_count}")
        
        return pred_name, arg_count
    else:
        raise ValueError("Cannot parse rule head.")

def get_label_dynamic(row, pred_name, arity, input_cols):
    """
    สร้าง Query: predicate(Input1, Input2, ..., ResultVar)
    โดยอัตโนมัติ ไม่สนว่าใน Rule ไฟล์เขียน Output เป็น Text หรือไม่
    """
    
    num_inputs = arity - 1
    
    current_inputs = []
    for col in input_cols[:num_inputs]:
        val = row[col]
        current_inputs.append(str(val))
    
    args_str = ", ".join(current_inputs + ["Label"]) 
    query_str = f"{pred_name}({args_str})"
    
    print("query_str",query_str)
    try:
        result = next(janus.query(query_str))
        # print(result)

        return result['Label'].strip()
    except StopIteration:
        return "Normal"
    except Exception as e:
        return f"Error: {e}"

def apply_rule_to_csv(use_case, csv_path, rules_file):
    # Load Prolog rules
    try:
        janus.consult(rules_file)
        print(f"Loaded rules from: {rules_file}")
    except Exception as e:
        print(f"Error loading Prolog rules: {e}")
        return None

    # Get predicate info
    pred_name, arity = get_predicate_info(rules_file)

    # Load CSV
    df = pd.read_csv(csv_path)
    df['Time'] = df['Time'].apply(lambda x: x.replace(":", "."))  # Format time

    # Define input columns based on use case
    if use_case == "PM_Temperature":
        input_columns = ['PM2.5', 'Temp', 'Time']
    else:
        input_columns = []  # Define for other use cases as needed

    # Apply labeling
    df['Auto_Label'] = df.apply(
        lambda row: get_label_dynamic(row, pred_name, arity, input_columns),
        axis=1
    )

    df['Time'] = df['Time'].apply(lambda x: x.replace(".", ":"))  # Format time

    return df

def save_labeled_csv(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"Labeled CSV saved to: {output_path}")

if __name__ == "__main__":
    # Example usage
    use_case = "PM_Temperature"
    csv_path = "data/PM_Temp.csv"
    rules_file = "KB/PM_Temperature/generated_rules_20251205_234147.pl"

    df_labeled = apply_rule_to_csv(use_case, csv_path, rules_file)
    if df_labeled is not None:
        print(df_labeled.head())

        output_csv_path = "data/PM_Temp_labeled.csv"
        save_labeled_csv(df_labeled, output_csv_path)