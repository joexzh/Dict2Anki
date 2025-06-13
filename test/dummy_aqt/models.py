from typing import Any, Union

NoteType = dict[str, Any]
FieldDict = dict[str, Any]
TemplateDict = dict[str, Union[str, int, None]]

class Model:
    def by_name(self, name: str):
        return NoteType()

    def new(self, *args, **kwargs) -> NoteType:
        return NoteType()

    def add_field(self, *args, **kwargs):
        pass

    def new_field(self, *args, **kwargs) -> FieldDict:
        return FieldDict()

    def update(self, *args, **kwargs):
        pass

    def new_template(self, name: str) -> TemplateDict:
        return TemplateDict()

    def addTemplate(self, *args, **kwargs):
        pass

    def remove(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        pass