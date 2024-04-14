import tkinter as tk
from login import LoginPage
from register import RegisterPage
from reset_pw import ResetPasswordPage
from translate import TranslatePage
from badge import BadgePage

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("American Sign Language Translator")
        self.container = tk.Frame(self)  # Make container an instance variable
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.username = None

        # Initialize only the necessary pages at startup
        for F in (LoginPage, RegisterPage, ResetPasswordPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")
        self.center_window()

    def init_frame(self, frame_class, container):
        frame = frame_class(parent=container, controller=self)
        self.frames[frame_class.__name__] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        # Check if the frame exists, if not, initialize it
        if page_name not in self.frames and page_name in {"TranslatePage", "BadgePage"}:
            self.init_frame(eval(page_name), self.frames["LoginPage"].parent)

        # Adjust window size based on the frame being shown
        self.adjust_window_size(page_name)
        self.frames[page_name].tkraise()
        self.center_window()

    def adjust_window_size(self, page_name):
        sizes = {
            "LoginPage": "350x350",
            "RegisterPage": "350x520",
            "ResetPasswordPage": "350x520",
            "TranslatePage": "1063x768",
            "BadgePage": "350x420"
        }
        if page_name in sizes:
            self.geometry(sizes[page_name])

    def set_username(self, username):
        self.username = username
        self.init_frame(TranslatePage, self.container)
        self.init_frame(BadgePage, self.container)
        self.show_frame("TranslatePage")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
