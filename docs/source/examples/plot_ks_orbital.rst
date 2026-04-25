Plotting Kohn-Sham Orbitals in Real Space
==========================================

.. seealso::
   Full script: ``examples/plot_real_space_ks_orbital.py``

Dopyqo can produce interactive 3D isosurface plots of Kohn-Sham orbitals directly from
the QE wavefunction files. This does not require running FCI or VQE — only the
:class:`~dopyqo.Wfc` object is needed.

Constructing the Wfc object without a full run
-----------------------------------------------

When only orbital plots are needed, it is wasteful to compute matrix elements. Instead
of calling :func:`~dopyqo.run`, build a :class:`~dopyqo.Wfc` object directly from the
QE output files:

.. code-block:: python

   import os
   import dopyqo

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Mg2Si"),
       prefix="Mg2Si",
       active_electrons=2,
       active_orbitals=2,
       n_threads=10,
   )

   xml_file = os.path.join(config.base_folder, f"{config.prefix}.save",
                            "data-file-schema.xml")
   wfc_file = os.path.join(config.base_folder, f"{config.prefix}.save", "wfc1.dat")

   wfc_obj = dopyqo.Wfc.from_file(wfc_file, xml_file,
                                    kpoint_idx=config.kpoint_idx)

The config is used here only to keep the folder and prefix in one place; it is not
passed to any Dopyqo solver.

Plotting the orbital
----------------------

:meth:`~dopyqo.Wfc.plot_real_space` generates an interactive HTML isosurface plot
using PyVista. Pass a list of band indices (zero-based) to select which orbitals to
visualise:

.. code-block:: python

   plotter = wfc_obj.plot_real_space(
       band_idc=[8],
       isosurfaces=5,
       opacity=0.6,
       extend_data=False,
       extend_atoms=False,
       plot_lattice_vectors=True,
       html_filename=os.path.join(config.base_folder, "plot_wfc_ks"),
   )

The result is saved as an HTML file at ``html_filename.html``. Open it in a browser for
an interactive view. ``isosurfaces`` sets the number of contour levels drawn, and
``opacity`` controls their transparency.
