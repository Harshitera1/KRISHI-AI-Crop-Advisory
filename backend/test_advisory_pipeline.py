import json
import sys
from pathlib import Path

from main import app
from services.agentic_service import export_advisory_pdf, run_advisory_pipeline

SAMPLE_FARMERS = [
    {
        "name": "Delhi loamy wheat field",
        "location": "Delhi",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "soil": "Loamy",
        "N": 25,
        "P": 12,
        "K": 140,
        "ph": 7.8,
        "temperature": 24,
        "humidity": 58,
        "rainfall": 180,
    },
    {
        "name": "Pune loamy cotton field",
        "location": "Pune",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "soil": "Loamy",
        "N": 35,
        "P": 16,
        "K": 150,
        "ph": 7.2,
        "temperature": 29,
        "humidity": 68,
        "rainfall": 620,
    },
    {
        "name": "Bangalore sandy maize field",
        "location": "Bangalore",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "soil": "Sandy",
        "N": 32,
        "P": 15,
        "K": 140,
        "ph": 6.5,
        "temperature": 27,
        "humidity": 74,
        "rainfall": 780,
    },
    {
        "name": "Jaipur sandy rainfed field",
        "location": "Jaipur",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "soil": "Sandy",
        "N": 12,
        "P": 7,
        "K": 95,
        "ph": 8.0,
        "temperature": 42,
        "humidity": 18,
        "rainfall": 12,
    },
]


def main() -> int:
    failures = 0
    print("KRISHI AI advisory pipeline smoke test")
    print("=" * 70)

    with app.app_context():
        for number, farmer_input in enumerate(SAMPLE_FARMERS, 1):
            name = farmer_input["name"]
            print(f"\nCASE {number}: {name}")
            print("-" * 70)
            try:
                result = run_advisory_pipeline(farmer_input)
                pdf_path = export_advisory_pdf(
                    result.get("advisory_text", ""),
                    {**farmer_input, **result},
                )

                print("FULL PIPELINE OUTPUT:")
                print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
                print("\nPDF CHECK:")
                print(f"path: {pdf_path}")
                print(f"created: {Path(pdf_path).is_file()}")

                if (
                    not result.get("success")
                    or not result.get("advisory_text", "").strip()
                    or not Path(pdf_path).is_file()
                ):
                    failures += 1
                    print("STATUS: FAIL")
                else:
                    print("STATUS: PASS")
            except Exception as error:
                failures += 1
                print(f"STATUS: FAIL ({type(error).__name__}: {error})")

    print("\n" + "=" * 70)
    if failures:
        print(f"SMOKE TEST FAILED: {failures} case(s) failed")
        return 1

    print(f"SMOKE TEST PASSED: {len(SAMPLE_FARMERS)} cases completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
