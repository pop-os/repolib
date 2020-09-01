#!/usr/bin/python3

"""
Copyright (c) 2020, Ian Santopietro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Module for adding repos to the system in CLI applications.
"""

import os
import sys

from ..deb import DebLine
from ..legacy_deb import LegacyDebSource
from ..ppa import PPALine

def add(log, args, parser):
    """ Add subcommand. 
    
    The add command is used for adding new software sources to the system. It
    requires root. 

    Options:
        --disable, -d
        --source-code, -s
        --expand, -e
    """

    if os.geteuid() != 0:
        parser.print_usage()
        log.error('You need to root, or use sudo.')
        sys.exit(1)

    verbose = False
    if args.debug > 1:
        verbose = True
    
    expand = args.expand

    debline = ' '.join(args.deb_line)
    if args.deb_line == '822styledeb':
        parser.print_usage()
        log.error('A repository is required.')
        sys.exit(1)
    
    if debline.startswith('http'):
        debline = f'deb {debline}'

    new_source = LegacyDebSource()
    if debline.startswith('ppa:'):
        add_source = PPALine(debline, verbose=verbose)
    
    elif debline.startswith('deb'):
        expand = False
        add_source = DebLine(debline)
    
    else:
        log.critical(
            'The line "%s" is malformed. Double-check the spelling.',
            debline
        )
        sys.exit(1)
    
    new_source.sources.append(add_source)

    if not debline.startswith('deb-src'):
        src_source = add_source.copy()
        src_source.enabled = False
    else:
        src_source = add_source
    
    if args.source_code:
        src_source.enabled = True

    if not debline.startswith('deb-src'):
        new_source.sources.append(src_source)

    new_source.sources[0].enabled = True
    
    if args.disable:
        for repo in new_source.sources:
            repo.enabled = False
    
    new_source.make_names()
    
    if args.debug > 0:
        log.info('Debug mode set, not saving.')
        for src in new_source.sources:
            print(f'{src.dump()}\n')
        log.info('Filename to save: %s', new_source.filename)
        print(f'{new_source.make_deblines()}')
        
    
    if expand:
        print(new_source.sources[0].make_source_string())
        print(f'{add_source.ppa_info["description"]}\n')
        print('Press [ENTER] to contine or Ctrl + C to cancel.')
        input()
    
    if args.debug == 0:
        new_source.save_to_disk()
    else:
        sys.exit(2)