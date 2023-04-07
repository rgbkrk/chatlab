#!/usr/bin/env python
"""Tests for `murkrow` package."""

from murkrow import assistant, human, narrate, system, user, ai


def test_messaging():
    """Test the messaging helpers for OpenAI role-based chat."""
    assert assistant('hello') == {'role': 'assistant', 'content': 'hello'}
    assert human('hello') == {'role': 'user', 'content': 'hello'}
    assert narrate('hello') == {'role': 'system', 'content': 'hello'}
    assert system('hello') == {'role': 'system', 'content': 'hello'}
    assert user('hello') == {'role': 'user', 'content': 'hello'}
    assert ai('hello') == {'role': 'assistant', 'content': 'hello'}
