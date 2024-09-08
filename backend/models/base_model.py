#!/usr/bin/env python3
"""Defines a basemodel all the other models inherit from"""
import uuid
from datetime import datetime
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    """A base class for all models"""
    pass


class BaseModel:
    """Defines all common attributes/methods for other classes"""

    id: Mapped[str] = mapped_column(String(60),
                                    primary_key=True,
                                    nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow,
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.utcnow,
                                                 nullable=False)

    def __init__(self, *args, **kwargs):
        """Loads an object from kwargs if not empty"""
        if kwargs:
            for key, value in kwargs.items():
                if key == '__class__':
                    continue
                if key == 'created_at' or key == 'updated_at':
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            # storage.new(self)

    def __str__(self):
        """Overwrites __str__ to print
        [<class name>] (<self.id>) <self.__dict__>
        """
        s = f'[{self.__class__.__name__}] ({self.id}) {self.__dict__}'
        return s

    def save(self):
        """Updates the public instance attribute
        updated_at with the current datetime
        """
        self.updated_at = datetime.utcnow()
        # storage.save()

    def to_dict(self):
        """Returns a dictionary containing all
        keys/values of __dict__ of the instance.
        A key __class__ is added with the class name
        of the object. Both created_at and updated_at
        attributes are converted into isoformat

        Returns: A dict representation of the object
        """
        dict_rep = self.__dict__.copy()
        dict_rep['__class__'] = self.__class__.__name__
        dict_rep['created_at'] = self.created_at.isoformat()
        dict_rep['updated_at'] = self.updated_at.isoformat()

        return dict_rep
