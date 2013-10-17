import abc

import recall.models


class EventRouter(object):
    """
    The Event Router Interface

    This is a class of objects which know how and where to send events once they
    occur.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def route(self, event):
        """
        Route the event

        :param event: The domain event
        :type event: :class:`recall.models.Event`
        """
        pass


class StdOut(EventRouter):
    """
    Print meta information for an event
    """
    def route(self, event):
        """
        Print the event to stdout

        :param event: The domain event
        :type event: :class:`recall.models.Event`
        """
        assert isinstance(event, recall.models.Event)
        print("[x] Routed event %s" % event.__class__.__name__)