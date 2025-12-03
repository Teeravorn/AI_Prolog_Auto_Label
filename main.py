import tkinter as tk 
from gemini_api import GEMINI_GOOGLE

class Project_UI:
    def __init__(self):
        self.gemini = GEMINI_GOOGLE()
        self.app = tk.Tk()
        self.setup_ui()

    def setup_ui(self):
        self.app.title('First Order Logic')

        self.input_text = tk.Text(width=40,height=12)
        self.input_text.pack()

        self.button = tk.Button(text='Submit rules!',command= self.convert_2_prolog)
        self.button.pack()

        self.result_label = tk.Label(text='',justify="left")
        self.result_label.pack(pady=10, padx=10)

    def mainloop(self):
        self.app.mainloop()

    def convert_2_prolog(self):
        input_rule_text : str = self.input_text.get('1.0', 'end-1c')
        if input_rule_text.strip() == "":
            self.display_output("")
            return

        prolog_rule = self.gemini.get_response(input_rule_text)

        self.display_output("Result: \n"  + prolog_rule)
        return prolog_rule

    def display_output(self,output):
        self.result_label["text"] = output

if __name__ == "__main__":
    app = Project_UI()
    app.mainloop()