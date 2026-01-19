# GitHub Beginner Issue Finder

### Made with some help from Claude Sonnet

A modern, user-friendly desktop application to help you find beginner-friendly GitHub issues to contribute to.

## Features

### Multi-Language Selection
- Select multiple programming languages from a list of 20 popular languages
- Add custom languages not in the pre-defined list
- Leave all unchecked to search across all languages

### Tag Selection
- Pre-made tags: `good first issue`, `good-first-issue`, `beginner`
- **Radio button selection** - choose exactly ONE tag
- Custom tag option available - enter your own tag name
- Default: "good first issue" (most common and reliable)

### Custom Search Terms
- Add your own search terms to narrow down results
- Examples: "documentation", "bug", "feature", "enhancement"
- Optional field - leave blank to search by language and tags only

### Advanced Features
- Filter by last update time (default: 90 days)
- Pagination through results (25 per page)
- View repository details and open issues
- Clickable links to repositories and sample issues
- GitHub token support for higher API rate limits

### Note
Repository descriptions and fork status are not displayed because the GitHub issue search API doesn't include this information. The focus is on finding repositories with matching open issues quickly.

## Installation

### Requirements
- Python 3.8 or higher
- Required packages: `requests`

### Setup
```bash
# Install dependencies
pip install requests

# Or if using a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
pip install requests
```

## Running the Application

### Windows (No Console Window)
Double-click one of these files:
- `search.pyw` - Direct Python launcher
- `run.bat` - Batch file launcher

Or run from command line:
```bash
pythonw search.py
```

### With Console (All Platforms)
```bash
python search.py
```

## Usage

1. **Select Languages** (optional)
   - Check the boxes for languages you're interested in
   - Or enter a custom language in the text field
   - Leave all unchecked to search all languages

2. **Select ONE Tag** (required)
   - Choose a pre-made tag: "good first issue", "good-first-issue", or "beginner"
   - OR select "Custom" and enter your own tag
   - Only one tag can be selected at a time

3. **Enter Custom Search Terms** (optional)
   - Add keywords to narrow your search
   - Examples: "documentation", "beginner-friendly", "help wanted"

4. **Set Update Time** (optional)
   - Default is 90 days
   - Adjust to see more recent or older issues

5. **Add GitHub Token** (optional)
   - For higher API rate limits
   - Can be set via environment variable `GITHUB_TOKEN`

6. **Click Search**
   - Wait for results to load
   - Browse through paginated results
   - Click on repository names or issue links to open in browser

## GitHub Token (Optional)

To avoid rate limiting, you can provide a GitHub personal access token:

### Method 1: Environment Variable
```bash
# Windows
set GITHUB_TOKEN=your_token_here

# Linux/Mac
export GITHUB_TOKEN=your_token_here
```

### Method 2: In Application
Paste your token into the "GitHub Token" field in the app.

### Creating a Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. No special permissions needed (can be read-only)

## Configuration

The app saves your selected tags to `label_config.json`. This file is created automatically.

## Tips

- Start with broader searches (fewer filters) to see more results
- Use custom search terms to find specific types of issues
- Sort by number of open issues to find active projects
- Click "View an issue" to see examples before committing

## Troubleshooting

### No Results Found
- Try fewer language filters
- Increase the "Updated Within" days
- Remove custom search terms
- Check your internet connection

### Rate Limit Errors
- Add a GitHub token
- Wait a few minutes and try again
- GitHub has a rate limit of 60 requests/hour without a token

### App Won't Start
- Ensure Python 3.8+ is installed
- Verify `requests` is installed: `pip install requests`
- On Windows, make sure `pythonw.exe` is in your PATH

## License

This project is licensed under the [MIT License](LICENSE).


