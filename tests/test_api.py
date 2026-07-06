#!/usr/bin/env python3
"""
Elder Company — live API smoke test.
Usage: python tests/test_api.py (requires backend on http://localhost:8000)
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def print_test(name, passed, message=""):
    """Print a single test result."""
    status = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {name}")
    if message:
        print(f"    {message}")


def test_health_check():
    """Health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            provider = data.get("provider", "unknown")
            provider_status = data.get("provider_status", "unknown")
            print_test(
                "Health check",
                True,
                f"status={status}, provider={provider} ({provider_status})",
            )
            return True
        print_test("Health check", False, f"status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Health check", False, f"error: {e}")
        return False


def test_ai_provider_info():
    """AI provider metadata."""
    try:
        response = requests.get(f"{BASE_URL}/api/ai/provider", timeout=5)
        if response.status_code == 200:
            data = response.json()
            provider = data.get("provider", "unknown")
            status = data.get("status", "unknown")
            supported = data.get("supported_providers", [])
            print_test(
                "AI provider info",
                True,
                f"provider={provider}, status={status}, supported={', '.join(supported)}",
            )
            return True
        print_test("AI provider info", False, f"status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("AI provider info", False, f"error: {e}")
        return False


def test_translate_ja_to_en():
    """Japanese to English translation."""
    try:
        payload = {
            "text": "こんにちは、お元気ですか？",
            "source_language": "ja",
            "target_language": "en",
        }
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            original = data.get("original_text", "")
            translated = data.get("translated_text", "")
            print_test(
                "Japanese to English",
                True,
                f"original: {original[:30]}... -> translation: {translated[:30]}...",
            )
            return True
        error_detail = (
            response.json().get("detail", "Unknown error")
            if response.content
            else "No error detail"
        )
        print_test(
            "Japanese to English",
            False,
            f"status code: {response.status_code}, error: {error_detail}",
        )
        return False
    except Exception as e:
        print_test("Japanese to English", False, f"error: {e}")
        return False


def test_translate_en_to_ja():
    """English to Japanese translation."""
    try:
        payload = {
            "text": "Good morning. How are you today?",
            "source_language": "en",
            "target_language": "ja",
        }
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            original = data.get("original_text", "")
            translated = data.get("translated_text", "")
            print_test(
                "English to Japanese",
                True,
                f"original: {original[:30]}... -> translation: {translated[:30]}...",
            )
            return True
        error_detail = (
            response.json().get("detail", "Unknown error")
            if response.content
            else "No error detail"
        )
        print_test(
            "English to Japanese",
            False,
            f"status code: {response.status_code}, error: {error_detail}",
        )
        return False
    except Exception as e:
        print_test("English to Japanese", False, f"error: {e}")
        return False


def test_translate_care_context():
    """Care scenario translation with context."""
    try:
        payload = {
            "text": "食事介助をお願いします",
            "source_language": "ja",
            "target_language": "en",
            "context": "Care scenario - meal assistance",
        }
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            translated = data.get("translated_text", "")
            print_test("Care context translation", True, f"translation: {translated}")
            return True
        error_detail = (
            response.json().get("detail", "Unknown error")
            if response.content
            else "No error detail"
        )
        print_test(
            "Care context translation",
            False,
            f"status code: {response.status_code}, error: {error_detail}",
        )
        return False
    except Exception as e:
        print_test("Care context translation", False, f"error: {e}")
        return False


def test_translate_empty_text():
    """Empty text should be rejected."""
    try:
        payload = {"text": "", "source_language": "ja", "target_language": "en"}
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=10)
        if response.status_code == 400:
            print_test("Empty text validation", True, "correctly rejected empty text")
            return True
        print_test(
            "Empty text validation",
            False,
            f"expected 400, got {response.status_code}",
        )
        return False
    except Exception as e:
        print_test("Empty text validation", False, f"error: {e}")
        return False


def test_translate_same_language():
    """Same source and target language returns original text."""
    try:
        payload = {
            "text": "こんにちは",
            "source_language": "ja",
            "target_language": "ja",
        }
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("original_text") == data.get("translated_text"):
                print_test("Same language handling", True, "returned original text")
                return True
            print_test(
                "Same language handling",
                False,
                "expected original text, got a different translation",
            )
            return False
        print_test("Same language handling", False, f"status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Same language handling", False, f"error: {e}")
        return False


