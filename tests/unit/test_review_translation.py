"""
Unit tests for /sc:review-translation command logic

Tests the localization quality review system's core algorithms:
- Scoring calculations (6-KPI weighted system)
- Severity classification
- Grading criteria (PASS/CONDITIONAL/FAIL)
- File detection patterns
- Placeholder validation
"""

import pytest
import re
import json


# =============================================================================
# SCORING SYSTEM TESTS
# =============================================================================

class TestScoringKPIs:
    """Test suite for 6-KPI weighted scoring system"""

    # Weights from review-translation.md Phase 2
    WEIGHTS = {
        "accuracy": 0.25,
        "fluency": 0.20,
        "terminology": 0.20,
        "tone_alignment": 0.15,
        "cultural_adaptation": 0.10,
        "technical_compliance": 0.10,
    }

    def calculate_weighted_score(self, scores: dict) -> float:
        """Helper to calculate weighted score from KPI scores"""
        total = 0.0
        for kpi, weight in self.WEIGHTS.items():
            total += scores.get(kpi, 0) * weight
        return total

    def test_perfect_score(self):
        """Test that all 100s yields 100 overall"""
        scores = {
            "accuracy": 100,
            "fluency": 100,
            "terminology": 100,
            "tone_alignment": 100,
            "cultural_adaptation": 100,
            "technical_compliance": 100,
        }
        result = self.calculate_weighted_score(scores)
        assert result == 100.0, f"Expected 100, got {result}"

    def test_zero_score(self):
        """Test that all 0s yields 0 overall"""
        scores = {
            "accuracy": 0,
            "fluency": 0,
            "terminology": 0,
            "tone_alignment": 0,
            "cultural_adaptation": 0,
            "technical_compliance": 0,
        }
        result = self.calculate_weighted_score(scores)
        assert result == 0.0, f"Expected 0, got {result}"

    def test_weights_sum_to_one(self):
        """Verify KPI weights sum to 100%"""
        total_weight = sum(self.WEIGHTS.values())
        assert total_weight == 1.0, f"Weights should sum to 1.0, got {total_weight}"

    def test_accuracy_has_highest_weight(self):
        """Accuracy should be the highest weighted KPI at 25%"""
        max_weight = max(self.WEIGHTS.values())
        assert self.WEIGHTS["accuracy"] == max_weight
        assert self.WEIGHTS["accuracy"] == 0.25

    def test_mixed_scores(self):
        """Test realistic mixed scores"""
        scores = {
            "accuracy": 85,      # 85 * 0.25 = 21.25
            "fluency": 80,       # 80 * 0.20 = 16.00
            "terminology": 75,   # 75 * 0.20 = 15.00
            "tone_alignment": 70,  # 70 * 0.15 = 10.50
            "cultural_adaptation": 65,  # 65 * 0.10 = 6.50
            "technical_compliance": 95,  # 95 * 0.10 = 9.50
        }
        result = self.calculate_weighted_score(scores)
        expected = 21.25 + 16.00 + 15.00 + 10.50 + 6.50 + 9.50  # = 78.75
        assert result == expected, f"Expected {expected}, got {result}"


# =============================================================================
# GRADING CRITERIA TESTS
# =============================================================================

