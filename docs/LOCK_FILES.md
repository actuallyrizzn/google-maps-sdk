# Lock Files for Reproducible Builds

This project uses `pip-tools` to generate lock files for reproducible builds.

## What are Lock Files?

Lock files (`requirements.lock` and `requirements-dev.lock`) contain the exact versions of all dependencies, including transitive dependencies. This ensures that builds are reproducible across different environments and times.

## Generating Lock Files

### Install pip-tools

```bash
pip install pip-tools
```

Or install from requirements-dev.txt:

```bash
pip install -r requirements-dev.txt
```

### Generate Lock Files

Generate production lock file:

```bash
pip-compile requirements.txt --output-file requirements.lock
```

Generate development lock file:

```bash
pip-compile requirements-dev.txt --output-file requirements-dev.lock
```

### Update Lock Files

When you update requirements.txt or requirements-dev.txt:

1. Update the source file (requirements.txt or requirements-dev.txt)
2. Regenerate the lock file:
   ```bash
   pip-compile requirements.txt --output-file requirements.lock
   ```
3. Commit both the source file and the lock file

## Using Lock Files

### Install from Lock Files

For production:

```bash
pip install -r requirements.lock
```

For development:

```bash
pip install -r requirements-dev.lock
```

### Benefits

- **Reproducible builds**: Same versions every time
- **Exact dependencies**: Includes all transitive dependencies
- **CI/CD consistency**: Same environment in CI as locally
- **Easier debugging**: Know exactly which versions are installed

## Updating Dependencies

1. Update version in requirements.txt or requirements-dev.txt
2. Run `pip-compile` to regenerate lock file
3. Test the updated dependencies
4. Commit both files

## CI/CD Integration

Lock files are automatically verified in CI to ensure they're up to date with source requirements files.

## Resources

- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
