import csv
from pathlib import Path

files = [
    "data/sl051bai.csv",
    "data/sl051bkn.csv",
    "data/sl051bow.csv",
]

output = "seed/school_data.csv"

Path("seed").mkdir(exist_ok=True)

header = None

with open(output, "w", newline="", encoding="utf-8") as out_f:
    writer = None

    for file in files:
        print(f"Leyendo {file}...")

        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            h = next(reader)

            if header is None:
                header = h
                writer = csv.writer(out_f)
                writer.writerow(header)

            for row in reader:
                writer.writerow(row)

print("\n✅ school_data.csv creado correctamente")