class TestGradingCriteria:
    """Test suite for three-tier grading system"""

    def grade_translation(self, score: float, critical: int, high: int) -> str:
        """
        Apply grading criteria from Phase 2:
        - ✅ PASS: Score ≥75 AND Critical = 0
        - ⚠️ CONDITIONAL PASS: Score ≥70 AND Critical = 0 AND High ≤ 3
        - ❌ FAIL: Score <70 OR Critical > 0
        """
        if critical > 0:
            return "FAIL"
        if score >= 75:
            return "PASS"
        if score >= 70 and high <= 3:
            return "CONDITIONAL"
        return "FAIL"

    def test_pass_high_score_no_issues(self):
        """Score 85, no critical or high issues → PASS"""
        result = self.grade_translation(score=85, critical=0, high=0)
        assert result == "PASS"

    def test_pass_exactly_75(self):
        """Score exactly 75, no critical → PASS"""
        result = self.grade_translation(score=75, critical=0, high=0)
        assert result == "PASS"

    def test_pass_with_high_issues(self):
        """Score 80 with high issues still passes (only critical blocks)"""
        result = self.grade_translation(score=80, critical=0, high=5)
        assert result == "PASS"

    def test_conditional_score_70_low_high(self):
        """Score 70, no critical, 2 high issues → CONDITIONAL"""
        result = self.grade_translation(score=70, critical=0, high=2)
        assert result == "CONDITIONAL"

    def test_conditional_exactly_3_high(self):
        """Score 72, no critical, exactly 3 high → CONDITIONAL"""
        result = self.grade_translation(score=72, critical=0, high=3)
        assert result == "CONDITIONAL"

    def test_fail_due_to_critical(self):
        """Any critical issue → FAIL regardless of score"""
        result = self.grade_translation(score=95, critical=1, high=0)
        assert result == "FAIL"

    def test_fail_due_to_low_score(self):
        """Score below 70 → FAIL"""
        result = self.grade_translation(score=65, critical=0, high=1)
        assert result == "FAIL"

    def test_fail_conditional_with_too_many_high(self):
        """Score 72 but 4 high issues → FAIL (exceeds high limit)"""
        result = self.grade_translation(score=72, critical=0, high=4)
        assert result == "FAIL"

    def test_fail_score_just_under_70(self):
        """Score 69.9 → FAIL"""
        result = self.grade_translation(score=69.9, critical=0, high=0)
        assert result == "FAIL"


# =============================================================================
# SEVERITY CLASSIFICATION TESTS
# =============================================================================

class TestSeverityClassification:
    """Test suite for issue severity classification"""

    SEVERITY_LEVELS = {
        "CRITICAL": ["meaning_reversal", "offensive_content", "broken_placeholder",
                     "legal_violation", "missing_critical_content"],
        "HIGH": ["notable_accuracy", "grammar_error_comprehension",
                 "inconsistent_terminology", "tone_misaligned", "formatting_display"],
        "MEDIUM": ["minor_fluency", "style_inconsistency", "non_optimal_word",
                   "minor_formatting"],
        "LOW": ["preference_improvement", "minor_polish", "alternative_phrasing",
                "regional_optimization"],
    }

    def classify_issue(self, issue_type: str) -> str:
        """Classify issue type to severity level"""
        for severity, types in self.SEVERITY_LEVELS.items():
            if issue_type in types:
                return severity
        return "UNKNOWN"

    def test_critical_meaning_reversal(self):
        """Meaning reversal is CRITICAL"""
        assert self.classify_issue("meaning_reversal") == "CRITICAL"

    def test_critical_broken_placeholder(self):
        """Broken placeholder is CRITICAL"""
        assert self.classify_issue("broken_placeholder") == "CRITICAL"

    def test_high_grammar_error(self):
        """Grammar error affecting comprehension is HIGH"""
        assert self.classify_issue("grammar_error_comprehension") == "HIGH"

    def test_medium_fluency_issue(self):
        """Minor fluency issue is MEDIUM"""
        assert self.classify_issue("minor_fluency") == "MEDIUM"

    def test_low_suggestion(self):
        """Alternative phrasing is LOW"""
        assert self.classify_issue("alternative_phrasing") == "LOW"


# =============================================================================
# PLACEHOLDER VALIDATION TESTS
# =============================================================================

