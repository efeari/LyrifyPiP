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
        
        self.m_screenWidth = defaultScreenWidth
        self.m_screenHeight = defaultScreenHeight
        self.m_backgroundChoice = backgroundChoice

        if (self.m_screenWidth == 0 and self.m_screenHeight == 0):
            self.m_root.attributes('-fullscreen', True)
            self.getCurrScreenGeometry()
            self.m_screenWidth = self.m_root.winfo_screenwidth()
            self.m_screenHeight = self.m_root.winfo_screenheight()
        else:
            self.m_root.geometry("%dx%d" % (self.m_screenWidth, self.m_screenHeight))
            self.m_root.overrideredirect(True)
            self.m_root.attributes("-topmost", True)

        self.m_textSize = self.m_screenWidth // resolutionToTextRatio
        self.m_root.protocol("WM_DELETE_WINDOW", self.onClosing)

        # Create a black backgroung for startup
        self.m_img = Image.new('RGB', (self.m_screenWidth, self.m_screenHeight), "black")
        self.m_img.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
        # And set it as background
        self.m_canvas = tk.Canvas(self.m_root, width=self.m_screenWidth, height=self.m_screenHeight)
        self.m_canvas.pack(expand=True, fill=tk.BOTH)
        self.m_albumImage = ImageTk.PhotoImage(self.m_img)
        self.m_imgContainer = self.m_canvas.create_image(0, 0, image=self.m_albumImage, anchor=tk.NW)

        # Create the text container
        self.m_textContainer = self.m_canvas.create_text(self.m_screenWidth/2, self.m_screenHeight/2, text="",font=("Purisa", self.m_textSize), width=self.m_screenWidth)
        
        self.m_NoneReceived = False

        self.m_root.bind("<B1-Motion>", lambda event:  self.m_root.geometry(f'+{event.x_root}+{event.y_root}'))

        self.createCloseButton()

    def getBackgroundChoice(self) -> BackgroundChoice:
        return self.m_backgroundChoice
    
    def startMainLoop(self):
        self.m_root.mainloop()

    def createCloseButton(self):
        """
        Creates an close button which becomes visible when hovered on the window only
        """
        icon_size = 15 
        padding = 10

        x1 = self.m_screenWidth - icon_size - padding
        y1 = padding
        x2 = self.m_screenWidth - padding
        y2 = icon_size + padding

        self.line1 = self.m_canvas.create_line(x1, y1, x2, y2, width=2, state=tk.HIDDEN)
        self.line2 = self.m_canvas.create_line(x1, y2, x2, y1, width=2, state=tk.HIDDEN)

        self.m_canvas.tag_bind(self.line1, "<Button-1>", lambda event: self.onClosing())
        self.m_canvas.tag_bind(self.line2, "<Button-1>", lambda event: self.onClosing())

        self.m_canvas.bind("<Enter>", self.showIcon)
        self.m_canvas.bind("<Leave>", self.hideIcon)

    def showIcon(self, event):
        """Make the 'X' icon visible."""
        self.m_canvas.itemconfig(self.line1, state=tk.NORMAL)
        self.m_canvas.itemconfig(self.line2, state=tk.NORMAL)

    def hideIcon(self, event):
        """Make the 'X' icon invisible."""
        self.m_canvas.itemconfig(self.line1, state=tk.HIDDEN)
        self.m_canvas.itemconfig(self.line2, state=tk.HIDDEN)

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
        self.m_img = self.m_img.filter(ImageFilter.GaussianBlur(radius=10))
        self.m_img = self.m_img.resize((self.m_screenWidth, self.m_screenHeight), Image.ADAPTIVE)
        self.m_albumImage = ImageTk.PhotoImage(self.m_img)
        self.m_canvas.itemconfig(self.m_imgContainer, image=self.m_albumImage)
        self.m_canvas.itemconfig(self.m_textContainer, text="", fill=self.suggestReadableTextColor())
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
                match self.m_backgroundChoice:
                    case BackgroundChoice.ALBUM_COVER:
                        self.updateAlbumCover()
                        return
                    case BackgroundChoice.COLOR:
                        self.setRandomBackgrounColor()
            case TrackState.UPDATE_IN_PROGRESS:
                if lyric is None and self.m_NoneReceived == False:
                    lyric = ""
                    self.m_canvas.itemconfig(self.m_textContainer, text=lyric)
                    self.m_NoneReceived = True
                elif lyric is not None:
                    self.m_canvas.itemconfig(self.m_textContainer, text=lyric)
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

    def setRandomBackgrounColor(self):
        """
        A function to generate a random RGB color and set it as background

        """
        randColor = tuple(choices(range(256), k=3))
        self.m_img = Image.new('RGB', (self.m_screenWidth, self.m_screenHeight), randColor)
        self.m_img.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
        self.m_albumImage = ImageTk.PhotoImage(self.m_img)
        self.m_canvas.itemconfig(self.m_imgContainer, image=self.m_albumImage)
        self.m_canvas.itemconfig(self.m_textContainer, text="", fill=self.suggestReadableTextColor())

