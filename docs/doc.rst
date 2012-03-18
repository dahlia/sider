Documentation guides
====================

This project use Sphinx_ for documentation and `Read the Docs`_ for
documentation hosting.  Build the documentation always before you commit ---
You must not miss documentation of your contributed code.

Be fluent in reStructuredText_.

.. _Sphinx: http://sphinx.pocoo.org/
.. _Read the Docs: http://readthedocs.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Build
-----

Install Sphinx 1.1 or higher first.  If it's been installed already, skip this.

.. sourcecode:: console

   $ easy_install "Sphinx>=1.1"

Use :program:`make` in the :file:`docs/` directory.

.. sourcecode:: console

   $ cd docs/
   $ make html

You can find the built documentation in the :file:`docs/_build/html/` directory.

.. sourcecode:: console

   $ python -m webbrowser docs/_build/html/  # in the root


Convention
----------

- Follow styles as it was.

- Every module/package has to start with docstring like this::

      """:mod:`sider.modulename` --- Module title
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

      Short description about the module.

      """

  and make reStructuredText file of the same name in the :file:`docs/sider/`
  directory.  Use :rst:dir:`automodule` directive.

- All published modules, constants, functions, classes, methods and attributes
  (properties) have to be documented in their docstrings.

- Source code to quote is in Python, use a `literal block`__.
  If the code is a Python interactive console session, don't use it (see below).

- The source code is not in Python, use a :rst:dir:`sourcecode` directive
  provided by Sphinx.  For example, if the code is a Python interactive
  console session:

  .. sourcecode:: rst

     .. sourcecode:: pycon

        >>> 1 + 1
        2

  See also the list of `Pygments lexers`__.

- Link Redis commands using :rst:role:`redis` role.  For example:

  .. sourcecode:: rst

     It may send :redis:`RPUSH` multiple times.

__ http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#literal-blocks
__ http://pygments.org/docs/lexers/

