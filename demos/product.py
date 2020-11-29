from enum import Enum


class Product(Enum):
    """Перечислимый тип Enum с обозначением продуктов.
       Может использоваться как ключ словарей с данными по продуктам.
   
    Использование:

    >>> [p for in Product] # перечисление
    >>> Product.A          # обозначение продукта
    >>> Product.A.name     # H 
    """

    A = "H"
    B = "H10"
    C = "TA-HSA-10"
    D = "TA-240"
