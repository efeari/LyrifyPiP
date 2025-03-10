import tkinter as tk
from PIL import ImageTk, Image, ImageFilter
from random import choices

from .config import *

class ScreenHandler:
    def __init__(self, defaultScreenWidth: int = 480, defaultScreenHeight: int = 480,
        backgroundChoice: BackgroundChoice = BackgroundChoice.COLOR):
        """       
        Constructor for the ScreenHandler
        m_root is the main tkinter object.

        Args:
            defaultScreenWidth (int, optional): Screen width given by the user. Defaults to 0.
            defaultScreenHeight (int, optional): Screen heigth given by the user. Defaults to 0.
        """
        self.m_root = tk.Tk()
        self.m_screen_width = defaultScreenWidth
        self.m_screen_height = defaultScreenHeight
        self.m_background_choice = backgroundChoice

        if (self.m_screen_width == 0 and self.m_screen_height == 0):
            self.m_root.attributes('-fullscreen', True)
            self.get_curr_screen_geometry()
            self.m_screen_width = self.m_root.winfo_screenwidth()
            self.m_screen_height = self.m_root.winfo_screenheight()
        else:
            self.m_root.geometry("%dx%d" % (self.m_screen_width, self.m_screen_height))
            self.m_root.overrideredirect(True)
            self.m_root.attributes("-topmost", True)

        self.m_textSize = self.m_screen_width // resolutionToTextRatio
        self.m_root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a black backgroung for startup
        self.m_img = Image.new('RGB', (self.m_screen_width, self.m_screen_height), "black")
        self.m_img.save("TrackInfo\Background.png")
        # And set it as background
        self.m_canvas = tk.Canvas(self.m_root, width=self.m_screen_width, height=self.m_screen_height)
        self.m_canvas.pack(expand=True, fill=tk.BOTH)
        self.m_album_image = ImageTk.PhotoImage(self.m_img)
        self.m_img_container = self.m_canvas.create_image(0, 0, image=self.m_album_image, anchor=tk.NW)

        # Create the text container
        self.m_text_container = self.m_canvas.create_text(self.m_screen_width/2, self.m_screen_height/2, text="",font=("Purisa", self.m_textSize), width=self.m_screen_width)
        
        self.m_none_received = False

        self.m_root.bind("<B1-Motion>", lambda event:  self.m_root.geometry(f'+{event.x_root}+{event.y_root}'))

        self.create_close_button()

    def get_background_choice(self) -> BackgroundChoice:
        return self.m_background_choice
    
    def start_main_loop(self):
        self.m_root.mainloop()

    def update(self):
        self.m_root.update_idletasks()
        self.m_root.update()

    def create_close_button(self):
        """
        Creates an close button which becomes visible when hovered on the window only
        """
        icon_size = 15 
        padding = 10

        x1 = self.m_screen_width - icon_size - padding
        y1 = padding
        x2 = self.m_screen_width - padding
        y2 = icon_size + padding

        self.line1 = self.m_canvas.create_line(x1, y1, x2, y2, width=2, state=tk.HIDDEN)
        self.line2 = self.m_canvas.create_line(x1, y2, x2, y1, width=2, state=tk.HIDDEN)

        self.m_canvas.tag_bind(self.line1, "<Button-1>", lambda event: self.on_closing())
        self.m_canvas.tag_bind(self.line2, "<Button-1>", lambda event: self.on_closing())

        self.m_canvas.bind("<Enter>", self.show_icon)
        self.m_canvas.bind("<Leave>", self.hide_icon)

    def show_icon(self, event):
        """Make the 'X' icon visible."""
        self.m_canvas.itemconfig(self.line1, state=tk.NORMAL)
        self.m_canvas.itemconfig(self.line2, state=tk.NORMAL)

    def hide_icon(self, event):
        """Make the 'X' icon invisible."""
        self.m_canvas.itemconfig(self.line1, state=tk.HIDDEN)
        self.m_canvas.itemconfig(self.line2, state=tk.HIDDEN)

    def on_closing(self):
        """
        Destroys the m_root

        Raises:
            SystemExit: _description_
        """
        self.m_root.destroy()
        raise SystemExit
    
    def get_curr_screen_geometry(self):
        """
        Workaround to get the size of the current screen in a multi-screen setup.
        https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python/56913005#56913005
         [width]x[height]+[left]+[top]
        """
        root = tk.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        self.m_root.geometry = root.winfo_geometry()
        root.destroy()
    
    def update_album_cover(self):
        """
        Updates the album cover on the display if a new track is found or
        updates the lyrics displayed
        
        1.Apply the necessary filters & blurs
        2.Sets the item as canvas
        3.Asks for a readable color
        """
        self.m_img = Image.open("TrackInfo\Background.png")
        self.m_img.putalpha(alphaValue)
        self.m_img = self.m_img.filter(ImageFilter.GaussianBlur(radius=10))
        self.m_img = self.m_img.resize((self.m_screen_width, self.m_screen_height), Image.ADAPTIVE)
        self.m_album_image = ImageTk.PhotoImage(self.m_img)
        self.m_canvas.itemconfig(self.m_img_container, image=self.m_album_image)
        self.m_canvas.itemconfig(self.m_text_container, text="", fill=self.suggest_readable_text_color())
        return
    
    def update_screen(self, trackStatus, lyric):
        """
        Based on the trackStatus, it updates the screen

        If there is a new track, it updates the cover and applies the lyrics if any
        If updateInProgress, it updates the lyrics
        Otherwise, stall
        Args:
            trackStatus (_type_): _description_
            lyric (_type_): _description_
        """
        if trackStatus == TrackState.NEW_TRACK:
            if self.m_background_choice == BackgroundChoice.ALBUM_COVER:
                #self.update_album_cover()
                return
            elif self.m_background_choice == BackgroundChoice.COLOR:
                self.set_random_backgroung_color()
                if lyric is not None:
                    self.m_canvas.itemconfig(self.m_text_container, text=lyric)
        elif trackStatus == TrackState.UPDATE_IN_PROGRESS:
            if lyric is None and self.m_none_received == False:
                lyric = ""
                self.m_canvas.itemconfig(self.m_text_container, text=lyric)
                self.m_none_received = True
            elif lyric is not None:
                self.m_canvas.itemconfig(self.m_text_container, text=lyric)
            return
        elif trackStatus == TrackState.PAUSED_TRACK:
            return
        elif trackStatus == TrackState.NOT_PLAYING:
            return


    def get_dominant_color(self):
        """
        Calculates the dominant color of the associated image.

        Returns:
            tuple[4]: A 4-tuple representing the dominant color in (R, G, B, A) format, 
               where each value is an integer between 0 and 255.
        """
        img = self.m_img
        img = img.convert("RGBA")
        img = img.resize((1, 1), resample=0)
        dominant_color = img.getpixel((0, 0))
        return dominant_color
    
    def suggest_readable_text_color(self):
        """
        Suggests a readable text color (black or white) based on the dominant color 
        of an associated image or background. Based on:
        https://stackoverflow.com/a/1855903

        Returns:
            tuple[3]: A hexadecimal color code representing the suggested text color 
        """
        dominant_color = self.get_dominant_color()
        # Calculate perceptive luminance (normalized to 1)
        luminance = (0.299 * dominant_color[0] + 0.587 * dominant_color[1] + 0.114 * dominant_color[2]) / 255
        # Determine the contrasting color
        d = 0 if luminance > 0.5 else 255        
        suggestedColorHex = "#{:02x}{:02x}{:02x}".format(*(d, d, d))
        
        return suggestedColorHex

    def set_random_backgroung_color(self):
        """
        A function to generate a random RGB color and set it as background

        """
        randColor = tuple(choices(range(256), k=3))
        self.m_img = Image.new('RGB', (self.m_screen_width, self.m_screen_height), randColor)
        self.m_img.save("TrackInfo\Background.png")
        self.m_album_image = ImageTk.PhotoImage(self.m_img)
        self.m_canvas.itemconfig(self.m_img_container, image=self.m_album_image)
        self.m_canvas.itemconfig(self.m_text_container, text="", fill=self.suggest_readable_text_color())

