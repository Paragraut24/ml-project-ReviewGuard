# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 4.2.x   | :white_check_mark: |
| < 4.2   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in ReviewGuard, please report it by:

1. **Email:** Create a GitHub issue with the title "SECURITY: [Brief Description]" and mark it as confidential
2. **Include:**
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability

## Security Measures

ReviewGuard implements the following security measures:

### Application Security

- **HTTPS Only** - All traffic is encrypted in transit
- **No Data Storage** - Reviews are analyzed in real-time and not persisted
- **Rate Limiting** - API endpoints are rate-limited to prevent abuse
- **Input Validation** - All user inputs are validated and sanitized
- **CORS Protection** - Cross-origin requests are restricted
- **Environment Variables** - Sensitive configuration stored securely

### Model Security

- **Private Models** - BERT model hosted on private HuggingFace repository
- **Token Authentication** - API access requires valid HuggingFace token
- **No Model Exposure** - Model weights are not downloadable via API
- **Inference Only** - No training or fine-tuning endpoints exposed

### Code Security

- **Dependency Scanning** - Regular security audits of dependencies
- **No Secrets in Code** - All secrets managed via environment variables
- **Minimal Permissions** - Application runs with least privilege
- **Error Handling** - Errors logged securely without exposing internals

## Security Best Practices for Deployment

If you're deploying your own instance (with explicit permission):

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong, random values for `SECRET_KEY`
   - Rotate secrets regularly
   - Use different secrets for dev/staging/production

2. **HTTPS Configuration**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates properly
   - Enable HSTS (HTTP Strict Transport Security)

3. **Access Control**
   - Implement IP whitelisting if needed
   - Use API keys for programmatic access
   - Monitor and log all API requests

4. **Monitoring**
   - Set up error tracking (e.g., Sentry)
   - Monitor for unusual traffic patterns
   - Set up alerts for security events

5. **Updates**
   - Keep dependencies up to date
   - Apply security patches promptly
   - Monitor security advisories

## Responsible Disclosure

We follow responsible disclosure practices:

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide an estimated timeline for a fix within 7 days
- We will notify you when the vulnerability is fixed
- We will credit you in our security acknowledgments (if desired)

## Security Acknowledgments

We thank the following researchers for responsibly disclosing security issues:

- None yet - be the first!

## Compliance

ReviewGuard is designed with the following compliance considerations:

- **GDPR** - No personal data is collected or stored
- **CCPA** - No user tracking or data selling
- **SOC 2** - Security best practices implemented
- **OWASP Top 10** - Common vulnerabilities mitigated

## Contact

For security-related questions or concerns:

- **GitHub Issues:** [Create a security issue](https://github.com/Paragraut24/ml-project-ReviewGuard/issues)
- **Repository:** https://github.com/Paragraut24/ml-project-ReviewGuard

---

**Last Updated:** 2026-01-01

