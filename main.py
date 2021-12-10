import json
from FHIRGroupR5 import GroupR5, CharacteristicCombinationR5, GroupCharacteristicR5, CodeableConcept, Coding, Quantity
from flask import Flask, request
from flask import jsonify


def translate_comparator(comparator):
    comparator_translation = {"eq": None,
                              "lt": "<",
                              "le": "<=",
                              "ge": ">=",
                              "gt": ">"}
    return comparator_translation[comparator]


def translate_term_code_to_coding(term_code):
    for code in term_code:
        coding = Coding()
        coding.code = code["code"]
        coding.system = code["system"]
        coding.display = code["display"]
        return coding


def translate_value(value_filter):
    if value_filter["type"] == "quantity-comparator":
        value_quantity = Quantity()
        value_quantity.value = value_filter["value"]
        value_quantity.comparator = translate_comparator(value_filter["comparator"])
        value_quantity.unit = value_filter["unit"]["code"]
        value_quantity.system = "http://unitsofmeasure.org"
        return value_quantity
    elif value_filter["type"] == "concept":
        value_concept = CodeableConcept()
        # TODO: Currently we would need a seperate critiera!
        for selectedConcept in value_filter["selectedConcepts"]:
            coding = Coding()
            coding.code = selectedConcept["code"]
            coding.system = selectedConcept["system"]
            coding.display = selectedConcept["display"]
            value_concept.coding.append(coding)
        return value_concept


def create_inclusion_group(inclusion_criteria):
    and_group = GroupR5()
    and_group.name = "inclusionCriteriaAnd"
    and_group.characteristicCombination = CharacteristicCombinationR5("all-of")
    for inclusion_criterion in inclusion_criteria:
        if len(inclusion_criterion) == 1:
            characteristic = GroupCharacteristicR5()
            concept = CodeableConcept()
            concept.coding = [translate_term_code_to_coding(inclusion_criterion[0]["termCodes"])]
            characteristic.code = concept
            if "valueFilter" in inclusion_criterion[0]:
                characteristic.value = translate_value(inclusion_criterion[0]["valueFilter"])
            and_group.characteristics.append(characteristic)
        else:
            characteristic = GroupCharacteristicR5()
            concept = CodeableConcept()
            concept.text = "Group"
            characteristic.code = concept
            subgroup = create_or_group(inclusion_criterion)
            characteristic.value = subgroup
            and_group.characteristics.append(characteristic)
    return and_group


def create_exclusion_group(exclusion_criteria):
    or_group = GroupR5()
    or_group.name = "exclusionCriteriaOr"
    or_group.characteristicCombination = CharacteristicCombinationR5("any-of")
    for exclusion_criterion in exclusion_criteria:
        if (len(exclusion_criterion)) == 1:
            characteristic = GroupCharacteristicR5()
            concept = CodeableConcept()
            concept.coding = [translate_term_code_to_coding(exclusion_criterion[0]["termCodes"])]
            characteristic.code = concept
            if "valueFilter" in exclusion_criterion[0]:
                characteristic.value = translate_value(exclusion_criterion[0]["valueFilter"])
            or_group.characteristics.append(characteristic)
        else:
            characteristic = GroupCharacteristicR5()
            concept = CodeableConcept()
            concept.text = "Group"
            characteristic.code = concept
            subgroup = create_and_group(exclusion_criterion)
            characteristic.value = subgroup
            or_group.characteristics.append(characteristic)
    return or_group


def create_or_group(inclusion_criteria_sub_group):
    or_group = GroupR5()
    or_group.name = "OrGroup"
    or_group.characteristicCombination = CharacteristicCombinationR5("any-of")
    for criteria in inclusion_criteria_sub_group:
        characteristic = GroupCharacteristicR5()
        concept = CodeableConcept()
        concept.coding = [translate_term_code_to_coding(criteria["termCodes"])]
        characteristic.code = concept
        if "valueFilter" in criteria:
            characteristic.value = translate_value(criteria["valueFilter"])
        or_group.characteristics.append(characteristic)
    return or_group


def create_and_group(inclusion_criteria_sub_group):
    and_group = GroupR5()
    and_group.name = "OrGroup"
    and_group.characteristicCombination = CharacteristicCombinationR5("all-of")
    for criteria in inclusion_criteria_sub_group:
        characteristic = GroupCharacteristicR5()
        concept = CodeableConcept()
        concept.coding = [translate_term_code_to_coding(criteria["termCodes"])]
        characteristic.code = concept
        if "valueFilter" in criteria:
            characteristic.value = translate_value(criteria["valueFilter"])
        and_group.characteristics.append(characteristic)
    return and_group


def translate_sq_to_group_r5(structured_query_json):
    structured_query = json.loads(structured_query_json)

    sq_group = GroupR5()
    sq_group.name = "Query"
    sq_group.characteristicCombination = CharacteristicCombinationR5("all-of")
    inclusion_characteristic = GroupCharacteristicR5()
    concept = CodeableConcept()
    concept.text = "Group"
    inclusion_characteristic.code = concept
    inclusion_group = create_inclusion_group(structured_query["inclusionCriteria"])
    inclusion_characteristic.value = inclusion_group
    sq_group.characteristics.append(inclusion_characteristic)

    if "exclusionCriteria" in structured_query:
        exclusion_characteristic = GroupCharacteristicR5()
        concept = CodeableConcept()
        concept.text = "Group"
        exclusion_characteristic.code = concept
        exclusion_group = create_exclusion_group(structured_query["exclusionCriteria"])
        exclusion_characteristic.value = exclusion_group
        exclusion_characteristic.exclude = True
        sq_group.characteristics.append(exclusion_characteristic)
    return sq_group


api = Flask(__name__)


@api.route("/query-sync", methods=["POST"])
def parse_query():
    query_input: str = request.data.decode("iso-8859-1")
    print(query_input)
    result = {'answer': 42}
    return jsonify(result)


@api.route("/query-translate", methods=["POST"])
def parse_translate():
    query_input: str = request.data.decode("iso-8859-1")
    print(query_input)
    print(translate_sq_to_group_r5(query_input).to_json())
    result = {'answer': 42}
    return jsonify(result)


if __name__ == '__main__':
    api.run(threaded=True)  # with open("1-age.json", 'r') as sq:
    #     print(translate_sq_to_group_r5(sq).to_json())
