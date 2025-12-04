import tkinter as tk 
from gemini_api import GEMINI_GOOGLE
from tkinter import font
import os
class Project_UI:
    def __init__(self):
        """Initialize the Project UI.

        Creates the Gemini API client, initializes the main Tkinter
        application window and builds the interface by calling
        ``setup_ui``.

        Side effects:
        - Instantiates ``self.gemini`` (a ``GEMINI_GOOGLE`` client).
        - Creates ``self.app`` (a ``tk.Tk`` root window).
        - Calls ``self.setup_ui()`` to construct widgets.
        """

        self.gemini = GEMINI_GOOGLE()
        self.app = tk.Tk()
        self.setup_ui()

    def setup_ui(self):
        """Build and arrange the Tkinter user interface.

        This method constructs the main layout and widgets used by the
        application: the text input for rules, the submit button, the
        result label, and radio buttons for selecting the KB/data source.

        Widgets created/assigned to ``self``:
        - ``self.text_input``: ``tk.Text`` where the user types rules.
        - ``self.result_label``: ``tk.Label`` for displaying the conversion
          result.
        - ``self.submit_btn``: ``tk.Button`` bound to ``self.submit_rules``.
        - ``self.selected_option``: ``tk.StringVar`` storing the selected
          data source option.
        """

        self.app.title('Auto-Labeling Application')
        self.app.geometry('500x400')

        # Left Panel
        content_frame = tk.Frame(self.app, bg="white")
        content_frame.pack(fill="both", expand=True, padx=10)

        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(side="left", fill="both", expand=True)

        # Label
        self.label = tk.Label(
            text_frame,
            text="Enter Your Rules (1 Rule per line):",
            bg="white",
            justify="left",
        )
        self.label.pack(anchor="center")

        # Text Input
        self.text_input = tk.Text(
            text_frame,
            height=12,
            width=25,
            highlightbackground="black",  # ขอบสีดำ
            highlightthickness=2,  # ความหนาขอบ
            relief="flat",
        )
        self.text_input.pack(fill="both", expand=True)

        # Result Label
        self.result_label = tk.Label(
            text_frame,
            text="Result: ",
            bg="white",
            wraplength=290,
            justify="left",
        )
        self.result_label.pack(anchor="w", pady=(0, 0))

        # Submit Button
        self.submit_btn = tk.Button(
            text_frame,
            text="Submit Rules",
            command=self.submit_rules,
            bg="#f0f0f0",
            relief="solid",  # ขอบแบบเส้นทึบ
            borderwidth=2,
            padx=5,
            pady=5,
        )
        self.submit_btn.pack(pady=20)

        # Right Panel
        options_frame = tk.Frame(content_frame, bg="white")
        options_frame.pack(side="right", fill="y", anchor="n", padx=(10, 0))

        # Data Sources Label
        tk.Label(options_frame, text="Data Sources", bg="white").pack(anchor="w", pady=(0, 5))

        self.selected_option = tk.StringVar(value="PM2.5 & Temp")

        # Radio Buttons case 1
        rb1 = tk.Radiobutton(
            options_frame,
            text="PM2.5 & Temp",
            variable=self.selected_option,
            value="PM2.5 & Temp",
            bg="white",
        )
        rb1.pack(anchor="w", pady=2)

        # Radio Buttons case 2
        rb2 = tk.Radiobutton(
            options_frame,
            text="useCase2",
            variable=self.selected_option,
            value="useCase2",
            bg="white",
        )
        rb2.pack(anchor="w", pady=2)

    def mainloop(self):
        """Enter the Tkinter main event loop.

        Blocks and dispatches GUI events until the main window is closed.
        """

        self.app.mainloop()

    
    def submit_rules(self):
        """Read user input, convert to Prolog rules via Gemini, and display.

        Steps performed:
        1. Read the text content from ``self.text_input``.
        2. If the input is empty, clear the output and return.
        3. Send the input to the Gemini API client (``self.gemini``) to
           obtain Prolog-formatted rules.
        4. Format and save the returned rules via ``format_rules`` and
           ``save_rules_to_file`` (indirectly), then update
           ``self.result_label`` with the formatted rules.

        Returns:
            The raw Prolog rule string returned by the Gemini client, or
            ``None`` if the input was empty.
        """

        input_rule_text : str = self.text_input.get('1.0', 'end-1c')
        if input_rule_text.strip() == "":
            self.display_output("")
            return

        # Get Prolog rule from Gemini API
        prolog_rule = self.gemini.get_response(input_rule_text)
        formatted_rules = self.format_rules(prolog_rule)

        self.display_output("Result: \n"  + formatted_rules)
        return prolog_rule

    def format_rules(self, prolog_rules):
        """Format a Prolog rules string and persist it to the KB.

        Args:
            prolog_rules (str): Multiline string containing one or more
                Prolog rules (typically produced by the Gemini API).

        Behavior:
            - Splits the input into individual lines/rules.
            - Writes the split rules to the appropriate KB file by
              calling ``self.save_rules_to_file``.
            - Returns a human-readable, numbered string of the rules.

        Returns:
            A single string where each rule is prefixed with its index
            ("1) <rule>", "2) <rule>", ...), suitable for display.
        """

        split_rules = prolog_rules.strip().split('\n')
        self.save_rules_to_file(split_rules)
        formatted_rules = "\n".join([str(num+1) + ") " +rule.strip() for num,rule in enumerate(split_rules)])

        return formatted_rules

    def save_rules_to_file(self, split_rules, filename="generated_rules.pl"):
        """Persist a list of Prolog rules to the KB directory.

        The destination subdirectory is chosen based on the currently
        selected option in the UI (``self.selected_option``).

        Args:
            split_rules (List[str]): Iterable of rule strings to write.
            filename (str): Target filename inside the KB subdirectory.

        Side effects:
            Writes ``filename`` under ``KB/<use_case>/`` (overwriting any
            existing file with the same name). The function prints each
            rule to stdout as it writes it.
        """

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
        """Update the result label text shown in the UI.

        Args:
            output (str): Text to display inside ``self.result_label``.
        """

        self.result_label["text"] = output

if __name__ == "__main__":
    app = Project_UI()
    app.mainloop()