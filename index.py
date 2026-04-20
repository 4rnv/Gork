from typing import Literal, NotRequired, Any, TypedDict, get_args, get_origin

class GorkSchema:
    def __init__(self, schema) -> None:
        self.schema = schema

class GorkError(Exception):
    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)

class GorkResponse(TypedDict):
    error : NotRequired[str]
    is_valid : bool

def is_this_true(response : Any, schema : GorkSchema):
    '''
    Validates response against provided schema.
    '''
    result : GorkResponse = {
        'is_valid': True, 
        'error': ''
    }
    for field, options in schema.schema.items():
        expected_type = options.get('type')
        if field not in response:
            result['is_valid'] = False
            result['error'] += f'Field {field} missing\n'
            continue
        value = response[field]
        if not _type_matches(value, expected_type):
            result['is_valid'] = False
            result['error'] += f'Type {type(value)} does not match {expected_type} in field {field}\n'
            continue
        if 'min' in options or 'max' in options:
            range_is_valid, range_error = _check_range(value, options, field)
            if not range_is_valid:
                result['is_valid'] = range_is_valid
                result['error'] += range_error + "\n"
            else:
                print(f'Field {field} passed all checks for value "{value}"')
        else:
            print(f'Field {field} passed all checks for value "{value}"')
    print(result['error'])
    # if result['error']:
    #     raise GorkError(f"Validation Failed:\n{result['error']}")
    return result

def validate(response : Any, schema : GorkSchema):
    '''
    Wrapper function for is_this_true() with a readable, sensible name. Works the same.
    '''
    return is_this_true(response, schema)

def _type_matches(value: Any, expected: Any) -> bool:
    '''
    Simple type checking that also handles Literal and basic generics.
    '''
    origin = get_origin(expected)

    if origin is Literal:
        return value in get_args(expected)

    if origin is not None:
        return isinstance(value, origin)

    if expected is str:
        return isinstance(value, str)
    if expected is int:
        return isinstance(value, int)
    if expected is float:
        return isinstance(value, (int, float))
    if expected is bool:
        return isinstance(value, bool)

    return isinstance(value, expected) if isinstance(expected, type) else True

def _check_range(value : int | float, options: dict, field : str):
    if isinstance(value, (int, float)):
        if 'min' in options and value < options['min']:
            return False, f'Value {value} < min {options['min']} for field {field}'
        if 'max' in options and value > options['max']:
            return False, f'Value {value} > max {options['max']} for field {field}'
    return True, ''
    