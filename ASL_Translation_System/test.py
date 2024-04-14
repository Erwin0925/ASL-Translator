import tkinter as tk

class TestPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Add components for the quiz functionality here

        translate_button = tk.Button(self, text="Go to Translate",
                                     command=lambda: controller.show_frame("TranslatePage"))
        translate_button.pack()
