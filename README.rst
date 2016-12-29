sand-shale-sequences
====================

Supplemental material for Interpretation paper
----------------------------------------------

These files show how the elemental composition of the XRD-determined clays
was computed.

A spreadsheet showing how the composition for cutting 1 from well XD-2 was
determined: clay_compositions_with_mixture_XD2_1.xlsx

A program that constructs MCNP input decks from a template for each of the
cuttings for which Core Labs determined the mineralogy: getdecks.py.  This
program requires the template, ctn8tmpl (which has had all of the tool
descriptions deleted), a table of XRD cuttings compositions, XRD.csv, 
and a routine to construct an MCNP material card from weight or mole
fractions, mcnpelements.py.

At the time of this work, the following versions of Python and associated
libraries was used:

* python 3.5
* numpy 1.10.4
* pandas 0.18.0
