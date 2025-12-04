import tkinter as tk
from gemini_api import GEMINI_GOOGLE
from tkinter import font
import os
from lib.auto_label.query_rule import apply_rule_to_csv
from datetime import datetime
import shutil
from lib.auto_label.query_engine_config import (
    load_config,
    get_rules_file,
    get_source_csv_path,
    get_output_csv_path
)
from render_graph import plot_labeled_results

class Project_UI:
    def __init__(self):
        self.gemini = GEMINI_GOOGLE()
        self.app = tk.Tk()
        self.setup_ui()

    def setup_ui(self):
        self.app.title('Auto-Labeling Application')
        self.app.geometry('500x400')

        # Left Panel
        content_frame = tk.Frame(self.app, bg="white")
        content_frame.pack(fill="both", expand=True, padx=10)

        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(side="left", fill="both", expand=True)

        self.label = tk.Label(
            text_frame, 
            text="Enter Your Rules (1 Rule per line):", 
            bg="white",
            justify="left"
        )
        self.label.pack(anchor="center")

        self.text_input = tk.Text(
            text_frame, 
            height=12, 
            width=25,
            highlightbackground="black", # ขอบสีดำ
            highlightthickness=2,        # ความหนาขอบ
            relief="flat"
        )
        self.text_input.pack(fill="both", expand=True)

        # test_text = "Result: "
        # rule = "label_air_pollution(PM2_5, 'มีมลพิษทางอากาศต่ำ') :- PM2_5 =< 15. \n\
        #         label_air_pollution(PM2_5, 'มีมลพิษทางอากาศปานกลาง') :- PM2_5 =< 35. \n\
        #         label_air_pollution(PM2_5, 'มีมลพิษทางอากาศสูง') :- PM2_5 > 35."

        # formatted_rule = self.format_rules(rule)

        self.result_label = tk.Label(
            text_frame, 
            # text="Result: \n" + formatted_rule,
            text="Result: ", 
            bg="white",
            wraplength=290,
            justify="left"
        )
        self.result_label.pack(anchor="w", pady=(0, 0))

        self.submit_btn = tk.Button(
            text_frame, 
            text="Submit Rules", 
            command=self.submit_rules,
            bg="#f0f0f0",
            relief="solid", # ขอบแบบเส้นทึบ
            borderwidth=2,
            padx=5, pady=5
        )
        self.submit_btn.pack(pady=20)

        # Right Panel
        options_frame = tk.Frame(content_frame, bg="white")
        options_frame.pack(side="right", fill="y", anchor="n", padx=(10, 0))

        tk.Label(options_frame, text="Data Sources", bg="white").pack(anchor="w", pady=(0, 5))

        self.selected_option = tk.StringVar(value="PM2.5 & Temp")

        rb1 = tk.Radiobutton(
            options_frame, 
            text="PM2.5 & Temp",
            variable=self.selected_option,
            value="PM2.5 & Temp",
            bg="white",
        )
        rb1.pack(anchor="w", pady=2)

        rb2 = tk.Radiobutton(
            options_frame, 
            text="useCase2", 
            variable=self.selected_option, 
            value="useCase2",
            bg="white",
        )
        rb2.pack(anchor="w", pady=2)

    def mainloop(self):
        self.app.mainloop()

    def submit_rules(self):
        input_rule_text : str = self.text_input.get('1.0', 'end-1c')
        if input_rule_text.strip() == "":
            self.display_output("")
            return

        # Load config for current use case
        use_case = "PM_Temperature" if "PM2.5" in self.selected_option.get() else "useCase2"
        config = load_config(use_case)
        
        # Get Prolog rule from Gemini API
        prolog_rule = self.gemini.get_response(input_rule_text, config)
        # prolog_rule = input_rule_text
        print("Prolog Rule: \n"  + prolog_rule)
        formatted_rules = self.format_rules(prolog_rule, use_case, config)
        
        self.display_output("Result: \n"  + formatted_rules)
        self.applied_rules()
        return prolog_rule

    def format_rules(self, prolog_rules, use_case, config):
        split_rules = prolog_rules.strip().split('\n')
        self.current_rules_file = self.save_rules_to_file(split_rules, use_case, config)
        formatted_rules = "\n".join([str(num+1) + ") " +rule.strip() for num,rule in enumerate(split_rules)])

        return formatted_rules

    def save_rules_to_file(self, split_rules, use_case, config):
        # Create timestamped rules file
        from lib.auto_label.query_engine_config import get_kb_dir
        kb_dir = get_kb_dir(config)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rules_filename = f"generated_rules_{timestamp}.pl"
        rules_file_path = os.path.join(kb_dir, use_case, rules_filename)
        
        with open(rules_file_path, "w", encoding='utf-8') as f:
            for rule in split_rules:
                print("rule",rule)
                f.write(rule + "\n")
        
        return rules_filename

    def display_output(self,output):
        self.result_label["text"] = output
        
    def applied_rules(self):
        # Apply rules to CSV and add auto-label column
        use_case = "PM_Temperature" if "PM2.5" in self.selected_option.get() else "useCase2"
        config = load_config(use_case)
        
        # Get paths from config
        source_file = get_source_csv_path(config)
        destination = get_output_csv_path(config)
        
        # Copy source file for usecase to new file before labeling
        self.copy_source_file(source_file, destination)
        try:
            # Pass the rules filename to apply_rule_to_csv
            rules_filename = getattr(self, 'current_rules_file', 'generated_rules.pl')
            df_labeled = apply_rule_to_csv(use_case, destination, rules_file=rules_filename)
            
            # Get actual output path from query_rule (it uses get_output_csv_path internally)
            output_path = get_output_csv_path(config)
            print(f"Auto-labeling complete. Output saved to: {output_path}")
            
            # Plot graph after labeling
            plot_labeled_results(output_path)
        except Exception as e:
            print(f"Error during auto-labeling: {e}")

    def copy_source_file(self, source, destination):
        if os.path.exists(source):
            shutil.copy(source, destination)
            print(f"Copied {source} to {destination}")
        else:
            print(f"Source file not found: {source}")
            
if __name__ == "__main__":
    app = Project_UI()
    app.mainloop()