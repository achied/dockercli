from __future__ import unicode_literals

import pytest
from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from dockercli.options import all_options
from dockercli.options import COMMAND_NAMES


@pytest.fixture
def completer():
    import dockercli.completer as cmp
    return cmp.DockerCompleter()


@pytest.fixture
def complete_event():
    from mock import Mock
    return Mock()

cs1 = ['newton', 'tesla', 'einstein', 'edison']
rs1 = ['einstein', 'edison']
im1 = ['ubuntu', 'hello-world', 'postgres', 'nginx']

cs2 = ['desperate_hodgkin', 'desperate_torvalds', 'silly_fermat', 'some-percona']


def test_empty_string_completion(completer, complete_event):
    """
    In the beginning of the line, all available commands are suggested.
    """
    text = ''
    position = 0
    result = set(completer.get_completions(
        Document(text=text, cursor_position=position),
        complete_event))
    assert result == set(map(Completion, COMMAND_NAMES))


def test_build_path_completion_absolute(completer, complete_event):
    """
    Suggest build paths from filesystem root.
    """
    command = 'build /'

    position = len(command)

    result = set(completer.get_completions(
        Document(text=command, cursor_position=position),
        complete_event))

    expected = ['etc', 'home', 'tmp', 'usr', 'var']

    expected = set(map(lambda t: Completion(t, 0), expected))

    assert expected.issubset(result)


@pytest.mark.skipif(True, reason='User path specific.')
def test_build_path_completion_user(completer, complete_event):
    """
    Suggest build paths from user home directory.
    """
    command = 'build ~'

    position = len(command)

    result = set(completer.get_completions(
        Document(text=command, cursor_position=position),
        complete_event))

    expected = ['~/Documents', '~/Downloads']

    expected = set(map(lambda t: Completion(t, -1), expected))

    assert expected.issubset(result)


@pytest.mark.skipif(True, reason='User path specific.')
def test_build_path_completion_user_dir(completer, complete_event):
    """
    Suggest build paths from user home directory.
    """
    command = 'build ~/s'

    position = len(command)

    result = set(completer.get_completions(
        Document(text=command, cursor_position=position),
        complete_event))

    expected = ['src']

    expected = set(map(lambda t: Completion(t, -1), expected))

    assert expected.issubset(result)


@pytest.mark.parametrize("command, expected", [
    ("h", ['help']),
    ("he", ['help']),
    ("hel", ['help']),
    ("help", ['help']),
    ('run -d ubuntu:14.04 /bin/sh -c "w', [])  # not complete in quoted string
])
def test_command_completion(command, expected):
    """
    Test command suggestions.
    :param command: string: text that user started typing
    :param expected: list: expected completions
    """
    c = completer()
    e = complete_event()

    position = len(command)
    result = set(c.get_completions(
        Document(text=command, cursor_position=position),
        e))

    expected = set(map(lambda t: Completion(t, -len(command)), expected))

    assert result == expected


@pytest.mark.parametrize("command, expected", [
    ("h", ['help', 'shell', 'push', 'attach', 'search', 'refresh']),
    ("he", ['help', 'shell']),
    ("hel", ['help', 'shell']),
    ("help", ['help']),
    ('run -d ubuntu:14.04 /bin/sh -c "w', [])  # not complete in quoted string
])
def test_command_completion_fuzzy(command, expected):
    """
    Test command suggestions.
    :param command: string: text that user started typing
    :param expected: list: expected completions
    """
    c = completer()
    e = complete_event()
    c.set_fuzzy_match(True)

    position = len(command)
    result = list(c.get_completions(
        Document(text=command, cursor_position=position),
        e))

    expected = list(map(lambda t: Completion(t, -len(command)), expected))

    assert result == expected


