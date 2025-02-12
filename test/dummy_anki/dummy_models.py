from typing import Any, Union

NoteType = dict[str, Any]
FieldDict = dict[str, Any]
TemplateDict = dict[str, Union[str, int, None]]

class Model:
    @staticmethod
    def by_name(name: str):
        return NoteType()

    @staticmethod
    def new(*args, **kwargs) -> NoteType:
        return NoteType()

    @staticmethod
    def add_field(*args, **kwargs):
        pass

    @staticmethod
    def new_field(*args, **kwargs) -> FieldDict:
        return FieldDict()

    @staticmethod
    def update(*args, **kwargs):
        pass

    @staticmethod
    def new_template(name: str) -> TemplateDict:
        return TemplateDict()

    @staticmethod
    def addTemplate(*args, **kwargs):
        pass

    @staticmethod
    def remove(*args, **kwargs):
        pass

    @staticmethod
    def save(*args, **kwargs):
        pass