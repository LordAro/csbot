from csbot.plugin import Plugin
from csbot.util import nick

class Exam(Plugin):

    PLUGIN_DEPENDS = ['usertrack', 'auth', 'mongodb']

    examdb = Plugin.use('mongodb', collection='exam')
    examuserdb = Plugin.use('mongodb', collection='examuser')

    @Plugin.command('exam', help=('exam: show time until your next (set) exam.'
                                  ' See also exam.set, exam.all & exam.list'))
    def exam(self, e):
        print("exam")
        ident = self.identify_user(nick(e['user']))
        examcodes = self.examuserdb.find_one(ident)

    @Plugin.command('exam.set', help=('exam.set [exam...]: List (space/comma'
                                      ' delimited) of exams you\'re taking'))
    def examset(self, e):
        print("exam.set")
        ident = self.identify_user(nick(e['user']))
        self.examuserdb.remove(ident)  # Remove any existing

        examlist = e['data']
        if ',' in examlist:
            exams = examlist.split(',')
            exams = exams.strip()
        else:
            exams = examlist.split()

        # TODO: Check exams exist, error/drop on missing exam
        # Also check exam is not yet in the past

        ident['data'] = exams
        self.examuserdb.insert_one(ident)
        e.reply('Set {} exams'.format(len(exams)))

    @Plugin.command('exam.all', help='exam.all: List all your set exams')
    def examall(self, e):
        print("exam.all")
        ident = self.identify_user(nick(e['user']))
        examcodes = self.examuserdb.find_one(ident)
        e.reply(examcodes)

    @Plugin.command('exam.list', help='exam.list: PMs a list of all available exams')
    def examlist(self, e):
        print("exam.list")
        ident = self.identify_user(nick(e['user']))
        exams = self.examdb.find({})
        print(list(exams))
        e.bot.reply(e['user'], list(exams))  # Only ever send PM to requester

    @Plugin.command('exam.add', help=('exam.add [code] [YYYY-mm-dd] [name]'))
    def examadd(self, e):
        print("exam.add")
        if not self.bot.plugins['auth'].check_or_error(e, 'exam', e['channel']):
            return False
        try:
            code, date, name = e['data'].split(' ', 2)
        except ValueError:
            # Not enough values to unpack
            e.reply('error: invalid format, expected [code] [YYYY-mm-dd] [name]')
            return False

        # TODO: Error on trying to add exam in the past
        exam = {code: {'date': date, 'name': name}}
        self.examdb.insert_one(exam)
        # TODO: User feedback?

    @Plugin.command('exam.clear', help='exam.clear: Clear all existing exam data')
    def examclear(self, e):
        print("exam.clear")
        # TODO: Force flag if exams not run yet?
        self.examdb.delete_many({})
        self.examuserdb.delete_many({})

    def identify_user(self, nick):
        """Identify a user: by account if authed, if not, by nick. Produces a dict
        suitable for throwing at mongo."""

        user = self.bot.plugins['usertrack'].get_user(nick)

        if user['account'] is not None:
            return {'account': user['account']}
        else:
            return {'nick': nick}
