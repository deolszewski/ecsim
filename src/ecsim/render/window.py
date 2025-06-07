import tkinter as tk


class CloseButton(tk.Button):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.config(
            bg=master.cget("bg"),
            activebackground=master.cget("bg"),
            fg="#9e9e9e",
            width=5,
            text="x",
            bd=0,
        )
        # Hover handling
        self.bind("<Enter>", lambda e: self.config(fg="#2b3d47"))
        self.bind("<Leave>", lambda e: self.config(fg="#9e9e9e"))


class SelectButton(tk.Button):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.config(
            bg="#100e26",
            activebackground="#201c4a",
            fg="#9e9e9e",
            width=5,
            text="Next",
            bd=0,
        )
        # Hover handling
        self.bind("<Enter>", lambda e: self.config(fg="#2b3d47"))
        self.bind("<Leave>", lambda e: self.config(fg="#9e9e9e"))


class Window(tk.Tk):
    def __init__(self, event_callback) -> None:
        tk.Tk.__init__(self)
        self.event_callback = event_callback
        self.HEIGHT = self.winfo_screenheight() * 0.6
        self.WIDTH = self.winfo_screenwidth() * 0.6
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self._offset_x = 0
        self._offset_y = 0
        self.bind("<Button-1>", self._click_window)
        self.bind("<B1-Motion>", self._drag_window)
        self.configure(
            bg="#1c1c1c",
        )
        self.geometry(f"{int(self.WIDTH)}x{int(self.HEIGHT)}")
        self.layout()

    def _drag_window(self, event) -> None:
        if event.widget == self.handle_bar:
            x = self.winfo_pointerx() - self._offset_x
            y = self.winfo_pointery() - self._offset_y
            self.geometry(f"+{x}+{y}")

    def _click_window(self, event) -> None:
        if event.widget == self.handle_bar:
            self._offset_x = event.x
            self._offset_y = event.y

    def _close_window(self) -> None:
        self.destroy()

    def _trigger_event(self, event_type, *args) -> None:
        if self.event_callback:
            self.event_callback(event_type, *args)

    def layout(self) -> None:
        # Handle bar
        self.handle_bar = tk.Frame(
            self,
            bg="#1c1c1f",
            height=20,
        )
        self.handle_bar.pack(side=tk.TOP, fill=tk.X)

        # Close button
        self.close_button = CloseButton(
            master=self.handle_bar,
            command=self._close_window,
        )
        self.close_button.pack(side=tk.RIGHT)

        # Controls panel
        self.controls_frame = tk.Frame(self, width=200, bg="#1c1f1f")
        self.controls_frame.pack(padx=5, pady=5, fill=tk.Y, side=tk.LEFT)
        self.controls_frame.pack_propagate(False)

        self.next_button = SelectButton(
            master=self.controls_frame,
            height=3,
            command=lambda: self._trigger_event("next_object"),
            font=tk.font.Font(family="Verdana", size=12),
        )  # TODO: clicked_obj on main canvas
        self.next_button.pack(padx=20, pady=20, fill=tk.X)
        self.next_button.pack_propagate(False)

        # FPS Slider
        self.fps_slider = tk.Scale(
            self.controls_frame,
            from_=1,
            to=200,
            orient="horizontal",
            bg="#100e26",
            bd=0,
            fg="#9c9c9c",
            label="FPS",
            relief="flat",
        )
        self.fps_slider.pack(padx=20, pady=20, fill=tk.X)
        self.fps_slider.set(30)

        # Pygame
        self.pygame_frame = tk.Frame(
            self,
            bg="#1c1c1c",
            height=self.HEIGHT,
            width=self.HEIGHT,
        )
        self.pygame_frame.pack(
            padx=5,
            pady=5,
            side=tk.LEFT,
        )
        self.pygame_frame.pack_propagate(False)

        # Matplotlib plots
        self.matplot_frame = tk.Frame(
            self,
            bg="#1c1c1c",
        )
        self.matplot_frame.pack(
            padx=5,
            pady=5,
            fill=tk.Y,
            side=tk.RIGHT,
        )
