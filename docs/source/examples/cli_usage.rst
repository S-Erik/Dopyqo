Command-Line Interface (TOML Input)
=====================================

.. seealso::
   Full input file: ``examples/dopyqo.toml``

Dopyqo can be driven from the command line using a TOML input file instead of a Python
script. This is convenient for simple, reproducible runs that do not require custom
post-processing.

.. note::
   The CLI covers a subset of the Python API. Features like custom matrix elements
   (:class:`~dopyqo.MatrixElements`), direct access to the returned ``wfc_obj`` and
   ``h_ks`` objects, custom excitation lists, and post-processing (Bader charges,
   orbital plots) are only available through the Python API.

Running Dopyqo from the command line
--------------------------------------

Point the ``dopyqo`` command at a TOML input file with the ``-i`` flag:

.. code-block:: bash

   dopyqo -i dopyqo.toml

The ``[control]`` section
---------------------------

The ``[control]`` table mirrors the main fields of :class:`~dopyqo.DopyqoConfig`. At
minimum, ``base_folder``, ``prefix``, ``active_electrons``, and ``active_orbitals``
must be set:

.. code-block:: toml

   [control]
   base_folder = "qe_files/Be"
   prefix = "Be"
   active_electrons = 2
   active_orbitals = 2
   run_vqe = true
   run_fci = true
   use_qiskit = false
   logging = false

The ``[geometry]`` section
----------------------------

Custom atom positions and lattice vectors can be specified in the ``[geometry]`` table.
The ``unit`` key sets the coordinate system for both ``coordinates`` and
``lattice_vectors``:

.. code-block:: toml

   [geometry]
   unit = "angstrom"
   coordinates = [
       [0.0, 0.0, 0.0],
       [0.5, 0.5, 0.5]
   ]
   lattice_vectors = [
       [1.0, 0.0, 0.0],
       [0.0, 1.0, 0.0],
       [0.0, 0.0, 1.0],
   ]

If ``[geometry]`` is omitted, atom positions and lattice vectors are read directly
from the QE output XML file.

The ``[vqe]`` section
-----------------------

VQE settings go in a separate ``[vqe]`` table. To use fixed parameters without
re-optimising, uncomment the ``parameters`` line:

.. code-block:: toml

   [vqe]
   # parameters = [0.4, 0.3, 0.1]
   optimizer = "ExcitationSolve"
   uccsd_reps = 1

The available optimizer names correspond to the members of
:class:`~dopyqo.VQEOptimizers`. See ``INPUT.md`` in the
`Dopyqo repository <https://github.com/dlr-wf/Dopyqo>`_ for the full list of
supported keys in each section.
