import os
from PIL import Image, ImageDraw

def ask_int(prompt, allowed=None, default=None):
    while True:
        raw = input(f"{prompt} " + (f"[default: {default}]: " if default is not None else ": "))
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if allowed and val not in allowed:
                print(f"Please enter one of: {allowed}")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def ask_yes_no(prompt, default="y"):
    default = default.lower()
    while True:
        raw = input(f"{prompt} [y/n, default: {default}]: ").strip().lower()
        if not raw:
            raw = default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please enter y or n.")


def split_image_to_grid(img, grid_count):
    """
    grid_count: 3, 6, or 9.
    We always use 3 columns.
    rows = grid_count / 3
    """
    cols = 3
    rows = grid_count // 3

    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows

    tiles = []
    for row in range(rows):
        for col in range(cols):
            left = col * tile_w
            upper = row * tile_h
            right = left + tile_w
            lower = upper + tile_h
            tile = img.crop((left, upper, right, lower))
            tiles.append((tile, row, col))
    return tiles, rows, cols, tile_w, tile_h


def build_preview_and_slices(
    img,
    grid_count,
    margin_tb,
    margin_side,
    frame_enabled,
    frame_thickness=4,
    frame_color=(255, 255, 255),
    bg_color=(0, 0, 0),
    out_dir="output",
):
    os.makedirs(out_dir, exist_ok=True)

    tiles, rows, cols, tile_w, tile_h = split_image_to_grid(img, grid_count)

    # Preview canvas size (one big grid, no gaps between tiles except outer margins)
    canvas_w = cols * tile_w + 2 * margin_side
    canvas_h = rows * tile_h + 2 * margin_tb

    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(canvas)

    # Paste tiles into the preview canvas
    for tile, row, col in tiles:
        x = margin_side + col * tile_w
        y = margin_tb + row * tile_h
        canvas.paste(tile, (x, y))

        if frame_enabled:
            # Draw frame segments only on the OUTER edges of the whole spread
            # so we don't double-draw lines between tiles.
            x0, y0 = x, y
            x1, y1 = x + tile_w - 1, y + tile_h - 1

            # Top edge (only for top row)
            if row == 0:
                for t in range(frame_thickness):
                    draw.line([(x0, y0 + t), (x1, y0 + t)], fill=frame_color)

            # Bottom edge (only for bottom row)
            if row == rows - 1:
                for t in range(frame_thickness):
                    draw.line([(x0, y1 - t), (x1, y1 - t)], fill=frame_color)

            # Left edge (only for first column)
            if col == 0:
                for t in range(frame_thickness):
                    draw.line([(x0 + t, y0), (x0 + t, y1)], fill=frame_color)

            # Right edge (only for last column)
            if col == cols - 1:
                for t in range(frame_thickness):
                    draw.line([(x1 - t, y0), (x1 - t, y1)], fill=frame_color)

    # Save preview of the entire grid
    preview_path = os.path.join(out_dir, "preview_grid.png")
    canvas.save(preview_path)
    print(f"Preview saved as: {preview_path}")

    # Now cut the preview back into individual post images (INCLUDING margins & frames)
    # This way, what you post matches the preview exactly.
    index = 1
    for row in range(rows):
        for col in range(cols):
            # Crop bounds for each post in the final preview
            if col == 0:
                left = 0
            else:
                left = margin_side + col * tile_w

            if col == cols - 1:
                right = canvas_w
            else:
                right = margin_side + (col + 1) * tile_w

            if row == 0:
                top = 0
            else:
                top = margin_tb + row * tile_h

            if row == rows - 1:
                bottom = canvas_h
            else:
                bottom = margin_tb + (row + 1) * tile_h

            slice_img = canvas.crop((left, top, right, bottom))
            # Naming: index is 1..grid_count in reading order (top-left to bottom-right)
            # Note: Instagram shows the LAST posted as top-left in your profile grid,
            # so if you want the preview to match exactly, you usually post files in
            # REVERSE order (grid_09, grid_08, ..., grid_01).
            slice_name = f"grid_{index:02d}.png"
            slice_path = os.path.join(out_dir, slice_name)
            slice_img.save(slice_path)
            print(f"Saved slice: {slice_path}")
            index += 1

    print("\nDone.")
    print("Upload order tip: Instagram profile shows the last uploaded at top-left.")
    print("So to match the preview, usually post the images in REVERSE filename order.")


def main():
    print("=== Instagram Grid Splitter ===")

    img_path = input("Enter path to the base image: ").strip()
    if not os.path.isfile(img_path):
        print("Error: file not found.")
        return

    grid_count = ask_int("Enter grid count (3, 6, or 9):", allowed=[3, 6, 9])
    margin_tb = ask_int("Enter top/bottom margin (in pixels):", default=40)
    margin_side = ask_int("Enter left/right margin (in pixels):", default=40)

    frame_enabled = ask_yes_no("Enable frame lines around the grid?", default="y")
    frame_thickness = 0
    if frame_enabled:
        frame_thickness = ask_int("Frame thickness (pixels):", default=4)

    out_dir = input("Output folder name [default: output]: ").strip() or "output"

    img = Image.open(img_path).convert("RGB")

    build_preview_and_slices(
        img=img,
        grid_count=grid_count,
        margin_tb=margin_tb,
        margin_side=margin_side,
        frame_enabled=frame_enabled,
        frame_thickness=frame_thickness if frame_enabled else 0,
        out_dir=out_dir,
    )


if __name__ == "__main__":
    main()
