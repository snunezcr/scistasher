# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from fuzzyfinder import fuzzyfinder
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from scistash.database.sqlitedb import SQLiteHandler
from scistash.database.memorydb import MemoryDBHandler
from scistash.entities.author import Author
from scistash.entities.article import Article
from scistash.entities.annotation import Annotation
import click
import uuid


class StashCompleter(Completer):
    def __init__(self):
        self.__vocabulary = ''

    def setvocab(self, vocabulary):
        self.__vocabulary = vocabulary

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, self.__vocabulary)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))


class ReplHandler:
    levels = {
        'stash': {
            'current': {
                'id': 'curr_id',                        # DONE
                'fetch': 'curr_fetch',                  # DONE
                'show': 'curr_show',                    # DONE
                'save': 'curr_save',                    # DONE
                'scratch': 'curr_scratch',              # DONE
                'edit': 'curr_edit',
                'annotate': 'curr_annot',
                'tag': {
                    'add': 'curr_tag_add',
                    'rem': 'curr_tag_rem',
                    'show': 'curr_tag_show'
                },
                'file': {
                    'add': 'curr_file_add',
                    'rem': 'curr_file_rem',
                    'show': 'curr_file_show',
                },
                'ref': {
                    'add': 'curr_att_rky_add',
                    'rem': 'curr_att_rky_rem',
                    'show': 'curr_att_rky_show'
                }
            },
            'pending': {
                'show': 'pend_show',                    # DONE
                'scratch' : 'pend_scratch',             # DONE
                'scratchall': 'pend_scratch_all',       # DONE
                'save': 'pend_save',                    # DONE
                'checkout': {
                    'author': 'pend_chko_auth',         # DONE
                    'article': 'pend_chko_art',         # DONE
                    'annotation': 'pend_chko_annot',    # DONE
                }
            },
            'authors': {
                'new': 'auth_new',                      # DONE
                'checkout': 'auth_checkout',
                'delete': 'auth_delete',
                'find': {
                    'uuid': 'auth_find_uuid',
                    'year': 'auth_find_year',
                    'fname': 'auth_find_fname',
                    'lname': 'auth_find_lname',
                    'title': 'auth_find_title'
                },
            },
            'articles': {
                'find': {
                    'refkey': 'art_find_refkey',
                    'fname': 'art_find_fname',
                    'lname': 'art_find_lname',
                    'year': 'art_find_year',
                    'title': 'art_find_title'
                },
                'new': 'art_new',
                'checkout': 'art_checkout',
                'delete': 'art_delete',
                'cite': {
                    'bibtex': 'art_cite_bibtex',
                    'apa': 'art_cite_apa'
                },
                'retract': 'art_retract'
            },
            'annotations': {
                'new': 'annot_new',
                'checkout': 'annot_checkout',
                'delete': 'annot_delete',
                'find': {
                    'annotkey': 'annot_find_annotkey',
                    'refkey': 'annot_find_refkey',
                    'fname': 'annot_find_fname',
                    'lname': 'annot_find_lname',
                    'year': 'annot_find_year',
                    'title': 'annot_find_title'
                },
            },
            'sdb': {
                'list': {
                    'authors': 'sdb_list_auths',        # DONE
                    'articles': 'sdb_list_arts',        # DONE
                    'annots': 'sdb_list_annots',        # DONE
                    'tags': 'sdb_list_tags',            # DONE
                    'files': 'sdb_list_files',          # DONE
                    'refs': 'sdb_list_refs'             # DONE
                },
                'stats': 'sdb_stats',
                'dump': {
                    'csv': 'sdb_dump_csv',
                    'sql': 'sdb_dump_sql',
                    'bibtex': 'sdb_dump_bibtex',
                    'apa': 'sdb_dump_apa'
                },
                'import': 'sdb_import'
            },
            'help': 'meta',
            'clear': 'meta',                        # DONE
            'end': 'meta',                          # DONE
            'top': 'meta',                          # DONE
            'quit': 'meta'                          # DONE
        }
    }

    def __init__(self, db, dryrun=False, create=True, memquota=0):
        click.echo(click.style('Scientific Reference Stasher', fg='green', bold=True))
        click.echo('Santiago Núñez-Corrales <nunezco2@illinois.edu>\n')
        click.echo('For available commands, enter \'help\' into the REPL.\n')
        # Database handlers
        self.__pending = MemoryDBHandler(memquota)
        self.__db = SQLiteHandler(db, dryrun, create)
        self.__createdb = create
        # Contextual and fetch hashes
        self.__fetchhash = self.__db.buildfetchhash()
        self.__cntxhash = self.__db.buildcontexthash()
        # Operation stack handler
        self.__opstack = ['stash']
        # Prompt handler
        self.__scomp = StashCompleter()
        self.__scomp.setvocab(self.levels.get('stash').keys())
        self.__currprompt = ''
        self.__current = None
    @property
    def db(self):
        return self.__db

    @property
    def current(self):
        return self.__current

    @current.setter
    def current(self, val):
        self.__pending.put(self.current, self.__fetchhash)
        self.__current = val

    def makeprompt(self):
        if len(self.__opstack) == 1:
            self.__currprompt = self.__opstack[0]
        elif len(self.__opstack) == 2:
            self.__currprompt = '{0}|{1}'.format(self.__opstack[0], self.__opstack[1])
        else:
            self.__currprompt = '|'.join(self.__opstack)

    def opstacktolevel(self):
        out = self.levels

        for i in self.__opstack:
            out = out.get(i)

        return out

    def run(self):
        while True:
            # Set the prompt based on the operation stack
            self.makeprompt()
            self.__scomp.setvocab(self.opstacktolevel())
            user_input = prompt(self.__currprompt + '> ',
                                history=FileHistory('history.stash'),
                                auto_suggest=AutoSuggestFromHistory(),
                                completer=self.__scomp)
            self.process_input(user_input.split())

    def process_input(self, user_input):
        if not user_input:
            return
        if user_input[0] == 'quit':
            # TODO: when changes are pending or database is open, ask user to resolve
            self.__db.close()
            click.echo(click.style('Exiting.', fg='magenta'))
            quit()
        elif user_input[0] == 'clear':
            click.clear()
        elif user_input[0] == 'top':
            self.__opstack = ['stash']
        elif user_input[0] == 'help':
            outtext = """
            \x1b[1m\x1b[32mScientific Reference Stasher\x1b[0m\x1b[0m
            \x1b[32mHelp Manual\x1b[0m
            
            
            \x1b[32mGeneral commands\x1b[0m
            
               \x1b[1mCommand\x1b[0m            \x1b[1mFunction\x1b[0m
                quit                Exit the interpreter
                clear               Clear the current screen
                curr                Display current data object under modification
                help                Display this help
                end                 Exit most immediate context (right-most in prompt)
                
            \x1b[32mAuthor\x1b[0m
            
               \x1b[1mCommand\x1b[0m            \x1b[1mFunction\x1b[0m
                list                List current authors
                new                 Add new author
                edit                Change information about an author
                find                Search an author
                save                Save information of the most recently updated author
            """
            click.echo_via_pager(outtext)
        elif user_input[0] == 'end':
            if len(self.__opstack) is 1:
                click.echo(click.style('Already at top level.', fg='magenta'))
            else:
                self.__opstack = self.__opstack[:-1]
        else:
            # Process each command depending on where the last runnable command stops
            def recursiveparse(level, cmdlist, context):
                # Case 1: the list has been exhausted with a non-executable command path
                if not cmdlist:
                    return context, 'none', [], level.keys()
                # Case 2: we have either a keyword that does not exhaust the terms or an unknown term
                elif len(cmdlist) == 1:
                    # Check if it is a valid command, i.e. in the current keys of the dictionary
                    if cmdlist[0] in list(level.keys()):
                        if type(level.get(cmdlist[0])) is str:
                            # This is an executable command
                            return context, level.get(cmdlist[0]), [], level.keys()
                        else:
                            # This is a non-executable command
                            return context + [cmdlist[0]], 'none', [], level.get(cmdlist[0]).keys()
                    else:
                        # Not a valid command or parameter
                        return context, 'none', [], level.keys()
                # Case 3: we have more elements, in which one is in the non-executable command path and the second is
                else:
                    # Check if the first parameter is a command
                    if not cmdlist[0] in list(level.keys()):
                        # Not a valid command or parameter
                        return context, 'none', [], level.keys()
                    # Check if the first parameter is an executable command
                    elif type(level.get(cmdlist[0])) is str:
                        return context, level.get(cmdlist[0]), cmdlist[1:], level.keys()
                    # Check if the second element is a valid keyword
                    elif not cmdlist[1] in list(level.get(cmdlist[0]).keys()):
                        return context, 'none', [], level.keys()
                    # Check if the second element is an executable command (no children)
                    elif type(level.get(cmdlist[0]).get(cmdlist[1])) is str:
                        return context+[cmdlist[0]], level.get(cmdlist[0]).get(cmdlist[1]), cmdlist[2:], \
                               level.get(cmdlist[0]).keys()
                    else:
                        # All other cases
                        return recursiveparse(level.get(cmdlist[0]), cmdlist[1:], context + [cmdlist[0]])

            ctx, cmd, args, voc = recursiveparse(self.opstacktolevel(), user_input, [])

            if (not ctx) and (cmd == 'none') and (not args):
                click.echo(click.style('Command not valid in this context.', fg='red'))
            else:
                if cmd != 'none':
                    self.dispatch(cmd, args)
                else:
                    self.__opstack += ctx

    # Implementation of each command
    def dispatch(self, cmd, args):
        ###########################################
        # Current
        ###########################################
        if cmd == 'curr_id':
            self.__dispatch_curr_id(args)
        elif cmd == 'curr_fetch':
            self.__dispatch_curr_fetch(args)
        elif cmd == 'curr_show':
            self.__dispatch_curr_show(args)
        elif cmd == 'curr_save':
            self.__dispatch_curr_save(args)
        elif cmd == 'curr_scratch':
            self.__dispatch_curr_scratch(args)
        ###########################################
        # Pending
        ###########################################
        elif cmd == 'pend_show':
            self.__dispatch_pend_show(args)
        elif cmd == 'pend_scratch':
            self.__dispatch_pend_scratch(args)
        elif cmd == 'pend_scratch_all':
            self.__dispatch_pend_scratch_all(args)
        elif cmd == 'pend_save':
            self.__dispatch_pend_save(args)
        elif cmd == 'pend_chko_auth':
            self.__dispatch_pend_chko_auth(args)
        elif cmd == 'pend_chko_art':
            self.__dispatch_pend_chko_art(args)
        elif cmd == 'pend_chko_annot':
            self.__dispatch_pend_chko_annot(args)
        ###########################################
        # Authors
        ###########################################
        elif cmd == 'auth_new':
            self.__dispatch_auth_new(args)
        elif cmd == 'auth_new':
            self.__dispatch_auth_new(args)
        ###########################################
        # SDB
        ###########################################
        elif cmd == 'sdb_list_auths':
            self.__dispatch_sdb_list_auths(args)
        elif cmd == 'sdb_list_arts':
            self.__dispatch_sdb_list_arts(args)
        elif cmd == 'sdb_list_annots':
            self.__dispatch_sdb_list_annots(args)
        elif cmd == 'sdb_list_tags':
            self.__dispatch_sdb_list_tags(args)
        elif cmd == 'sdb_list_files':
            self.__dispatch_sdb_list_files(args)
        elif cmd == 'sdb_list_refs':
            self.__dispatch_sdb_list_refs(args)
        else:
            pass

    ###########################################
    # Current
    ###########################################

    def __dispatch_curr_id(self, args):
        if self.current is None:
            click.echo(click.style('No current working element has been set.', fg='magenta'))
        else:
            click.echo(click.style('ID of current working element:\t{0}'.format(self.current.id), fg='blue'))

    def __dispatch_curr_fetch(self, args: list):
        if not args:
            user_input = prompt('Entity identifier: ',
                                completer=self.__cntxhash.values())
            args.append(user_input.split()[0])

        try:
            obj = self.__db.object_fetch(uuid.UUID(args[0]), self.__fetchhash[uuid.UUID(args[0])])
        except Exception as e:
            click.echo(click.style('Malformed uuid ({0}).'.format(e), fg='red'))
            obj = None

        if obj is not None:
            self.current = obj

    def __dispatch_curr_show(self, args):
        if self.current is None:
            click.echo(click.style('No current working element has been set.', fg='magenta'))
        else:
            if type(self.current) is Author:
                currtype = 'Author'
            elif type(self.current) is Article:
                currtype = 'Article'
            elif type(self.current) is Annotation:
                currtype = 'Annotation'
            else:
                currtype = 'Unknown'

            click.echo(click.style('Current: {}\n'.format(currtype), fg='blue') + str(self.current))

    def __dispatch_curr_save(self, args):
        if self.current is not None:
            # Saving takes care of the fetch hash per object type
            self.__db.save(self.current, self.__fetchhash)
            self.current = None
        else:
            click.echo(click.style('No current working element has been set.', fg='magenta'))

    def __dispatch_curr_scratch(self, args):
        if self.current is not None:
            self.current = None

    def __editauthor(self, args, prmpt=False):
        if prmpt:
            # Horrible Python shortcoming. This should be a do...while structure.
            while True:
                click.echo(self.current)
                message = '''
                Edit author:
                ============
                [1] Change first name
                [2] Change last name
                
                [0] Exit editor
                
                '''
                click.echo(message)
                choice = click.prompt('Your edit choice: ', type=int)

                if choice == 0:
                    return
                elif choice == 1:
                    fname = click.prompt('Enter the new first name: ', type=str)
                    self.current.firstname = fname
                elif choice == 2:
                    lname = click.prompt('Enter the new last name: ', type=str)
                    self.current.lastname = lname
                else:
                    click.echo(click.style('Unrecognized option.', fg='red'))
        else:
            fields = ['firstname', 'lastname']
            for i in range(0, len(args), 2):
                if args[i] not in fields:
                    click.echo(click.style(f'Unrecognized field {args[i]}.', fg='red'))
                else:
                    pass

    def __editarticle(self, args, prmpt=False):
        if prmpt:
            # Horrible Python shortcoming. This should be a do...while structure.
            while True:
                click.echo(self.current)
                message = '''
                Edit article:
                =============
                [1] Change refkey
                [2] Change year
                [3] Change title
                [4] Change journal
                [5] Change volume
                [6] Change number
                [7] Change pages
                [8] Add author to article
                [9] Delete author from article

                [0] Exit editor

                '''
                click.echo(message)
                choice = click.prompt('Your edit choice: ', type=int)

                if choice == 0:
                    return
                elif choice == 1:
                    rkey = click.prompt('Enter the new refkey: ', type=str)
                    self.current.refkey = rkey
                elif choice == 2:
                    yr = click.prompt('Enter the new year: ', type=str)
                    self.current.year = yr
                elif choice == 3:
                    ttl = click.prompt('Enter the new title: ', type=str)
                    self.current.title = ttl
                elif choice == 4:
                    jrnl = click.prompt('Enter the new journal: ', type=str)
                    self.current.journal = jrnl
                elif choice == 5:
                    vlm = click.prompt('Enter the new volume: ', type=str)
                    self.current.volume = vlm
                elif choice == 6:
                    nmbr = click.prompt('Enter the new number: ', type=str)
                    self.current.number = nmbr
                elif choice == 7:
                    pgs_txt = (click.prompt('Enter the new pages (start-end): ', type=str)).split('-')
                    if len(pgs_txt) != 2:
                        click.echo(click.style('Wrong pages input format.', fg='red'))
                    else:
                        self.current.pages = (pgs_txt[0], pgs_txt[1])
                elif choice == 8:
                    auuid = click.prompt('Enter the new author uuid: ', type=str)

                    # Case 1: search in pending
                    if self.__pending.exists_fetch(auuid, Author):
                        author = self.__pending.object_fetch(auuid, Author)
                    # Case 2: search in DB, add to pending (in case modifications are needed)
                    elif self.__db.exists_fetch(auuid, Author):
                        author = self.__db.object_fetch(auuid, Author)
                        self.__pending.put(author, self.__fetchhash)
                    # Case 3: create a new author from scratch and add it
                    else:
                        fname = prompt('First name: ')
                        lname = prompt('Last name: ')
                        author = Author(fname, lname, False)
                        self.__pending.put(author, self.__fetchhash)
                    if not self.current.authors.addauthor(author):
                        click.echo(click.style('Author has already been associated with this article.', fg='magenta'))
                elif choice == 9:
                    nmbr = click.prompt('Enter the new author uuid: ', type=str)

                    self.current.number = nmbr
                else:
                    click.echo(click.style('Unrecognized option.', fg='red'))
        else:
            fields = ['refkey', 'year', 'title', 'journal', 'volume', 'number', 'pages']
            for i in range(0, len(args), 2):
                if args[i] not in fields:
                    click.echo(click.style(f'Unrecognized field {args[i]}.', fg='red'))
                else:
                    pass

    def __editannotation(self, args, prmpt=False):
        if prmpt:
            # Horrible Python shortcoming. This should be a do...while structure.
            while True:
                click.echo(self.current)
                message = '''
                Edit annotation:
                ============
                [1] Change summary
                [2] Change information

                [0] Exit editor

                '''
                click.echo(message)
                choice = click.prompt('Your edit choice: ', type=int)

                if choice == 0:
                    return
                elif choice == 1:
                    smry = click.prompt('Enter the new summary: ', type=str)
                    self.current.summary = smry
                elif choice == 2:
                    info = click.edit('Enter the new information: ')
                    self.current.info = info
                else:
                    click.echo(click.style('Unrecognized option.', fg='red'))
        else:
            fields = ['summary', 'info']
            for i in range(0, len(args), 2):
                if args[i] not in fields:
                    click.echo(click.style(f'Unrecognized field {args[i]}.', fg='red'))
                else:
                    pass

    def __dispatch_curr_edit(self, args):
        if self.current is not None:
            prmpt = False
            editable = {
                Author: self.__editauthor,
                Article: self.__editarticle,
                Annotation: self.__editannotation
            }

            if type(self.current) not in editable.keys():
                click.echo(click.style('Tags, files and references can only be added or deleted.', fg='red'))
                return

            if not args:
                prmpt = True
            else:
                if len(args) % 2 != 0:
                    click.echo(click.style('Malformed argument list.', fg='red'))
                    return

            editable[type(self.current)](args, prmpt)

        else:
            click.echo(click.style('No current working element has been set.', fg='magenta'))

    ###########################################
    # Pending
    ###########################################

    def __dispatch_pend_show(self, args):
        if not args:
            self.__pending.show('all')
        else:
            self.__pending.show(args[0])

    def __dispatch_pend_scratch(self, args):
        self.__pending.scratch(self.__fetchhash)

    def __dispatch_pend_scratch_all(self, args):
        self.__pending.scratchall(self.__fetchhash)

    def __dispatch_pend_save(self, args):
        if not args:
            self.__pending.save('all', self.__db, self.__fetchhash)
        else:
            self.__pending.save(args[0], self.__db, self.__fetchhash)

    def __dispatch_pend_chko_auth(self, args):
        data = self.__pending.checkout_fetch(args[0], Author, self.__fetchhash)
        if data is not None:
            self.current = data
        else:
            click.echo(click.style(f'Author with UUID { args[0] } does not exist.', fg='magenta'))

    def __dispatch_pend_chko_art(self, args):
        data = self.__pending.checkout_fetch(args[0], Article, self.__fetchhash)
        if data is not None:
            self.current = data
        else:
            click.echo(click.style(f'Article with UUID {args[0]} does not exist.', fg='magenta'))

    def __dispatch_pend_chko_annot(self, args):
        data = self.__pending.checkout_fetch(args[0], Annotation, self.__fetchhash)
        if data is not None:
            self.current = data
        else:
            click.echo(click.style(f'Annotation with UUID {args[0]} does not exist.', fg='magenta'))

    ###########################################
    # Authors
    ###########################################

    def __dispatch_auth_new(self, args):
        if args:
            auth = Author(args[0], args[1], False)
            self.current = auth
            click.echo(click.style('New author created.', fg='blue'))
        else:
            fname = prompt('First name: ')
            lname = prompt('Last name: ')
            auth = Author(fname, lname, False)
            self.current = auth
            click.echo(click.style('New author created.', fg='blue'))

    ###########################################
    # SDB
    ###########################################

    def __dispatch_sdb_list_auths(self, args):
        outcome = self.__db.list('authors')

        if outcome is not None:
            click.echo_via_pager(outcome)

    def __dispatch_sdb_list_arts(self, args):
        outcome = self.__db.list('articles')

        if outcome is not None:
            click.echo_via_pager(outcome)

    def __dispatch_sdb_list_annots(self, args):
        outcome = self.__db.list('annotations')

        if outcome is not None:
            click.echo_via_pager(outcome)

    def __dispatch_sdb_list_tags(self, args):
        outcome = self.__db.list('tags')

        if outcome is not None:
            click.echo_via_pager(outcome)

    def __dispatch_sdb_list_files(self, args):
        outcome = self.__db.list('files')

        if outcome is not None:
            click.echo_via_pager(outcome)

    def __dispatch_sdb_list_refs(self, args):
        outcome = self.__db.list('refs')

        if outcome is not None:
            click.echo_via_pager(outcome)
