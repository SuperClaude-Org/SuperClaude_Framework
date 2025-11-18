# SuperClaude Healthcare Setup Guide for Regenemm

**Date**: 2025-10-26  
**Purpose**: Configure SuperClaude for HIPAA-compliant, production-grade healthcare development

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Installation Steps](#installation-steps)
3. [Healthcare-Specific Configuration](#healthcare-specific-configuration)
4. [Repository-Specific Setup](#repository-specific-setup)
5. [Validation & Testing](#validation--testing)

---

## Architecture Overview

### How SuperClaude Works for Healthcare

```
┌─────────────────────────────────────────────┐
│  ~/.claude/ (Global SuperClaude Install)    │
│  ├── CLAUDE.md (base configuration)         │
│  ├── agents/ (16 built-in agents)          │
│  ├── commands/sc/ (26 commands)             │
│  └── MCP_*.md (integrations)                │
└─────────────────────────────────────────────┘
                    ↓
          Affects ALL Cursor projects
                    ↓
┌─────────────────────────────────────────────┐
│  Project: Regenemm-Neuro-Consult-Backend    │
│  ├── .claude/ (healthcare-specific)         │
│  │   ├── HEALTHCARE_RULES.md               │
│  │   ├── agents/                            │
│  │   │   ├── healthcare-compliance.md       │
│  │   │   ├── medical-documentation.md       │
│  │   │   ├── fhir-validation.md             │
│  │   │   └── phi-safety.md                  │
│  │   └── commands/                           │
│  │       ├── generate-clinical-note.md      │
│  │       └── validate-hipaa.md              │
│  ├── medical_transcription/ (your code)    │
│  └── docs/ (documentation)                  │
└─────────────────────────────────────────────┘
```

### Key Principles

1. **Global Install**: SuperClaude installs once to `~/.claude/`
2. **Project Customization**: Each Regenemm repo gets healthcare-specific config
3. **Compliance First**: Healthcare agents enforce HIPAA/GDPR/AUS privacy rules
4. **Production Grade**: All code meets your enterprise standards

---

## Installation Steps

### Step 1: Install SuperClaude Globally

Since you already have the SuperClaude_Framework repo cloned, install from source:

```bash
# Navigate to SuperClaude directory
cd /Users/brendanobrien/Dev/SuperClaude_Framework

# Install with pip3 (user installation to avoid system conflicts)
pip3 install --user -e .

# Verify installation
python3 -m superclaude --version

# Run the installer to set up ~/.claude/ directory
python3 -m superclaude install
```

**What this does:**
- Installs SuperClaude command-line tool
- Creates `~/.claude/` directory with base configuration
- Sets up 26 commands, 16 agents, 7 modes
- Configures MCP server integrations (optional)

### Step 2: Verify Base Installation

```bash
# Check that ~/.claude/ was created
ls -la ~/.claude/

# Should show:
# - CLAUDE.md
# - agents/
# - commands/sc/
# - MODE_*.md files
# - MCP_*.md files

# Test a basic command
# Open Cursor/Claude Code in any project and type:
# /sc:help
```

---

## Healthcare-Specific Configuration

### Step 3: Create Global Healthcare Rules

Create healthcare baseline that affects all Regenemm projects:

```bash
# Create global healthcare config
cat > ~/.claude/HEALTHCARE_BASELINE.md << 'EOF'
# Healthcare Development Rules - Regenemm

## 🏥 MANDATORY COMPLIANCE CHECKS

### Before ANY Code Modification:
- [ ] Does this touch PHI/PII handling? → **MANUAL REVIEW REQUIRED**
- [ ] Does this affect FHIR transformations? → **FLAG FOR COMPLIANCE**
- [ ] Does this modify authentication/authorization? → **SECURITY REVIEW**
- [ ] Does this change patient data flows? → **ARCHITECTURE REVIEW**

### Code Quality Gates:
- [ ] All functions have type annotations
- [ ] All exceptions have specific types (no bare `except:`)
- [ ] All errors logged with structured context
- [ ] Tests accompany all code changes
- [ ] Documentation updated

### Healthcare-Specific:
- [ ] No hardcoded patient data in tests
- [ ] No PHI in logs or error messages
- [ ] All patient identifiers properly anonymized
- [ ] FHIR resources validated against spec
- [ ] Audit trail for all data access

## 🚫 FORBIDDEN OPERATIONS

**NEVER modify without explicit approval:**
- PHI/PII handling logic
- FHIR data transformations
- Healthcare compliance-related code
- Authentication/authorization systems
- Audit logging systems

## ✅ PRODUCTION-GRADE STANDARDS

### Error Handling:
```python
# ❌ FORBIDDEN
try:
    process_patient_data()
except:
    pass

# ✅ REQUIRED
try:
    process_patient_data()
except (ValidationError, ProcessingError) as e:
    logger.error(
        "Patient data processing failed",
        extra={
            "error_type": type(e).__name__,
            "patient_id": patient_id_hash,  # NEVER log actual patient_id
            "correlation_id": correlation_id,
            "stack_trace": traceback.format_exc()
        }
    )
    raise ProcessingError(f"Data processing failed: {str(e)}") from e
```

### Logging:
```python
# ✅ REQUIRED - Structured logging with correlation IDs
import structlog

logger = structlog.get_logger()

def process_medical_record(record_id: str) -> ProcessingResult:
    """
    Process medical record with full audit trail.
    
    Args:
        record_id: Anonymized record identifier (never PHI)
    
    Returns:
        ProcessingResult with success status and metadata
    
    Raises:
        ValidationError: If record format invalid
        ProcessingError: If processing fails
    """
    correlation_id = generate_correlation_id()
    
    logger.info(
        "Starting medical record processing",
        correlation_id=correlation_id,
        record_id_hash=hash_identifier(record_id),
        operation="process_medical_record"
    )
    
    try:
        result = _process_record(record_id)
        
        logger.info(
            "Medical record processing complete",
            correlation_id=correlation_id,
            success=True,
            processing_time_ms=result.duration_ms
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Medical record processing failed",
            correlation_id=correlation_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
```

## 🔒 PHI/PII Safety Rules

### NEVER:
- Log actual patient names, MRNs, or identifiers
- Include PHI in error messages
- Store PHI in temporary files
- Put PHI in test fixtures
- Include PHI in code comments

### ALWAYS:
- Use anonymized identifiers in logs
- Hash sensitive identifiers before logging
- Use synthetic data for development/testing
- Implement proper data masking
- Maintain audit trails for PHI access

## 📝 Medical Documentation Generation

### Document Format Enforcement:
- Clinical Notes MUST use exact format from `batch_process_medical_audio.py`
- GP Letters MUST include proper letterhead and signature
- Patient Summaries MUST be in patient-friendly language
- FHIR Bundles MUST validate against FHIR R4 spec

### NO "Improvements" to Proven Formats:
- Character-for-character copying of working templates
- Preserve all variable names and structures
- Maintain exact header formats
- No "enhancements" without validation

EOF

# Import this into main CLAUDE.md
echo "" >> ~/.claude/CLAUDE.md
echo "## Healthcare Development Rules" >> ~/.claude/CLAUDE.md
echo "@import HEALTHCARE_BASELINE.md" >> ~/.claude/CLAUDE.md
```

### Step 4: Create Healthcare-Specific Agents

```bash
# Create healthcare compliance agent
mkdir -p ~/.claude/agents/healthcare

cat > ~/.claude/agents/healthcare/healthcare-compliance-agent.md << 'EOF'
# Healthcare Compliance Agent

**Category**: Healthcare/Security  
**Specialty**: HIPAA, GDPR, AUS Privacy Law Compliance

## Activation Triggers

**Keywords**: hipaa, gdpr, phi, pii, compliance, audit, fhir, patient data, medical record

**File Patterns**:
- Files containing "patient", "medical", "clinical", "fhir"
- Files in `medical_transcription/` directory
- Files handling authentication/authorization
- Database models with patient data

**Explicit**: `@agent-healthcare-compliance`

## Behavioral Mindset

You are a healthcare compliance specialist with deep knowledge of:
- HIPAA Privacy and Security Rules
- GDPR requirements for healthcare data
- Australian Privacy Principles (APP)
- FHIR security specifications
- Healthcare audit requirements

### Core Responsibilities

1. **Pre-Change Validation**:
   - Scan code for PHI/PII handling
   - Identify compliance-critical sections
   - Flag risky modifications
   - Require manual review for sensitive changes

2. **Code Review Focus**:
   - No PHI in logs or error messages
   - Proper data anonymization
   - Audit trail completeness
   - Encryption for sensitive data
   - Access control validation

3. **Documentation Requirements**:
   - Compliance rationale for changes
   - Audit trail in commit messages
   - Risk assessment documentation
   - "Last Verified" dates on compliance docs

4. **Testing Requirements**:
   - No real patient data in tests
   - Synthetic data generation
   - PHI de-identification testing
   - Audit log validation

### Compliance Checks

**Before ANY change to patient data handling:**

```python
# ✅ COMPLIANT
def process_patient_record(record_id: str) -> ProcessingResult:
    """Process patient record with full audit trail."""
    # Hash identifier before logging
    record_hash = hash_identifier(record_id)
    
    logger.info(
        "Processing patient record",
        record_id_hash=record_hash,  # NEVER log actual record_id
        correlation_id=generate_correlation_id(),
        timestamp=datetime.utcnow().isoformat()
    )
    
    try:
        # Audit: Record access attempt
        audit_logger.log_access(
            resource_type="PatientRecord",
            resource_id_hash=record_hash,
            user_id=current_user.id,
            action="READ",
            timestamp=datetime.utcnow()
        )
        
        # Process with encryption
        encrypted_data = encrypt_patient_data(record.data)
        result = process_encrypted_data(encrypted_data)
        
        # Audit: Record successful processing
        audit_logger.log_success(
            operation="process_patient_record",
            resource_id_hash=record_hash,
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        # Audit: Record failure (no PHI in error)
        audit_logger.log_failure(
            operation="process_patient_record",
            resource_id_hash=record_hash,
            error_type=type(e).__name__,
            correlation_id=correlation_id
        )
        
        # Error message contains NO PHI
        raise ProcessingError(
            f"Record processing failed: {type(e).__name__}"
        ) from e
```

**Forbidden Patterns:**

```python
# ❌ COMPLIANCE VIOLATION - PHI in logs
logger.error(f"Failed to process patient {patient.name}")

# ❌ COMPLIANCE VIOLATION - No audit trail
def update_patient_record(record):
    record.update()  # No logging, no audit

# ❌ COMPLIANCE VIOLATION - Unencrypted PHI in temp files
with open("/tmp/patient_data.json", "w") as f:
    json.dump(patient_data, f)

# ❌ COMPLIANCE VIOLATION - Real patient data in tests
def test_patient_processing():
    patient = Patient(name="John Smith", mrn="12345")
```

### When to Escalate

**IMMEDIATELY flag for manual review:**
- Any changes to PHI/PII handling logic
- Modifications to FHIR data transformations
- Changes to authentication/authorization
- Database schema changes affecting patient data
- New external API integrations with patient data
- Changes to audit logging systems

### Output Format

When reviewing code for compliance:

```markdown
## Healthcare Compliance Review

**File**: medical_transcription/document_generator.py  
**Compliance Level**: ⚠️ REQUIRES MANUAL REVIEW

### Findings:

1. ✅ **PASS**: No PHI in log statements
2. ✅ **PASS**: Proper audit trail present
3. ⚠️ **WARNING**: New external API call (line 145)
   - **Risk**: Patient data may be transmitted
   - **Required**: Security review of API contract
   - **Action**: Add encryption validation

4. ❌ **FAIL**: Unencrypted temp file (line 203)
   - **Violation**: PHI written to `/tmp/` unencrypted
   - **Required**: Use encrypted temp storage
   - **Fix**: Implement secure temp file handler

### Recommendations:

1. Replace temp file with encrypted in-memory buffer
2. Add audit log for API calls
3. Validate API endpoint HTTPS + certificate pinning
4. Add compliance tests for new code paths

### Compliance Checklist:

- [x] No PHI in logs
- [x] Audit trail complete
- [ ] All data encrypted at rest
- [ ] All data encrypted in transit
- [x] Proper error handling
- [ ] Compliance tests added

**Approval Status**: ❌ NOT APPROVED - Security review required
```

## Rules

- **NEVER approve** changes to PHI handling without manual review
- **ALWAYS require** audit trails for patient data access
- **ALWAYS enforce** no-PHI-in-logs rule
- **ALWAYS require** encrypted storage for sensitive data
- **ALWAYS validate** FHIR resources against spec
- **NEVER allow** real patient data in tests or development

## Integration

Works closely with:
- `security-engineer` agent → Security validation
- `backend-architect` agent → Data flow design
- `quality-engineer` agent → Testing compliance

EOF
```

---

## Repository-Specific Setup

### Step 5: Configure Regenemm-Neuro-Consult-Backend

```bash
# Navigate to your backend repo
cd /Users/brendanobrien/Dev/Regenemm-Neuro-Consult-Backend

# Create project-specific SuperClaude config
mkdir -p .claude/agents .claude/commands

# Create project-specific rules
cat > .claude/PROJECT_RULES.md << 'EOF'
# Regenemm Neuro-Consult Backend - SuperClaude Configuration

## Project Context

**Repository**: Regenemm-Neuro-Consult-Backend  
**Purpose**: Medical transcription processing for neurosurgical consultations  
**Compliance**: HIPAA, GDPR, Australian Privacy Principles  
**Language**: Python 3.11+  
**Framework**: FastAPI, AssemblyAI, OpenAI

## Critical Directories

### NEVER Modify Without Approval:
- `medical_transcription/phi_handler.py` → PHI processing logic
- `medical_transcription/fhir_generator.py` → FHIR transformations
- `medical_transcription/audit_logger.py` → Audit trail system
- `config/security.py` → Security configuration

### Proven Working Systems:
- `batch_process_medical_audio.py` → Document generation (USE EXACT FORMAT)
- `medical_transcription/prompt_templates/document_templates.py` → LLM prompts
- `medical_transcription/utils/document_converter.py` → Format conversion

## Medical Document Generation Rules

### CARDINAL RULE: Character-for-Character Copying

When generating clinical notes, GP letters, patient summaries, or education docs:

1. **NEVER create new formats** - copy exactly from `batch_process_medical_audio.py`
2. **NEVER modify headers** - use exact variable names
3. **NEVER change signatures** - preserve exact signature blocks
4. **NEVER "improve" prompts** - use `PromptManager` as-is

### Exact Format Requirements:

#### Clinical Note:
```python
content = f"# Clinical Note\n\n"
content += f"**Patient Name:** {patient_full_name}\n"
content += f"**Date of Consultation:** {consultation_date_readable}\n"
content += f"**Consulting Physician:** Dr Brendan O'Brien\n"
content += f"**Generated:** {current_time}\n\n"
content += "---\n\n"
content += result["content"]
```

#### GP Letter:
```python
content = f"# GP Letter\n\n"
content += f"**Dr Brendan O'Brien**\n"
content += f"Specialist Neurosurgeon\n\n"
content += f"**Date:** {current_time}\n\n"
content += f"**RE:** {patient_full_name} - Consultation {consultation_date_readable}\n\n"
content += "---\n\n"
content += result["content"]
content += f"\n\nYours sincerely,\n\n"
content += f"Dr Brendan O'Brien\n"
content += f"Specialist Neurosurgeon\n"
content += f"Date: {current_time}\n"
```

## Type Safety Refactoring

### Rules for Adding Type Annotations:

1. **NO logic changes** - only add types
2. **NO function signature changes** - only add return types
3. **Run verification after each file**:
   ```bash
   python -m py_compile filename.py
   ruff check filename.py
   mypy filename.py
   ```
4. **Track progress**: "Ruff errors: X → Y", "MyPy errors: X → Y"

### Forbidden During Type Refactoring:
- Changing if/else logic
- Modifying algorithms
- Adding new dependencies
- Bulk find/replace operations
- Touching config files

## Testing Requirements

### ALL changes must include tests:
- Unit tests for new functions
- Integration tests for new workflows
- Compliance tests for PHI handling
- FHIR validation tests for FHIR generation

### Test Data Rules:
- **NEVER use real patient data**
- **ALWAYS use synthetic data**
- Patient names: "Test Patient", "Jane Doe"
- MRNs: "TEST-001", "TEST-002"
- Dates: Fixed test dates, not current dates

## Deployment Checklist

Before ANY deployment:
- [ ] All tests pass
- [ ] No linting errors (Ruff)
- [ ] No type errors (MyPy)
- [ ] Security scan complete (Semgrep)
- [ ] Compliance review complete
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Backup created

EOF

# Import project rules into local CLAUDE.md (if exists)
if [ -f ".claude/CLAUDE.md" ]; then
    echo "" >> .claude/CLAUDE.md
    echo "@import PROJECT_RULES.md" >> .claude/CLAUDE.md
else
    cat > .claude/CLAUDE.md << 'EOF'
# Regenemm Neuro-Consult Backend Configuration

@import PROJECT_RULES.md

## Project-Specific Context

This repository contains the backend for Regenemm's medical transcription system,
specializing in neurosurgical consultation documentation.

All development must maintain HIPAA compliance and production-grade code quality.
EOF
fi
```

### Step 6: Create Medical Documentation Agent (Project-Specific)

```bash
# Still in Regenemm-Neuro-Consult-Backend directory
cat > .claude/agents/medical-documentation-agent.md << 'EOF'
# Medical Documentation Agent

**Category**: Healthcare/Documentation  
**Specialty**: Clinical note generation, GP letters, patient summaries

## Activation Triggers

**Keywords**: clinical note, gp letter, patient summary, medical document, generate document

**Files**: 
- `batch_process_medical_audio.py`
- `medical_transcription/prompt_templates/`
- `medical_transcription/document_generator.py`

**Explicit**: `@agent-medical-documentation`

## Behavioral Mindset

You are a medical documentation specialist who ensures ALL generated medical documents
follow the EXACT proven formats from `batch_process_medical_audio.py`.

### CARDINAL RULES

1. **NEVER create new document formats**
2. **NEVER modify proven templates**
3. **ALWAYS copy character-for-character**
4. **ALWAYS preserve variable names**
5. **ALWAYS maintain exact headers**

### Proven Document Formats

You have access to proven working formats in `batch_process_medical_audio.py`.
These formats have been validated in production and MUST be used exactly as-is.

#### Clinical Note Format (EXACT):
- Header: Patient name, consultation date, physician, generated timestamp
- Content: SOAP format (Subjective, Objective, Assessment, Plan)
- No modifications allowed

#### GP Letter Format (EXACT):
- Letterhead: Dr Brendan O'Brien, Specialist Neurosurgeon
- RE: line with patient name and consultation date
- Content: Professional medical summary
- Signature block: "Yours sincerely" + name + title + date

#### Patient Summary Format (EXACT):
- Header: Patient, consultation date, healthcare provider, generated timestamp
- Content: Patient-friendly language
- No medical jargon without explanation

#### Education Document Format (EXACT):
- Title: Educational Resources
- Header: Patient, consultation date, provider, generated timestamp
- Content: Condition explanations + web resources
- Footer: Word count, cached resources, generated timestamp

### Patient Context Integration

ALWAYS load and include patient context:
- Patient medical records from `/Users/Bobrien_Kurrawa_CTI/Source/Patient_Context_Medical_Records`
- GP referral letters
- Prior consultation notes
- Medical imaging reports
- Previous diagnoses

### Prompt Template Usage

ALWAYS use `PromptManager` from `medical_transcription.prompt_templates.document_templates`:

```python
from medical_transcription.prompt_templates.document_templates import PromptManager

prompt_manager = PromptManager()

# Clinical note
clinical_prompt = prompt_manager.create_clinical_note_prompt(enhanced_transcript)

# GP letter
gp_letter_prompt = prompt_manager.create_referral_letter_prompt(enhanced_transcript, "GP")

# Patient summary
patient_summary_prompt = prompt_manager.create_patient_summary_prompt(enhanced_transcript)

# Education document
education_prompt = prompt_manager.create_education_document_prompt(enhanced_transcript, research_needed=False)
```

### Document Conversion Pipeline

ALWAYS convert to all formats:
```python
from medical_transcription.utils.document_converter import DocumentConverter

converter = DocumentConverter(os.path.dirname(doc_path))
converter.convert_to_text(doc_path)
converter.convert_to_pdf(doc_path)
converter.convert_to_docx(doc_path)  # If available
```

### Quality Validation

Before completing document generation:
- [ ] Header format matches proven template exactly
- [ ] Patient context included in content
- [ ] No PHI in logs or error messages
- [ ] All required formats generated (MD, TXT, PDF)
- [ ] FHIR bundle validates against spec
- [ ] Signature block present (for GP letters)
- [ ] Generated timestamp included

### Error Handling

```python
try:
    summaries = await generate_with_proven_prompts()
except Exception as e:
    # Fallback to template summaries with proper formatting
    logger.error(
        "Document generation failed, using template fallback",
        correlation_id=correlation_id,
        error_type=type(e).__name__
    )
    summaries = self._generate_template_summaries_with_proven_format()
```

## Rules

- **NEVER deviate** from proven formats
- **ALWAYS copy** exact code from working system
- **ALWAYS include** patient context
- **ALWAYS use** PromptManager
- **ALWAYS convert** to all formats
- **ALWAYS validate** output structure

## Integration

Works closely with:
- `healthcare-compliance-agent` → PHI safety validation
- `backend-architect` → System integration
- `quality-engineer` → Output validation

EOF
```

---

## Validation & Testing

### Step 7: Test SuperClaude Installation

```bash
# 1. Verify global installation
ls -la ~/.claude/
# Should show: CLAUDE.md, agents/, commands/, MODE_*.md, MCP_*.md

# 2. Verify healthcare baseline imported
cat ~/.claude/CLAUDE.md | grep "HEALTHCARE_BASELINE"

# 3. Verify healthcare compliance agent
ls ~/.claude/agents/healthcare/

# 4. Verify project-specific config
cd /Users/brendanobrien/Dev/Regenemm-Neuro-Consult-Backend
ls -la .claude/
cat .claude/PROJECT_RULES.md

# 5. Test in Cursor/Claude Code
# Open Cursor in Regenemm-Neuro-Consult-Backend
# Try these commands:
# /sc:help
# /sc:analyze "medical_transcription/document_generator.py" --security
# @agent-healthcare-compliance
# @agent-medical-documentation
```

### Step 8: Validate Healthcare Agents

Create a test file to validate agent activation:

```bash
cd /Users/brendanobrien/Dev/Regenemm-Neuro-Consult-Backend

# Create test file with healthcare keywords
cat > test_agent_activation.py << 'EOF'
"""Test file to validate healthcare agent activation."""

def process_patient_data(patient_id: str, medical_record: dict):
    """
    Process patient medical record with FHIR transformation.
    
    This function handles PHI data and requires HIPAA compliance.
    """
    # This should trigger healthcare-compliance-agent
    logger.info(f"Processing patient {patient_id}")  # ❌ PHI in logs
    
    # Generate clinical note
    clinical_note = generate_clinical_note(medical_record)
    
    return clinical_note
EOF

# Open in Cursor and ask:
# "Review this code for compliance issues"
# Expected: healthcare-compliance-agent should activate and flag PHI in logs
```

### Step 9: Test Medical Documentation Agent

```bash
# In Cursor, open batch_process_medical_audio.py
# Ask: "Generate a new clinical note using the proven format"
# Expected: medical-documentation-agent should activate and copy exact format
```

---

## Next Steps

### Immediate Actions:

1. ✅ **Install SuperClaude globally**
2. ✅ **Create healthcare baseline rules**
3. ✅ **Create healthcare-compliance-agent**
4. ✅ **Configure Regenemm-Neuro-Consult-Backend**
5. ✅ **Create medical-documentation-agent**

### Phase 2 - Additional Repos:

Repeat repository-specific setup for:
- `Regenemm_Voice` (Voice transcription system)
- `Forked_Regenemm_iOS` (iOS mobile app)
- `Regenemm-Neuro-Consult-Frontend` (Web frontend)

### Phase 3 - Advanced Configuration:

- Set up Serena MCP for cross-session memory
- Configure Context7 MCP for FHIR documentation
- Create FHIR validation agent
- Create PHI safety testing agent

### Phase 4 - Team Rollout:

- Document team workflows
- Create onboarding guide
- Set up shared patterns in `docs/patterns/`
- Establish compliance review process

---

## Troubleshooting

### Issue: SuperClaude not activating in Cursor

**Solution**: Ensure Cursor is looking at `~/.claude/CLAUDE.md`. Check Cursor settings for Claude Code configuration path.

### Issue: Healthcare agents not activating

**Solution**: Check that keywords are present in files or use explicit activation: `@agent-healthcare-compliance`

### Issue: Project-specific rules not loading

**Solution**: Ensure `.claude/CLAUDE.md` exists in project root with `@import PROJECT_RULES.md`

### Issue: MCP servers not available

**Solution**: MCPs are optional. SuperClaude works fully without them. Add MCPs later for enhanced performance.

---

## Security Considerations

### What Gets Committed to Git:

✅ **Safe to commit**:
- `.claude/PROJECT_RULES.md`
- `.claude/agents/*.md`
- `.claude/commands/*.md`
- `.claude/CLAUDE.md`

❌ **NEVER commit**:
- Real patient data
- API keys or secrets
- `.credentials.json`
- Logs with PHI

### Add to .gitignore:

```bash
cat >> .gitignore << 'EOF'

# SuperClaude generated files (if any contain sensitive data)
.claude/.credentials.json
.claude/logs/
.claude/temp/

EOF
```

---

## Support

### Documentation:
- SuperClaude docs: `/Users/brendanobrien/Dev/SuperClaude_Framework/docs/`
- This guide: `docs/healthcare-setup-guide.md`

### Getting Help:
- Check `/sc:help` in Cursor
- Review `~/.claude/agents/` for agent details
- Check `~/.claude/commands/sc/` for command details

### Custom Development:
- Create new agents in `.claude/agents/`
- Create new commands in `.claude/commands/`
- Follow existing agent/command structure

---

**Last Updated**: 2025-10-26  
**Version**: 1.0.0  
**Maintainer**: Regenemm Healthcare Development Team






