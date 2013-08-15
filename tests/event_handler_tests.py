import unittest

import recall.event_handler as eh
import recall.models as m


class MockEntity(m.Entity):
    pass


class MockEventHandler(eh.DomainEventHandler):
    def __call__(self, *args):
        return


class DomainEventHandlerTest(unittest.TestCase):
    def test_base_class_is_abstract(self):
        with self.assertRaises(TypeError):
            eh.DomainEventHandler(MockEntity())

        self.assertIsInstance(
            MockEventHandler(MockEntity()),
            eh.DomainEventHandler)