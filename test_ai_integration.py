#!/usr/bin/env python3
"""
Simple test to verify AI integration works (without real API calls)
"""

import sys
import os
sys.path.insert(0, 'src')

from janusz.models import DocumentStructure, AIInsight, AIExtractionResult
from janusz.converter import UniversalToYAMLConverter

def test_ai_models():
    """Test that AI models can be imported and initialized"""
    print("Testing AI model imports...")

    try:
        from janusz.ai.ai_content_analyzer import AIContentAnalyzer, OpenRouterClient
        print("✅ AI modules imported successfully")

        # Test model creation (should fail without API key, but not crash)
        try:
            analyzer = AIContentAnalyzer(api_key="dummy_key")
            print("❌ AI analyzer should fail without valid API key")
        except ValueError as e:
            print("✅ AI analyzer correctly requires valid API key")

        # Test model structures
        insight = AIInsight(
            text="Test insight",
            insight_type="improvement",
            confidence_score=0.8,
            reasoning="Test reasoning"
        )
        print("✅ AIInsight model works")

        result = AIExtractionResult(
            summary="Test summary",
            quality_score=0.7
        )
        print("✅ AIExtractionResult model works")

    except ImportError as e:
        print(f"❌ AI modules not available: {e}")

def test_converter_ai_integration():
    """Test that converter accepts AI parameters"""
    print("\nTesting converter AI integration...")

    # Create a simple test file
    test_content = """# Test Document

This is a test document for AI integration.

## Best Practices

- Always test your code
- Use meaningful names
- Write documentation

## Examples

Here's an example:
```python
def hello():
    print("Hello, World!")
```
"""

    with open("test_doc.md", "w") as f:
        f.write(test_content)

    try:
        # Test converter with AI disabled
        converter = UniversalToYAMLConverter("test_doc.md", use_ai=False)
        print("✅ Converter works without AI")

        # Test converter with AI enabled (should not crash)
        converter_ai = UniversalToYAMLConverter("test_doc.md", use_ai=True)
        print("✅ Converter accepts AI parameter")

        # Test conversion
        success = converter.convert_to_yaml()
        if success:
            print("✅ Conversion successful")

            # Check if YAML was created
            import os
            if os.path.exists("test_doc.yaml"):
                print("✅ YAML file created")
            else:
                print("❌ YAML file not created")
        else:
            print("❌ Conversion failed")

    except Exception as e:
        print(f"❌ Converter test failed: {e}")
    finally:
        # Cleanup
        for f in ["test_doc.md", "test_doc.yaml"]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    test_ai_models()
    test_converter_ai_integration()
    print("\n🎉 AI integration test completed!")
