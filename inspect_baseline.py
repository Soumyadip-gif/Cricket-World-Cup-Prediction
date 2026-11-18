import joblib
from config import BASELINE_MODEL

model = joblib.load(BASELINE_MODEL)

preprocessor = model.named_steps["preprocessor"]
classifier = model.named_steps["classifier"]

print("PREPROCESSING DETAILS:")

for name, transformer, columns in preprocessor.transformers_:
    print(f"\n{name}")
    print("Transformer:", type(transformer).__name__)
    print("Columns:", columns)

    if hasattr(transformer, "categories_"):
        print("Categories:", transformer.categories_)

print("\nLOGISTIC REGRESSION PARAMETERS:")
print("C:", classifier.C)
print("Max iterations:", classifier.max_iter)
print("Class weight:", classifier.class_weight)
print("Solver:", classifier.solver)