powerbi_anonymisation
====================================

Coverage
--------
.. image:: https://code.mazars.global/mz/powerbi_anonymisation/badges/dev/pipeline.svg?key_text=Pipeline
.. image:: https://code.mazars.global/mz/powerbi_anonymisation/badges/dev/coverage.svg?job=Unit%20Tests%20API&key_text=API%20Cov
.. image:: https://code.mazars.global/mz/powerbi_anonymisation/badges/dev/coverage.svg?job=Unit%20Tests%20PKG&key_text=PKG%20Cov


Project Setup
-------------
Let's clone this project to your PC --> Use the "Clone with SSH" key that you can find under the blue button "Clone"

.. code:: python

    git clone git@code.mazars.global:2023/powerbi-anonymisation.git


Create your virtual environment, if you don't have one yet. Let's name it ``anonymisation``:

.. code:: python

    ~$ pyenv virtualenv anonymisation

Here you just created a virtual environment 

.. code:: python

    ~$ pyenv local anonymisation

Now your developments will be locally on your computer

.. code:: python

    ~$ make dev_install

With this command you have all the commands you need to make your work run

Launch framework
------------
Please go into the package and execute the make ``run_powerbi`` function

.. code:: python

    ~$ cd powerbi-anonymisation/pkg/
    ~$ make run_powerbi

.. code:: python

    You can use "Ctrl + Left Click" to execute the URL :
    You can now view your Streamlit app in your browser.
    Local URL: http://localhost:8501
    Network URL: http://172.25.46.241:8501

Use the framework
-----------------
**Drag & Drop** your files as requested.

You will then have a quick overview of all the tables you've just deposited :

.. figure:: ./doc/src/images/Picture1.png
  

Below those tables, you pick the column you would like to anonymise. 

1. Simple Tranformation

Your column can contain *Numeric* or *Category* type of data:

**NUMERIC**

  Here we are anonymising *Sales Price*. You can choose your coeffient range, and it will multiply your data randomly in between this range.
  
  .. figure:: ./doc/src/images/Picture2.png

**CATEGORY**
 
  If you choose a category type of column (like our Product column here), then it will implement your lines one by one {Prod 1; Prod 2; ...}

  .. figure:: ./doc/src/images/Picture3.png

2. Transformation with linked columns

Sometimes, you will have 2 identical columns in different tables. It is possible to anonymise them in exacctly the same way.

For instance, in the example below, both "Pays" and "Country" hold the same countries {Canada; France; ...}. If we rename **Canada** "Country 1" in ``Orders_Table``, then **Canada** will also be renamed "Country 1" in ``responsable comptes``
  
  .. figure:: ./doc/src/images/Picture5.png

--> If *Column X* in [Table 1] is your referential, then link *Column Y* in [Table 2] to [Table 1] as **Source_Table** & to *Column X* as **Source_Column**

3. Download your last configuration

If you want to keep your work, you can save the configuration that you currently have on streamlit. 

Just click here : 
  .. figure:: ./doc/src/images/Picture4.png
      :width: 50px 

--> Next time you launch your anonymisation, just drag and drop the configuration file (.json) with the others excel files.