class TestPlaceholderValidation:
    """Test suite for placeholder preservation validation"""

    # Patterns from Phase 0 automated validation
    PLACEHOLDER_PATTERNS = [
        r"\{.*?\}",           # {0}, {name}
        r"\[.*?\]",           # [button]
        r"%[sd]",             # %s, %d
        r"\$\w+\$",           # $VAR$
        r"<<.*?>>",           # <<special>>
    ]

    def extract_placeholders(self, text: str) -> list:
        """Extract all placeholders from text"""
        placeholders = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)
        return placeholders

    def validate_placeholder_preservation(self, source: str, translation: str) -> bool:
        """Check if all source placeholders are preserved in translation"""
        source_placeholders = sorted(self.extract_placeholders(source))
        translation_placeholders = sorted(self.extract_placeholders(translation))
        return source_placeholders == translation_placeholders

    def test_curly_brace_placeholder(self):
        """Detect {0}, {name} style placeholders"""
        placeholders = self.extract_placeholders("Hello {name}, you have {count} items")
        assert "{name}" in placeholders
        assert "{count}" in placeholders
        assert len(placeholders) == 2

    def test_percent_placeholder(self):
        """Detect %s, %d style placeholders"""
        placeholders = self.extract_placeholders("Player %s scored %d points")
        assert "%s" in placeholders
        assert "%d" in placeholders
        assert len(placeholders) == 2

    def test_dollar_placeholder(self):
        """Detect $VAR$ style placeholders"""
        placeholders = self.extract_placeholders("Welcome $USER$ to $GAME$")
        assert "$USER$" in placeholders
        assert "$GAME$" in placeholders

    def test_bracket_placeholder(self):
        """Detect [button] style placeholders"""
        placeholders = self.extract_placeholders("Press [A] to jump, [B] to crouch")
        assert "[A]" in placeholders
        assert "[B]" in placeholders

    def test_valid_placeholder_preservation(self):
        """Source and translation have same placeholders"""
        source = "Hello {name}, your score is {score}"
        translation = "Hallo {name}, dein Punktestand ist {score}"
        assert self.validate_placeholder_preservation(source, translation) is True

    def test_missing_placeholder_fails(self):
        """Missing placeholder should fail validation"""
        source = "Hello {name}, your score is {score}"
        translation = "Hallo {name}, dein Punktestand ist 100"  # Missing {score}
        assert self.validate_placeholder_preservation(source, translation) is False

    def test_modified_placeholder_fails(self):
        """Modified placeholder should fail validation"""
        source = "Hello {name}"
        translation = "Hallo {nombre}"  # Changed placeholder name
        assert self.validate_placeholder_preservation(source, translation) is False

    def test_reordered_placeholders_pass(self):
        """Reordered placeholders should still pass (same set)"""
        source = "From {start} to {end}"
        translation = "Von {end} bis {start}"  # Different order, same set
        assert self.validate_placeholder_preservation(source, translation) is True


# =============================================================================
# FILE DETECTION TESTS
# =============================================================================

class TestFileDetection:
    """Test suite for translation file detection patterns"""

    LANGUAGE_CODE_PATTERN = r"_([a-z]{2}(?:_[A-Z]{2})?)\.json$"

    def detect_language_code(self, filename: str) -> str | None:
        """Extract language code from filename"""
        match = re.search(self.LANGUAGE_CODE_PATTERN, filename)
        return match.group(1) if match else None

    def is_translation_file(self, filename: str) -> bool:
        """Check if file matches translation pattern"""
        return bool(re.search(self.LANGUAGE_CODE_PATTERN, filename))

    def test_simple_language_code(self):
        """Detect simple language codes like _de, _fr"""
        assert self.detect_language_code("strings_de.json") == "de"
        assert self.detect_language_code("strings_fr.json") == "fr"
        assert self.detect_language_code("strings_es.json") == "es"

    def test_regional_language_code(self):
        """Detect regional codes like _de_DE, _pt_BR"""
        assert self.detect_language_code("strings_de_DE.json") == "de_DE"
        assert self.detect_language_code("strings_pt_BR.json") == "pt_BR"
        assert self.detect_language_code("strings_zh_CN.json") == "zh_CN"

    def test_english_source_not_translation(self):
        """English files may not be detected as translations (depends on naming)"""
        # _en.json would match, but english.json would not
        assert self.detect_language_code("strings_en.json") == "en"
        assert self.detect_language_code("english.json") is None

    def test_non_translation_file(self):
        """Non-translation files should not match"""
        assert self.is_translation_file("config.json") is False
        assert self.is_translation_file("package.json") is False
        assert self.is_translation_file("strings.json") is False

    def test_translation_file_detection(self):
        """Translation files should match pattern"""
        assert self.is_translation_file("strings_de.json") is True
        assert self.is_translation_file("steam_page_fr_FR.json") is True
        assert self.is_translation_file("ui_text_ja.json") is True


