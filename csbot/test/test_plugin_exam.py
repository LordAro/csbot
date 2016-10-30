from unittest import mock

from csbot.test import BotTestCase, read_fixture_file

class TestExam(BotTestCase):
    CONFIG = """\
    [@bot]
    plugins = auth usertrack mongodb exam
    """

    PLUGINS = ['auth', 'usertrack', 'mongodb', 'exam']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_set(self):
        pass

    def test_all(self):
        pass

    def test_list(self):
        pass

    def test_add(self):
        pass

    def test_clear(self):
        pass
