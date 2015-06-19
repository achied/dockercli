# -*- coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function

from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys


def get_key_manager(set_long_options, get_long_options):
    """
    Create and initialize keybinding manager
    :return: KeyBindingManager
    """

    assert callable(set_long_options)
    assert callable(get_long_options)

    manager = KeyBindingManager()

    @manager.registry.add_binding(Keys.F2)
    def _(event):
        """
        When F2 has been pressed, fill in the "help" command.
        """
        event.cli.current_buffer.insert_text("help")

    @manager.registry.add_binding(Keys.F3)
    def _(_):
        """
        Enable/Disable long option name suggestion.
        """
        set_long_options(not get_long_options())

    @manager.registry.add_binding(Keys.F10)
    def _(event):
        """
        When F10 has been pressed, quit.
        """
        # Unused parameters for linter.
        _ = event
        raise EOFError

    @manager.registry.add_binding(Keys.ControlSpace)
    def _(event):
        """
        Initialize autocompletion at cursor.

        If the autocompletion menu is not showing, display it with the
        appropriate completions for the context.

        If the menu is showing, select the next completion.
        """
        b = event.cli.current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            event.cli.start_completion(select_first=False)

    return manager