def test_chat_translation():
    """Chat endpoint translation."""
    try:
        payload = {
            "message": "おはようございます。今日はどうですか？",
            "source_language": "ja",
            "target_language": "en",
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            provider = data.get("provider", "unknown")
            print_test(
                "Chat translation",
                True,
                f"message: {message[:40]}... (provider: {provider})",
            )
            return True
        error_detail = (
            response.json().get("detail", "Unknown error")
            if response.content
            else "No error detail"
        )
        print_test(
            "Chat translation",
            False,
            f"status code: {response.status_code}, error: {error_detail}",
        )
        return False
    except Exception as e:
        print_test("Chat translation", False, f"error: {e}")
        return False


def test_get_languages():
    """Supported languages list."""
    try:
        response = requests.get(f"{BASE_URL}/api/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            languages = data.get("languages", [])
            lang_codes = [lang.get("code", "") for lang in languages]
            print_test("Language list", True, f"supported: {', '.join(lang_codes)}")
            return True
        print_test("Language list", False, f"status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Language list", False, f"error: {e}")
        return False


def test_get_care_terms():
    """Care terminology list."""
    try:
        response = requests.get(f"{BASE_URL}/api/terms", timeout=5)
        if response.status_code == 200:
            data = response.json()
            terms = data.get("terms", [])
            print_test("Care terms", True, f"term count: {len(terms)}")
            if terms:
                first_term = terms[0]
                print(f"    example: {first_term.get('ja', '')} -> {first_term.get('en', '')}")
            return True
        print_test("Care terms", False, f"status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Care terms", False, f"error: {e}")
        return False


def test_translate_long_text():
    """Long text translation."""
    try:
        long_text = "こんにちは。" * 20
        payload = {
            "text": long_text,
            "source_language": "ja",
            "target_language": "en",
        }
        response = requests.post(f"{BASE_URL}/api/translate", json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            translated = data.get("translated_text", "")
            print_test(
                "Long text translation",
                True,
                f"source length: {len(long_text)}, translation length: {len(translated)}",
            )
            return True
        error_detail = (
            response.json().get("detail", "Unknown error")
            if response.content
            else "No error detail"
        )
        print_test(
            "Long text translation",
            False,
            f"status code: {response.status_code}, error: {error_detail}",
        )
        return False
    except Exception as e:
        print_test("Long text translation", False, f"error: {e}")
        return False


def check_server_running():
    """Return True if the backend responds."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def run_section(title, tests, results):
    """Run a group of tests and append results."""
    print(title)
    print("-" * 60)
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result is not False and result is not None))
        except Exception as e:
            print(f"FAIL {name} - exception: {e}")
            results.append((name, False))
        print()


def main():
    """Run all smoke tests."""
    print("\n" + "=" * 60)
    print("Elder Company — API smoke test")
    print("=" * 60 + "\n")

    if not check_server_running():
        print("\033[91mFAIL\033[0m Cannot connect to server")
        print(f"   Ensure the backend is running at {BASE_URL}")
        print("   Start: cd backend && uvicorn main:app --reload\n")
        return 1

    print(f"Server: {BASE_URL}\n")

    basic_tests = [
        ("Health check", test_health_check),
        ("AI provider info", test_ai_provider_info),
        ("Language list", test_get_languages),
        ("Care terms", test_get_care_terms),
    ]

    translation_tests = [
        ("Japanese to English", test_translate_ja_to_en),
        ("English to Japanese", test_translate_en_to_ja),
        ("Care context translation", test_translate_care_context),
        ("Chat translation", test_chat_translation),
        ("Long text translation", test_translate_long_text),
    ]

    edge_case_tests = [
        ("Empty text validation", test_translate_empty_text),
        ("Same language handling", test_translate_same_language),
    ]

    results = []
    run_section("Basic endpoints", basic_tests, results)
    print()
    run_section("Translation", translation_tests, results)
    print()
    run_section("Edge cases", edge_case_tests, results)

    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    print("=" * 60 + "\n")

    if passed == total:
        print("\033[92mAll tests passed.\033[0m\n")
        return 0

    failed_tests = [name for name, result in results if not result]
    print("\033[91mSome tests failed.\033[0m")
    if failed_tests:
        print(f"Failed: {', '.join(failed_tests)}\n")
    print("Check that:")
    print("1. The backend server is running")
    print("2. do-not-upload/env/.env contains valid API keys")
    print("3. The configured AI provider is reachable\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