# =============================================================================
# JSON STRUCTURE VALIDATION TESTS
# =============================================================================

class TestJSONValidation:
    """Test suite for JSON structure validation"""

    def validate_key_parity(self, source_keys: set, translation_keys: set) -> dict:
        """Check for missing or extra keys between source and translation"""
        missing = source_keys - translation_keys
        extra = translation_keys - source_keys
        return {
            "valid": len(missing) == 0 and len(extra) == 0,
            "missing_keys": list(missing),
            "extra_keys": list(extra),
        }

    def test_matching_keys(self):
        """Source and translation with same keys are valid"""
        source = {"title", "description", "button_ok"}
        translation = {"title", "description", "button_ok"}
        result = self.validate_key_parity(source, translation)
        assert result["valid"] is True
        assert len(result["missing_keys"]) == 0
        assert len(result["extra_keys"]) == 0

    def test_missing_keys_detected(self):
        """Missing keys should be detected"""
        source = {"title", "description", "button_ok"}
        translation = {"title", "description"}  # Missing button_ok
        result = self.validate_key_parity(source, translation)
        assert result["valid"] is False
        assert "button_ok" in result["missing_keys"]

    def test_extra_keys_detected(self):
        """Extra keys should be detected"""
        source = {"title", "description"}
        translation = {"title", "description", "legacy_field"}  # Extra
        result = self.validate_key_parity(source, translation)
        assert result["valid"] is False
        assert "legacy_field" in result["extra_keys"]


# =============================================================================
# BBCODE/HTML PRESERVATION TESTS
# =============================================================================

class TestFormattingPreservation:
    """Test suite for BBCode/HTML tag preservation (Steam platform)"""

    BBCODE_TAGS = ["h1", "h2", "b", "i", "u", "list", "img", "url", "quote", "code"]

    BBCODE_PATTERN = r"\[(/?)(" + "|".join(BBCODE_TAGS) + r")(?:=[^\]]+)?\]"

    def extract_bbcode_tags(self, text: str) -> list:
        """Extract all BBCode tags from text"""
        return re.findall(self.BBCODE_PATTERN, text, re.IGNORECASE)

    def validate_bbcode_preservation(self, source: str, translation: str) -> bool:
        """Check if BBCode structure is preserved"""
        source_tags = self.extract_bbcode_tags(source)
        translation_tags = self.extract_bbcode_tags(translation)
        return source_tags == translation_tags

    def test_detect_bbcode_headers(self):
        """Detect [h1] and [h2] tags"""
        text = "[h1]Main Title[/h1] and [h2]Subtitle[/h2]"
        tags = self.extract_bbcode_tags(text)
        assert len(tags) == 4
        assert ("", "h1") in tags
        assert ("/", "h1") in tags

    def test_detect_formatting_tags(self):
        """Detect [b], [i], [u] tags"""
        text = "This is [b]bold[/b] and [i]italic[/i]"
        tags = self.extract_bbcode_tags(text)
        assert len(tags) == 4

    def test_bbcode_preserved_passes(self):
        """Translation with same BBCode structure passes"""
        source = "[h1]Welcome[/h1][b]Play now![/b]"
        translation = "[h1]Willkommen[/h1][b]Jetzt spielen![/b]"
        assert self.validate_bbcode_preservation(source, translation) is True

    def test_missing_bbcode_fails(self):
        """Translation missing BBCode tags fails"""
        source = "[h1]Welcome[/h1]"
        translation = "Willkommen"  # Missing tags
        assert self.validate_bbcode_preservation(source, translation) is False


