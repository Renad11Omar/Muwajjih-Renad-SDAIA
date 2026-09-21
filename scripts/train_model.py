from __future__ import annotations

import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "muwajjih_v1.joblib"
DATA_PATH = ROOT / "data" / "training.csv"

DEPARTMENTS: dict[str, list[tuple[str, str]]] = {
    "roads": [
        ("pothole on the main road near the school", "طريق فيه حفرة كبيرة قرب المدرسة"),
        ("damaged street pavement needs repair", "رصف الشارع متضرر ويحتاج إصلاح"),
        ("broken traffic sign at the intersection", "لوحة مرورية مكسورة عند التقاطع"),
        ("street light pole damaged after accident", "عمود إنارة الشارع متضرر بعد حادث"),
        ("sidewalk is cracked and unsafe", "الرصيف متشقق وغير آمن"),
        ("road surface collapsed after rain", "هبوط في سطح الطريق بعد المطر"),
    ],
    "water": [
        ("water pipe is leaking in the neighborhood", "تسرب من أنبوب المياه في الحي"),
        ("no water supply since this morning", "انقطاع المياه منذ هذا الصباح"),
        ("water meter is broken", "عداد المياه متعطل"),
        ("sewage overflow in the street", "فيضان مياه الصرف الصحي في الشارع"),
        ("water pressure is very low", "ضغط المياه منخفض جدًا"),
        ("drain is blocked and water is pooling", "المصرف مسدود وتتجمع المياه"),
    ],
    "waste": [
        ("garbage containers are overflowing", "حاويات النفايات ممتلئة وتفيض"),
        ("trash has not been collected for days", "لم يتم جمع النفايات منذ عدة أيام"),
        ("there is illegal dumping near the park", "هناك رمي نفايات غير نظامي قرب الحديقة"),
        ("the waste bin is damaged", "حاوية النفايات متضررة"),
        ("recycling collection was missed", "لم يتم جمع مواد إعادة التدوير"),
        ("street is full of household waste", "الشارع مليء بالنفايات المنزلية"),
    ],
    "electricity": [
        ("power is out in the building", "الكهرباء منقطعة في المبنى"),
        ("electricity meter is damaged", "عداد الكهرباء متضرر"),
        ("street light is not working", "إنارة الشارع لا تعمل"),
        ("sparking from electrical cabinet", "شرر يخرج من لوحة الكهرباء"),
        ("frequent power interruptions in the area", "انقطاعات كهرباء متكررة في المنطقة"),
        ("electric cable is exposed", "سلك كهربائي مكشوف"),
    ],
    "public_safety": [
        ("smoke is coming from an empty building", "يوجد دخان يخرج من مبنى مهجور"),
        ("fire risk near the public park", "خطر حريق قرب الحديقة العامة"),
        ("gas leak smell in the street", "رائحة تسرب غاز في الشارع"),
        ("dangerous open hole without barriers", "حفرة خطرة مفتوحة دون حواجز"),
        ("fallen tree blocking emergency access", "شجرة ساقطة تعيق وصول الطوارئ"),
        ("explosion sound was heard nearby", "تم سماع صوت انفجار بالقرب من الموقع"),
    ],
    "permits": [
        ("I need a building permit application", "أحتاج إلى تقديم طلب رخصة بناء"),
        ("how can I renew my shop permit", "كيف أجدد رخصة المحل"),
        ("permit status has not changed", "حالة الرخصة لم تتغير"),
        ("there is a mistake in my permit record", "هناك خطأ في بيانات الرخصة"),
        ("I want to request a temporary event permit", "أرغب في طلب رخصة فعالية مؤقتة"),
        ("what documents are required for a permit", "ما المستندات المطلوبة للرخصة"),
    ],
}

NORMAL_SUFFIXES = [
    "please help", "please review", "يرجى المعالجة", "يرجى المراجعة", "احتاج المساعدة",
]
URGENT_SEEDS = [
    ("fire emergency at the site", "حالة حريق طارئة في الموقع"),
    ("gas leak emergency", "حالة تسرب غاز طارئة"),
    ("smoke and immediate danger", "دخان وخطر فوري"),
    ("explosion and public danger", "انفجار وخطر على الناس"),
]


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for department, pairs in DEPARTMENTS.items():
        for en, ar in pairs:
            for suffix in NORMAL_SUFFIXES:
                if suffix in {"please help", "please review"}:
                    text = f"{en}; {suffix}"
                else:
                    text = f"{ar}؛ {suffix}"
                rows.append({"text": text, "department": department, "priority": "normal"})
    # Explicit urgent examples train priority; the domain policy guarantees the safety override.
    for en, ar in URGENT_SEEDS:
        rows.append({"text": en, "department": "public_safety", "priority": "urgent"})
        rows.append({"text": ar, "department": "public_safety", "priority": "urgent"})
    # Representative urgent examples across operational departments.
    extra_urgent = [
        ("power lines are sparking and people are nearby", "electricity", "urgent"),
        ("major water leak is flooding the road", "water", "urgent"),
        ("garbage fire near houses", "waste", "urgent"),
        ("road collapse is blocking traffic", "roads", "urgent"),
    ]
    rows.extend(
        {"text": text, "department": dept, "priority": priority}
        for text, dept, priority in extra_urgent
    )
    return rows


def main() -> None:
    rows = build_rows()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["text", "department", "priority"])
        writer.writeheader()
        writer.writerows(rows)

    texts = [row["text"].strip().casefold() for row in rows]
    y_department = [row["department"] for row in rows]
    y_priority = [row["priority"] for row in rows]

    def make_pipeline() -> Pipeline:
        return Pipeline(
            [
                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)),
                ("clf", LogisticRegression(max_iter=2000, random_state=42)),
            ]
        )

    bundle = {
        "department_model": make_pipeline().fit(texts, y_department),
        "priority_model": make_pipeline().fit(texts, y_priority),
        "model_version": "muwajjih-v1",
        "training_rows": len(rows),
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_PATH, compress=3)
    print(f"trained_rows={len(rows)}")
    print(f"model={MODEL_PATH}")


if __name__ == "__main__":
    main()
