import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import os
import math

# Constants
POST_W = 1080
POST_H = 1350

# Colors (Instagram-inspired)
COLORS = {
    "bg_dark": "#0a0a0a",
    "bg_card": "#141414",
    "bg_input": "#1a1a1a",
    "border": "#2a2a2a",
    "text": "#ffffff",
    "text_secondary": "#888888",
    "text_muted": "#555555",
    "pink": "#E4405F",
    "purple": "#833AB4",
    "orange": "#F77737",
    "green": "#28a745",
}


class InnieUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Innie — Instagram Grid Splitter")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.minsize(900, 600)
        
        # State
        self.source_image = None
        self.source_path = None
        self.thumb_photo = None
        self.grid_count = 6
        self.rows = 2
        self.cols = 3
        self.margin_tb = 80
        self.margin_side = 80
        self.frame_enabled = True
        self.frame_thickness = 4
        self.frame_style = "outer"
        self.mode = "cover"
        self.edge_tiles_enabled = False
        self.edge_margin = 0
        
        # Generated tiles
        self.tiles = {}
        self.photo_images = {}
        self.labels = {}
        
        # Display sizes
        self.cell_w = 140
        self.cell_h = 175
        
        self.setup_styles()
        self.setup_ui()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Combobox style
        style.configure("Dark.TCombobox",
            fieldbackground=COLORS["bg_input"],
            background=COLORS["bg_input"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["text_secondary"],
            selectbackground=COLORS["pink"],
            selectforeground=COLORS["text"]
        )
        style.map("Dark.TCombobox",
            fieldbackground=[("readonly", COLORS["bg_input"])],
            selectbackground=[("readonly", COLORS["bg_input"])],
            selectforeground=[("readonly", COLORS["text"])]
        )
    
    def setup_ui(self):
        # Main container
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Sidebar
        self.create_sidebar()
        
        # Preview area
        self.create_preview_area()
    
    def create_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg_card"], height=50)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        # Brand
        brand_frame = tk.Frame(header, bg=COLORS["bg_card"])
        brand_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        brand = tk.Label(brand_frame, text="Innie", font=("Helvetica", 20, "bold"),
                        bg=COLORS["bg_card"], fg=COLORS["pink"])
        brand.pack(side=tk.LEFT)
        
        divider = tk.Frame(brand_frame, bg=COLORS["border"], width=1, height=20)
        divider.pack(side=tk.LEFT, padx=12)
        
        tagline = tk.Label(brand_frame, text="Split. Post. Impress.",
                          font=("Helvetica", 10), bg=COLORS["bg_card"], fg=COLORS["text_secondary"])
        tagline.pack(side=tk.LEFT)
        
        # GitHub link
        github = tk.Label(header, text="⭐ GitHub", font=("Helvetica", 10),
                         bg=COLORS["bg_input"], fg=COLORS["text"], padx=12, pady=4, cursor="hand2")
        github.pack(side=tk.RIGHT, padx=20)
        github.bind("<Button-1>", lambda e: os.startfile("https://github.com/govinda-vurjana/Innie") if os.name == 'nt' else None)
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=COLORS["bg_card"], width=280)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        
        # Scrollable content
        canvas = tk.Canvas(sidebar, bg=COLORS["bg_card"], highlightthickness=0)
        scrollbar = tk.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=COLORS["bg_card"])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=content, anchor="nw", width=260)
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Source Image Section
        self.create_section(content, "SOURCE IMAGE")
        self.create_image_upload(content)
        
        # Settings Section
        self.create_section(content, "SETTINGS")
        self.create_settings(content)
        
        # Frame Section
        self.create_section(content, "FRAME")
        self.create_frame_settings(content)
        
        # Actions
        self.create_actions(content)
    
    def create_section(self, parent, title):
        frame = tk.Frame(parent, bg=COLORS["bg_card"])
        frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        
        accent = tk.Frame(frame, bg=COLORS["pink"], width=3, height=12)
        accent.pack(side=tk.LEFT, padx=(0, 8))
        
        label = tk.Label(frame, text=title, font=("Helvetica", 9, "bold"),
                        bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        label.pack(side=tk.LEFT)
    
    def create_image_upload(self, parent):
        container = tk.Frame(parent, bg=COLORS["bg_card"])
        container.pack(fill=tk.X, padx=16, pady=4)
        
        # Upload zone
        self.upload_zone = tk.Frame(container, bg=COLORS["bg_input"], 
                                    highlightbackground=COLORS["border"], highlightthickness=2)
        self.upload_zone.pack(fill=tk.X, ipady=20)
        
        upload_content = tk.Frame(self.upload_zone, bg=COLORS["bg_input"])
        upload_content.pack(expand=True)
        
        icon = tk.Label(upload_content, text="🖼️", font=("Helvetica", 24), bg=COLORS["bg_input"])
        icon.pack()
        
        text = tk.Label(upload_content, text="Click to upload", font=("Helvetica", 11),
                       bg=COLORS["bg_input"], fg=COLORS["text_secondary"])
        text.pack()
        
        self.upload_zone.bind("<Button-1>", lambda e: self.select_image())
        upload_content.bind("<Button-1>", lambda e: self.select_image())
        icon.bind("<Button-1>", lambda e: self.select_image())
        text.bind("<Button-1>", lambda e: self.select_image())
        
        # Image thumbnail (hidden initially)
        self.thumb_frame = tk.Frame(container, bg=COLORS["bg_input"])
        
        self.thumb_label = tk.Label(self.thumb_frame, bg=COLORS["bg_input"])
        self.thumb_label.pack(fill=tk.X)
        
        info_frame = tk.Frame(self.thumb_frame, bg=COLORS["bg_input"])
        info_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.filename_label = tk.Label(info_frame, text="", font=("Helvetica", 10),
                                       bg=COLORS["bg_input"], fg=COLORS["text_secondary"], anchor="w")
        self.filename_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        remove_btn = tk.Label(info_frame, text="✕", font=("Helvetica", 12, "bold"),
                             bg=COLORS["pink"], fg="white", padx=6, pady=2, cursor="hand2")
        remove_btn.pack(side=tk.RIGHT)
        remove_btn.bind("<Button-1>", lambda e: self.clear_image())
    
    def create_settings(self, parent):
        container = tk.Frame(parent, bg=COLORS["bg_card"])
        container.pack(fill=tk.X, padx=16, pady=4)
        
        # Row 1: Grid + Mode
        row1 = tk.Frame(container, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=4)
        
        # Grid
        grid_frame = tk.Frame(row1, bg=COLORS["bg_card"])
        grid_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Label(grid_frame, text="Grid", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.grid_var = tk.StringVar(value="6")
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_var, 
                                  values=["3", "6", "9"], state="readonly", style="Dark.TCombobox")
        grid_combo.pack(fill=tk.X, pady=2)
        grid_combo.bind("<<ComboboxSelected>>", self.on_grid_change)
        
        # Mode
        mode_frame = tk.Frame(row1, bg=COLORS["bg_card"])
        mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(mode_frame, text="Mode", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.mode_var = tk.StringVar(value="cover")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                  values=["cover", "fit"], state="readonly", style="Dark.TCombobox")
        mode_combo.pack(fill=tk.X, pady=2)
        
        # Row 2: Margins
        row2 = tk.Frame(container, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X, pady=4)
        
        # Margin TB
        mtb_frame = tk.Frame(row2, bg=COLORS["bg_card"])
        mtb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Label(mtb_frame, text="Margin TB", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.margin_tb_var = tk.StringVar(value="80")
        mtb_entry = tk.Entry(mtb_frame, textvariable=self.margin_tb_var, font=("Helvetica", 11),
                            bg=COLORS["bg_input"], fg=COLORS["text"], insertbackground=COLORS["text"],
                            relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        mtb_entry.pack(fill=tk.X, pady=2, ipady=4)
        
        # Margin LR
        mlr_frame = tk.Frame(row2, bg=COLORS["bg_card"])
        mlr_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(mlr_frame, text="Margin LR", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.margin_side_var = tk.StringVar(value="80")
        mlr_entry = tk.Entry(mlr_frame, textvariable=self.margin_side_var, font=("Helvetica", 11),
                            bg=COLORS["bg_input"], fg=COLORS["text"], insertbackground=COLORS["text"],
                            relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        mlr_entry.pack(fill=tk.X, pady=2, ipady=4)
        
        # Edge Tiles Margin checkbox
        self.edge_tiles_var = tk.BooleanVar(value=False)
        edge_check_frame = tk.Frame(container, bg=COLORS["bg_card"])
        edge_check_frame.pack(fill=tk.X, pady=4)
        
        edge_cb = tk.Checkbutton(edge_check_frame, text="Edge Tiles Margin", variable=self.edge_tiles_var,
                                font=("Helvetica", 10), bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                                selectcolor=COLORS["bg_input"], activebackground=COLORS["bg_card"],
                                activeforeground=COLORS["text"], command=self.toggle_edge_margin)
        edge_cb.pack(anchor="w")
        
        # Edge margin input (hidden by default)
        self.edge_margin_frame = tk.Frame(container, bg=COLORS["bg_card"])
        
        tk.Label(self.edge_margin_frame, text="Edge Margin (px)", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.edge_margin_var = tk.StringVar(value="36")
        edge_entry = tk.Entry(self.edge_margin_frame, textvariable=self.edge_margin_var, font=("Helvetica", 11),
                             bg=COLORS["bg_input"], fg=COLORS["text"], insertbackground=COLORS["text"],
                             relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        edge_entry.pack(fill=tk.X, pady=2, ipady=4)
    
    def toggle_edge_margin(self):
        if self.edge_tiles_var.get():
            self.edge_margin_frame.pack(fill=tk.X, pady=4)
        else:
            self.edge_margin_frame.pack_forget()
    
    def create_frame_settings(self, parent):
        container = tk.Frame(parent, bg=COLORS["bg_card"])
        container.pack(fill=tk.X, padx=16, pady=4)
        
        # Enable checkbox
        self.frame_var = tk.BooleanVar(value=True)
        check_frame = tk.Frame(container, bg=COLORS["bg_card"])
        check_frame.pack(fill=tk.X, pady=4)
        
        cb = tk.Checkbutton(check_frame, text="Enable Frame", variable=self.frame_var,
                           font=("Helvetica", 11), bg=COLORS["bg_card"], fg=COLORS["text"],
                           selectcolor=COLORS["bg_input"], activebackground=COLORS["bg_card"],
                           activeforeground=COLORS["text"])
        cb.pack(anchor="w")
        
        # Row: Style + Thickness
        row = tk.Frame(container, bg=COLORS["bg_card"])
        row.pack(fill=tk.X, pady=4)
        
        # Style
        style_frame = tk.Frame(row, bg=COLORS["bg_card"])
        style_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Label(style_frame, text="Style", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.frame_style_var = tk.StringVar(value="outer")
        style_combo = ttk.Combobox(style_frame, textvariable=self.frame_style_var,
                                   values=["outer", "individual"], state="readonly", style="Dark.TCombobox")
        style_combo.pack(fill=tk.X, pady=2)
        
        # Thickness
        thick_frame = tk.Frame(row, bg=COLORS["bg_card"])
        thick_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(thick_frame, text="Thickness", font=("Helvetica", 10),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
        
        self.frame_thick_var = tk.StringVar(value="4")
        thick_entry = tk.Entry(thick_frame, textvariable=self.frame_thick_var, font=("Helvetica", 11),
                              bg=COLORS["bg_input"], fg=COLORS["text"], insertbackground=COLORS["text"],
                              relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        thick_entry.pack(fill=tk.X, pady=2, ipady=4)
    
    def create_actions(self, parent):
        container = tk.Frame(parent, bg=COLORS["bg_card"])
        container.pack(fill=tk.X, padx=16, pady=20)
        
        # Render button
        render_btn = tk.Button(container, text="✨ Render", font=("Helvetica", 11, "bold"),
                              bg=COLORS["pink"], fg="white", relief="flat", cursor="hand2",
                              activebackground=COLORS["purple"], activeforeground="white",
                              command=self.render_preview)
        render_btn.pack(fill=tk.X, pady=4, ipady=8)
        
        # Download button
        download_btn = tk.Button(container, text="📥 Download", font=("Helvetica", 11),
                                bg=COLORS["bg_input"], fg=COLORS["text"], relief="flat", cursor="hand2",
                                activebackground=COLORS["border"], activeforeground=COLORS["text"],
                                highlightthickness=1, highlightbackground=COLORS["border"],
                                command=self.save_to_folder)
        download_btn.pack(fill=tk.X, pady=4, ipady=8)
    
    def create_preview_area(self):
        preview_area = tk.Frame(self.root, bg=COLORS["bg_dark"])
        preview_area.grid(row=1, column=1, sticky="nsew")
        
        # Center container
        center = tk.Frame(preview_area, bg=COLORS["bg_dark"])
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        # Grid container
        self.grid_frame = tk.Frame(center, bg="#000000", padx=3, pady=3)
        self.grid_frame.pack()
        
        self.create_grid_display()
        
        # Badge
        self.badge = tk.Label(center, text="Upload an image and click Render",
                             font=("Helvetica", 10), bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                             padx=12, pady=6)
        self.badge.pack(pady=16)
    
    def create_grid_display(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        self.labels = {}
        self.photo_images = {}
        
        for row in range(self.rows):
            for col in range(self.cols):
                index = row * self.cols + col + 1
                
                cell = tk.Frame(self.grid_frame, bg=COLORS["bg_input"], 
                               width=self.cell_w, height=self.cell_h)
                cell.grid(row=row, column=col, padx=2, pady=2)
                cell.pack_propagate(False)
                
                label = tk.Label(cell, text=str(index), font=("Helvetica", 12),
                                bg=COLORS["bg_input"], fg=COLORS["text_muted"])
                label.pack(expand=True, fill=tk.BOTH)
                
                self.labels[index] = label
    
    def select_image(self):
        path = filedialog.askopenfilename(
            title="Select source image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
        )
        if path:
            try:
                self.source_image = Image.open(path).convert("RGB")
                self.source_path = path
                filename = os.path.basename(path)
                
                # Create thumbnail
                thumb = self.source_image.copy()
                thumb.thumbnail((248, 120), Image.LANCZOS)
                self.thumb_photo = ImageTk.PhotoImage(thumb)
                self.thumb_label.config(image=self.thumb_photo)
                
                # Update filename
                self.filename_label.config(text=filename[:30] + "..." if len(filename) > 30 else filename)
                
                # Show thumbnail, hide upload zone
                self.upload_zone.pack_forget()
                self.thumb_frame.pack(fill=tk.X)
                
                self.badge.config(text=f"Loaded: {self.source_image.size[0]}×{self.source_image.size[1]}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def clear_image(self):
        self.source_image = None
        self.source_path = None
        self.thumb_photo = None
        self.tiles = {}
        
        # Hide thumbnail, show upload zone
        self.thumb_frame.pack_forget()
        self.upload_zone.pack(fill=tk.X, ipady=20)
        
        self.create_grid_display()
        self.badge.config(text="Upload an image and click Render")
    
    def on_grid_change(self, event=None):
        self.grid_count = int(self.grid_var.get())
        self.rows = self.grid_count // 3
        self.create_grid_display()
        self.tiles = {}
    
    def render_preview(self):
        if not self.source_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.margin_tb = int(self.margin_tb_var.get())
            self.margin_side = int(self.margin_side_var.get())
            self.frame_enabled = self.frame_var.get()
            self.frame_thickness = int(self.frame_thick_var.get()) if self.frame_enabled else 0
            self.frame_style = self.frame_style_var.get()
            self.mode = self.mode_var.get()
            self.edge_tiles_enabled = self.edge_tiles_var.get()
            self.edge_margin = int(self.edge_margin_var.get()) if self.edge_tiles_enabled else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid margin or thickness values")
            return
        
        try:
            self.generate_tiles()
            self.display_tiles()
            self.badge.config(text="✓ Rendered successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to render: {e}")
    
    def generate_tiles(self):
        img = self.source_image
        cols, rows = self.cols, self.rows
        Ms, Mt = self.margin_side, self.margin_tb
        edge_margin = self.edge_margin
        
        if Ms * 2 >= POST_W:
            raise ValueError("Side margins too large")
        if rows == 1 and Mt * 2 >= POST_H:
            raise ValueError("Top/bottom margins too large")
        
        content_widths = [POST_W - (Ms if c == 0 else 0) - (Ms if c == cols - 1 else 0) for c in range(cols)]
        content_heights = []
        for r in range(rows):
            top_m = Mt if (rows == 1 or r == 0) else 0
            bottom_m = Mt if (rows == 1 or r == rows - 1) else 0
            content_heights.append(POST_H - top_m - bottom_m)
        
        # Edge tiles padding: col 0 gets RIGHT padding, col 2 gets LEFT padding
        # Middle column (col 1, tiles 2,5,8) gets both left and right padding
        edge_padding = []
        for c in range(cols):
            pad_left = edge_margin if c == cols - 1 else 0   # Col 2 (tiles 3,6,9): LEFT padding
            pad_right = edge_margin if c == 0 else 0         # Col 0 (tiles 1,4,7): RIGHT padding
            
            # Middle column gets both sides
            if c == 1:
                pad_left = edge_margin
                pad_right = edge_margin
            edge_padding.append({'pad_left': pad_left, 'pad_right': pad_right})
        
        # Actual image content = content area minus edge padding
        actual_content_widths = [content_widths[c] - edge_padding[c]['pad_left'] - edge_padding[c]['pad_right'] for c in range(cols)]
        
        W_visible, H_visible = sum(actual_content_widths), sum(content_heights)
        
        if self.mode == "cover":
            img_resized = self.resize_cover(img, W_visible, H_visible)
        else:
            img_resized = self.resize_fit(img, W_visible, H_visible)
        
        cum_w = [sum(actual_content_widths[:i]) for i in range(cols)]
        cum_h = [sum(content_heights[:i]) for i in range(rows)]
        
        self.tiles = {}
        index = 1
        for r in range(rows):
            for c in range(cols):
                x0, y0 = cum_w[c], cum_h[r]
                src_w, src_h = actual_content_widths[c], content_heights[r]
                tile_content = img_resized.crop((x0, y0, x0 + src_w, y0 + src_h))
                
                top_m = Mt if (rows == 1 or r == 0) else 0
                left_m = Ms if c == 0 else 0
                
                # Edge padding for this column
                e_pad_left = edge_padding[c]['pad_left']
                
                post = Image.new("RGB", (POST_W, POST_H), (0, 0, 0))
                # Draw image shifted by edge padding (leaves black margin on edge)
                draw_x = left_m + e_pad_left
                post.paste(tile_content, (draw_x, top_m))
                
                # Content area for frame (full content width including edge padding)
                cw, ch = content_widths[c], content_heights[r]
                
                # Skip frame on sides where edge margin is applied
                skip_left = e_pad_left > 0
                skip_right = edge_padding[c]['pad_right'] > 0
                
                if self.frame_enabled:
                    draw = ImageDraw.Draw(post)
                    fl, ft = left_m, top_m
                    fr, fb = left_m + cw - 1, top_m + ch - 1
                    
                    if self.frame_style == "outer":
                        # Outer frame: only on grid outer edges
                        if r == 0:
                            for t in range(self.frame_thickness):
                                draw.line([(fl, ft + t), (fr, ft + t)], fill="white")
                        if r == rows - 1:
                            for t in range(self.frame_thickness):
                                draw.line([(fl, fb - t), (fr, fb - t)], fill="white")
                        if c == 0 and not skip_left:
                            for t in range(self.frame_thickness):
                                draw.line([(fl + t, ft), (fl + t, fb)], fill="white")
                        if c == cols - 1 and not skip_right:
                            for t in range(self.frame_thickness):
                                draw.line([(fr - t, ft), (fr - t, fb)], fill="white")
                    else:
                        # Individual frame: on grid outer edges, using image content bounds for fit mode
                        if self.mode == "fit":
                            # Fit mode: frame around actual image bounds, only on outer edges
                            bbox = tile_content.getbbox()
                            if bbox:
                                ix0 = draw_x + bbox[0]
                                iy0 = top_m + bbox[1]
                                ix1 = draw_x + bbox[2] - 1
                                iy1 = top_m + bbox[3] - 1
                                if r == 0:
                                    for t in range(self.frame_thickness):
                                        draw.line([(ix0, iy0 + t), (ix1, iy0 + t)], fill="white")  # top
                                if r == rows - 1:
                                    for t in range(self.frame_thickness):
                                        draw.line([(ix0, iy1 - t), (ix1, iy1 - t)], fill="white")  # bottom
                                if c == 0 and not skip_left:
                                    for t in range(self.frame_thickness):
                                        draw.line([(ix0 + t, iy0), (ix0 + t, iy1)], fill="white")  # left
                                if c == cols - 1 and not skip_right:
                                    for t in range(self.frame_thickness):
                                        draw.line([(ix1 - t, iy0), (ix1 - t, iy1)], fill="white")  # right
                        else:
                            # Cover mode: frame around content area, only on outer edges
                            if r == 0:
                                for t in range(self.frame_thickness):
                                    draw.line([(fl, ft + t), (fr, ft + t)], fill="white")  # top
                            if r == rows - 1:
                                for t in range(self.frame_thickness):
                                    draw.line([(fl, fb - t), (fr, fb - t)], fill="white")  # bottom
                            if c == 0 and not skip_left:
                                for t in range(self.frame_thickness):
                                    draw.line([(fl + t, ft), (fl + t, fb)], fill="white")  # left
                            if c == cols - 1 and not skip_right:
                                for t in range(self.frame_thickness):
                                    draw.line([(fr - t, ft), (fr - t, fb)], fill="white")  # right
                
                self.tiles[index] = post
                index += 1
    
    def resize_cover(self, img, target_w, target_h):
        scale = max(target_w / img.size[0], target_h / img.size[1])
        new_w, new_h = int(math.ceil(img.size[0] * scale)), int(math.ceil(img.size[1] * scale))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        left, top = (new_w - target_w) // 2, (new_h - target_h) // 2
        return img_resized.crop((left, top, left + target_w, top + target_h))
    
    def resize_fit(self, img, target_w, target_h):
        scale = min(target_w / img.size[0], target_h / img.size[1])
        new_w, new_h = int(round(img.size[0] * scale)), int(round(img.size[1] * scale))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        canvas.paste(img_resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
        return canvas
    
    def display_tiles(self):
        for index, tile in self.tiles.items():
            display_img = tile.resize((self.cell_w, self.cell_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(display_img)
            self.photo_images[index] = photo
            self.labels[index].config(image=photo, text="")
    
    def save_to_folder(self):
        if not self.tiles:
            messagebox.showwarning("Warning", "Please render preview first")
            return
        
        if not self.source_path:
            messagebox.showwarning("Warning", "No source image loaded")
            return
        
        try:
            source_dir = os.path.dirname(self.source_path)
            source_name = os.path.splitext(os.path.basename(self.source_path))[0]
            folder = os.path.join(source_dir, f"{source_name}_grid_{self.grid_count}")
            os.makedirs(folder, exist_ok=True)
            
            for index, tile in self.tiles.items():
                tile.save(os.path.join(folder, f"grid_{index:02d}.png"))
            
            preview = Image.new("RGB", (self.cols * POST_W, self.rows * POST_H), (0, 0, 0))
            for index, tile in self.tiles.items():
                row, col = (index - 1) // self.cols, (index - 1) % self.cols
                preview.paste(tile, (col * POST_W, row * POST_H))
            preview.save(os.path.join(folder, "preview_grid.png"))
            
            messagebox.showinfo("Success", f"Saved {len(self.tiles)} images + preview to:\n{folder}")
            self.badge.config(text=f"✓ Saved to {os.path.basename(folder)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


def main():
    root = tk.Tk()
    root.resizable(True, True)
    app = InnieUI(root)
    
    root.update_idletasks()
    w, h = 950, 650
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
