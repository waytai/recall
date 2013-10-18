Recall, a CQRS library for Python
=================================

Recall provides a library of classes useful for implementing the "write"-side of
a CQRS system (with event sourcing). It currently has a memento-like repository
for dealing with `Aggregate Roots`_ in a DDD_-way, and several interfaces for
adding your own event routers, event stores, and snapshot stores.

.. _DDD: http://en.wikipedia.org/wiki/Domain-driven_design
.. _`Aggregate Roots`: http://www.udidahan.com/2009/06/29/dont-create-aggregate-roots/

Contents:

.. toctree::
   :maxdepth: 2
   :glob:

   *


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

