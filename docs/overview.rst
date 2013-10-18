Overview
=========

.. toctree::


CQRS
----
Command/Query Responsibility Segregation is a fancy-sounding term for what turns
out to be this elegant, structured, and scalable way to design a service (within
a `Bounded Context`_). It goes beyond Bertrand Meyer's admonition to `separate
Commands and Queries`__ within objects and makes them separate models: a
Command-only, "write", model and a Query-only, "read", model. Turns out, this
simple extension of Meyer has some dramatic implications for the ability to
scale a system while providing Availability and Partition Tolerance (with
Eventual Consistency -- cf. the `CAP Theorem`_).

.. _`Bounded Context`: http://dddcommunity.org/uncategorized/bounded-context/
.. _CQS: http://en.wikipedia.org/wiki/Command%E2%80%93query_separation
.. _`CAP Theorem`: http://en.wikipedia.org/wiki/CAP_theorem
__ CQS_


Event-Sourcing
--------------
Building on top of CQRS, the storage of your write model could actually just be
a sequence of all the events that happened to your domain model. Aside from
making it easy to publish these events for different kinds of analysis, this
sequence would, in effect, become a *perfect* audit log of your system.


CQRS with Recall
----------------
Recall provides abstract implementations of Aggregate Roots, Domain Entities,
Events, and Commands along with a Repository which handles saving and loading an
AggregateRoot, writing to the Event stream, snapshot-ing the AR, and routing
events. In short, the heavy-lifting of the "write" model. In the example
directory is the simple **planet_express.py** example which uses in-memory
storage and a router to stdout.


Further Reading
---------------
- `Unshackle Your Domain (Greg Young)`_
- `Command-Query-Responsibility-Segregation (Udi Dahan)`_

.. _`Unshackle Your Domain (Greg Young)`: http://www.infoq.com/presentations/greg-young-unshackle-qcon08
.. _`Command-Query-Responsibility-Segregation (Udi Dahan)`: http://www.infoq.com/presentations/Command-Query-Responsibility-Segregation