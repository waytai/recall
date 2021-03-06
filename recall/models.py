import abc
import collections
import itertools
import uuid

import event_handler


class Command(collections.Mapping):
    """
    A command object -- not to be confused with the command pattern. This object
    is simply used to shuttle data between the client and the domain (write)
    model. Conceptually, it represents the client instructing the domain to
    perform some action which may or may not result in a state change in the
    domain. In practice, it's a :class:`dict`, though it should be assumed to be
    immutable.
    """
    def __init__(self, *args, **kwargs):
        assert not args
        assert kwargs
        self._data = kwargs
        self.require(**kwargs)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @abc.abstractmethod
    def require(self, **kwargs):
        pass


class Event(collections.Mapping):
    """
    An event object. This object is simply used to shuttle data between the
    write model and the read model. Conceptually, it is a token which represents
    that some action has happened in the domain (write) model which may or may
    not have resulted in a state change. In practice, it's a :class:`dict`,
    though it should be assumed to be immutable.

    **Important**: An event can *never* be rejected (though it can be ignored).
    It represents a *change which has already happened* -- rejecting it would
    imply history can be re-written.
    """
    def __init__(self, *args, **kwargs):
        assert not args
        assert kwargs
        self._data = kwargs
        self.require(**kwargs)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @abc.abstractmethod
    def require(self, **kwargs):
        pass

    def keys(self):
        """
        :rtype: :class:`iterator`
        """
        return self._data.keys()

    def items(self):
        """
        :rtype: :class:`iterator`
        """
        return self._data.items()


class EntityList(collections.MutableMapping):
    """
    A collection of domain entities, implemented as a :class:`dict` to allow
    efficient, random access by key.
    """
    def __init__(self, *args, **kwargs):
        assert not args
        self._data = kwargs

    def __delitem__(self, key):
        del(self._data[key])

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self._data[key] = value

    def add(self, entity):
        """
        Add an entity to the collection

        :param entity: The domain entity
        :type entity: :class:`recall.models.Entity`
        """
        assert isinstance(entity, Entity)
        self.update({entity.guid: entity})

    def get_all_events(self):
        """
        Get a flattened list of all the events for all the entities of the
        collection.

        :rtype: :class:`iterator`
        """
        return itertools.chain.from_iterable(
            x._events for x in self._get_all_entities())

    def _get_child_entities(self):
        """
        Get a flattened list of all the child entities of the collection.

        :rtype: :class:`iterator`
        """
        return itertools.chain.from_iterable(
            x._get_all_entities() for x in self.values()
            if isinstance(x, EntityList) or isinstance(x, Entity))

    def _get_all_entities(self):
        """
        Get a flattened list of all the child entities of the collection.

        :rtype: :class:`iterator`
        """
        return self._get_child_entities()


class Entity(object):
    """
    A domain entity. This is a base implementation of a domain model in the
    sense of Domain Driven Design by Eric Evans. This model is also event-
    sourced, supporting an event-driven style of architecture.
    """
    def __init__(self):
        self.guid = None
        self._version = 0
        self._events = []
        self._handlers = {}

    def get_all_events(self):
        """
        Get a flattened list of all the events for all the entities of the
        collection.

        :rtype: :class:`iterator`
        """
        return itertools.chain.from_iterable(
            x._events for x in self._get_all_entities())

    def _apply_event(self, event):
        """
        Applies a domain event to a domain entity, i.e. performs the represented
        state change, and stages the event for storage. At this point, the state
        has changed, but no data has been persisted to the event store, i.e.
        this is a non-authoritative change.

        :param event: The event to apply
        :type event: :class:`recall.models.Event`
        """
        assert isinstance(event, Event)
        self._handle_domain_event(event)
        self._events += [event]

    def _get_child_entities(self):
        """
        Get a flattened list of all the child entities of this entity.

        :rtype: :class:`iterator`
        """
        return itertools.chain.from_iterable(
            x._get_all_entities() for x in self.__dict__.values()
            if isinstance(x, EntityList) or isinstance(x, Entity))

    def _get_all_entities(self):
        """
        Get a flattened list of this entity and all the child entities of this
        entity.

        :rtype: :class:`iterator`
        """
        return itertools.chain([self], self._get_child_entities())

    def _create_guid(self):
        """
        Create an entity GUID

        :rtype: :class:`uuid.UUID`
        """
        return uuid.uuid4()

    def _handle_domain_event(self, event):
        """
        Applies a domain event to a domain entity (non-authoritative).

        :param event: The event to apply
        :type event: :class:`recall.models.Event`
        """
        assert isinstance(event, Event)
        event_cls = event.__class__
        if event_cls in self._handlers:
            self._handlers[event_cls](self)(event)

    def _increment_version(self, amount=1):
        """
        Increments a domain entity's version by the given amount

        :param amount: The amount to increment
        :type amount: :class:`int`
        """
        assert isinstance(amount, int)
        self._version += amount

    def _clear_events(self):
        """
        Removes a domain entity's staged events.
        """
        self._events = []

    def _register_event_handler(self, event_cls, callback_cls):
        """
        Register a domain event handler for an event

        :param event_cls: The event type to handle
        :type event_cls: :class:`type`

        :param callback_cls: The callback class
        :type callback_cls: :class:`type`
        """
        assert isinstance(event_cls, type(Event))
        assert isinstance(
            callback_cls,
            type(event_handler.DomainEventHandler))

        self._handlers[event_cls] = callback_cls


class AggregateRoot(Entity):
    """
    An aggregate root. This represents a single entity which may or may not
    contain an object graph which represents a logical and cohesive group of
    domain models.
    """
    pass