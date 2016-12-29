#! /usr/bin/env python
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
import re
import pandas as pd

#Table of elements with mcnp libraries
#                 Symbol Z    Mass    mcnp
_ELEMENTINFO = """H      1     1.008  1001.60c
                  He     2     4.003  2000.01
                  He-3   2     3.016  2003.60c
                  Li     3     6.940  3000.01
                  Be     4     9.013  4009.60c
                  B      5    10.820  5000.01
                  B-10   5    10.013  5010.74c
                  B-11   5    11.009  5011.74c
                  C      6    12.011  6000.60c
                  N      7    14.008  7014.60c
                  O      8    16.000  8016.60c
                  F      9    19.000  9019.60c
                  Na    11    22.991  11023.60c
                  Mg    12    24.320  12000.60c
                  Al    13    26.980  13027.60c
                  Si    14    28.090  14000.60c
                  P     15    30.975  15031.60c
                  S     16    32.066  16032.60c
                  Cl    17    35.457  17000.60c
                  K     19    39.100  19000.60c
                  Ca    20    40.080  20000.60c
                  Ti    22    47.900  22000.60c
                  V     23    50.950  23000.60c
                  Cr    24    52.010  24000.50c
                  Mn    25    54.940  25055.60c
                  Fe    26    55.850  26000.55c
                  Co    27    58.940  27059.60c
                  Ni    28    58.710  28000.50c
                  Cu    29    63.540  29000.50c
                  Zn    30    65.380  30000.40c
                  Br    35    79.916  35000.01
                  Sr    38    87.630  38000.01
                  Zr    40    91.220  40000.60c
                  Nb    41    92.910  41093.60c
                  Mo    42    95.950  42000.60c
                  Ag    47   107.880  47000.01
                  Cd    48   112.410  48000.50c
                  Sn    50   118.700  50000.42c
                  Cs    55   131.764  55133.60c
                  Ba    56   137.360  56138.60c
                  La    57   138.920  57000.01
                  Ce    58   140.130  58000.01
                  Sm    62   150.350  62000.01
                  Eu    63   152.000  63000.42c
                  Gd    64   157.250  64000.35c
                  Ta    73   180.950  73181.60c
                  W     74   183.860  74000.55c
                  Pb    82   207.210  82000.50c
                  Th    90   232.038  90232.74c
                  U     92   238.029  92000.01
                  U-234 92   238.029  92234.74c
                  U-235 92   238.029  92235.74c
                  U-238 92   238.029  92238.74c"""

ELEMENTS = {}
for line in _ELEMENTINFO.split('\n'):
    items = line.strip().split()
    ELEMENTS[items[0]] = dict(Z=int(items[1]),
                              A=float(items[2]),
                              mcnp=items[3])

# ELEMENTS is exposed directly, but here
# are some helper routines
def atomic_mass(element):
    "Return the atomic mass of element 'element'"
    return ELEMENTS[element]["A"]
def atomic_number(element):
    "Return the atomic number of element 'element'"
    return ELEMENTS[element]["Z"]
def mcnp_library(element):
    "Return the mcnp library string for element 'element'"
    return ELEMENTS[element]["mcnp"]

# Some natural (mole-fraction) abundances because MCNP5 and MCNP6 have dropped some natural
# libraries
ABUNDANCES = {'B-10': 0.199,
              'B-11': 0.801,
              'U-238': 0.99275,
              'U-235': 0.0072,
              'U-234': 0.00054,
             }

# Regex to match an element (with an optional isotope tag)
# followed by an optional float
_RE_ELEMENTS = re.compile(r"""
    ([A-Z][a-z]?(?:-\d+)?)                    #element w/ opt isotope
    \s*                                       #opt whitespace
    ([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)?        #opt weight
    """, re.VERBOSE)


class ElementalComposition(dict):
    """Class for elemental compositions.

       Uses elements in the composition as keys,
       and each element's mole fraction as the value.

       Can be initialized with a string,
       such as 'C2H2OH', or with another
       ElemnetalComposition instance (which
       makes a copy), or with nothing,
       in which case the composition is an empty dict.

       Note: Parentheses are not allowed in a
       formula string, but spaces may be used
       to separate an element with an isotope tag
       from its mole fraction.

       >>> comp = ElementalComposition('B-10H3')
       >>> print(comp)
       {'H': 3.0, 'B-10': 1}
       >>> comp = ElementalComposition('CaCO3MgCO3')
       >>> print(comp)
       {'Mg': 1, 'Ca': 1, 'C': 2, 'O': 6.0}
    """
    def __init__(self, input=None):
        not_a_dict = not_a_string = False
        try:
            elements = list(input.keys())
            for key in keys:
                self[key] = input[key]
        except AttributeError:
            not_a_dict = True
        if type(input) is type('foo'):
            self._parse_formula(input)
        else:
            not_a_string = True
        if input and not_a_dict and not_a_string:
            raise ValueError(
                "Invalid input to ElementalComposition: "
                "{0}".format(input))
    @property
    def molar_mass(self):
        return sum(
            ELEMENTS[x]['A']*self[x] for x in self)
    def norm_fracs_to_one(self):
        fracsum = sum(self[element] for element in self)
        for element in self:
            self[element] /= fracsum
    def _parse_formula(self, formula):
        for m in _RE_ELEMENTS.finditer(formula):
            element = m.group(1)
            wt = m.group(2)
            if wt:
                wt = float(wt)
            else:
                wt = 1
            try:
                self[element] += wt
            except KeyError:
                self[element] = wt
    def separate_boron(self):
        if 'B' in self:
            for isotope in ('B-10', 'B-11'):
                molefrac = ABUNDANCES[isotope]*self['B']
                if isotope in self:
                    self[isotope] += molefrac
                else:
                    self[isotope] = molefrac
            del self['B']
    def separate_uranium(self):
        if 'U' in self:
            for isotope in ('U-238', 'U-235', 'U-234'):
                molefrac = ABUNDANCES[isotope]*self['U']
                if isotope in self:
                    self[isotope] += molefrac
                else:
                    self[isotope] = molefrac
            del self['U']
    def remove_zero_fracs(self):
        empties = [isotope for isotope in self if self[isotope] == 0.0]
        for isotope in empties:
            del self[isotope]




