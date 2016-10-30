import datetime
import pymongo

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
        exam_codes = self.examuserdb.find_one(ident)
        next_exam = self.examdb.find_one({'code': {'$in': exam_codes}}).sort('date', pymongo.DESCENDING)
        e.reply('{name} ({code}) on {date}'.format(**next_exam))

    @Plugin.command('exam.set', help=('exam.set [exam...]: List (space/comma'
                                      ' delimited) of exams you\'re taking'))
    def examset(self, e):
        print("exam.set")
        ident = self.identify_user(nick(e['user']))
        self.examuserdb.remove(ident)  # Remove any existing

        user_set = e['data']
        if ',' in user_set:
            user_list = user_set.split(',')
            user_list = user_list.strip()
        else:
            user_list = user_set.split()

        # Error on missing exam
        # Also check exam is not yet in the past
        all_exams = list(self.examdb.find({}))
        for e in user_list:
            if e not in all_exams:
                e.reply('error: Unrecognised exam {}'.format(e))
                return False
            if all_exams[e].date < datetime.datetime.today():
                e.reply('error: {} has already happened')
                return False

        ident['data'] = user_list
        self.examuserdb.insert_one(ident)
        e.reply('Set {} exams'.format(len(user_list)))

    @Plugin.command('exam.all', help='exam.all: List all your set exams')
    def examall(self, e):
        print("exam.all")
        ident = self.identify_user(nick(e['user']))

        exam_codes = self.examuserdb.find_one(ident)
        exam_docs = self.examdb.find({'code': {'$in': exam_codes}})

        e.reply('Your remaining exams: ' +
                '; '.join('{name} ({code}) on {date}'.format(**e) for e in exam_docs))

    @Plugin.command('exam.list', help='exam.list: PMs a list of all available exams')
    def examlist(self, e):
        print("exam.list")
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

        # Error on trying to add exam in the past
        if date < datetime.datetime.today():
            e.reply('error: Exam in the past')

        exam = {'code': code, 'date': date, 'name': name}
        self.examdb.insert_one(exam)
        # TODO: User feedback?

    @Plugin.command('exam.clear', help='exam.clear [-f]: Clear all existing exam data')
    def examclear(self, e):
        print("exam.clear")
        # Force flag if exams not run yet
        if self.examdb.find({'date': {'$lt': datetime.datetime.today()}}).count() > 0:
            e.reply('error: Not all exams have run. Use -f to force')
        self.examdb.delete_many({})
        self.examuserdb.delete_many({})
        e.reply('Cleared all exams')

    def identify_user(self, nick):
        """Identify a user: by account if authed, if not, by nick. Produces a dict
        suitable for throwing at mongo."""

        user = self.bot.plugins['usertrack'].get_user(nick)

        if user['account'] is not None:
            return {'account': user['account']}
        else:
            return {'nick': nick}
