#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 16th February, 2017:

File containing all useful functions for the different executables.

@author: Benjamin Yvernault, Electrical Engineering, Vanderbilt University
'''

import logging
import os
import sys

from dax.errors import XnatToolsError, XnatToolsUserError


LENGTH = 64
DISPLAY_TEMPLATE = """#######################################################\
#########
{name}
#                                                              #
# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
# If issues, please start a thread here:                       #
# https://groups.google.com/forum/#!forum/vuiis-cci            #
# Usage:                                                       #
{description}
# Examples:                                                    #
#     Check the help for examples by running --help            #
################################################################
"""
ARGS_DISPLAY = """Arguments:
{args}"""


def parse_args(name, description, add_tools_arguments, purpose):
    """
    Method to parse arguments base on argparse

    :param name: name of the script
    :return: parser object
    """
    from argparse import ArgumentParser, RawTextHelpFormatter
    parser = ArgumentParser(prog=name, description=description,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--host', dest='host', default=None,
                        help='Host for XNAT. Default: env XNAT_HOST.')
    parser.add_argument('-u', '--username', dest='username', default=None,
                        help='Username for XNAT.')
    parser = add_tools_arguments(parser)
    main_display(name, purpose)
    args = parser.parse_args()
    args_display(args)
    return args


def main_display(name, description):
    """
    Main display of the executables before any process

    :param name: name of the executable
    :param description: description to display
    :return: None
    """
    _spaces = (LENGTH - len(name))/2
    _name = edit_string_size(name, left_spaces=_spaces)
    _desc = edit_string_size(description, left_spaces=4)
    print DISPLAY_TEMPLATE.format(name=_name, description=_desc)
    print_separators(symbol='-')


def args_display(args):
    """
    Display arguments set by user

    :param args: arguments from parse_args
    :param description: description to display
    :return: None
    """
    _args = list()
    for key, value in vars(args).items():
        _format = '    %*s -> %*s'
        if isinstance(value, bool):
            if value:
                _args.append(_format % (-15, key.replace('_', ' '), -45, 'on'))
        else:
            if value:
                _args.append(_format % (-15, key.replace('_', ' '),
                                        -45, get_proper_str(value, True)))

    print ARGS_DISPLAY.format(args='\n'.join(_args))
    print_separators(symbol='-')


def run_tool(script, description, add_tools_arguments, purpose, run_tool_fct,
             check_arguments=None, extra_display=False):
    """
    Main function to run for all xnat tools.
    Set args/display and run core function (run_tool_fct)
    See tools for example.

    :param script: name of script
    :param add_tools_arguments: fct adding arguments to parser
    :param display: dictionary coding display
    :param run_tool_fct: core fct for the tool
    :param extra_display: extra display after checking args
    :return: None
    """
    args = parse_args(script, description, add_tools_arguments, purpose)

    if extra_display:
        print extra_display

    run = True
    if check_arguments:
        run = check_arguments(script, args)

    if run:
        run_tool_fct(args)


def setup_info_logger(name, log_file=None):
    """
    Using logger for the executables output.
     Setting the information for the logger.

    :param name: Name of the logger
    :param log_file: log file path to write outputs
    :return: logging object
    """
    if log_file:
        handler = logging.FileHandler(log_file, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def edit_string_size(strings, max_length=LENGTH-4, left_spaces=0,
                     sformat='# %s%s #', symbol=' '):
    """
    Edit the string to by adding spaces at the beginning and end.
    If string is a list, return list of strings edited.

    :param string: string to edit or list of strings
    :param length: length of the string
    :return: new string of length 60
    """
    if isinstance(strings, str):
        _lspaces = symbol * left_spaces
        if symbol != ' ':
            _lspaces = '%s ' % _lspaces[:-1]
        _str = '%s%s' % (_lspaces, strings)
        _space = (max_length - len(_str))
        return sformat % (_str, symbol * _space)
    elif isinstance(strings, list):
        # Separate the string in several
        new_strings = list()
        for string in strings:
            _str = edit_string_size(string, max_length, left_spaces)
            new_strings.append(_str)
        return '\n'.join(new_strings)
    else:
        err = "Wrong type for 'strings' argument in edit_string_size. Required\
 <type 'str'> or <type 'list'>, found: %s"
        raise XnatToolsError(err % type(string))


def read_txt(txt_file, exe_name=''):
    """
    Method to read the txt file path with per line, the name
     of the variable on REDCap you want to extract

    :param txt_file: filepath
    :return: list of REDCap variables
    """
    if txt_file:
        print 'INFO: Export data from text file %s ...' % txt_file
        obj_list = list()
        if not os.path.exists(txt_file):
            err = 'file %s does not exist.'
            raise XnatToolsUserError(exe_name, err % txt_file)
        else:
            with open(txt_file, 'r') as input_file:
                for line in input_file:
                    obj_list.append(line.strip().split('\n')[0])
    else:
        obj_list = None
    return obj_list


def write_csv(csv_string, csv_file, exe_name=''):
    """
    Method to write the report as a csv file
     with the values from REDCap

    :param csv_string: data to write in the csv
    :param csv_file: csv filepath
    :param exe_name: name of executable running the function for error
    :return: None
    """
    print 'INFO: Writing report ...'
    basedir = os.path.basedir(csv_file)
    if not os.path.exists(basedir):
        err = 'Path %s not found for report. Give an existing parent folder.'
        raise XnatToolsUserError(exe_name, err % csv_file)
    with open(csv_file, 'w') as output_file:
        for line in csv_string:
            output_file.write(line)


def get_option_list(string):
    """
    Method to switch the string of value separated by a comma into a list.
     If the value is 'all', keep all.

    :param string: string to change
    :return: None if not set, all if all, list of value otherwise
    """
    if not string:
        return None
    elif string == 'all':
        return 'all'
    elif string == 'nan':
        return None
    else:
        return string.split(',')


def get_proper_str(str_option, end=False):
    """
    Method to shorten a string into the proper size for display

    :param str_option: string to shorten
    :param end: keep the end of the string visible (default beginning)
    :return: shortened string
    """
    if len(str_option) > 45:
        if end:
            return '...%s' % str_option[-42:]
        else:
            return '%s...' % str_option[:42]
    else:
        return str_option


def prompt_user_yes_no(question):
    """Prompt the user for a question with answer Y/N.

    :return: True if yes, False if no, ask again if any other answer
    """
    value = ''
    while value.lower() not in ['yes', 'no', 'n', 'y']:
        value = raw_input("%s [yes/no] " % question)
    if value.lower() in ['yes', 'y']:
        return True
    else:
        return False


def print_separators(symbol='=', length=LENGTH):
    """
    Print line to separate: symbolx60

    :param symbol: symbol to print length time (60)
    """
    print '%s' % (symbol * length)


def print_end(name):
    """
    Last display when the tool script finish.
    """
    _spaces = (LENGTH-6 - len(name))/2
    print edit_string_size(name, max_length=LENGTH-6, left_spaces=_spaces,
                           sformat='%s DONE %s', symbol='=')
    print '\n'


def get_gender_from_label(gender):
    """
    Method to get the passed gender in XNAT format

    :param gender: gender selected
    :return: value accepted by xnat: 'female' or 'male'
    """
    if gender.lower() in ['female', 'f']:
        return 'female'
    elif gender.lower() in ['male', 'm']:
        return 'male'
    else:
        return 'unknown'


def get_handedness_from_label(handedness):
    """
    Method to get the passed handedness in XNAT format

    :param handedness: handedness selected
    :return: value accepted by xnat: 'right', 'left', or 'ambidextrous'
    """
    if handedness.lower() in ['right', 'r']:
        return 'right'
    elif handedness.lower() in ['left', 'l']:
        return 'left'
    elif handedness.lower() in ['ambidextrous', 'a']:
        return 'ambidextrous'
    else:
        return 'unknown'


def get_resources_list(object_dict, resources_list):
    """
    Method to get the list of resources labels

    :param object_dict: dictionary to describe XNAT object parameters
    :param resources_list: list of resources requested from the user
    :return: None if empty, 'all' if all selected, list otherwise
    """
    # Get list of resources' label
    if resources_list == 'all':
        res_list = object_dict['resources']
    else:
        res_list = resources_list
    return res_list


def display_item(project, subject=None, session=None):
    """
    Method to display the tree

    :param project: project ID on XNAT
    :param subject: subject label on XNAT
    :param session: session label on XNAT
    :return: None
    """
    print'Project: %s' % (project)
    if subject:
        print '  +Subject: %s' % (subject)
        if session:
            print '    *Session: %s' % (session)
