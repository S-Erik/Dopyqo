Generating a QE Input File from Wfc
=====================================

.. seealso::
   Full script: ``examples/wfc_to_qe_input.py``

The :class:`~dopyqo.Wfc` class can export a Quantum ESPRESSO SCF input file. This is
useful when you want to run a follow-up QE calculation with slightly modified crystal
geometry — for example, a displaced structure for phonon calculations or a lattice
constant scan.

Loading the Wfc object
------------------------

Read the wavefunction and XML files from a completed QE calculation using
:meth:`~dopyqo.Wfc.from_file`:

.. code-block:: python

   import os
   import dopyqo
   from dopyqo.units import Unit

   base_folder = os.path.join("qe_files", "Be")
   prefix = "Be"

   xml_file = os.path.join(base_folder, f"{prefix}.save", "data-file-schema.xml")
   wfc_file = os.path.join(base_folder, f"{prefix}.save", "wfc1.dat")

   wfc_obj = dopyqo.Wfc.from_file(wfc_file, xml_file)

Modifying the structure
------------------------

Atom positions and lattice vectors can be updated before writing the input file. Both
setters accept a ``unit`` argument to specify the coordinate system:

.. code-block:: python

   # Shift all atom positions by 0.01 Bohr
   wfc_obj.set_atom_positions(wfc_obj.atom_positions_hartree + 0.01, unit=Unit.HARTREE)

   # Expand the lattice vectors by 0.5 Bohr
   wfc_obj.set_lattice_vectors(wfc_obj.a + 0.5, unit=Unit.HARTREE)

   # Increase the number of bands to include in the input
   wfc_obj.nbnd = 20

Writing the QE input file
---------------------------

:meth:`~dopyqo.Wfc.to_qe_input` writes a self-contained SCF input file that can be
passed directly to ``pw.x``:

.. code-block:: python

   input_file = os.path.join("qe_files", "Be", "Be_from_dopyqo.scf.in")
   wfc_obj.to_qe_input(input_file, prefix="Be")

The output file contains the ``&CONTROL``, ``&SYSTEM``, ``&ELECTRONS``, ``ATOMIC_SPECIES``,
``ATOMIC_POSITIONS``, and ``K_POINTS`` cards populated from the ``Wfc`` object's data.
