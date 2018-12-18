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
                'tag': {
                    'add': 'art_tag_add',
                    'rem': 'art_tag_rem',
                    'show': 'art_tag_show'
                },
                'attach': {
                    'file': {
                        'add': 'curr_att_file_add',
                        'edit': 'curr_att_file_edit',
                        'rem': 'curr_att_file_rem',
                        'show': 'curr_att_file_show',
                        'save': 'curr_att_file_save'
                    },
                    'refkey': {
                        'add': 'curr_att_rky_add',
                        'rem': 'curr_att_rky_rem',
                        'show': 'curr_att_rky_show'
                    }
                }
            },
            'pending': {
                'show': 'pend_show',
                'scratch': 'pend_scratch',
                'checkout': {
                    'author': 'pend_chko_auth',
                    'article': 'pend_chko_art',
                    'annotation': 'pend_chko_annot',
                    'tag': 'pend_chko_tag',
                    'file': 'pend_chko_file',
                    'ref': 'pend_chko_ref'
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
            'tags': {
                'new': 'tags_new',
                'show': 'tags_show',
                'delete': 'tags_delete'
            },
            'files': {
                'new': 'files_new',
                'show': 'files_show',
                'delete': 'files_delete'
            },
            'refs': {
                'new': 'refs_new',
                'show': 'refs_show',
                'delete': 'refs_delete'
            },
            'sdb': {
                'list': {
                    'authors': 'sdb_list_auths',        # DONE
                    'articles': 'sdb_list_arts',        # DONE
                    'annots': 'sdb_list_annots',
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
                }
            },
            'help': 'meta',
            'saveall': 'meta',
            'scratchall': 'meta',                   # DONE
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
        self.__prioruuid = None

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
        elif user_input[0] == 'saveall':
            # TODO
            pass
        elif user_input[0] == 'scratchall':
            self.__pending.scratchall(self.__fetchhash)
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
        # Current
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
        # Authors
        elif cmd == 'auth_new':
            self.__dispatch_auth_new(args)
        # Sdb
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
            obj = self.__db.fetch(uuid.UUID(args[0]), self.__fetchhash[uuid.UUID(args[0])])
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
            self.__db.save(self.current, self.__prioruuid, self.__fetchhash)
            self.current = None
        else:
            click.echo(click.style('No current working element has been set.', fg='magenta'))

    def __dispatch_curr_scratch(self, args):
        if self.current is not None:
            self.current = None

    def __dispatch_auth_new(self, args):
        if args:
            auth = Author(args[0], args[1])
            self.current = auth
            click.echo(click.style('New author created.', fg='blue'))
        else:
            fname = prompt('First name: ')
            lname = prompt('Last name: ')
            auth = Author(fname, lname)
            self.current = auth
            click.echo(click.style('New author created.', fg='blue'))

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
