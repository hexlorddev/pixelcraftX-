# PixelCrafter X

PixelCrafter X is a next-gen AI-powered creative suite built with Python, PyQt6, and advanced AI modules. It aims to provide a Photoshop-level image editing experience with additional features like AI enhancements, GPU acceleration, and plugin support.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PixelCrafterX.git
   cd PixelCrafterX
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Features

- **Canvas Engine**: Layer-based rendering with infinite canvas support and GPU acceleration.
- **Professional Toolset**: Brush engine, selection tools, shape tools, and more.
- **AI-Enhanced Features**: Background removal, inpainting, style transfer, and more.
- **Plugin System**: Extend functionality with custom plugins.
- **UI/UX**: Dark/light theme toggle, dockable panels, and keyboard shortcuts.

## Project Structure

```
PixelCrafterX/
├── core/           # Rendering engine, layer system, canvas logic
├── ui/             # PyQt6 UI components, panels, theme manager
├── tools/          # Tool modules (brush, eraser, etc.)
├── filters/        # Non-AI filters (sharpen, blur, color correction)
├── ai/             # AI modules (upscaling, inpainting, style transfer)
├── assets/         # Icons, default brushes, UI themes
├── plugins/        # Plugin system for 3rd-party tools/filters
├── utils/          # Utility functions (file I/O, memory, GPU checks)
├── config/         # JSON/YAML settings
└── main.py         # App entry point
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 