# =============================================================================
# TONE CALIBRATION TESTS (Optional Feature)
# =============================================================================

class TestToneCalibration:
    """Test suite for tone calibration matrix (--tone-matrix flag)"""

    # Expected deviations from review-translation.md
    CULTURAL_DEVIATIONS = {
        "de": {"formality": 0.5, "intensity": -1.0},
        "ja": {"formality": 1.0, "intensity": -1.5},
        "pt_BR": {"formality": -0.5, "intensity": 0.5},
    }

    def calculate_deviation(self, source: float, target: float) -> float:
        """Calculate deviation between source and target tone"""
        return target - source

    def validate_deviation(self, lang: str, dimension: str,
                           source: float, target: float, tolerance: float = 0.5) -> bool:
        """Check if actual deviation is within expected range"""
        expected = self.CULTURAL_DEVIATIONS.get(lang, {}).get(dimension, 0)
        actual = self.calculate_deviation(source, target)
        return abs(actual - expected) <= tolerance

    def test_german_formality_increase_expected(self):
        """German should be more formal (deviation +0.5)"""
        # Source formality: 3.0, German target should be ~3.5
        assert self.validate_deviation("de", "formality", 3.0, 3.5) is True

    def test_japanese_intensity_decrease_expected(self):
        """Japanese should be less intense (deviation -1.5)"""
        # Source intensity: 4.0, Japanese target should be ~2.5
        assert self.validate_deviation("ja", "intensity", 4.0, 2.5) is True

    def test_brazilian_portuguese_informal_expected(self):
        """Brazilian Portuguese should be less formal (deviation -0.5)"""
        assert self.validate_deviation("pt_BR", "formality", 3.0, 2.5) is True


# =============================================================================
# INTEGRATION FIXTURE TESTS
# =============================================================================

@pytest.fixture
def sample_translation_pair():
    """Provide sample source/translation pair for testing"""
    return {
        "source": {
            "game_title": "Epic Adventure",
            "description": "Embark on a {count} hour journey!",
            "cta_button": "[b]Play Now[/b]",
            "price_note": "Only $PRICE$",
        },
        "translation_de": {
            "game_title": "Episches Abenteuer",
            "description": "Begib dich auf eine {count} Stunden lange Reise!",
            "cta_button": "[b]Jetzt spielen[/b]",
            "price_note": "Nur $PRICE$",
        },
    }


@pytest.fixture
def sample_bad_translation():
    """Provide sample translation with various issues"""
    return {
        "source": {
            "title": "Welcome {player}!",
            "action": "[b]Click here[/b]",
        },
        "translation_broken": {
            "title": "Willkommen Spieler!",  # Missing {player}
            "action": "Klicken Sie hier",  # Missing [b] tags
        },
    }


def test_good_translation_validation(sample_translation_pair):
    """Good translation should pass all validation checks"""
    source = sample_translation_pair["source"]
    translation = sample_translation_pair["translation_de"]

    # Check key parity
    assert set(source.keys()) == set(translation.keys())

    # Check placeholder preservation for description
    placeholders_source = re.findall(r"\{.*?\}", source["description"])
    placeholders_trans = re.findall(r"\{.*?\}", translation["description"])
    assert placeholders_source == placeholders_trans


def test_bad_translation_detection(sample_bad_translation):
    """Bad translation should fail validation checks"""
    source = sample_bad_translation["source"]
    translation = sample_bad_translation["translation_broken"]

    # Missing placeholder
    source_placeholders = re.findall(r"\{.*?\}", source["title"])
    trans_placeholders = re.findall(r"\{.*?\}", translation["title"])
    assert source_placeholders != trans_placeholders  # Should differ

    # Missing BBCode
    source_tags = re.findall(r"\[/?b\]", source["action"])
    trans_tags = re.findall(r"\[/?b\]", translation["action"])
    assert source_tags != trans_tags  # Should differ
