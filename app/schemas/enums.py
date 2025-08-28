from enum import Enum


class RegistrationType(str, Enum):
    INDIVIDUAL = 'individual'
    GROUP = 'group'


class TransportationMode(str, Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


class Gender(str, Enum):
    MALE = 'M'
    FEMALE = 'F'


class RegistrationStatus(str, Enum):
    REGISTERED = 'registered'
    WAITING = 'waiting'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'


class ToiletPreference(str, Enum):
    INDIAN = 'indian'
    WESTERN = 'western'


class ToiletFacilities(str, Enum):
    INDIAN = 'indian'
    WESTERN = 'western'
    BOTH = 'both'


class GenderPreference(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    BOTH = 'both'


class UserType(str, Enum):
    ORGANISER = 'organiser'
    ADMIN = 'admin'
