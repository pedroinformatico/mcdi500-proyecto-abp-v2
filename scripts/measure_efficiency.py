"""Mide tiempo y memoria de cada operación del pipeline con datos sintéticos de varios tamaños.

Compara la versión que usa el pipeline con una versión fila por fila, después de
comprobar que ambas dan el mismo resultado. Los datos salen del generador sintético:
no se usa ni se toca data/raw/.

Uso:
    python scripts/measure_efficiency.py                          # 1.000 y 10.000 órdenes
    python scripts/measure_efficiency.py --orders 10000 50000 200000
    python scripts/measure_efficiency.py --out data/external/eficiencia.csv

Los tiempos dependen de la máquina; lo que se compara es la razón entre versiones.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from pipeline import medicion, sinteticos
from pipeline.config import RANDOM_SEED, RAW_DATA_DIR

MAX_ITERROWS_ORDERS = 50_000  # sobre este tamaño `iterrows` tarda demasiado y no agrega información


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--orders", type=int, nargs="+", default=[1_000, 10_000], help="Tamaños a medir, en órdenes")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Semilla del generador sintético")
    parser.add_argument("--repeats", type=int, default=medicion.REPEATS, help="Repeticiones por medición")
    parser.add_argument("--out", type=Path, help="Archivo CSV donde guardar la tabla (fuera de data/raw/)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.out and RAW_DATA_DIR.resolve() in args.out.resolve().parents:
        print("La salida no puede estar en data/raw/: ahí vive la copia congelada de los datos reales.", file=sys.stderr)
        return 1
    tables = []
    for size in args.orders:
        lines = sinteticos.make_order_lines(orders=size, seed=args.seed)
        skip = ("iterrows",) if size > MAX_ITERROWS_ORDERS else ()
        table = medicion.compare(lines, repeats=args.repeats, skip=skip)
        table.insert(0, "ordenes", size)
        tables.append(table)
        print(f"\n{size:,} órdenes · {len(lines):,} líneas")
        print(table.drop(columns=["ordenes", "en_pipeline"]).to_string(index=False))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        pd.concat(tables, ignore_index=True).to_csv(args.out, index=False)
        print(f"\nTabla guardada en {args.out}")
    print("\n'aceleracion': cuántas veces más rápida es la versión del pipeline que esa fila (bajo 1, es más lenta).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
