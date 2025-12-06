import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import os
import math


# Constants
POST_W = 1080
POST_H = 1350


class InnieUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Grid Splitter")
        self.root.configure(bg="#1a1a1a")
        
        # State
        self.source_image = None
        self.source_path = None
        self.grid_count = 6
        self.rows = 2
        self.cols = 3
        self.margin_tb = 80
        self.margin_side = 80
        self.frame_enabled = True
        self.frame_thickness = 4
        self.mode = "cover"  # cover or fit
        
        # Generated tiles
        self.tiles = {}  # {index: PIL Image}
        self.preview_image = None
        
        # Display
        self.display_w = 180
        self.display_h = 225
        self.photo_images = {}
        self.labels = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(padx=15, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg="#1a1a1a")
        left_panel.pack(side=tk.LEFT, padx=(0, 15), anchor=tk.N)
        
        # Image selection
        img_frame = tk.LabelFrame(left_panel, text="Source Image", bg="#1a1a1a", fg="white", padx=10, pady=5)
        img_frame.pack(fill=tk.X, pady=5)
        
        self.img_label = tk.Label(img_frame, text="No image selected", bg="#1a1a1a", fg="#888", width=25, anchor=tk.W)
        self.img_label.pack(side=tk.LEFT)
        
        tk.Button(img_frame, text="Browse", command=self.select_image, bg="#4a9eff", fg="white").pack(side=tk.RIGHT)
        
        # Grid settings
        grid_frame = tk.LabelFrame(left_panel, text="Grid Settings", bg="#1a1a1a", fg="white", padx=10, pady=5)
        grid_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(grid_frame, text="Grid Count:", bg="#1a1a1a", fg="white").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.grid_var = tk.StringVar(value="6")
        grid_menu = ttk.Combobox(grid_frame, textvariable=self.grid_var, values=["3", "6", "9"], width=8, state="readonly")
        grid_menu.grid(row=0, column=1, pady=2)
        grid_menu.bind("<<ComboboxSelected>>", self.on_grid_change)
        
        tk.Label(grid_frame, text="Mode:", bg="#1a1a1a", fg="white").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.mode_var = tk.StringVar(value="cover")
        mode_menu = ttk.Combobox(grid_frame, textvariable=self.mode_var, values=["cover", "fit"], width=8, state="readonly")
        mode_menu.grid(row=1, column=1, pady=2)
        
        # Margins
        margin_frame = tk.LabelFrame(left_panel, text="Margins (px)", bg="#1a1a1a", fg="white", padx=10, pady=5)
        margin_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(margin_frame, text="Top/Bottom:", bg="#1a1a1a", fg="white").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.margin_tb_var = tk.StringVar(value="80")
        tk.Entry(margin_frame, textvariable=self.margin_tb_var, width=10).grid(row=0, column=1, pady=2)
        
        tk.Label(margin_frame, text="Left/Right:", bg="#1a1a1a", fg="white").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.margin_side_var = tk.StringVar(value="80")
        tk.Entry(margin_frame, textvariable=self.margin_side_var, width=10).grid(row=1, column=1, pady=2)
        
        # Frame settings
        frame_settings = tk.LabelFrame(left_panel, text="Frame", bg="#1a1a1a", fg="white", padx=10, pady=5)
        frame_settings.pack(fill=tk.X, pady=5)
        
        self.frame_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_settings, text="Enable Frame", variable=self.frame_var, bg="#1a1a1a", fg="white",
                       selectcolor="#333", activebackground="#1a1a1a").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        tk.Label(frame_settings, text="Frame Style:", bg="#1a1a1a", fg="white").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.frame_style_var = tk.StringVar(value="outer")
        frame_style_menu = ttk.Combobox(frame_settings, textvariable=self.frame_style_var, 
                                        values=["outer", "individual"], width=8, state="readonly")
        frame_style_menu.grid(row=1, column=1, pady=2)
        
        tk.Label(frame_settings, text="Thickness:", bg="#1a1a1a", fg="white").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.frame_thick_var = tk.StringVar(value="4")
        tk.Entry(frame_settings, textvariable=self.frame_thick_var, width=10).grid(row=2, column=1, pady=2)
        
        # Action buttons
        action_frame = tk.Frame(left_panel, bg="#1a1a1a")
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(action_frame, text="Render Preview", command=self.render_preview, 
                  bg="#28a745", fg="white", width=15, height=2).pack(pady=3)
        
        tk.Button(action_frame, text="Save to Folder", command=self.save_to_folder,
                  bg="#4a9eff", fg="white", width=15, height=2).pack(pady=3)
        
        tk.Button(action_frame, text="Discard / Clear", command=self.discard_all,
                  bg="#ff4a4a", fg="white", width=15, height=2).pack(pady=3)
        
        # Right panel - Preview grid
        right_panel = tk.Frame(main_frame, bg="#1a1a1a")
        right_panel.pack(side=tk.LEFT, anchor=tk.N)
        
        tk.Label(right_panel, text="Preview", bg="#1a1a1a", fg="white", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        self.grid_frame = tk.Frame(right_panel, bg="#1a1a1a")
        self.grid_frame.pack()
        
        self.create_grid_display()
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Select an image to begin", bg="#1a1a1a", fg="#888")
        self.status_label.pack(pady=5)
    
    def create_grid_display(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        self.labels = {}
        self.photo_images = {}
        
        for row in range(self.rows):
            for col in range(self.cols):
                index = row * self.cols + col + 1
                
                cell = tk.Frame(self.grid_frame, bg="#333", width=self.display_w, height=self.display_h,
                                highlightbackground="#555", highlightthickness=1)
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell.pack_propagate(False)
                
                label = tk.Label(cell, text=f"Grid {index}", bg="#333", fg="#666", font=("Arial", 10))
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
                self.img_label.config(text=filename[:25] + "..." if len(filename) > 25 else filename)
                self.update_status(f"Loaded: {self.source_image.size[0]}x{self.source_image.size[1]}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def on_grid_change(self, event=None):
        self.grid_count = int(self.grid_var.get())
        self.rows = self.grid_count // 3
        self.create_grid_display()
        self.tiles = {}
        self.update_status(f"Grid changed to {self.grid_count}")
    
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
        except ValueError:
            messagebox.showerror("Error", "Invalid margin or thickness values")
            return
        
        try:
            self.generate_tiles()
            self.display_tiles()
            self.update_status("Preview rendered successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to render: {e}")
    
    def generate_tiles(self):
        img = self.source_image
        cols = self.cols
        rows = self.rows
        Ms = self.margin_side
        Mt = self.margin_tb
        
        # Validate margins
        if Ms * 2 >= POST_W:
            raise ValueError("Side margins too large")
        if rows == 1 and Mt * 2 >= POST_H:
            raise ValueError("Top/bottom margins too large")
        
        # Calculate content dimensions per cell (area where content can live inside each tile)
        content_widths = []
        for col in range(cols):
            left_m = Ms if col == 0 else 0
            right_m = Ms if col == cols - 1 else 0
            content_widths.append(POST_W - left_m - right_m)
        
        content_heights = []
        for row in range(rows):
            if rows == 1:
                top_m, bottom_m = Mt, Mt
            else:
                top_m = Mt if row == 0 else 0
                bottom_m = Mt if row == rows - 1 else 0
            content_heights.append(POST_H - top_m - bottom_m)
        
        W_visible = sum(content_widths)
        H_visible = sum(content_heights)
        
        # Resize source image into a big canvas W_visible x H_visible
        if self.mode == "cover":
            img_resized = self.resize_cover(img, W_visible, H_visible)
        else:  # fit
            img_resized = self.resize_fit(img, W_visible, H_visible)
        
        # Cumulative positions (split the big fitted image)
        cum_w = [0]
        for cw in content_widths[:-1]:
            cum_w.append(cum_w[-1] + cw)
        
        cum_h = [0]
        for ch in content_heights[:-1]:
            cum_h.append(cum_h[-1] + ch)
        
        # Generate each tile
        self.tiles = {}
        index = 1
        for r in range(rows):
            for c in range(cols):
                x0, y0 = cum_w[c], cum_h[r]
                x1, y1 = x0 + content_widths[c], y0 + content_heights[r]
                tile_content = img_resized.crop((x0, y0, x1, y1))
                
                # Margins for this tile (where content sits inside the post)
                if rows == 1:
                    top_m, bottom_m = Mt, Mt
                else:
                    top_m = Mt if r == 0 else 0
                    bottom_m = Mt if r == rows - 1 else 0
                left_m = Ms if c == 0 else 0
                # right margin is implicit as empty area on the right
                
                # Create post canvas
                post = Image.new("RGB", (POST_W, POST_H), (0, 0, 0))
                post.paste(tile_content, (left_m, top_m))
                
                # Draw frame
                if self.frame_enabled:
                    draw = ImageDraw.Draw(post)

                    # Detect actual image bounds inside tile_content (ignoring pure black background)
                    bbox = tile_content.getbbox()
                    if bbox is not None:
                        ix0, iy0, ix1, iy1 = bbox
                        # convert to post coordinates
                        fl = left_m + ix0
                        ft = top_m + iy0
                        fr = left_m + ix1 - 1
                        fb = top_m + iy1 - 1
                    else:
                        # No non-black content; skip frame
                        fl = ft = fr = fb = None

                    if fl is not None:
                        cw = fr - fl + 1
                        ch = fb - ft + 1

                        if self.frame_style == "outer":
                            # Frame only on outer edges of the complete grid (on image bounds)
                            if r == 0:  # top row
                                for t in range(self.frame_thickness):
                                    draw.line([(fl, ft + t), (fr, ft + t)], fill="white")
                            if r == rows - 1:  # bottom row
                                for t in range(self.frame_thickness):
                                    draw.line([(fl, fb - t), (fr, fb - t)], fill="white")
                            if c == 0:  # left column
                                for t in range(self.frame_thickness):
                                    draw.line([(fl + t, ft), (fl + t, fb)], fill="white")
                            if c == cols - 1:  # right column
                                for t in range(self.frame_thickness):
                                    draw.line([(fr - t, ft), (fr - t, fb)], fill="white")
                        
                        else:  # frame_style == "individual"
                            if self.mode == "fit":
                                # FIT MODE: treat each tile as its own image; but still only draw
                                # the segments that correspond to outer edges of the full grid.
                                if r == 0:  # top
                                    for t in range(self.frame_thickness):
                                        draw.line(
                                            [(fl, ft + t), (fr, ft + t)],
                                            fill="white",
                                        )
                                if r == rows - 1:  # bottom
                                    for t in range(self.frame_thickness):
                                        draw.line(
                                            [(fl, fb - t), (fr, fb - t)],
                                            fill="white",
                                        )
                                if c == 0:  # left
                                    for t in range(self.frame_thickness):
                                        draw.line(
                                            [(fl + t, ft), (fl + t, fb)],
                                            fill="white",
                                        )
                                if c == cols - 1:  # right
                                    for t in range(self.frame_thickness):
                                        draw.line(
                                            [(fr - t, ft), (fr - t, fb)],
                                            fill="white",
                                        )
                            else:
                                # COVER MODE: full rectangle around the image bounds in every tile
                                for t in range(self.frame_thickness):
                                    # Top
                                    draw.line(
                                        [(fl, ft + t), (fr, ft + t)],
                                        fill="white",
                                    )
                                    # Bottom
                                    draw.line(
                                        [(fl, fb - t), (fr, fb - t)],
                                        fill="white",
                                    )
                                    # Left
                                    draw.line(
                                        [(fl + t, ft), (fl + t, fb)],
                                        fill="white",
                                    )
                                    # Right
                                    draw.line(
                                        [(fr - t, ft), (fr - t, fb)],
                                        fill="white",
                                    )
                
                self.tiles[index] = post
                index += 1
    
    def resize_cover(self, img, target_w, target_h):
        orig_w, orig_h = img.size
        scale = max(target_w / orig_w, target_h / orig_h)
        new_w = int(math.ceil(orig_w * scale))
        new_h = int(math.ceil(orig_h * scale))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img_resized.crop((left, top, left + target_w, top + target_h))
    
    def resize_fit(self, img, target_w, target_h):
        orig_w, orig_h = img.size
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = int(round(orig_w * scale))
        new_h = int(round(orig_h * scale))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        left = (target_w - new_w) // 2
        top = (target_h - new_h) // 2
        canvas.paste(img_resized, (left, top))
        return canvas
    
    def display_tiles(self):
        for index, tile in self.tiles.items():
            display_img = tile.resize((self.display_w, self.display_h), Image.LANCZOS)
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
            # Auto-generate output folder next to source image
            source_dir = os.path.dirname(self.source_path)
            source_name = os.path.splitext(os.path.basename(self.source_path))[0]
            folder = os.path.join(source_dir, f"{source_name}_grid_{self.grid_count}")
            
            # Create folder if it doesn't exist
            os.makedirs(folder, exist_ok=True)
            
            for index, tile in self.tiles.items():
                path = os.path.join(folder, f"grid_{index:02d}.png")
                tile.save(path)
            
            # Save preview
            preview = self.create_preview_image()
            preview.save(os.path.join(folder, "preview_grid.png"))
            
            messagebox.showinfo("Success", f"Saved {len(self.tiles)} images + preview to:\n{folder}")
            self.update_status(f"Saved to {folder}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
    
    def create_preview_image(self):
        preview = Image.new("RGB", (self.cols * POST_W, self.rows * POST_H), (0, 0, 0))
        for index, tile in self.tiles.items():
            row = (index - 1) // self.cols
            col = (index - 1) % self.cols
            preview.paste(tile, (col * POST_W, row * POST_H))
        return preview
    
    def discard_all(self):
        self.source_image = None
        self.source_path = None
        self.tiles = {}
        self.photo_images = {}
        self.img_label.config(text="No image selected")
        self.create_grid_display()
        self.update_status("Cleared all")
    
    def update_status(self, msg):
        self.status_label.config(text=msg)


def main():
    root = tk.Tk()
    root.resizable(True, True)
    app = InnieUI(root)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
