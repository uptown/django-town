class ValidationError(Exception):
    def __init__(self, field_name, error_message):
        self.field_name = field_name
        self.error_message = error_message