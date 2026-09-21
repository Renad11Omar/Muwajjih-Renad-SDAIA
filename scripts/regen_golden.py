from __future__ import annotations

import csv
import os
from pathlib import Path

from muwajjih.adapters.sklearn_model import SklearnMuwajjihModel
from muwajjih.domain.entities import Complaint
from muwajjih.service.scorer import TriageScorer

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "models" / "golden_scores_v1.csv"

CASES = [
    ("MWJ-G001", "هناك حفرة كبيرة في الطريق قرب المدرسة"),
    ("MWJ-G002", "street pavement is cracked and damaged"),
    ("MWJ-G003", "انقطاع المياه منذ الصباح في الحي"),
    ("MWJ-G004", "water pipe is leaking in the neighborhood"),
    ("MWJ-G005", "حاويات النفايات ممتلئة وتفيض"),
    ("MWJ-G006", "trash has not been collected for days"),
    ("MWJ-G007", "الكهرباء منقطعة في المبنى"),
    ("MWJ-G008", "electric cable is exposed"),
    ("MWJ-G009", "دخان يخرج من مبنى مهجور"),
    ("MWJ-G010", "gas leak emergency near houses"),
    ("MWJ-G011", "أحتاج رخصة بناء جديدة"),
    ("MWJ-G012", "how can I renew my shop permit"),
    ("MWJ-G013", "power is out in the building"),
    ("MWJ-G014", "sewage overflow in the street"),
    ("MWJ-G015", "illegal dumping near the public park"),
    ("MWJ-G016", "fire risk near the public park"),
    ("MWJ-G017", "رائحة تسرب الغاز في الشارع"),
    ("MWJ-G018", "broken traffic sign at the intersection"),
    ("MWJ-G019", "ما المستندات المطلوبة للرخصة"),
    ("MWJ-G020", "street light pole damaged after accident"),
]


def main() -> None:
    if os.environ.get("APPROVE_GOLDEN_REGEN") != "1":
        raise SystemExit("Golden regeneration is deliberate: set APPROVE_GOLDEN_REGEN=1")
    model = SklearnMuwajjihModel.load(ROOT / "models" / "muwajjih_v1.joblib", "muwajjih-v1")
    scorer = TriageScorer(model)
    with GOLDEN.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["complaint_id", "text", "department", "priority", "confidence"])
        for complaint_id, text in CASES:
            decision = scorer.score(Complaint(complaint_id, text))
            writer.writerow([
                complaint_id,
                text,
                decision.department.value,
                decision.priority.value,
                f"{decision.confidence:.8f}",
            ])
    print(f"wrote {GOLDEN}")


if __name__ == "__main__":
    main()
