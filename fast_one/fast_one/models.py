from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey,Date
from fast_one.db_conection import reg, engine
from geoalchemy2 import Geometry
from typing import Any
from datetime import datetime

@reg.mapped_as_dataclass
class NomeMunicipio:
    __tablename__ = "municipio"

    id: Mapped[int] = mapped_column(primary_key=True)
    municipio: Mapped[str] = mapped_column()
    cod_ibge: Mapped[int] = mapped_column()

@reg.mapped_as_dataclass
class Registro:
    __tablename__ = "registro_mensal"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_mes: Mapped[float] = mapped_column()
    mes: Mapped[int] = mapped_column()
    ano: Mapped[int] = mapped_column()
    id_posto: Mapped[int] = mapped_column(ForeignKey("posto.id_posto"))

@reg.mapped_as_dataclass
class NomePosto:
    __tablename__ = "posto"

    id_posto: Mapped[int] = mapped_column(primary_key=True)
    nome_posto: Mapped[str] = mapped_column()
    numero_dias_medidos: Mapped[int] = mapped_column()
    numero_dias_falhos: Mapped[int] = mapped_column()
    numero_meses_medidos: Mapped[int] = mapped_column()
    numero_meses_falhos: Mapped[int] = mapped_column()
    numero_anos_falha: Mapped[int] = mapped_column()
    numero_anos_medidos: Mapped[int] = mapped_column()
    precipitacao_media_anual: Mapped[float] = mapped_column()
    coordenadas: Mapped[any] = mapped_column(Geometry(geometry_type="POINT", srid=4326))

@reg.mapped_as_dataclass
class NomeEstado:
    __tablename__ = "registro-diario"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_posto: Mapped[int] = mapped_column(ForeignKey("posto.id_posto"))
    data: Mapped[datetime] = mapped_column(Date)
    valor: Mapped[float] = mapped_column()

reg.metadata.create_all(engine)