def add_compositions_by_mole_fracs(comps, mole_fracs, norm=True):
    """Combine a list of compositions according to their mole fractions.

       >>> comps = [ElementalComposition('CaCO3MgCO3')]
       >>> comps.append(ElementalComposition('B-10'))
       >>> fracs = (0.99902, 0.00092)
       >>> total = add_compositions_by_mole_fracs(comps, fracs)
       >>> print(total)
       {'C': 0.19998158364627788, 'Mg': 0.099990791823138941, 'B-10': 9.2081768610526152e-05, 'Ca': 0.099990791823138941, 'O': 0.5999447509388337}
    """
    sumcomp = ElementalComposition()
    for comp, frac in zip(comps, mole_fracs):
        for element in comp:
            try:
                sumcomp[element] += comp[element]*frac
            except KeyError:
                sumcomp[element] = comp[element]*frac
    if norm:
        sumcomp.norm_fracs_to_one()
    return sumcomp


def add_compositions_by_mass_fracs(comps, mass_fracs, norm=True):
    """Combine a list of compositions according to their mass fractions.

       >>> comps = [ElementalComposition('CaCO3MgCO3')]
       >>> comps.append(ElementalComposition('B-10'))
       >>> fracs = (0.99995, 0.00005)
       >>> total = add_compositions_by_mass_fracs(comps, fracs)
       >>> print(total)
       {'C': 0.19998158251894854, 'Mg': 0.099990791259474271, 'B-10': 9.2087405257383425e-05, 'Ca': 0.099990791259474271, 'O': 0.59994474755684557}
    """
    mole_fracs = _mass_fracs_to_mol_fracs(comps, mass_fracs)
    return add_compositions_by_mole_fracs(comps, mole_fracs, norm)


def _mass_fracs_to_mol_fracs(comps, mass_fracs):
    mole_fracs = [f/c.molar_mass for (c, f) in zip(comps,mass_fracs)]
    tot = float(sum(mole_fracs))
    return [f/tot for f in mole_fracs]


_CARD_HEADER = """c
c    ===================================================================
c    ==== Material #    {0:d}
c    ===================================================================
c    Name    = {1}
c    Density =    {2:.4f} g/cc
c"""
def get_material_card(name, density, composition, material_number=1):
    """Return a string containing an mcnp material card.

       'name': name of the material
       'density': density of the material in g/mL
       'composition': An ElementComposition object describing the material.
       'material_number': MCNP material number for the card.
       >>> comps = [ElementalComposition('CaCO3MgCO3')]
       >>> comps.append(ElementalComposition('B-10'))
       >>> fracs = (0.99995, 0.00005)
       >>> total = add_compositions_by_mass_fracs(comps, fracs)
       >>> card = get_material_card('formation',2.851, total)
       >>> print(card)
       c
       c    ===================================================================
       c    ==== Material #    1
       c    ===================================================================
       c    Name    = formation
       c    Density =    2.8510 g/cc
       c
          m1  6000.60c 0.199982  12000.60c 0.099991   5010.60c 0.000092
             20000.60c 0.099991   8016.60c 0.599945
    """
    header = _CARD_HEADER.format(material_number, name, density)
    lines = header.split('\n')
    m = "m{0:d}".format(material_number)
    leader = "{0:>5}".format(m)
    line = [leader]
    composition.separate_boron() # no 5000 library in MCNP5 or MCNP6
    composition.separate_uranium() # no 92000 library in MCNP5 or MCNP6
    composition.remove_zero_fracs() # no need to list isotopes that aren't there
    elements = list(composition.keys())
    tmpdf = pd.DataFrame({'Z':[atomic_number(element) for element in elements],
                          'A':[atomic_mass(element) for element in elements]})
    tmpdf.index = elements
    sortdf = tmpdf.sort_values(['Z', 'A'])
    sorted_elements = sortdf.index
    #for n,element in enumerate(composition):
    for n,element in enumerate(sorted_elements):
        line.append("{0:>10} {1:.7e} ".format(
            mcnp_library(element),
            composition[element]))
        if (n+1)%3 == 0:
            lines.append("".join(line))
            line = ["     "]
    remainder = "".join(line).rstrip()
    if remainder:
        lines.append(remainder)
    return "\n".join(lines)


if __name__ == "__main__":
    import pprint
    pprint.pprint(ELEMENTS)
    import doctest
    doctest.testmod()

