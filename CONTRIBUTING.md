# Contributing to The Third Voice

Thank you for considering contributing! 🎉  
We welcome improvements, bug fixes, new features, and documentation updates.

---

## 🏗️ Branch Strategy

**`main`** → Production-ready code (deployed on Vercel)

**`develop`** → Active development branch (all feature work and bug fixes go here)

👉 **Contributors must branch off `develop` and open PRs back into `develop`.**  
The `main` branch is updated only through tested merges from `develop`.

---

## 🚀 How to Contribute

### 1. Fork the Repository

Click **Fork** on GitHub to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/your-username/the-third-voice-mvp.git
cd the-third-voice-mvp
```

### 3. Create a Branch

Make sure you're up to date with the remote `develop` branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

**Branch naming convention:**

| Type    | Prefix      | Example                |
|---------|-------------|------------------------|
| Feature | `feature/`  | `feature/login-ui`     |
| Bugfix  | `fix/`      | `fix/api-timeout`      |
| Docs    | `docs/`     | `docs/update-readme`   |
| Chore   | `chore/`    | `chore/deps-update`    |

---

## 🛠️ Development Setup

### Local Frontend

Run locally with:

```bash
npm install
npm run dev
```

Configure `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://100.x.x.x:8000   # Pi backend via Tailscale
```

### Backend

- Runs on Raspberry Pi server (via Tailscale for development)
- Production frontend connects via Cloudflare to Pi backend

---

## ✅ Contribution Workflow

### 4. Make Your Changes

- Follow project coding style
- Write or update tests if needed
- Keep changes focused and small

### 5. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add login button component"
git commit -m "fix: resolve mobile navigation issue"
git commit -m "docs: update API documentation"
```

### 6. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 7. Open a Pull Request (PR)

- **Base branch:** `develop`
- Describe your changes clearly
- Reference related issues (e.g. `Closes #42`)

### 8. Code Review

- Maintainers will review your PR
- Be open to feedback and requested changes
- Once approved → merged into `develop`
- Later, `develop` will be merged into `main` for production release

---

## 🤝 Guidelines

- Write meaningful commit messages
- Keep PRs small, focused, and single-purpose
- Update or add tests for new functionality
- Be respectful and constructive in discussions

💡 **Tip:** If you're unsure about something, open a **Draft PR** early to get feedback!

---

## ✨ Thank you for helping improve The Third Voice! 🙌
