Reusing and Modifying Configurations
======================================

.. seealso::
   Full script: ``examples/reuse_dopyqo_config.py``

:class:`~dopyqo.DopyqoConfig` is a *frozen* dataclass: once created, its fields cannot
be changed in-place. This is intentional — it prevents accidental mutation and makes
configs safe to pass around and store. This example shows the recommended pattern for
creating a modified copy of an existing config.

A base configuration
---------------------

Start with a standard config:

.. code-block:: python

   import os
   import dopyqo

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be"),
       prefix="Be",
       active_electrons=2,
       active_orbitals=2,
       run_fci=True,
       n_threads=10,
   )

Why direct assignment fails
-----------------------------

Trying to modify a field after construction raises a ``FrozenInstanceError``:

.. code-block:: python

   import copy
   from dopyqo.units import Unit
   import numpy as np

   atom_positions = np.array([0.0, 0.5])

   # This will raise dataclasses.FrozenInstanceError:
   config_bad = copy.copy(config)
   config_bad.atom_positions = atom_positions  # ERROR

Using ``dataclasses.replace``
------------------------------

The correct approach is :func:`dataclasses.replace`, which creates a new config with
the specified fields overridden. All unspecified fields are copied from the original,
and all validation checks run on the new object:

.. code-block:: python

   from dataclasses import replace

   config_new_pos = replace(
       config,
       atom_positions=atom_positions,
       unit=Unit.CRYSTAL,
   )

This is exactly equivalent to constructing a new :class:`~dopyqo.DopyqoConfig` from
scratch with the updated values, but without having to repeat every unchanged field.

.. note::
   When ``atom_positions`` is set, ``unit`` must also be provided so Dopyqo knows
   which coordinate system the positions are expressed in.
