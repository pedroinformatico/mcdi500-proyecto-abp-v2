"""Transformadores: los pasos del pipeline que aprenden algo de los datos.

Criterio de diseño: un paso es una clase solo si necesita recordar algo entre una
llamada y otra. Lo aprende con `fit` y lo usa después con `transform`, incluso sobre
otros datos. Los pasos que no aprenden nada siguen siendo funciones (ordenes.py) y
entran al pipeline envueltos en `FunctionStep`.

    Transformer            clase base: el contrato común
    ├── OutlierFlagger     aprende el límite de monto extremo
    ├── TopSupplierMarker  aprende quiénes son los mayores proveedores
    ├── SupplierAnonymizer aprende el código de cada proveedor persona natural
    └── FunctionStep       adapta una función sin estado

Las clases no repiten la lógica: llaman a las funciones ya probadas de ordenes.py y
anonimizacion.py. Así el código vive en una sola versión.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

import pandas as pd

from . import anonimizacion, ordenes

TOP_COLUMN = "proveedor_top"
SUPPLIER_COLUMN = "CodigoProveedor"


class Transformer(ABC):
    """Clase base abstracta: lo que todos los pasos del pipeline comparten.

    No se puede instanciar directamente. Define el contrato (`fit` y `transform`) y controla el
    estado; cada clase hija solo dice qué aprende (`_learn`) y cómo lo aplica (`_apply`).
    """

    # Columnas que el paso necesita en los datos. Cada clase hija declara las suyas.
    required_columns: tuple[str, ...] = ()

    def __init__(self) -> None:
        # El guion bajo marca el estado interno: no se modifica desde fuera de la clase.
        self._params: dict = {}
        self._fitted = False

    @property
    def name(self) -> str:
        """Nombre del paso: el de su clase real, no el de la clase base."""
        return type(self).__name__

    @property
    def fitted(self) -> bool:
        return self._fitted

    @property
    def params(self) -> dict:
        """Copia de lo aprendido. Es una copia para que nadie altere el estado interno."""
        return dict(self._params)

    def fit(self, frame: pd.DataFrame) -> Transformer:
        """Aprende de los datos que recibe y devuelve el mismo objeto, para encadenar llamadas."""
        self._check_columns(frame)
        self._params = self._learn(frame)
        self._fitted = True
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Aplica lo aprendido y devuelve un DataFrame nuevo, sin modificar el que recibe."""
        if not self._fitted:
            raise RuntimeError(f"{self.name}: hay que llamar a fit() antes de transform().")
        self._check_columns(frame)
        return self._apply(frame.copy())

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Atajo para el caso habitual: aprender y aplicar sobre los mismos datos."""
        return self.fit(frame).transform(frame)

    def summary(self) -> dict:
        """Lo aprendido, en una forma que se puede mostrar en una bitácora."""
        return self.params

    def _check_columns(self, frame: pd.DataFrame) -> None:
        if not isinstance(frame, pd.DataFrame):
            raise TypeError(f"{self.name}: se esperaba un DataFrame y se recibió {type(frame).__name__}.")
        missing = [column for column in self.required_columns if column not in frame.columns]
        if missing:
            raise KeyError(f"{self.name}: faltan columnas en los datos: {missing}")

    # --- Lo que cada clase hija debe implementar ---

    @abstractmethod
    def _learn(self, frame: pd.DataFrame) -> dict:
        raise NotImplementedError(f"{self.name} debe implementar _learn().")

    @abstractmethod
    def _apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(f"{self.name} debe implementar _apply().")

    def __repr__(self) -> str:
        return f"{self.name}({'ajustado' if self._fitted else 'sin ajustar'})"


class OutlierFlagger(Transformer):
    """Marca las órdenes de monto extremo.

    Aprende el límite (rango intercuartílico del logaritmo del monto) y lo aplica
    después. Ajustado con un período, permite marcar otro con la misma vara.
    """

    required_columns = (ordenes.AMOUNT_COLUMN,)

    def __init__(self, factor: float = ordenes.EXTREME_IQR_FACTOR) -> None:
        super().__init__()
        if factor <= 0:
            raise ValueError("El factor del rango intercuartílico debe ser mayor que cero.")
        self.factor = factor

    def _learn(self, frame: pd.DataFrame) -> dict:
        limit = ordenes.extreme_amount_limit(frame[ordenes.AMOUNT_COLUMN], self.factor)
        return {"limit": limit, "orders_seen": len(frame)}

    def _apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        return ordenes.flag_extreme_amounts(frame, self._params["limit"])


class TopSupplierMarker(Transformer):
    """Marca las órdenes de los mayores proveedores.

    Aprende quiénes son los `top` proveedores por monto. Ajustado con un período y
    aplicado a otro, responde cuánto pesan después los que antes eran los mayores.
    """

    required_columns = (SUPPLIER_COLUMN, ordenes.AMOUNT_COLUMN)

    def __init__(self, top: int = ordenes.TOP_SUPPLIERS) -> None:
        super().__init__()
        if top < 1:
            raise ValueError("El número de proveedores debe ser al menos 1.")
        self.top = top

    def _learn(self, frame: pd.DataFrame) -> dict:
        by_supplier = frame.groupby(SUPPLIER_COLUMN)[ordenes.AMOUNT_COLUMN].sum()
        largest = by_supplier.nlargest(self.top)
        return {"suppliers": tuple(largest.index), "share": float(largest.sum() / by_supplier.sum() * 100)}

    def _apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame[TOP_COLUMN] = frame[SUPPLIER_COLUMN].isin(self._params["suppliers"])
        return frame

    def summary(self) -> dict:
        return {"suppliers": len(self._params["suppliers"]), "share": round(self._params["share"], 1)}


class SupplierAnonymizer(Transformer):
    """Reemplaza por un código a los proveedores que son personas naturales.

    Aprende la correspondencia RUT -> código y la aplica a cualquier conjunto: una misma
    persona conserva su código en todos los archivos.
    """

    def __init__(
        self,
        rut_column: str,
        code_columns: tuple[str, ...] = (),
        name_columns: tuple[str, ...] = (),
        text_columns: tuple[str, ...] = (),
        known_codes: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.rut_column = rut_column
        self.code_columns = tuple(code_columns)
        self.name_columns = tuple(name_columns)
        self.text_columns = tuple(text_columns)
        self._known_codes = dict(known_codes or {})
        self.required_columns = (rut_column, *self.code_columns, *self.name_columns, *self.text_columns)

    def _learn(self, frame: pd.DataFrame) -> dict:
        return {"codes": anonimizacion.learn_supplier_codes(frame[self.rut_column], self._known_codes)}

    def _apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        return anonimizacion.anonymize_suppliers(
            frame, self._params["codes"], self.rut_column, self.code_columns, self.name_columns, self.text_columns
        )

    def summary(self) -> dict:
        # La correspondencia permite volver del código al RUT: en la bitácora solo va el total.
        return {"natural_persons": len(self._params["codes"])}


class FunctionStep(Transformer):
    """Adapta una función sin estado para que el pipeline la trate como a cualquier paso.

    No aprende nada. Existe para que el pipeline llame a todos los pasos de la misma
    forma, sin preguntar si son clases o funciones.
    """

    def __init__(self, function: Callable[[pd.DataFrame], pd.DataFrame], name: str | None = None) -> None:
        super().__init__()
        if not callable(function):
            raise TypeError("FunctionStep necesita una función que reciba y devuelva un DataFrame.")
        self._function = function
        self._name = name or getattr(function, "__name__", "funcion")

    @property
    def name(self) -> str:
        return self._name

    def _learn(self, frame: pd.DataFrame) -> dict:
        return {}

    def _apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self._function(frame)
