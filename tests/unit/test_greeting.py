"""Test greeting detection — bug fix: sapaan tidak boleh trigger RAG search."""
import os
import sys

sys.path.insert(0, os.getcwd())

from src.services.chat import is_greeting

# (input, expected_is_greeting)
cases = [
    # Sapaan yang HARUSNYA return True
    ("hai", True),
    ("Hai", True),
    ("hai!", True),
    ("halo", True),
    ("haloo", True),
    ("hi", True),
    ("hello", True),
    ("hei", True),
    ("Selamat pagi", True),
    ("selamat siang", True),
    ("Selamat sore", True),
    ("selamat malam", True),
    ("assalamualaikum", True),
    ("Hai, apa kabar?", True),
    ("halo semua", True),
    ("   hai   ", True),
    ("Halo. Apa kabar?", True),
    # Bukan sapaan — HARUSNYA return False
    ("hai, saya mau bertanya tentang SOP cuti yang berlaku di departemen HR", False),
    ("berapa lama proses pengajuan cuti tahunan?", False),
    ("tolong carikan dokumen tentang kebijakan remunerasi", False),
    ("", False),
    ("hai selamat pagi saya ingin bertanya tentang rencana phk yang akan dilakukan oleh perusahaan bulan depan", False),
    ("resep rendang", False),
]

passed = 0
failed = 0

for text, expected in cases:
    got = is_greeting(text)
    status = "✅" if got == expected else "❌"
    if got == expected:
        passed += 1
    else:
        failed += 1
    print(f"  {status} {text!r:55s} expected={expected} got={got}")

print(f"\n{'='*60}")
print(f"Passed: {passed}/{len(cases)}")
if failed:
    print(f"Failed: {failed}")
    sys.exit(1)
else:
    print("=== ALL GREETING TESTS PASSED ===")