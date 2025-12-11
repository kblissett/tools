# HTML Tools: Technical Specification & Patterns

## Overview

An **HTML tool** is a self-contained, single-file web application combining HTML, JavaScript, and CSS that provides useful functionality without requiring a build step, server-side processing, or complex deployment.

---

## Core Requirements

### Single-File Architecture
- All HTML, CSS, and JavaScript must be contained in **one `.html` file**
- Inline `<style>` tags for CSS
- Inline `<script>` tags for JavaScript
- The file should be directly copyable and immediately functional

### No Build Steps
- **Do not use React** (JSX requires compilation)
- **Do not use TypeScript** (requires compilation)
- **Do not use npm/webpack/vite** or any bundler
- Use vanilla JavaScript or libraries that work directly in the browser

### Size Constraints
- Target **a few hundred lines of code**
- Small enough that an LLM can read and understand the entire file
- Small enough to rewrite from scratch quickly if needed

### Dependencies via CDN Only
- Load external libraries from CDNs (cdnjs, jsdelivr, unpkg)
- Include version numbers in CDN URLs for stability
- Minimize dependencies—only use well-known, trusted libraries
- Example: `<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>`

---

## Input/Output Patterns

### Copy & Paste as Primary I/O
- Design tools to accept pasted content as input
- Provide "Copy to clipboard" buttons for output
- Use the Clipboard API: `navigator.clipboard.writeText(text)`
- Handle rich clipboard data via paste events:

```javascript
document.addEventListener('paste', (event) => {
    const items = event.clipboardData.items;
    for (const item of items) {
        if (item.type.startsWith('image/')) {
            const blob = item.getAsFile();
            // Process image
        }
        if (item.type === 'text/html') {
            item.getAsString((html) => {
                // Process rich text
            });
        }
    }
});
```

### File Input Without Server Upload
- Use `<input type="file">` to let users select local files
- Read files entirely in JavaScript—no server needed:

```javascript
const input = document.querySelector('input[type="file"]');
input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target.result;
        // Process file content
    };
    reader.readAsText(file); // or readAsDataURL, readAsArrayBuffer
});
```

### Generate Downloadable Files
- Create files for download without a server:

```javascript
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
```

- Use libraries for complex formats (e.g., generating PNGs, PDFs, ICS calendar files)

---

## State Management

### URL-Based State (Preferred for Shareable State)
- Store state in URL hash or query parameters
- Enables bookmarking and sharing
- Example:

```javascript
// Save state to URL
function saveToUrl(state) {
    const encoded = btoa(JSON.stringify(state));
    window.location.hash = encoded;
}

// Load state from URL
function loadFromUrl() {
    if (window.location.hash) {
        return JSON.parse(atob(window.location.hash.slice(1)));
    }
    return null;
}
```

### localStorage (For Secrets & Large State)
- Use for API keys, user preferences, or data too large for URLs
- **Never expose API keys in source code**—prompt users to enter their own keys
- Example:

```javascript
// Store API key
localStorage.setItem('openai_api_key', key);

// Retrieve API key
const apiKey = localStorage.getItem('openai_api_key');

// Prompt user if not set
if (!apiKey) {
    const key = prompt('Enter your OpenAI API key:');
    if (key) localStorage.setItem('openai_api_key', key);
}
```

---

## Working with External APIs

### CORS-Enabled APIs
These APIs allow direct browser access without a proxy server:

| API | Use Case |
|-----|----------|
| **PyPI** (`pypi.org/pypi/{package}/json`) | Python package metadata |
| **GitHub Raw** (`raw.githubusercontent.com`) | Fetch public repo files |
| **GitHub API** (`api.github.com`) | Issues, repos, gists |
| **iNaturalist** | Species observations, photos |
| **Bluesky** (`public.api.bsky.app`) | Social media data |
| **Mastodon** (most instances) | Social media data |

### LLM APIs with CORS Support
OpenAI, Anthropic, and Google Gemini APIs support CORS for direct browser calls:

```javascript
async function callClaude(prompt, apiKey) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
        },
        body: JSON.stringify({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 1024,
            messages: [{ role: 'user', content: prompt }]
        })
    });
    return response.json();
}
```

**Important:** Always store API keys in localStorage, never in source code.

---

## Advanced Capabilities

### Pyodide (Python in Browser)
Run Python code directly in the browser via WebAssembly:

