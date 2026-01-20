# Migrating from venv to Pipenv

## What is Pipenv?

Pipenv is a modern Python dependency management tool that combines `pip` and `virtualenv`. It's the officially recommended packaging tool by Python.org.

## Why Use Pipenv?

✅ **Automatic virtual environment management** - No need to manually create/activate venvs
✅ **Better dependency resolution** - Prevents version conflicts
✅ **Pipfile and Pipfile.lock** - More reliable than requirements.txt
✅ **Security scanning** - Built-in vulnerability checking
✅ **Separate dev dependencies** - Keep development tools separate
✅ **Deterministic builds** - Pipfile.lock ensures same versions everywhere

## Migration Steps

### 1. Install Pipenv

```bash
# Install pipenv globally
pip install pipenv
```

### 2. Navigate to Your Django Project

```bash
cd "c:\Users\HP\Desktop\django hospital booking management app\Django_Course\django_tutorial"
```

### 3. Create Pipfile from Existing requirements.txt

```bash
# This reads requirements.txt and creates Pipfile + Pipfile.lock
pipenv install -r requirements.txt
```

This will:
- Create a new virtual environment
- Install all packages from requirements.txt
- Create Pipfile and Pipfile.lock

### 4. Activate Pipenv Shell

```bash
# Activate the pipenv virtual environment
pipenv shell
```

You'll see your prompt change, indicating you're in the pipenv environment.

### 5. Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pipenv graph

# Run Django
python manage.py runserver
```

## Common Pipenv Commands

### Environment Management

```bash
# Activate virtual environment
pipenv shell

# Deactivate (exit shell)
exit

# Run command without activating shell
pipenv run python manage.py runserver

# Show virtual environment location
pipenv --venv

# Remove virtual environment
pipenv --rm
```

### Package Management

```bash
# Install a package (adds to Pipfile)
pipenv install django

# Install a specific version
pipenv install django==4.2.0

# Install dev-only package
pipenv install --dev pytest

# Uninstall a package
pipenv uninstall package-name

# Update all packages
pipenv update

# Update a specific package
pipenv update django
```

### Dependency Information

```bash
# List all installed packages
pipenv graph

# Check for security vulnerabilities
pipenv check

# Show outdated packages
pipenv update --outdated

# Show dependency graph
pipenv graph --reverse
```

### Working with requirements.txt

```bash
# Generate requirements.txt from Pipfile.lock
pipenv requirements > requirements.txt

# Generate dev requirements
pipenv requirements --dev > requirements-dev.txt
```

## File Structure Changes

### Before (venv):
```
django_tutorial/
├── djvenv/              # Virtual environment folder
├── requirements.txt     # Dependencies
└── ...
```

### After (pipenv):
```
django_tutorial/
├── Pipfile             # Main dependency file
├── Pipfile.lock        # Locked versions
├── requirements.txt    # Can keep for compatibility
└── ...
```

Note: The virtual environment is stored in a global location (not in your project folder).

## Pipfile Example

```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = "==6.0.1"
pillow = "*"
django-crispy-forms = "*"
crispy-bootstrap4 = "*"

[dev-packages]
pytest = "*"
black = "*"

[requires]
python_version = "3.12"
```

## Important Differences

### venv vs Pipenv

| Task | venv + pip | Pipenv |
|------|-----------|--------|
| Create environment | `python -m venv venv` | Automatic |
| Activate | `venv\Scripts\activate` | `pipenv shell` |
| Install package | `pip install django` | `pipenv install django` |
| Save dependencies | `pip freeze > requirements.txt` | Automatic (Pipfile) |
| Install from file | `pip install -r requirements.txt` | `pipenv install` |
| Deactivate | `deactivate` | `exit` |

## Best Practices

### 1. Commit Pipfile and Pipfile.lock
```bash
git add Pipfile Pipfile.lock
git commit -m "Migrated to pipenv"
```

### 2. Update .gitignore
Make sure these are in your `.gitignore`:
```
# Virtual environments
venv/
env/
djvenv/
.venv/
```

Note: With pipenv, the virtual environment is NOT in your project folder, so you don't need to ignore it.

### 3. Keep requirements.txt (Optional)
For compatibility with systems that don't use pipenv:
```bash
pipenv requirements > requirements.txt
```

### 4. Use Separate Dev Dependencies
```bash
# Production packages
pipenv install django pillow

# Development packages only
pipenv install --dev pytest black flake8
```

## Deployment

### Development
```bash
# Install all dependencies (including dev)
pipenv install --dev
```

### Production
```bash
# Install only production dependencies
pipenv install --ignore-pipfile
```

This uses Pipfile.lock for deterministic builds.

## Troubleshooting

### Issue: "pipenv: command not found"
**Solution**: Reinstall pipenv
```bash
pip install --user pipenv
```
Then add Python Scripts to PATH.

### Issue: Virtual environment in wrong location
**Solution**: Set environment variable
```bash
# Store venv in project folder
set PIPENV_VENV_IN_PROJECT=1
pipenv install
```

### Issue: SSL certificate errors
**Solution**: Disable SSL verification (not recommended for production)
```bash
pipenv install --trusted-host pypi.org
```

## Migration Checklist

- [ ] Install pipenv: `pip install pipenv`
- [ ] Create Pipfile: `pipenv install -r requirements.txt`
- [ ] Test activation: `pipenv shell`
- [ ] Test Django: `python manage.py runserver`
- [ ] Verify all packages: `pipenv graph`
- [ ] Check for vulnerabilities: `pipenv check`
- [ ] Update .gitignore if needed
- [ ] Commit Pipfile and Pipfile.lock
- [ ] (Optional) Keep requirements.txt for compatibility
- [ ] Document for team members

## Team Usage

When a team member clones the project:

```bash
# Clone repository
git clone <repo-url>
cd django_tutorial

# Install dependencies from Pipfile.lock
pipenv install

# Activate shell
pipenv shell

# Run project
python manage.py runserver
```

## Quick Reference

```bash
# Setup (one time)
pip install pipenv
cd django_tutorial
pipenv install -r requirements.txt

# Daily usage
pipenv shell               # Start working
python manage.py runserver # Run Django
exit                      # Stop working

# Add new package
pipenv install package-name

# Update Pipfile.lock
pipenv lock

# Security check
pipenv check
```

## Summary

Pipenv simplifies Python dependency management by:
- Automatically managing virtual environments
- Preventing dependency conflicts
- Ensuring reproducible builds
- Providing security scanning
- Separating dev and production dependencies

**Migration is simple**: Just run `pipenv install -r requirements.txt` and you're done! ✅

## Additional Resources

- Official Docs: https://pipenv.pypa.io/
- GitHub: https://github.com/pypa/pipenv
- Tutorial: https://realpython.com/pipenv-guide/
