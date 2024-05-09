from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.base_class import Base

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def create_multi(self, db: Session, *, obj_in) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        obj_list = []
        for obj in obj_in_data:
            db_obj = self.model(**obj)
            obj_list.append(db_obj)  # type: ignore
        db.add_all(obj_list)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.flush()
        return obj

    def get_orders(self, db_obj, orders, fields_dict, order_list):
        """
        Appends applicable orders to `orders` list and return `orders`

        :param orders: list List which may contain peewee fields to order
        :param fields_dict: dict Dict which contains key as field names and value as peewee fields
        :param order_list: list Every element should be list of two element. first is field_name
        from fields_dict and second is order direction 1 for ascending and -1 for descending
        :return: list
        """
        if not order_list:
            return orders
        for item in order_list:
            if item['desc']:  # descending order
                orders.append(fields_dict[item['id']].desc())
            else:  # ascending order
                orders.append(fields_dict[item['id']])
        return tuple(orders)

    # async def dynamic_filter_up(self, db: Session, filter_fields: Dict, date_from, date_to, paginate: Paginate = None,
    #                             sort_fields=None,additional_query=None):
    #     '''
    #         Return filtered queryset based on condition.
    #         :param query: takes query
    #         :param filter_condition: Its a list, ie: [(key,operator,value)]
    #         operator list:
    #             eq for ==
    #             lt for <
    #             ge for >=
    #             in for in_
    #             like for like
    #             value could be list or a string
    #         :return: queryset
    #     '''
    #     try:
    #         if additional_query:
    #             query = additional_query
    #         else:
    #             query = db.query(self.model)
    #
    #         fields_dict = {
    #             "name": self.model.name
    #         }
    #
    #         for raw in filter_condition:
    #             try:
    #                 key, op, value = raw
    #             except ValueError:
    #                 raise Exception('Invalid filter: %s' % raw)
    #             column = getattr(self.model, key, None)
    #             if not column:
    #                 raise Exception('Invalid filter column: %s' % key)
    #             if op == 'in':
    #                 if isinstance(value, list):
    #                     filt = column.in_(value)
    #                 else:
    #                     filt = column.in_(value.split(','))
    #             else:
    #                 attr = op
    #                 if value == 'null':
    #                     value = None
    #                 if attr == "like":
    #                     search = "%{}%".format(value)
    #                     query = query.filter(column.like(search))
    #                 elif attr == "starts_with":
    #                     search = "{}%".format(value)
    #                     query = query.filter(column.like(search))
    #                 elif attr == 'eq':
    #                     # filt = getattr(column, attr)(value)
    #                     search = "{}".format(value)
    #                     query = query.filter(column.like(search))
    #         result = query.all()
    #         return result
    #     except Exception as e:
    #         raise e

    def dynamic_filter(self, db: Session, filter_condition, additional_filter=None, additional_query=None, limit=None):
        '''
            Return filtered queryset based on condition.
            :param query: takes query
            :param filter_condition: Its a list, ie: [(key,operator,value)]
            operator list:
                eq for ==
                lt for <
                ge for >=
                in for in_
                like for like
                value could be list or a string
            :return: queryset
        '''
        try:
            if additional_query:
                query = additional_query
            else:
                query = db.query(self.model)
            for raw in filter_condition:
                try:
                    key, op, value = raw
                except ValueError:
                    raise Exception('Invalid filter: %s' % raw)
                column = getattr(self.model, key, None)
                if not column:
                    raise Exception('Invalid filter column: %s' % key)
                if op == 'in':
                    if isinstance(value, list):
                        filt = column.in_(value)
                    else:
                        filt = column.in_(value.split(','))
                else:
                    attr = op
                    if value == 'null':
                        value = None
                    if attr == "like":
                        search = "%{}%".format(value)
                        query = query.filter(column.ilike(search))
                    elif attr == "starts_with":
                        search = "{}%".format(value)
                        query = query.filter(column.ilike(search))
                    elif attr == 'eq':
                        # filt = getattr(column, attr)(value)
                        search = "{}".format(value)
                        query = query.filter(column.like(search))
            result = query.all()
            return result
        except Exception as e:
            raise e




