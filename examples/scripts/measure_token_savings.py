#!/usr/bin/env python3
"""
Token Savings Measurement Script for Janusz

This script demonstrates the token compression benefits of Janusz by comparing
raw text, structured YAML/JSON, and optimized TOON formats.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from janusz.converter import UniversalToYAMLConverter
from janusz.json_to_toon import JSONToTOONConverter
from janusz.toon_adapter import YAMLToTOONConverter


def count_text_tokens(text: str) -> int:
    """
    Estimate token count for text using a simple approximation.
    This is a rough estimate - real tokenizers would give more accurate counts.
    """
    if not text:
        return 0

    # Simple tokenization: split on whitespace and punctuation
    import re
    tokens = re.findall(r'\S+', text)
    return len(tokens)


def measure_file_token_savings(input_path: str, output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Process a file through Janusz pipeline and measure token savings.

    Returns a dictionary with token statistics.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"🔄 Processing {input_path.name}...")

    # Read original file
    with open(input_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    original_tokens = count_text_tokens(original_text)
    print(f"📄 Original text tokens: {original_tokens}")

    results = {
        "input_file": str(input_path),
        "original_tokens": original_tokens,
        "formats": {}
    }

    # Convert to YAML
    try:
        converter = UniversalToYAMLConverter(str(input_path))
        success = converter.convert_to_yaml()

        if success:
            yaml_path = input_path.with_suffix('.yaml')
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()

            yaml_tokens = count_text_tokens(yaml_content)
            results["formats"]["yaml"] = {
                "tokens": yaml_tokens,
                "savings_percent": ((original_tokens - yaml_tokens) / original_tokens) * 100,
                "file_size": yaml_path.stat().st_size
            }
            print(f"📋 YAML tokens: {yaml_tokens} ({results['formats']['yaml']['savings_percent']:.1f}% savings)")

            # Copy to examples output
            example_yaml = output_dir / f"{input_path.stem}_janusz.yaml"
            with open(example_yaml, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

    except Exception as e:
        print(f"⚠️  YAML conversion failed: {e}")
        results["formats"]["yaml"] = {"error": str(e)}

    # Convert YAML to TOON (if YAML was successful)
    if "yaml" in results["formats"] and "error" not in results["formats"]["yaml"]:
        try:
            toon_converter = YAMLToTOONConverter(str(yaml_path))
            success = toon_converter.convert()

            if success:
                # Get token statistics
                stats = toon_converter.get_token_stats()
                if stats:
                    toon_tokens = stats.get("toon_stats", {}).get("tokens", 0)
                    results["formats"]["toon"] = {
                        "tokens": toon_tokens,
                        "savings_percent": ((original_tokens - toon_tokens) / original_tokens) * 100,
                        "compression_ratio": stats.get("compression_ratio", 0),
                        "json_tokens": stats.get("json_stats", {}).get("tokens", 0)
                    }
                    print(f"🎨 TOON tokens: {toon_tokens} ({results['formats']['toon']['savings_percent']:.1f}% savings)")
                    print(".1f")

                    # Copy token stats to examples output
                    example_stats = output_dir / f"{input_path.stem}_token_stats.json"
                    with open(example_stats, 'w', encoding='utf-8') as f:
                        json.dump(stats, f, indent=2)
                else:
                    print("⚠️  Could not retrieve TOON token statistics")
            else:
                print("⚠️  TOON conversion failed")

        except Exception as e:
            print(f"⚠️  TOON processing failed: {e}")

    return results


def print_summary(results: Dict[str, Any]):
    """Print a formatted summary of token savings."""
    print("\n" + "="*60)
    print("📊 TOKEN SAVINGS SUMMARY")
    print("="*60)

    print(f"📁 Input: {Path(results['input_file']).name}")
    print(f"📄 Original tokens: {results['original_tokens']}")

    if "yaml" in results["formats"] and "error" not in results["formats"]["yaml"]:
        yaml_data = results["formats"]["yaml"]
        print(f"📋 YAML: {yaml_data['tokens']} tokens ({yaml_data['savings_percent']:+.1f}%)")

    if "toon" in results["formats"] and "error" not in results["formats"]["toon"]:
        toon_data = results["formats"]["toon"]
        print(f"🎨 TOON: {toon_data['tokens']} tokens ({toon_data['savings_percent']:+.1f}%)")
        print(".2f")
        print(f"   JSON tokens: {toon_data['json_tokens']}")

    print("\n💡 Benefits:")
    print("   • Structured data enables better AI understanding")
    print("   • TOON format provides optimal token efficiency")
    print("   • Hierarchical parsing preserves document structure")
    print("   • Confidence levels help prioritize important content")


def main():
    parser = argparse.ArgumentParser(
        description="Measure token savings with Janusz pipeline"
    )
    parser.add_argument(
        "input_file",
        help="Path to input document file"
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory to save output files (default: outputs)"
    )

    args = parser.parse_args()

    try:
        results = measure_file_token_savings(args.input_file, args.output_dir)
        print_summary(results)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
