<p align="center">
  <img src="https://img.shields.io/badge/Innie-Instagram%20Grid%20Splitter-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Innie"/>
</p>

<h1 align="center">Innie</h1>

<p align="center">
  <strong>Split. Post. Impress.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Web-HTML%2FJS-E4405F?style=flat-square&logo=html5&logoColor=white" alt="Web"/>
  <img src="https://img.shields.io/badge/License-MIT-833AB4?style=flat-square" alt="License"/>
</p>

<p align="center">
  <a href="https://govinda-vurjana.github.io/Innie">🚀 Launch Web App</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-how-it-works">How It Works</a>
</p>

---

## 🎨 What is Innie?

**Innie** transforms a single image into perfectly aligned grid tiles for your Instagram profile. Create stunning 3, 6, or 9-post grid layouts that seamlessly connect when viewed on your profile.

```
┌─────────┬─────────┬─────────┐
│ Grid 1  │ Grid 2  │ Grid 3  │
├─────────┼─────────┼─────────┤
│ Grid 4  │ Grid 5  │ Grid 6  │
└─────────┴─────────┴─────────┘
        Your Instagram Profile
```

## ✨ Features

🖼️ **Smart Splitting** — Perfectly aligned tiles with no pixel loss

📐 **Multiple Layouts** — Support for 3, 6, or 9 grid configurations

🎯 **Precise Margins** — Customizable spacing for that clean aesthetic

🖌️ **Frame Options** — Outer grid frame or individual tile borders

📱 **Instagram Ready** — Outputs at 1080×1350 (optimal portrait ratio)

🌐 **Web & Desktop** — Use online or run locally

## 🚀 Quick Start

### Web Version (No Install)

👉 **[Launch Innie Web App](https://govinda-vurjana.github.io/Innie)**

Just open in your browser — no installation required. Works on any device.

### Desktop Version

```bash
# Clone the repo
git clone https://github.com/govinda-vurjana/Innie.git
cd Innie

# Install dependencies
pip install -r requirements.txt

# Run the app
python innie_ui.py
```

## 🌐 Web Version

The web version runs entirely in your browser — no uploads, no server, complete privacy.

- 📁 Load images from your device
- 👁️ Real-time preview
- 📦 Download as ZIP or individual PNGs

## 🖥️ Desktop App

The Python desktop app offers the full experience with a native UI.

| Setting | Description |
|---------|-------------|
| Grid Count | 3 (1×3), 6 (2×3), or 9 (3×3) |
| Mode | Cover (crop to fill) or Fit (no crop) |
| Margins | Top/Bottom and Left/Right spacing |
| Frame Style | Outer (grid boundary) or Individual (each tile) |
| Frame Thickness | Border width in pixels |

## 📸 How It Works

1. **Select** your image
2. **Configure** grid count, margins, and frame style
3. **Preview** the result in real-time
4. **Save** — tiles are exported with proper naming

### Output Structure

```
your_image_grid_6/
├── grid_01.png
├── grid_02.png
├── grid_03.png
├── grid_04.png
├── grid_05.png
├── grid_06.png
└── preview_grid.png
```

### Upload Order

Instagram displays the **most recent post at top-left**. Upload in reverse order:

```
grid_06 → grid_05 → grid_04 → grid_03 → grid_02 → grid_01
```

## 🎨 Frame Styles

### Outer Frame
Frame appears only on the outer boundary of the complete grid.

### Individual Frame
Each tile gets its own border around the image content.

## 📋 Requirements

```
Pillow>=10.0.0
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📄 License

MIT License — feel free to use in your projects.

---

<p align="center">
  Made with 💜 for the Instagram community
</p>

<p align="center">
  <a href="https://govinda-vurjana.github.io/Innie">
    <img src="https://img.shields.io/badge/Try%20Innie-Online-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Try Innie Online"/>
  </a>
</p>
