from fhir.resources.identifier import Identifier
from fhir.resources.reference import Reference
from fhir.resources.range import Range
from fhir.resources.period import Period
from typing import Union
import json

from StructuredQuery import del_none, del_keys


class GroupR5(object):
    DO_NOT_SERIALIZE = ["DO_NOT_SERIALIZE"]

    def __init__(self):
        self.resourceType = "Group"
        self.identifier: IdentifierList = None
        self.active: bool = True
        self.type: str = "person"
        self.actual: bool = False
        self.code: CodeableConcept = None
        self.name: str = ""
        self.quantity: int = None
        self.managingEntity: Reference = None
        self.characteristics: GroupR5Characteristics = []
        self.member = None
        self.characteristicCombination: CharacteristicCombinationR5 = None

    def to_json(self):
        return json.dumps(self, default=lambda o: del_none(
            del_keys(o.__dict__, self.DO_NOT_SERIALIZE)),
                          sort_keys=True, indent=4)


class CodeableConcept:
    def __init__(self):
        self.coding = []
        self.text = None


class Coding:
    def __init__(self):
        self.code = None
        self.system = None
        self.version = None
        self.display = None


class Quantity:
    def __init__(self):
        self.unit = None
        self.system = None
        self.value = None
        self.comparator = None


class GroupCharacteristicR5:
    def __init__(self):
        self.code: CodeableConcept = None
        self.value: CharacteristicValue = None
        self.exclude: bool = False
        self.period: Period = None


class CharacteristicCombinationR5:
    def __init__(self, code):
        self.code: str = code
        self.threshold: int = None


GroupR5Characteristics = list[GroupCharacteristicR5]
IdentifierList = list[Identifier]
CharacteristicValue = Union[CodeableConcept, bool, Quantity, Range, GroupR5]
