# Contributing to The Third Voice

First of all, thank you for considering contributing to this project! 🎉 We welcome contributions from everyone, whether you're fixing a typo, adding a feature, or improving documentation.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Git configured with your GitHub account
- Code editor of your choice

### Initial Setup
1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/the-third-voice.git
   cd the-third-voice
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Verify your setup**
   ```bash
   npm test          # Run tests
   npm run dev       # Start development server
   npm run lint      # Check code style
   ```

## 🔄 Development Workflow

### 1. Sync with upstream
Always start with the latest changes:
```bash
git checkout dev
git pull upstream dev  # Sync with main repo
git push origin dev    # Update your fork
```

### 2. Create a feature branch
```bash
git checkout -b feature/your-feature-name
# Examples: feature/user-authentication, fix/mobile-responsive, docs/api-reference
```

### 3. Make your changes
- Write clean, readable code
- Follow existing conventions and patterns
- Add comments for complex logic
- Update documentation if needed

### 4. Test thoroughly
```bash
npm test              # Run all tests
npm run test:watch    # Run tests in watch mode
npm run lint          # Check code style
npm run type-check    # TypeScript validation
```

### 5. Commit your changes
We use [Conventional Commits](https://conventionalcommits.org/):
```bash
git add .
git commit -m "feat: add user profile dashboard"
git commit -m "fix: resolve mobile navigation issue"
git commit -m "docs: update API documentation"
git commit -m "refactor: simplify authentication logic
