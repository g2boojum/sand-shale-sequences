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

Chemical compositions (and densities) of the various clays come from
`J. La Vigne, M. Herron, and R. Hertzog, "Density-neutron interpretation in
shaly sands", 35th SPWLA Annual Logging Symposium in
Tulsa, OK, paper EEE (1994)
<https://www.onepetro.org/conference-paper/SPWLA-1994-EEE>`_, 
with the exception of chlorite, which comes from
`S. Herron, M. Herron, I Pirie, P. Saldungaray, P. Craddock, A. Charsky,
M. Polyakov, F. Shray, and T. Li, "Application and quality control of core
data for the development and validation of elemental spectroscopy log
interpretation", *Petrophysics* **55(5)**, pp. 392-414 (2014)
<https://www.onepetro.org/journal-paper/SPWLA-2014-v55n5a2>_`.
