# Python 3.14 compatibility notes

The project targets CPython 3.14.x on Windows x86-64. The prior pins `faiss-cpu==1.9.0.post1` and `sentence-transformers==3.3.1` were retained from an older environment and caused the install failure seen during setup.

Updated pins:
- `faiss-cpu==1.16.0`: PyPI publishes `cp314-cp314-win_amd64` wheels.
- `sentence-transformers==6.3.0`: published as a Python 3 universal wheel and its PyPI metadata lists Python 3.14.
- Updated NumPy, PyYAML and Pydantic pins to newer releases for current interpreter support.

Important: availability of a wheel does not prove the whole dependency set or the application has been tested on the candidate's Windows machine. Install the requirements, run `python -m pip check`, then run the smoke tests and project commands. Record any changes made after that.

The assessment itself allows Python 3.10 or later. Python 3.14 is therefore within the stated range, but dependency compatibility must still be verified.
