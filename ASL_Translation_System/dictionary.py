import tkinter as tk
import customtkinter as ctk
import pygame
from threading import Thread
from moviepy.editor import VideoFileClip

class DictionaryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        self.setup_ui_components()

    def setup_ui_components(self):
        # Top bar with title
        top_bar = tk.Frame(self, bg='#03045E', height=60)  
        top_bar.pack(fill='x', side='top', expand=False)

        title_label = tk.Label(top_bar, text="American Sign Language Translator", bg='#03045E', fg='white', font=("Roboto", 24))
        title_label.pack(pady=20)
       
        dictionary_label = tk.Label(self, text="Dictionary", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        dictionary_label.pack(side="top", pady=(15,0))

        # Buttons frame
        buttons_frame = tk.Frame(self, bg='white')
        buttons_frame.pack(fill='x', expand=True, padx=(150,150))
        
        # Dictionary linking button texts to their respective video file paths
        button_links = {
            "Car": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Car.mp4",
            "Family": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Family.mp4",
            "Friends": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Friends.mp4", 
            "Work": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Work.mp4",
            "School": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\School.mp4",
            "Home": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Home.mp4",
            "Happy": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Happy.mp4",
            "Sad": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Sad.mp4",
            "Play": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Play.mp4", 
            "Help": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Help.mp4", 
            "Eat": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Eat.mp4", 
            "Drink": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Drink.mp4", 
            "Sleep": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Sleep.mp4", 
            "Sorry": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Sorry.mp4", 
            "Computer": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Computer.mp4", 
            "Money": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Money.mp4", 
            "Phone": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Phone.mp4", 
            "Cloth": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Cloth.mp4", 
            "Me": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Me.mp4", 
            "Stop": "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\ASL_Sign_Demo_Video\\Stop.mp4"
        }

        button_texts = ["Family", "Friends", "Work", "School", "Home", 
                "Car", "Happy", "Sad", "Play", "Help", 
                "Eat", "Drink", "Sleep", "Sorry", "Computer", 
                "Money", "Phone", "Cloth", "Me", "Stop"]
        columns = 4
        button_width = 171  
        button_height = 115  

        for index, text in enumerate(button_texts):
            button_action = lambda x=button_links[text]: self.open_video(x)
            btn = ctk.CTkButton(buttons_frame, text=text, command=button_action, 
                                corner_radius=20,  # Set the corner radius for rounded corners
                                fg_color="#B2C4D2", hover_color="#5D8FB3", 
                                font=("Roboto", 16), text_color="#03045E")
            btn.grid(row=index//columns, column=index%columns, padx=10, pady=10, sticky='nsew')
            buttons_frame.grid_rowconfigure(index//columns, weight=1, minsize=button_height)
            buttons_frame.grid_columnconfigure(index%columns, weight=1, minsize=button_width)

        # Back button
        back_button = tk.Button(self, text="Back", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), 
                                borderwidth=0, padx=15, pady=15, command=lambda: self.controller.show_frame("TranslatePage"))  # Increase font size or add padx and pady for bigger buttons
        back_button.pack(side='bottom', fill='x', expand=False, padx=0, pady=0)
     
    def open_video(self, video_path):
        # This function will run the video and close the window after it ends.
        def video_player(path):
            clip = VideoFileClip(path)
            clip_resized = clip.resize(newsize=(900, 520))
            clip_resized.preview()
            # The preview function ends here when the video is done playing.
            pygame.quit()  # Attempt to close the pygame window.

        # Load the video in a separate thread and play it.
        player_thread = Thread(target=video_player, args=(video_path,), daemon=True)
        player_thread.start()