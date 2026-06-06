from project.database.models_base import MBase


from sqlalchemy.orm import Mapped


class MCartItem(MBase):
    __tablename__= "catr_itemms"

    username: Mapped[str]
    nom_id: Mapped[int]
    quantity: Mapped[int]