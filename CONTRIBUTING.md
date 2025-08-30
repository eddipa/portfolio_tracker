# Contributing Guidelines

Thank you for considering contributing to **Python Portfolio Tracker**!

## How to Contribute

### 1. Fork & Clone
- Fork the repository on GitHub.
- Clone your fork locally and create a new branch for your feature or bugfix.

### 2. Development Setup
Install in editable mode with development dependencies:

```bash
pip install -e .[dev]
```

Run tests with:

```bash
pytest -q
```

### 3. Code Style
- Use **4 spaces** for indentation.
- Keep functions small and readable.
- Add docstrings where helpful.

### 4. Testing
- All new features and bug fixes should include **unit tests**.
- Place tests in the `tests/` folder, using `pytest`.

### 5. Commit Messages
- Use clear, descriptive commit messages.
- Example: `fix: correct FIFO realized PnL calculation`

### 6. Pull Requests
- Open a PR against the `main` branch.
- Ensure all tests pass before requesting review.

## Reporting Issues
If you find a bug, please [open an issue](../../issues) with steps to reproduce.  
Feature requests are also welcome!

---
Happy coding 🚀
