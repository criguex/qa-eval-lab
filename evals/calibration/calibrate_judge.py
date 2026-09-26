"""
Modulo 4 — calibracion del LLM-as-judge (la skill que separa a un AI-Eval Engineer).
Un judge solo es confiable si concuerda con humanos. Etiqueta N casos a mano
(human_label), corre el judge sobre los mismos (judge_label) y mide el acuerdo.

Lee labeled_sample.csv y reporta:
  - % de acuerdo
  - Cohen's kappa (acuerdo corregido por azar)
  - los casos en desacuerdo (a revisar: ¿mala rubrica o mal humano?)

Correr (offline, sin API):  python evals/calibration/calibrate_judge.py
"""
import os
import pandas as pd
from sklearn.metrics import cohen_kappa_score

HERE = os.path.dirname(__file__)

def main():
    df = pd.read_csv(os.path.join(HERE, "labeled_sample.csv"))
    total = len(df)
    agree = (df["human_label"] == df["judge_label"]).sum()
    pct = agree / total * 100
    kappa = cohen_kappa_score(df["human_label"], df["judge_label"])
    disagreements = df[df["human_label"] != df["judge_label"]]

    print(f"Casos: {total}")
    print(f"Acuerdo: {agree}/{total} ({pct:.1f}%)")
    print(f"Cohen's kappa: {kappa:.2f}  (>0.8 excelente · 0.6-0.8 aceptable · <0.6 recalibrar rubrica)")
    if len(disagreements):
        print("\nDesacuerdos (revisar rubrica/etiqueta humana):")
        for _, r in disagreements.iterrows():
            print(f"  - {r['case_id']}: humano={r['human_label']} vs judge={r['judge_label']}")
    else:
        print("\nSin desacuerdos.")

if __name__ == "__main__":
    main()
