import abc

import models


class DomainEventHandler(object):
    """
    A simple object representing the state change of a domain once an event
    occurs.

    :param entity: The domain entity
    :type entity: :class:`recall.models.Entity`
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, entity):
        assert isinstance(entity, models.Entity)
        self.entity = entity

    @abc.abstractmethod
    def __call__(self, event):
        """
        Handle the domain state change

        :param event: The domain event
        :type event: :class:`recall.models.Event`
        """
        pass
