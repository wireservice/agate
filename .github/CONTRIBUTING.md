Contributing
============

Principles
----------

agate is a intended to fill a very particular programming niche. It should not be allowed to become as complex as [numpy] or [pandas]. Please bear in mind the following principles when contemplating an addition:

-   Humans have less time than computers. Optimize for humans.
-   Most datasets are small. Don’t optimize for “big data”.
-   Text is data. It must always be a first-class citizen.
-   Python gets it right. Make it work like Python does.
-   Humans lives are nasty, brutish and short. Make it easy.
-   Mutability leads to confusion. Processes that alter data must create new copies.
-   Extensions are the way. Don’t add it to core unless everybody needs it.

Process for contributing code
-----------------------------

Contributors should use the following roadmap to guide them through the process of submitting a contribution:

1.  Fork the project on [Github].
2.  Check out the [issue tracker] and find a task that needs to be done and is of a scope you can realistically expect to complete in a few days. Don’t worry about the priority of the issues at first, but try to choose something you’ll enjoy. You’re much more likely to finish something to the point it can be merged if it’s something you really enjoy hacking on.
3.  Comment on the ticket letting everyone know you’re going to be hacking on it so that nobody duplicates your effort. It’s also good practice to provide some general idea of how you plan on resolving the issue so that other developers can make suggestions.
4.  Write tests for the feature you’re building. Follow the format of the existing tests in the test directory to see how this works. You can run all the tests with the command `nosetests tests`. (Or `tox` to run across all supported versions of Python.)
5.  Write the code. Try to stay consistent with the style and organization of the existing codebase. A good patch won’t be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that.
6.  As you are coding, periodically merge in work from the master branch and verify you haven’t broken anything by running the test suite.
7.  Write documentation. Seriously.
8.  Once it works, is tested, and has documentation, submit a pull request on Github.
9.  Wait for it to either be merged or to receive a comment about what needs to be fixed.
10. Rejoice.

Legalese
--------

To the extent that they care, contributors should keep in mind that the source of agate and therefore of any contributions are licensed under the permissive [MIT license]. By submitting a patch or pull request you are agreeing to release your code under this license. You will be acknowledged in the AUTHORS list, the commit history and the hearts and minds of jo

  [numpy]: http://www.numpy.org/
  [pandas]: http://pandas.pydata.org/
  [Github]: https://github.com/onyxfish/agate
  [issue tracker]: https://github.com/onyxfish/agate/issues
  [MIT license]: http://www.opensource.org/licenses/mit-license.php
