#!/usr/bin/env python
"""Tests for `murkrow` package."""

from murkrow import assistant, human, narrate, system, user


def test_messaging():
    """Test the messaging helpers for OpenAI role-based chat."""
    assert assistant('hello') == {'role': 'assistant', 'message': 'hello'}
    assert human('hello') == {'role': 'user', 'message': 'hello'}
    assert narrate('hello') == {'role': 'system', 'message': 'hello'}
    assert system('hello') == {'role': 'system', 'message': 'hello'}
    assert user('hello') == {'role': 'user', 'message': 'hello'}
