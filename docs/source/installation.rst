Installation
============

Dopyqo is available on `PyPI <https://pypi.org/project/dopyqo/>`_ and can be
installed with pip:

.. code-block:: bash

   pip install dopyqo

Requirements
------------

- Python >= 3.10 (tested on 3.11)
- Quantum ESPRESSO 7.1 (tested with and without HDF5 1.14.0)
- Only norm-conserving pseudopotentials are supported
- Only spin-restricted QE calculations are supported

Optional dependencies
---------------------

**Rust acceleration** (faster matrix element calculations via
`dopyqo-rs <https://github.com/dlr-wf/dopyqo-rs>`_):

.. code-block:: bash

   pip install dopyqo[rs]

Requires the `Rust toolchain <https://rustup.rs/>`_ and the
`GNU Scientific Library <https://www.gnu.org/software/gsl/>`_
(``sudo apt install libgsl-dev`` on Debian/Ubuntu).
Without ``dopyqo-rs``, a slower NumPy/SciPy implementation is used.

**GPU acceleration** for ERI calculations via
`CuPy <https://docs.cupy.dev/en/stable/index.html>`_:

.. code-block:: bash

   pip install dopyqo[gpu]

Make sure to install the CuPy version matching your CUDA version.
Without CuPy, NumPy is used. GPU can be explicitly disabled by setting
``use_gpu=False`` in :class:`~dopyqo.DopyqoConfig`.

**Install all optional dependencies:**

.. code-block:: bash

   pip install dopyqo[all]

Bader charge analysis
---------------------

To calculate Bader charges, install the external
`Bader charge analysis code <https://theory.cm.utexas.edu/henkelman/code/bader/>`_
and make sure it is available on your ``PATH``.

VQE thread usage
----------------

On Linux, set the ``OMP_NUM_THREADS`` environment variable to limit CPU usage
during VQE calculations:

.. code-block:: bash

   export OMP_NUM_THREADS=4
