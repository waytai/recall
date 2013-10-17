import abc
import copy
import uuid

import models


class EventStore(object):
    """
    The Event Store interface
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_all_events(self, guid):
        """
        Get all events for a domain entity

        :param guid: The guid of the domain entity
        :type guid: :class:`uuid.UUID`

        :rtype: :class:`iterator`
        """
        pass

    @abc.abstractmethod
    def get_events_from_version(self, guid, version):
        """
        Get events for a domain entity as of a given version

        :param guid: The guid of the domain entity
        :type guid: :class:`uuid.UUID`

        :param version: The version of the domain entity
        :type version: :class:`int`

        :rtype: :class:`iterator`
        """
        pass

    @abc.abstractmethod
    def save(self, entity):
        """
        Save a domain entity's events

        :param entity: The domain entity
        :type entity: :class:`recall.models.Entity`
        """
        pass


class Memory(EventStore):
    """
    An in-memory event store
    """

    def __init__(self):
        self._events = {}
        self._entities = {}

    def get_all_events(self, guid):
        """
        Get all events for a domain entity

        :param guid: The guid of the domain entity
        :type guid: :class:`uuid.UUID`

        :rtype: :class:`iterator`
        """
        assert isinstance(guid, uuid.UUID)
        return self._events.get(guid)

    def get_events_from_version(self, guid, version):
        """
        Get events for a domain entity as of a given version

        :param guid: The guid of the domain entity
        :type guid: :class:`uuid.UUID`

        :param version: The version of the domain entity
        :type version: :class:`int`

        :rtype: :class:`iterator`
        """
        assert isinstance(guid, uuid.UUID)
        assert isinstance(version, int)
        return (self._events.get(guid) or [])[version:]

    def save(self, entity):
        """
        Save a domain entity's events

        :param entity: The domain entity
        :type entity: :class:`recall.models.Entity`
        """
        assert isinstance(entity, models.Entity)
        for provider in entity._get_all_entities():
            self._create_entity(provider)
            for event in provider._events:
                self._events[provider.guid].append(copy.copy(event))

    def _create_entity(self, entity):
        """
        Creates the array members for the entity if it is not found

        :param entity: The domain entity
        :type entity: :class:`recall.models.Entity`
        """
        assert isinstance(entity, models.Entity)
        if not self._events.get(entity.guid):
            self._events[entity.guid] = []
