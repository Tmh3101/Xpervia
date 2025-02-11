from enum import Enum

class RoleEnum(Enum):
    ADMIN = ('admin', 'Administrator with full access')
    TEACHER = ('teacher', 'Teacher with access to course management')
    STUDENT = ('student', 'Student with access to enrolled courses')

    def __init__(self, name, description):
        self._value_ = name
        self.description = description

    @property
    def name(self):
        return self._value_