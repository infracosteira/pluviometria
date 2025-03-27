from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from db_conection import reg, engine


@reg.mapped_as_dataclass
class NomeMunicipio:
    __tablename__ = "nome_municipio"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_municipio: Mapped[str] = mapped_column()
    cod_ibge: Mapped[int] = mapped_column()

@reg.mapped_as_dataclass
class Registro:
    __tablename__ = "registro"

    id: Mapped[int] = mapped_column(primary_key=True)
    dia: Mapped[int] = mapped_column()
    total_dia: Mapped[float] = mapped_column()
    mes: Mapped[float] = mapped_column()
    ano: Mapped[float] = mapped_column()

@reg.mapped_as_dataclass
class NomePosto:
    __tablename__ = "nome_posto"

    id_posto: Mapped[int] = mapped_column(primary_key=True)
    nome_posto: Mapped[str] = mapped_column()
    dias_dados_medidos: Mapped[int] = mapped_column()
    dias_falhos: Mapped[int] = mapped_column()
    meses_dados_medidos: Mapped[int] = mapped_column()
    meses_falhos: Mapped[int] = mapped_column()
    numero_anos_falha: Mapped[int] = mapped_column()
    numero_anos_completos: Mapped[int] = mapped_column()
    precipitacao_media_anual: Mapped[float] = mapped_column(ForeignKey("registro.id"))
    coordenadas: Mapped[str] = mapped_column()

# Criar as tabelas no banco
reg.metadata.create_all(engine)
