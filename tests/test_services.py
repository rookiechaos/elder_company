#!/usr/bin/env python3
"""
Elder Company — translation service smoke test (no HTTP server required).
Usage: python tests/test_services.py
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_ROOT = _REPO_ROOT / "backend"
for _path in (_REPO_ROOT, _BACKEND_ROOT):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from utils.local_paths import env_file_path

load_dotenv(env_file_path())
load_dotenv(_BACKEND_ROOT / ".env")


def print_test(name, passed, message=""):
    """Print a single test result."""
    status = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {name}")
    if message:
        print(f"    {message}")


def test_ai_provider_initialization():
    """AI provider initialization."""
    try:
        from services.ai_providers import get_ai_provider

        get_ai_provider()
        provider_name = os.getenv("AI_PROVIDER", "openai").lower()
        print_test("AI provider init", True, f"initialized: {provider_name}")
        return True
    except ValueError as e:
        print_test("AI provider init", False, f"config error: {e}")
        return False
    except Exception as e:
        print_test("AI provider init", False, f"init failed: {e}")
        return False


def test_translation_service_initialization():
    """Translation service initialization."""
    try:
        from services.translation_service import TranslationService

        service = TranslationService()
        print_test("Translation service init", True, "service ready")
        return service
    except Exception as e:
        print_test("Translation service init", False, f"init failed: {e}")
        return None


def test_basic_translation(service):
    """Basic ja -> en translation."""
    if not service:
        print_test("Basic translation", False, "service not initialized")
        return False

    try:

        async def run_test():
            return await service.translate(
                text="こんにちは",
                source_language="ja",
                target_language="en",
            )

        result = asyncio.run(run_test())
        if result and result.get("translated_text"):
            translated = result.get("translated_text", "")
            print_test("Basic translation", True, f"こんにちは -> {translated}")
            return True
        print_test("Basic translation", False, "empty translation result")
        return False
    except Exception as e:
        print_test("Basic translation", False, f"translation failed: {e}")
        return False


def test_same_language_translation(service):
    """Same source and target language returns original text."""
    if not service:
        print_test("Same language", False, "service not initialized")
        return False

    try:

        async def run_test():
            return await service.translate(
                text="こんにちは",
                source_language="ja",
                target_language="ja",
            )

        result = asyncio.run(run_test())
        original = result.get("original_text", "")
        translated = result.get("translated_text", "")
        if original == translated:
            print_test("Same language", True, "returned original text")
            return True
        print_test("Same language", False, f"mismatch: {original} vs {translated}")
        return False
    except Exception as e:
        print_test("Same language", False, f"test failed: {e}")
        return False


def test_care_context_translation(service):
    """Care scenario translation with context."""
    if not service:
        print_test("Care context translation", False, "service not initialized")
        return False

    try:

        async def run_test():
            return await service.translate(
                text="食事介助をお願いします",
                source_language="ja",
                target_language="en",
                context="Care scenario - meal assistance",
            )

        result = asyncio.run(run_test())
        if result and result.get("translated_text"):
            translated = result.get("translated_text", "")
            print_test("Care context translation", True, f"translation: {translated}")
            return True
        print_test("Care context translation", False, "empty translation result")
        return False
    except Exception as e:
        print_test("Care context translation", False, f"translation failed: {e}")
        return False


def test_empty_text_handling(service):
    """Empty text should raise ValueError."""
    if not service:
        print_test("Empty text handling", False, "service not initialized")
        return False

    try:

        async def run_test():
            try:
                await service.translate(
                    text="",
                    source_language="ja",
                    target_language="en",
                )
                return False, "expected ValueError but none was raised"
            except ValueError:
                return True, "correctly rejected empty text"
            except Exception as e:
                return False, f"unexpected exception: {e}"

        passed, message = asyncio.run(run_test())
        print_test("Empty text handling", passed, message)
        return passed
    except Exception as e:
        print_test("Empty text handling", False, f"test failed: {e}")
        return False


def test_conversation_translation(service):
    """Conversation translation helper."""
    if not service:
        print_test("Conversation translation", False, "service not initialized")
        return False

    try:

        async def run_test():
            return await service.translate_conversation(
                message="おはようございます",
                source_language="ja",
                target_language="en",
            )

        result = asyncio.run(run_test())
        if result and result.get("translated_text"):
            translated = result.get("translated_text", "")
            print_test("Conversation translation", True, f"translation: {translated}")
            return True
        print_test("Conversation translation", False, "empty translation result")
        return False
    except Exception as e:
        print_test("Conversation translation", False, f"translation failed: {e}")
        return False


def check_env_config():
    """Verify AI provider env vars."""
    provider = os.getenv("AI_PROVIDER", "").lower()
    if not provider:
        print_test("Environment check", False, "AI_PROVIDER is not set")
        return False

    key_checks = {
        "openai": ("OPENAI_API_KEY", "your_openai_api_key_here"),
        "claude": ("ANTHROPIC_API_KEY", "your_anthropic_api_key_here"),
        "gemini": ("GOOGLE_API_KEY", "your_google_api_key_here"),
    }
    if provider not in key_checks:
        print_test("Environment check", False, f"unsupported AI provider: {provider}")
        return False

    env_name, placeholder = key_checks[provider]
    api_key = os.getenv(env_name)
    if not api_key or api_key == placeholder:
        print_test("Environment check", False, f"{env_name} is not configured")
        return False

    print_test("Environment check", True, f"provider={provider}, API key configured")
    return True


def main():
    """Run all service-layer smoke tests."""
    print("\n" + "=" * 60)
    print("Elder Company — translation service smoke test")
    print("=" * 60 + "\n")

    print("Environment")
    print("-" * 60)
    env_ok = check_env_config()
    print()
    if not env_ok:
        print("\033[91mFAIL\033[0m Invalid environment — check do-not-upload/env/.env\n")
        return 1

    print("Initialization")
    print("-" * 60)
    test_ai_provider_initialization()
    print()
    service = test_translation_service_initialization()
    print()
    if not service:
        print("\033[91mFAIL\033[0m Service initialization failed\n")
        return 1

    print("Functionality")
    print("-" * 60)
    tests = [
        ("Basic translation", lambda: test_basic_translation(service)),
        ("Same language", lambda: test_same_language_translation(service)),
        ("Care context translation", lambda: test_care_context_translation(service)),
        ("Conversation translation", lambda: test_conversation_translation(service)),
        ("Empty text handling", lambda: test_empty_text_handling(service)),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result is not False and result is not None))
        except Exception as e:
            print(f"FAIL {name} - exception: {e}")
            results.append((name, False))
        print()

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
    return 1


if __name__ == "__main__":
    sys.exit(main())
