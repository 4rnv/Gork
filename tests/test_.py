# import pytest
import index as gork
from typing import Literal

schema = gork.GorkSchema({
    'answer': {"type": str},
    'confidence': {"type": float, "min": 0, "max": 1},
    'subject': {"type": Literal['physics','chemistry','mathematics']},
    'id': {"type": int}
})


def test_valid_input():
    response = {
        'answer': 'Correct answer',
        'confidence': 0.87,
        'subject': 'physics',
        'id': 42
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is True


def test_missing_field():
    response = {
        'answer': 'Missing id',
        'confidence': 0.5,
        'subject': 'physics'
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False
    assert 'id' in result['error']


def test_wrong_type():
    response = {
        'answer': 'Wrong type',
        'confidence': 0.5,
        'subject': 'physics',
        'id': "not_an_int"
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False
    assert 'int' in result['error']


def test_range_violation():
    response = {
        'answer': 'Out of range',
        'confidence': 5.0,
        'subject': 'chemistry',
        'id': 1
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False
    assert 'range' in result['error'] or '>' in result['error']


def test_literal_invalid():
    response = {
        'answer': 'Invalid subject',
        'confidence': 0.5,
        'subject': 'biology',
        'id': 1
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False
    assert 'Literal' in result['error'] or 'does not match' in result['error']


def test_multiple_errors():
    response = {
        'answer': 123,                 # wrong type
        'confidence': -10,            # range violation
        'subject': 'invalid',         # literal fail
        'id': "wrong"                 # wrong type
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False

    # ensure multiple errors are reported
    error = result['error']
    assert 'answer' in error
    assert 'confidence' in error
    assert 'subject' in error
    assert 'id' in error


def test_boundary_values():
    response = {
        'answer': 'Edge case',
        'confidence': 0,
        'subject': 'mathematics',
        'id': 0
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is True

    response['confidence'] = 1
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is True


def test_extra_fields_ignored():
    response = {
        'answer': 'Extra field present',
        'confidence': 0.5,
        'subject': 'physics',
        'id': 10,
        'extra': 'ignored'
    }
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is True


def test_empty_response():
    response = {}
    result = gork.is_this_true(response, schema)
    assert result['is_valid'] is False
    assert 'missing' in result['error'].lower()