.. Dopyqo documentation master file

.. code-block:: text

   oooooooooo.
   `888'   `Y8b
    888      888  .ooooo.  oo.ooooo.  oooo    ooo  .ooooo oo  .ooooo.
    888      888 d88' `88b  888' `88b  `88.  .8'  d88' `888  d88' `88b
    888      888 888   888  888   888   `88..8'   888   888  888   888
    888     d88' 888   888  888   888    `888'    888   888  888   888
   o888bood8P'   `Y8bod8P'  888bod8P'     .8'     `V8bod888  `Y8bod8P'
                            888       .o..P'            888.
                           o888o      `Y8P'             8P'
                                                        "

      Many-body analysis on top of Quantum ESPRESSO calculations


======

Dopyqo is a Python package for many-body post-processing of
`Quantum ESPRESSO <https://www.quantum-espresso.org/>`_ (QE) DFT calculations.
It reads Kohn-Sham orbitals from a QE calculation, constructs a second-quantized
many-body Hamiltonian, and solves it using classical (FCI via
`PySCF <https://pyscf.org/>`_) or quantum (VQE via
`TenCirChem <https://tensorcircuit.github.io/TenCirChem-NG/index.html>`_ or
`Qiskit <https://www.ibm.com/quantum/qiskit>`_) algorithms. It also supports
Bader charge analysis.

.. grid:: 2

   .. grid-item-card:: :octicon:`mark-github` GitHub (dopyqo)
      :link: https://github.com/dlr-wf/Dopyqo

      Source code, issue tracker, and contributions.

   .. grid-item-card:: :octicon:`mark-github` GitHub (dopyqo-rs)
      :link: https://github.com/dlr-wf/dopyqo-rs

      Optional Rust extension for faster matrix element calculations.

.. grid:: 2

   .. grid-item-card:: :octicon:`package` PyPI
      :link: https://pypi.org/project/dopyqo/

      Install with ``pip install dopyqo``

   .. grid-item-card:: :octicon:`file` Paper
      :link: https://arxiv.org/abs/2510.12887

      Schultheis et al. 2025 — Many-body post-processing of DFT calculations
      using VQE for Bader charge analysis.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   overview
   examples/index
   tutorials/index
   api/index
   citation
