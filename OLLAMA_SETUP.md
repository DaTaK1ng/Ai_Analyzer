# Local AI model setup (Ollama)

This project uses a **local LLM** via [Ollama](https://ollama.com) so no API key is needed. Follow these steps once on your machine.

## 1. Install Ollama

- **macOS**: Download from [ollama.com](https://ollama.com) and open the app, or install via Homebrew:
  ```bash
  brew install ollama
  brew services start ollama
  ```
- **Windows**: Download the installer from [ollama.com](https://ollama.com).
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

Ensure Ollama is running (you should see it in the menu bar or system tray).

## 2. Pull a model

In a terminal, run:

```bash
ollama pull qwen2.5:7b
```

Or a smaller option (less RAM):

```bash
ollama pull qwen2.5:1.5b
```

The app will call `http://localhost:11434`. No model files go in this project folder; Ollama stores them in its own directory.

## 3. Verify

```bash
ollama list
```

You should see the model you pulled. Then run your dashboard; the AI step will use this model.
