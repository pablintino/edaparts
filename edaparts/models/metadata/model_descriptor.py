class FieldModelDescriptor:
    def __init__(self, name, is_mandatory, is_pk, data_type):
        self.name = name
        self.is_mandatory = is_mandatory
        self.is_pk = is_pk
        self.data_type = data_type

    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )


class ModelDescriptor:

    def __init__(self, model_name):
        self.model_name = model_name
        self.fields = {}

    def add_field(self, name, is_mandatory, is_pk, data_type):
        if name not in self.fields:
            self.fields[name] = FieldModelDescriptor(
                name, is_mandatory, is_pk, data_type
            )

    def get_field(self, name):
        return self.fields.get(name, None)

    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )
