# Quick Start Guide

## First Time Setup

1. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - Version 3.8 or higher required
   - On Windows, check "Add Python to PATH" during installation

2. **Install Required Package**
   ```bash
   pip install requests
   ```

3. **Run the App**
   - Windows: Double-click `search.pyw` or `run.bat`
   - Other: Run `python search.py` from terminal

## Quick Search Example

1. **Languages**: Check "Python" and "JavaScript"
2. **Tags**: One tag at a time.
3. **Custom Terms**: Leave blank (or try "documentation")
4. **Click**: "🔍 Search for Issues"
5. **Wait**: Results will appear in a few seconds
6. **Click**: Any blue repository name to open in browser

## Running Without Console (Windows)

### Option 1: Use .pyw file
Double-click `search.pyw` - opens app without console window

### Option 2: Use batch file
Double-click `run.bat` - same as above

### Option 3: Command line
```bash
pythonw search.py
```

## Common Issues

**"No module named 'requests'"**
- Run: `pip install requests`

**"python is not recognized"**
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python3X\python.exe search.py`

**No results found**
- Try increasing "Updated Within" to 180 days
- Uncheck all languages to search all
- Make sure at least one tag is checked

**App runs but freezes**
- Wait a bit - searching GitHub takes time
- Check internet connection
- Add GitHub token to avoid rate limits

## Next Steps

- Add a GitHub token for unlimited searches
- Try different tag combinations
- Explore custom search terms
- Bookmark repositories you want to contribute to

Enjoy finding your first open source contribution! 🚀