pso = list(filter(lambda x: x.name.startswith('-'), all_options('ps')))


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("ps ", pso, 0),
    ("ps --", list(filter(
        lambda x: x.long_name and x.long_name.startswith('--'), pso)), -2),
    ("ps --h", list(filter(
        lambda x: x.long_name and x.long_name.startswith('--h'), pso)), -3),
    ("ps --all ", list(filter(
        lambda x: x.long_name not in ['--all'], pso)), 0),
    ("ps --all --quiet ", list(filter(
        lambda x: x.long_name not in ['--all', '--quiet'], pso)), 0),
])
def test_options_completion_long(command, expected, expected_pos):
    """
    Test command options suggestions.
    :param command: string: text that user started typing
    :param expected: list: expected completions
    """
    c = completer()
    e = complete_event()

    position = len(command)

    result = set(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected = set(map(lambda t: Completion(
        t.get_name(is_long=True), expected_pos, t.display), expected))

    assert result == expected


def option_map(cmd, is_long):
    return {
        x.get_name(is_long): x.display for x in all_options(cmd) if x.name.startswith('-')
    }

psm = option_map('ps', True)


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("ps ", sorted(psm.keys()), 0),
    ("ps h", ['--help'], -1),
    ("ps i", ['--since', '--size', '--quiet'], -1),
    ("ps ze", ['--size'], -2),
])
def test_options_completion_long_fuzzy(command, expected, expected_pos):
    """
    Test command options suggestions.
    :param command: string: text that user started typing
    :param expected: list: expected completions
    """
    c = completer()
    e = complete_event()
    c.set_fuzzy_match(True)

    position = len(command)

    result = list(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected = list(map(lambda t: Completion(
        t, expected_pos, psm[t]), expected))

    assert result == expected


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("ps ", pso, 0),
    ("ps -", filter(
        lambda x: x.name.startswith('-'), pso), -1),
    ("ps -h", filter(
        lambda x: x.short_name and x.short_name.startswith('-h'), pso), -2),
])
def test_options_completion_short(command, expected, expected_pos):
    """
    Test command options suggestions.
    :param command: string: text that user started typing
    :param expected: list: expected completions
    """
    c = completer()
    e = complete_event()
    c.set_long_options(False)

    position = len(command)

    result = set(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected = set(map(lambda t: Completion(
        t.get_name(
            is_long=c.get_long_options()), expected_pos, t.display), expected))

    assert result == expected


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("ps --before ", cs1, 0),
    ("ps --before e", filter(lambda x: x.startswith('e'), cs1), -1),
    ("ps --before ei", filter(lambda x: x.startswith('ei'), cs1), -2),
])
def test_options_container_completion(command, expected, expected_pos):
    """
    Suggest container names in relevant options (ps --before)
    """
    c = completer()
    e = complete_event()

    c.set_containers(cs1)

    position = len(command)

    result = set(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected = set(map(lambda t: Completion(t, expected_pos), expected))

    assert result == expected


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("top ", list(map(
        lambda x: (x, x), rs1)) + [('--help', '-h/--help')], 0),
    ("top e", map(
        lambda x: (x, x), filter(lambda x: x.startswith('e'), rs1)), -1),
])
def test_options_container_running_completion(command, expected, expected_pos):
    """
    Suggest running container names (top [container])
    """
    c = completer()
    e = complete_event()

    c.set_containers(cs1)
    c.set_running(rs1)

    position = len(command)

    result = set(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected_completions = set()
    for text, display in expected:
        if display:
            expected_completions.add(Completion(text, expected_pos, display))
        else:
            expected_completions.add(Completion(text, expected_pos))

    assert result == expected_completions


@pytest.mark.parametrize("command, expected, expected_pos", [
    ("rm ", ['--all-stopped', ('--help', '-h/--help')] + cs2, 0),
    ("rm spe", ['--all-stopped', 'desperate_hodgkin', 'desperate_torvalds', 'some-percona'], -3),
])
def test_options_container_completion_fuzzy(command, expected, expected_pos):
    """
    Suggest running container names (top [container])
    """
    c = completer()
    e = complete_event()

    c.set_containers(cs2)

    c.set_fuzzy_match(True)

    position = len(command)

    result = list(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected_completions = []
    for x in expected:
        if isinstance(x, tuple):
            expected_completions.append(Completion(x[0], expected_pos, x[1]))
        else:
            expected_completions.append(Completion(x, expected_pos))

    assert result == expected_completions


def test_options_image_completion(completer, complete_event):
    """
    Suggest image names in relevant options (images --filter)
    """
    command = 'images --filter '
    expected = ['ubuntu', 'hello-world', 'postgres', 'nginx']
    expected_pos = 0

    completer.set_images(expected)
    position = len(command)

    result = set(completer.get_completions(
        Document(text=command, cursor_position=position), complete_event))

    expected = set(map(lambda t: Completion(t, expected_pos), expected))

    assert result == expected


@pytest.mark.parametrize("command, expected, expected_pos", [
    ('images --filter ', ['hello-world', 'nginx', 'postgres', 'ubuntu'], 0),
    ('images --filter n', ['nginx', 'ubuntu'], -1),
    ('images --filter g', ['nginx', 'postgres'], -1),
    ('images --filter u', ['ubuntu'], -1),
])
def test_options_image_completion_fuzzy(command, expected, expected_pos):
    """
    Suggest image names in relevant options (images --filter)
    """
    c = completer()
    e = complete_event()

    c.set_images(im1)

    c.set_fuzzy_match(True)

    position = len(command)

    result = list(c.get_completions(
        Document(text=command, cursor_position=position), e))

    expected = list(map(lambda t: Completion(t, expected_pos), expected))

    assert result == expected
