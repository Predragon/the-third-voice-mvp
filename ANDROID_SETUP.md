# Android Development Setup for The Third Voice AI

## Why Android Development?

The Third Voice AI was built entirely on an Android phone using Termux during 15 months in immigration detention. This setup proves that meaningful open source development is possible without expensive hardware - just an Android device and determination.

## Prerequisites

- **Android device** (Android 7.0+, any budget phone works)
- **Storage**: ~1GB free space
- **Network**: WiFi or mobile data
- **Time**: ~30 minutes for initial setup

## Installation

### Step 1: Install Termux

**Important**: Download from F-Droid, NOT Google Play Store (Play Store version is outdated and broken).

1. Install F-Droid: https://f-droid.org/
2. Open F-Droid → Search "Termux"
3. Install Termux and Termux:API (optional but recommended)

### Step 2: Setup Termux Environment

```bash
# Update package repositories
pkg update && pkg upgrade

# Install required packages
pkg install python nodejs-lts git nano

# Install Python package manager
pip install --upgrade pip

# Verify installations
python --version  # Should be 3.11+
node --version    # Should be 18+
npm --version     # Should be 9+
```

### Step 3: Clone Repository

```bash
# Clone the project
git clone https://github.com/Predragon/the-third-voice-mvp.git
cd the-third-voice-mvp

# Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 4: Setup Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

### Step 5: Setup Frontend

```bash
cd ../frontend

# Install Node dependencies (takes 2-3 minutes)
npm install

# Verify installation
npm list react
```

## Running the Development Environment

### Method 1: Two Terminal Sessions (Recommended)

**Terminal Session 1 - Backend:**
```bash
cd ~/the-third-voice-mvp/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Terminal Session 2 - Frontend:**

Swipe from left edge → "New session" to open second terminal:

```bash
cd ~/the-third-voice-mvp/frontend
npm run dev
```

You should see:
```
VITE ready in 2.5s
Local: http://localhost:3000/
```

**Access the Application:**

Open Chrome or Firefox on your phone and visit:
- **Frontend**: http://localhost:3000
- **Backend API docs**: http://localhost:8000/docs

### Method 2: Using Screen (Advanced)

Run both servers in background with `screen`:

```bash
# Install screen
pkg install screen

# Start backend in background
screen -dmS backend bash -c "cd ~/the-third-voice-mvp/backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Start frontend in background
screen -dmS frontend bash -c "cd ~/the-third-voice-mvp/frontend && npm run dev"

# List running screens
screen -ls

# Attach to a screen
screen -r backend  # or 'frontend'

# Detach from screen: Ctrl+A then D
```

## Development Workflow

### 1. Make Changes

Edit files using nano or vim:

```bash
# Edit backend
nano backend/src/api/routes/messages.py

# Edit frontend
nano frontend/src/App.jsx
```

**Nano basics:**
- `Ctrl+O` - Save
- `Ctrl+X` - Exit
- `Ctrl+W` - Search
- `Ctrl+K` - Cut line
- `Ctrl+U` - Paste

### 2. See Changes Live

Both servers support hot reload:
- **Backend**: Automatically reloads when you save Python files
- **Frontend**: Updates instantly in browser when you save

Just save the file and refresh your browser.

### 3. Test Your Changes

Visit http://localhost:3000 in your phone's browser:
- Test message transformation
- Test message interpretation
- Check the browser console for errors (Menu → More Tools → Developer Tools)

### 4. Commit Your Changes

```bash
# Check what changed
git status

# Add files
git add .

# Commit with descriptive message
git commit -m "Add feature: improve coparenting suggestions"

# Push to your fork
git push origin your-branch-name
```

## Common Tasks

### Stop Servers

```bash
# Kill all running servers
pkill -f uvicorn
pkill -f vite
```

### Restart Servers

```bash
# Restart backend
cd ~/the-third-voice-mvp/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Restart frontend (in new session)
cd ~/the-third-voice-mvp/frontend
npm run dev
```

### Update Dependencies

```bash
# Update Python packages
cd ~/the-third-voice-mvp/backend
pip install -r requirements.txt --upgrade

# Update Node packages
cd ~/the-third-voice-mvp/frontend
npm update
```

### Check Logs

```bash
# Backend logs appear in the terminal
# Frontend logs appear in browser console

# Monitor system resources
htop  # Install with: pkg install htop
```

### Run Tests

```bash
# Backend tests
cd ~/the-third-voice-mvp/backend
pytest

# Frontend tests
cd ~/the-third-voice-mvp/frontend
npm test
```

## Troubleshooting

### Port Already in Use

```bash
# Kill existing processes
pkill -f uvicorn
pkill -f vite

# Or find and kill specific process
lsof -i :8000  # Check what's using port 8000
kill -9 <PID>  # Kill that process
```

### Out of Memory

```bash
# Clear npm cache
npm cache clean --force

# Close other apps on your phone
# Restart Termux
```

### Permission Denied

```bash
# Fix storage permissions
termux-setup-storage

# Fix file permissions
chmod +x filename
```

### Module Not Found

```bash
# Reinstall Python dependencies
cd backend
pip install -r requirements.txt --force-reinstall

# Reinstall Node dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Hot Reload Not Working

```bash
# Try saving the file twice
# Or restart the dev server

# Backend
pkill -f uvicorn
python -m uvicorn main:app --reload

# Frontend
pkill -f vite
npm run dev
```

### Can't Access localhost:3000

- Ensure dev server is running (check terminal)
- Try http://127.0.0.1:3000 instead
- Check firewall/VPN settings
- Restart browser

## Tips for Mobile Development

### Battery Management
- Keep phone plugged in during development
- Use battery saver mode when not actively coding
- Close unused background apps

### Screen Management
- Use split screen if your phone supports it (Termux + Browser)
- Enable "Stay awake" in Developer Options
- Adjust screen timeout to prevent lock during compilation

### Keyboard Shortcuts
- Volume Up = Ctrl key in Termux
- Volume Down + Q = Show extra keys bar
- Use external Bluetooth keyboard for longer sessions

### Code Editing
- Use nano for quick edits
- Install code-server for VS Code in browser (advanced)
- Use GitHub web editor for complex changes

### Session Management
- Use screen or tmux to persist sessions
- Name your terminal windows for clarity
- Keep notes of running processes

## Performance Optimization

### For Low-End Devices
```bash
# Reduce Vite memory usage
export NODE_OPTIONS="--max-old-space-size=512"

# Run backend without reload (faster)
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### For Better Performance
- Close unused Termux sessions
- Clear browser cache regularly
- Use lighter browser (Firefox Focus, Kiwi Browser)
- Disable unnecessary system animations

## Next Steps

Once your development environment is working:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
2. Check [ROADMAP.md](ROADMAP.md) for features to work on
3. Join our community discussions
4. Pick an issue labeled "good first issue"

## Resources

- **Termux Wiki**: https://wiki.termux.com/
- **Termux Community**: https://www.reddit.com/r/termux/
- **The Third Voice Docs**: See `/docs` folder
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Vite Docs**: https://vitejs.dev/
- **React Docs**: https://react.dev/

## Getting Help

Having issues? 

1. Check this guide again
2. Search existing GitHub issues
3. Ask in GitHub Discussions
4. Open a new issue with:
   - Your Android version
   - Termux version
   - Error messages
   - What you tried

---

**Built with love on an Android phone during 15 months in detention.**

For Samantha. For all families trying to communicate better.
