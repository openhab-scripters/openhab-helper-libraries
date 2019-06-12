***********
First Steps
***********

.. tabs::

    .. group-tab:: Python

        If you have made it to this page you should have entries from the ``hello_world.py`` script appearing in your openHAB log.
        Let's take a closer look at what is making that happen.
        Here is the rule from ``hello_world.py``:

            .. code-block:: python

                from core.rules import rule
                from core.triggers import when

                @rule("Hello World cron rule (decorator)", description="This is an example rule that demonstrates using a cron rule with decorators", tags=["Test tag", "Hello World"])# [description and tags are optional]
                @when("Time cron 0/10 * * * * ?")
                def helloWorldDecoratorCron(event):
                    helloWorldDecoratorCron.log.info("This is a 'hello world!' from a Jython rule (decorator): Cron")
            
        It is written using the decorators provided by this library.
        This is by far the easiest way to write rules, and has been modelled after the syntax of the openHAB DSL to ease migration.
        Here we will take a closer look at what is happening.
        Lets start with the python code to be executed when the rule triggers.
        This needs to be written as a function with one argument:

            .. code-block:: python

                def helloWorldDecoratorCron(event):
                    # your code here

        You can name this function almost anything you want, but it must be unique in the file it is in.
        The code you write in the function is entirely python.
        The ``rule`` decorator provides your rule function with a built-in logger to make things easy.
        It is an attribute of your function and is accessed using ``myFunctionName.log`` followed by ``.level`` to indicate the logging level, and finally ``('My log message')`` like so:

            .. code-block:: python

                def helloWorldDecoratorCron(event):
                    helloWorldDecoratorCron.log.info("This is a 'hello world!' from a Jython rule (decorator): Cron")

        The ``.info`` part is the log level.
        More information on these can be found in :doc:`../Guides/Logging`.

        Now lets dig in to the good stuff... the decorators! 
        Decorators are basically just functions that modify other functions, but Python lets us put them on a single line starting with ``@`` above the function we want to "decorate".
        This makes the code much easier to read.
        First we need to import the ``rule`` and ``when`` decorators. This only needs to be done once at the top of each file you will be writing rules in.

            .. code-block:: python

                from core.rules import rule
                from core.triggers import when

        When writing an automation rule, we need to start with the ``@rule`` decorator.
        It needs to be first, and there can only be one for each rule you write.
        The rule decorator must be provided a name you want to use for your rule as the first argument.
        This name must be unique in your openHAB instance and will be used as the display name of your rule in PaperUI.
        Optionally, you can also provide a longer description of what your rule does and a list of tags that can be used to categorize and help search for rules in Paper UI.

            .. code-block:: python

                @rule("My Rule Name", description="My Rule Description", tags=["Test tag", "Hello World"])
                def helloWorldDecoratorCron(event):
                    # your code here

        Now the rule above is written correctly, but it will never run because we haven't told openHAB what should trigger the rule.
        The last piece is the ``@when`` decorator.
        Each event that you want to trigger the rule needs its own ``@when`` line, but you can add as many as you want.
        The ``@when`` decorator only needs one argument which is a string representing the event that should trigger the rule.
        In this example, we are using ``Time cron`` which allows triggering rules at a certain time of day (every 10s in this case).

            .. code-block:: python

                @when("Time cron 0/10 * * * * ?")

        Put all of these concepts together and we have a rule that prints to the *info* log once every 10 seconds.
        Head over to :doc:`../Guides/Rules` to learn more about writing your own rules.

    .. group-tab:: Javascript

            Nothing has been written yet

    .. group-tab:: Groovy

            Nothing has been written yet
