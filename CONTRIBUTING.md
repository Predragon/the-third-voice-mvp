# Contributing to The Third Voice AI

Thank you for your interest in contributing to The Third Voice AI. This project was born from a personal need to improve communication between co-parents for the benefit of children, and every contribution helps more families communicate better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

### Our Mission

The Third Voice AI exists to help families communicate better, especially during difficult times. We expect all contributors to approach this work with empathy, respect, and a genuine desire to help people.

### Expected Behavior

- **Be respectful**: Treat everyone with dignity and kindness
- **Be empathetic**: Remember that behind every feature is a family trying to communicate
- **Be constructive**: Offer helpful feedback, not just criticism
- **Be inclusive**: Welcome contributors of all backgrounds and skill levels
- **Be patient**: Many contributors may be learning (just like the founder learned on Android)

### Unacceptable Behavior

- Harassment, discrimination, or hate speech of any kind
- Dismissive or condescending comments
- Personal attacks or trolling
- Publishing others' private information
- Any behavior that would discourage participation

## Getting Started

### Prerequisites

Choose your development environment:

**Option A: Android/Termux** (How this project was built)
- Follow [ANDROID_SETUP.md](ANDROID_SETUP.md)
- Perfect for mobile-only developers

**Option B: Traditional Setup** (Laptop/Desktop)
- Python 3.11+
- Node.js 18+
- Git

### First-Time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/the-third-voice-mvp.git
   cd the-third-voice-mvp
   ```
3. **Set up development environment** (see ANDROID_SETUP.md)
4. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Finding an Issue to Work On

- Look for issues labeled `good first issue`
- Check issues labeled `help wanted`
- Review [ROADMAP.md](ROADMAP.md) for planned features
- Propose your own improvement (open an issue first!)

## Development Setup

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

See [ANDROID_SETUP.md](ANDROID_SETUP.md) for detailed Android/Termux instructions.

## How to Contribute

### Types of Contributions

We welcome:

- **Bug fixes**: Squash those bugs
- **New features**: Enhance communication capabilities
- **AI improvements**: Better prompts, better responses
- **Documentation**: Help others understand the project
- **Tests**: Improve code coverage and reliability
- **UI/UX**: Make the interface more intuitive
- **Translations**: Help non-English speakers (future feature)
- **Mobile optimization**: Better Android/iOS experience

### Before You Start

1. **Check existing issues**: Someone might already be working on it
2. **Open an issue first**: Discuss major changes before coding
3. **Ask questions**: Better to ask than assume
4. **Start small**: Get comfortable with the codebase first

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/improve-coparenting-prompts
   ```

2. **Make your changes**:
   - Write clear, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "Improve coparenting context prompts for scheduling conflicts"
   ```

### Commit Message Guidelines

Use clear, descriptive commit messages:

**Good commits:**
- `Add deep analysis option for message interpretation`
- `Fix CORS issue with production API calls`
- `Improve healing score algorithm for transform mode`
- `Update Android setup documentation`

**Bad commits:**
- `fix bug`
- `update`
- `changes`
- `asdf`

**Format:**
```
<type>: <short summary>

<optional detailed description>

<optional issue reference>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat: Add emotion detection to message interpretation

Implements basic emotion detection using sentiment analysis
to better understand the emotional state behind messages.
This helps provide more empathetic response suggestions.

Closes #42
```

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated if needed
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### Submitting a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template**:
   - What does this PR do?
   - Why is this change needed?
   - How has it been tested?
   - Screenshots (if UI changes)
   - Related issues

4. **Respond to feedback**:
   - Address reviewer comments
   - Make requested changes
   - Be open to suggestions

### PR Review Process

- A maintainer will review your PR within 3-5 days
- You may be asked to make changes
- Once approved, a maintainer will merge your PR
- Your contribution will be credited in release notes

### After Your PR is Merged

- Delete your feature branch
- Pull the latest changes from main
- Celebrate! You've helped families communicate better

## Coding Standards

### Backend (Python/FastAPI)

**Style:**
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Use meaningful variable names

**Example:**
```python
async def transform_message(
    message: str,
    contact_context: str,
    analysis_depth: AnalysisDepth
) -> AIResponse:
    """
    Transform a message to be more constructive.
    
    Args:
        message: Original message text
        contact_context: Relationship context (coparenting, romantic, etc.)
        analysis_depth: Quick or deep analysis
        
    Returns:
        AIResponse with transformed message and metadata
    """
    # Implementation
```

**Structure:**
- Keep functions small and focused
- Use async/await properly
- Handle errors gracefully
- Log important events

### Frontend (React/TypeScript)

**Style:**
- Use functional components
- Use hooks properly
- TypeScript for type safety
- Clear prop interfaces

**Example:**
```typescript
interface MessageInputProps {
  onSubmit: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

function MessageInput({ onSubmit, placeholder, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('');
  
  const handleSubmit = () => {
    if (message.trim()) {
      onSubmit(message);
      setMessage('');
    }
  };
  
  return (
    // JSX
  );
}
```

**Structure:**
- Component files in `src/components/`
- One component per file
- Extract reusable logic to hooks
- Keep components focused

### General Principles

- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **Write for humans**: Code is read more than written

## Testing Guidelines

### Backend Tests

```bash
cd backend
pytest
```

**Write tests for:**
- API endpoints
- AI engine logic
- Database operations
- Authentication flows

**Example:**
```python
def test_transform_message():
    """Test message transformation produces valid output"""
    response = client.post("/api/messages/quick-transform", json={
        "message": "You're always late",
        "contact_context": "coparenting",
        "use_deep_analysis": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "transformed_message" in data
    assert len(data["transformed_message"]) > 0
```

### Frontend Tests

```bash
cd frontend
npm test
```

**Write tests for:**
- Component rendering
- User interactions
- API integration
- State management

### Test Coverage

- Aim for 70%+ coverage
- Focus on critical paths
- Test edge cases
- Test error handling

## Documentation

### When to Update Documentation

- Adding new features
- Changing API endpoints
- Modifying configuration
- Fixing unclear documentation

### Documentation Types

**Code Documentation:**
- Docstrings for functions
- Comments for complex logic
- Type hints/interfaces

**User Documentation:**
- README.md updates
- API endpoint documentation
- Setup guides

**Developer Documentation:**
- Architecture decisions
- Development workflows
- Troubleshooting guides

## Community

### Getting Help

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Pull Requests**: Get code review feedback

### Staying Connected

- Watch the repository for updates
- Star the project to show support
- Share the project with others who might benefit

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## Special Notes

### Android Development

This project was built entirely on Android using Termux. If you're developing on Android:

- You're not alone - the founder did the same
- See ANDROID_SETUP.md for complete guide
- Share your experience to help others
- Your perspective is valuable

### AI Ethics

When working on AI features:

- Never manipulate messages to change meaning
- Always be transparent about AI involvement
- Prioritize user privacy and data security
- Focus on helping, not replacing, human communication

### Co-Parenting Focus

Remember that most users are:

- In stressful situations
- Trying to do right by their children
- May be dealing with conflict or trauma
- Need reliable, empathetic tools

Design and code with this empathy.

## Questions?

- Open a GitHub Discussion
- Comment on related issues
- Reach out to maintainers

---

**Thank you for contributing to better family communication.**

Built with love for Samantha and all children whose parents are learning to communicate better.