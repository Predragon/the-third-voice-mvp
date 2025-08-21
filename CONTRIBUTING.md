# Contributing to The Third Voice

Thank you for considering contributing! 🎉  
We welcome improvements, bug fixes, new features, and documentation updates.

---

## 🚀 How to Contribute

### 1. Fork the Repository
Click **Fork** on GitHub to create your own copy of the repository.

### 2. Clone Your Fork
Clone the fork to your local machine:

```bash
git clone https://github.com/your-username/the-third-voice.git
cd the-third-voice
```

### 3. Create a Branch

Create a branch from dev (never from main):

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

Branch naming convention:

| Type | Prefix | Example |
|------|--------|---------|
| Features | `feature/` | `feature/login-ui` |
| Bugfix | `fix/` | `fix/api-timeout` |
| Docs | `docs/` | `docs/update-readme` |
| Chores | `chore/` | `chore/deps-update` |

### 4. Make Your Changes

- Follow project coding style
- Write or update tests if needed
- Keep changes focused and small

### 5. Commit Your Changes

Use Conventional Commits for clear commit messages:

```bash
git add .
git commit -m "feat: add login button component"
git commit -m "fix: resolve mobile navigation issue"
git commit -m "docs: update API documentation"
```

### 6. Push Your Branch

Push your branch to your fork:

```bash
git push origin feature/your-feature-name
```

### 7. Open a Pull Request (PR)

1. Go to your fork on GitHub
2. Click **Compare & pull request**
3. Base branch: `dev`
4. Describe your changes clearly
5. Reference issues, e.g., `Closes #42`

### 8. Code Review

- Maintainers will review your PR
- Be open to feedback and requested changes
- Once approved, PR will be merged into `dev`
- The `dev` branch will later be merged into `main` for releases

---

## ✅ Contribution Guidelines

- Write meaningful commit messages
- Keep PRs small, focused, and single-purpose
- Update or add tests for new functionality
- Be respectful and constructive in discussions

💡 **Tip**: If you're unsure about something, open a Draft PR early to get feedback!

---

Thank you for helping improve The Third Voice! 🙌
