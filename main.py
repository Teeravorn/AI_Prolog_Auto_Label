import tkinter as tk 
from gemini_api import GEMINI_GOOGLE
from tkinter import font
import os
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

        # Get Prolog rule from Gemini API
        prolog_rule = self.gemini.get_response(input_rule_text)

        print("Prolog Rule: \n"  + prolog_rule)
        formatted_rules = self.format_rules(prolog_rule)

        self.display_output("Result: \n"  + formatted_rules)
        return prolog_rule

    def format_rules(self, prolog_rules):
        split_rules = prolog_rules.strip().split('\n')
        self.save_rules_to_file(split_rules)
        formatted_rules = "\n".join([str(num+1) + ") " +rule.strip() for num,rule in enumerate(split_rules)])

        return formatted_rules

    def save_rules_to_file(self, split_rules, filename="generated_rules.pl"):
        use_case = ""
        if "PM2.5" in self.selected_option.get():
            use_case = "PM_Temperature"
        elif "useCase2" in self.selected_option.get():
            use_case = "useCase2"

        KB_dir = "KB/{}/".format(use_case)
        with open(os.path.join(KB_dir,filename), "w", encoding='utf-8') as f:
            for rule in split_rules:
                print("rule",rule)
                f.write(rule + "\n")

    def display_output(self,output):
        self.result_label["text"] = output

if __name__ == "__main__":
    app = Project_UI()
    app.mainloop()