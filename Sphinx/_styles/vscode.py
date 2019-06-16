# -*- coding: utf-8 -*-
"""
    pygments.styles.vscode
    ~~~~~~~~~~~~~~~~~~~~~~~

    Style similar to the style used in VS Code Dark theme.
"""

from pygments.style import Style
from pygments.token import Token, Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Whitespace


class VscodeStyle(Style):
    """
    Style similar to the style used in VS Code Dark theme.
    """

    background_color = '#1e1e1e'
    default_style = ''

    styles = {
        Token:                  '#d4d4d4',# text
        Whitespace:             '#bbbbbb',
        Comment:                '#6A9955',
        Comment.Preproc:        '#1e889b',
        Comment.Special:        '#8B008B bold',

        String:                 '#ce9178',
        String.Heredoc:         '#1c7e71 italic',
        String.Regex:           '#646695',
        String.Other:           '#cb6c20',

        #Number:                 '#B452CD',

        #Operator.Word:          '#d4d4d4',

        Keyword:                '#569cd6 bold',# import, for, etc.
        Keyword.Namespace:      '#c586c0 bold',# import, for, etc.
        Keyword.Type:           '#00688B',

        Name:                   '#d4d4d4',
        Name.Class:             '#4EC9B0',
        #Name.Other:             '#4EC9B0 bold',
        #Name.Property:          '#4EC9B0 bold',
        #Name.Variable.Instance: '#4EC9B0 bold',
        #Name.Variable.Class:    '#4EC9B0 bold',
        #Name.Entity:            '#4EC9B0 bold',
        
        Name.Exception:         '#008b45 bold',
        Name.Function:          '#d7ba7d',
        #Name.Namespace:         '#d4d4d4',# imported namespace
        Name.Variable:          '#00688B',
        Name.Constant:          '#00688B',
        Name.Decorator:         '#d7ba7d',
        Name.Tag:               '#8B008B bold',
        Name.Attribute:         '#d4d4d4',
        Name.Builtin:           '#4EC9B0',
        Name.Builtin.Pseudo:    '#569cd6',

        Generic.Heading:        'bold #000080',
        Generic.Subheading:     'bold #800080',
        Generic.Deleted:        '#aa0000',
        Generic.Inserted:       '#00aa00',
        Generic.Error:          '#aa0000',
        Generic.Emph:           'italic',
        Generic.Strong:         'bold',
        Generic.Prompt:         '#555555',
        Generic.Output:         '#888888',
        Generic.Traceback:      '#aa0000',

        Error:                  'bg:#e3d2d2 #a61717'
    }
