********
Metadata
********

A Metadata object looks like this:

.. code-block::

    Metadata [key=Namespace_Name:Item_Name, value=namespace value, configuration=[Key_1="key 1 value", Key_2=5.5, Key_3=false, Key_4={Subkey={Subsubkey="nested value"}}]]

Metadata objects are uniquely defined by an Item name and a namespace name, and contain a "value" and the "configuration".
The "value" is not very useful, as it only holds a single value.
The "configuration" provides the actual metadata as a dictionary.

.. code-block:: none

    └── Item
        ├── Namespace 1
        │   ├── Value
        │   └── Configuration
        │       ├── Key 1
        │       │   └── Value
        │       └── Key 2
        │           └── Value
        └── Namespace 2
            ├── Value
            └── Configuration
                ├── Key 1
                │   ├── Subkey 1
                │   │   └── Subsubkey
                │   │       └── Value
                │   └── Subkey 2
                │       └── Value
                └── Key 2
                    └── Value

Refer to the language-specific documentation for details on use of this library.
