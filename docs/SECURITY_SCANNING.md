# Dependency Security Scanning

This project uses `pip-audit` for automated dependency security scanning.

## Running Security Scans Locally

### Install pip-audit

```bash
pip install pip-audit
```

Or install from requirements-dev.txt:

```bash
pip install -r requirements-dev.txt
```

### Run Security Scan

Scan production dependencies:

```bash
pip-audit --requirement requirements.txt
```

Scan all dependencies (production + dev):

```bash
pip-audit --requirement requirements.txt --requirement requirements-dev.txt
```

### Generate Reports

Generate JSON report:

```bash
pip-audit --requirement requirements.txt --format json --output security-report.json
```

Generate text report with descriptions:

```bash
pip-audit --requirement requirements.txt --desc
```

## CI/CD Integration

Security scanning runs automatically:
- On every push to main/develop branches
- On every pull request
- Weekly on Mondays (scheduled)

## Handling Vulnerabilities

When vulnerabilities are found:

1. Review the security report
2. Check if a patched version is available
3. Update the affected dependency in requirements.txt or requirements-dev.txt
4. Test the updated dependency
5. Commit and push the fix

## Resources

- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [PyPA Security Advisory Database](https://github.com/pypa/advisory-db)
