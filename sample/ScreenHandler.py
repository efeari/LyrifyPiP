import os
import tkinter as tk
from tkinter import PhotoImage
from PIL import ImageTk, Image, ImageFilter

from .config import *

class ScreenHandler:
    def __init__(self, defaultScreenWidth: int = 0, defaultScreenHeight: int = 0):
        """       
        Constructor for the ScreenHandler
        m_root is the main tkinter object.

        Args:
            defaultScreenWidth (int, optional): Screen width given by the user. Defaults to 0.
            defaultScreenHeight (int, optional): Screen heigth given by the user. Defaults to 0.
        """
        self.m_root = tk.Tk()
        
        self.screenWidth = defaultScreenWidth
        self.screenHeight = defaultScreenHeight
        
        if (self.screenWidth == 0 and self.screenHeight == 0):
            self.m_root.attributes('-fullscreen', True)
            self.getCurrScreenGeometry()
            self.screenWidth = self.m_root.winfo_screenwidth()
            self.screenHeight = self.m_root.winfo_screenheight()
        else:
            self.m_root.geometry("%dx%d" % (self.screenWidth, self.screenHeight))
            self.m_root.overrideredirect(True)
            self.m_root.attributes("-topmost", True)

        self.textSize = self.screenHeight * self.screenWidth // resolutionToTextRatio
        self.m_root.protocol("WM_DELETE_WINDOW", self.onClosing)

        # Create the image
        self.m_img = Image.new('RGB', (self.screenWidth, self.screenHeight), "black")
        self.m_img.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
        self.m_img.putalpha(alphaValue)
        self.m_img = self.m_img.filter(ImageFilter.BLUR)
        self.m_img = self.m_img.resize((self.screenWidth,self.screenHeight))

        # Set the background
        self.m_canvas = tk.Canvas(self.m_root, width=self.screenWidth, height=self.screenHeight)
        self.m_canvas.pack(expand=True, fill=tk.BOTH)
        self.m_albumImage = ImageTk.PhotoImage(self.m_img)
        self.imgContainer = self.m_canvas.create_image(0, 0, image=self.m_albumImage, anchor=tk.NW)

        self.textContainer = self.m_canvas.create_text(self.screenWidth/2, self.screenHeight/2, text="",font=("Purisa", self.textSize))

        self.m_NoneReceived = False

        self.m_root.bind("<B1-Motion>", lambda event:  self.m_root.geometry(f'+{event.x_root}+{event.y_root}'))

        icon_path = os.path.join("assets", "icons", "close.png")
        close_img = Image.open(icon_path)
        close_img = close_img.resize((30, 30))
        close_button = tk.Label(self.m_root, image=ImageTk.PhotoImage(close_img), relief="flat", cursor="hand2")
        close_button.place(x=self.screenWidth - 30, y=0)
        close_button.bind("<Button-1>", lambda event: self.m_root.destroy())

    def move(self, event):
        x = self.m_root.winfo_pointerx()
        y = self.m_root.winfo_pointery()
        self.m_root.geometry('+{x}+{y}'.format(x=x,y=y))

    def startMainLoop(self):
        self.m_root.mainloop()

    def onClosing(self):
        """
        Destroys the m_root

        Raises:
            SystemExit: _description_
        """
        self.m_root.destroy()
        raise SystemExit
    
    def getCurrScreenGeometry(self):
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
    
    def updateAlbumCover(self):
        """
        Updates the album cover on the display if a new track is found or
        updates the lyrics displayed
        
        1.Apply the necessary filters & blurs
        2.Sets the item as canvas
        3.Asks for a readable color
        """
        self.m_img = Image.open(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
        self.m_img.putalpha(alphaValue)
        self.m_img = self.m_img.filter(ImageFilter.BLUR)
        self.m_img = self.m_img.resize((self.screenWidth, self.screenHeight), Image.ADAPTIVE)
        self.m_albumImage = ImageTk.PhotoImage(self.m_img)
        self.m_canvas.itemconfig(self.imgContainer, image=self.m_albumImage)
        self.m_canvas.itemconfig(self.textContainer, text="", fill=self.suggestReadableTextColor())
        return
    
    def updateScreen(self, trackStatus, lyric):
        """
        Based on the trackStatus, it updates the screen

        If there is a new track, it updates the cover and applies the lyrics if any
        If updateInProgress, it updates the lyrics
        Otherwise, stall
        Args:
            trackStatus (_type_): _description_
            lyric (_type_): _description_
        """
        match trackStatus:
            case TrackState.NEW_TRACK:
                self.updateAlbumCover()
            case TrackState.UPDATE_IN_PROGRESS:
                if lyric is None and self.m_NoneReceived == False:
                    lyric = ""
                    self.m_canvas.itemconfig(self.textContainer, text=lyric)
                    self.m_NoneReceived = True
                elif lyric is not None:
                    self.m_canvas.itemconfig(self.textContainer, text=lyric)
                return
            case TrackState.PAUSED_TRACK:
                return
            case TrackState.NOT_PLAYING:
                return

    def getDominantColor(self):
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
    
    def suggestReadableTextColor(self):
        """
        Suggests a readable text color (black or white) based on the dominant color 
        of an associated image or background. Based on:
        https://stackoverflow.com/a/1855903

        Returns:
            tuple[3]: A hexadecimal color code representing the suggested text color 
        """
        dominant_color = self.getDominantColor()
        # Calculate perceptive luminance (normalized to 1)
        luminance = (0.299 * dominant_color[0] + 0.587 * dominant_color[1] + 0.114 * dominant_color[2]) / 255
        # Determine the contrasting color
        d = 0 if luminance > 0.5 else 255        
        suggestedColorHex = "#{:02x}{:02x}{:02x}".format(*(d, d, d))
        
        return suggestedColorHex