```html
<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
<script>
async function runPython() {
    const pyodide = await loadPyodide();
    // Install packages
    await pyodide.loadPackage(['numpy', 'pandas']);
    // Run Python code
    const result = pyodide.runPython(`
        import pandas as pd
        df = pd.DataFrame({'a': [1, 2, 3]})
        df.sum().to_dict()
    `);
    console.log(result.toJs());
}
</script>
```

### WebAssembly Libraries
Many powerful tools are available as WebAssembly ports:
- **Tesseract.js** - OCR
- **FFmpeg.wasm** - Video/audio processing
- **PDF.js** - PDF rendering
- **sql.js** - SQLite in browser

---

## UI/UX Guidelines

### Minimal, Functional Design
- Focus on functionality over aesthetics
- Clear labels and intuitive layout
- Show results immediately when possible

### Mobile Considerations
- Copy/paste is harder on mobile—provide explicit "Copy" buttons
- Ensure touch targets are large enough
- Test paste functionality on mobile devices

### Error Handling
- Display clear error messages to users
- Validate input before processing
- Handle API failures gracefully

---

## Example Tool Types

### Data Transformation Tools
- JSON ↔ YAML converter
- CSV ↔ JSON converter
- Markdown → HTML renderer
- Base64 encoder/decoder

### API Exploration Tools
- Package version diff viewer (PyPI, npm)
- GitHub issue → Markdown exporter
- Social media thread viewer (Bluesky, HN)

### Media Processing Tools
- Image cropper for social media dimensions
- SVG → PNG/JPEG renderer
- OCR from images/PDFs
- EXIF data viewer

### Development Utilities
- Code formatter/linter viewer
- Regex tester
- Color picker/converter
- JWT decoder

### Debugging/Exploration Tools
- Clipboard format inspector
- Keyboard event viewer
- CORS availability checker
- HTTP header inspector

### LLM-Powered Tools
- Image description generator (using vision APIs)
- Text summarizer
- Code explainer

---

## Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Name</title>
    <style>
        /* Minimal, functional CSS */
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            line-height: 1.6;
        }
        textarea { width: 100%; min-height: 150px; font-family: monospace; }
        button { padding: 8px 16px; cursor: pointer; margin: 5px 0; }
        .output { background: #f5f5f5; padding: 15px; margin-top: 10px; border-radius: 4px; }
        .error { color: #c00; }
    </style>
</head>
<body>
    <h1>Tool Name</h1>
    <p>Brief description of what this tool does.</p>
    
    <!-- Input Section -->
    <div>
        <label for="input">Input:</label>
        <textarea id="input" placeholder="Paste content here..."></textarea>
    </div>
    
    <!-- Action Buttons -->
    <div>
        <button id="process">Process</button>
        <button id="copy">Copy Result</button>
        <button id="clear">Clear</button>
    </div>
    
    <!-- Output Section -->
    <div id="output" class="output"></div>

    <!-- Load dependencies from CDN if needed -->
    <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/..."></script> -->
    
    <script>
        const inputEl = document.getElementById('input');
        const outputEl = document.getElementById('output');
        
        document.getElementById('process').addEventListener('click', () => {
            try {
                const input = inputEl.value;
                // Process input
                const result = processInput(input);
                outputEl.textContent = result;
                outputEl.classList.remove('error');
            } catch (e) {
                outputEl.textContent = 'Error: ' + e.message;
                outputEl.classList.add('error');
            }
        });
        
        document.getElementById('copy').addEventListener('click', async () => {
            await navigator.clipboard.writeText(outputEl.textContent);
            // Optional: show feedback
        });
        
        document.getElementById('clear').addEventListener('click', () => {
            inputEl.value = '';
            outputEl.textContent = '';
        });
        
        function processInput(input) {
            // Tool-specific logic here
            return input;
        }
    </script>
</body>
</html>
```

---

## Checklist Before Completion

- [ ] Single `.html` file with all code inline
- [ ] No React, TypeScript, or build steps
- [ ] Dependencies loaded from CDNs with version numbers
- [ ] Works when opened directly in a browser (`file://` protocol) or served statically
- [ ] Copy/paste functionality for input and output
- [ ] Clear error messages for invalid input
- [ ] Mobile-friendly (if applicable)
- [ ] State persisted in URL (if shareable) or localStorage (if private/large)
- [ ] API keys stored in localStorage, never in source code
- [ ] Under 500 lines of code (ideally under 300)