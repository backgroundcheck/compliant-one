# Contributing to Compliant.One RegTech Platform

Thank you for your interest in contributing to Compliant.One! We welcome contributions from the community and are excited to see what you can bring to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- MongoDB (for local development)
- Basic understanding of RegTech/FinTech domain

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/compliant-one-regtech.git
   cd compliant-one-regtech
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## 📋 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. **Check the roadmap** to see if it's already planned
2. **Open a feature request issue**
3. **Describe the use case** and why it would be valuable
4. **Provide mockups or examples** if applicable

### Code Contributions

#### Types of Contributions Welcome

- 🐛 **Bug fixes**
- ✨ **New features** (compliance services, AI models, integrations)
- 📚 **Documentation improvements**
- 🔧 **Performance optimizations**
- 🧪 **Test coverage improvements**
- 🌐 **Internationalization**

#### Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following our coding standards

3. **Write or update tests** for your changes

4. **Run the test suite**:
   ```bash
   python -m pytest
   ```

5. **Check code quality**:
   ```bash
   flake8 .
   black .
   mypy .
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Create a Pull Request** on GitHub

## 🎯 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **Black** for code formatting
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes

### Code Organization

- **Services**: Business logic in `services/` directory
- **Models**: Data structures in appropriate service modules
- **Tests**: Mirror the source structure in `tests/`
- **Documentation**: Keep `docs/` updated

### Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(scraping): add transparency monitoring module
fix(auth): resolve login redirect issue
docs(api): update endpoint documentation
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=services

# Run specific test file
python -m pytest tests/test_sanctions.py

# Run tests matching pattern
python -m pytest -k "test_kyc"
```

### Writing Tests

- Write tests for all new functionality
- Use **pytest** for test framework
- Follow **AAA pattern** (Arrange, Act, Assert)
- Mock external dependencies
- Test both success and failure scenarios

Example test structure:
```python
def test_sanctions_screening():
    # Arrange
    screener = SanctionsScreener()
    test_entity = {"name": "John Doe", "dob": "1980-01-01"}
    
    # Act
    result = screener.screen(test_entity)
    
    # Assert
    assert result.risk_level == "LOW"
    assert len(result.matches) == 0
```

## 📚 Documentation

### Documentation Standards

- Update documentation for any new features
- Include code examples where helpful
- Use clear, concise language
- Follow the existing documentation style

### Types of Documentation

- **API Documentation**: Document all public APIs
- **User Guides**: Step-by-step instructions
- **Developer Docs**: Technical implementation details
- **Examples**: Real-world usage scenarios

## 🔒 Security Considerations

### Security Guidelines

- **Never commit secrets** (API keys, passwords, etc.)
- **Validate all inputs** to prevent injection attacks
- **Use parameterized queries** for database operations
- **Follow OWASP guidelines** for web applications
- **Report security issues** privately via email

### Sensitive Data

- Use environment variables for configuration
- Encrypt sensitive data at rest
- Implement proper access controls
- Log security events for audit trails

## 📦 Dependencies

### Adding Dependencies

1. **Check if really needed** - avoid dependency bloat
2. **Verify license compatibility** - must be MIT compatible
3. **Add to appropriate requirements file**:
   - `requirements.txt` - production dependencies
   - `requirements-dev.txt` - development dependencies
4. **Update dependency documentation**

### Dependency Guidelines

- Prefer well-maintained packages
- Pin versions to ensure reproducibility
- Keep dependencies up to date
- Document any special installation requirements

## 🌍 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful** and professional
- **Be patient** with newcomers
- **Give constructive feedback**
- **Focus on the contribution**, not the contributor
- **Help others learn** and grow

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code discussions
- **Discussions**: General questions and ideas
- **Email**: Security issues and private matters

## 🎉 Recognition

Contributors will be:

- Listed in the project README
- Mentioned in release notes for significant contributions
- Invited to join the core team for outstanding contributions

## 📞 Getting Help

If you need help:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Ask questions** in GitHub Discussions
4. **Join our community** channels

## 🚀 Next Steps

Ready to contribute? Here are some good first issues:

- Documentation improvements
- Adding tests for existing code
- Fixing small bugs
- Implementing new compliance rules
- Adding new data sources

Thank you for contributing to Compliant.One! 🛡️✨
