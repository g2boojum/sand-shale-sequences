#! /usr/bin/env python

import datetime
import random
import numpy as np
import pandas as pd
import mcnpelements as el
from string import Template


class PctTemplate(Template):
    """string.Template class using '%' as the delimeter"""
    delimiter = '%'

submit_header = """Executable = mcnp611.sh
+AccountingGroup = "grant"
Universe = vanilla
should_transfer_files = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
Requirements = ( OpSys == "WINDOWS" && Arch == "X86_64" )
"""

MATERIALS = {"muscovite": {'density': 2.810,
                       'formula': "H 0.096497792 O 0.56992953 Al 0.142631295 B 0.000787623 Si 0.142590863 K 0.047562842 U 0.000000056"},
             "muscovite_no_B": {'density': 2.810,
                                'formula': "H 0.096497792 O 0.56992953 Al 0.142631295 B 0.000787623 Si 0.142590863 K 0.047562842 U 0.000000056"},
             "biotite": {'density': 3.020,
                         'formula': "H 0.09247669 O 0.55282165 Na 0.00295231 Fe 0.05019706 Mg 0.06283923 Al 0.06312393 B 0.00006653 Si 0.12784924 Gd 0.00000003 K 0.03708668 Th 0.00000013 Ca 0.00277122 U 0.00000006 Ti 0.00781523"},
             "glauconite": {'density': 2.960,
                            'formula': "H 0.09576625 O 0.57619703 Na 0.00310464 Fe 0.05860738 Mg 0.01895158 Al 0.03771891 B 0.00094242 Si 0.17460787 Gd 0.00000052 K 0.03124284 Th 0.00000026 Ca 0.0023915 U 0.00000046 Ti 0.00046834"},
             "glauconite_no_B": {'density': 2.960,
                                 'formula': "H 0.09579548 O 0.57701039 Na 0.00310558 Fe 0.05862527 Mg 0.01895736 Al 0.03773042 B 0 Si 0.17466116 Gd 0.00000052 K 0.03125238 Th 0.00000026 Ca 0.00239223 U 0.00000046 Ti 0.00046848"},
             "kaolinite": {'density': 2.520,
                           'formula': "H 0.23699578 O 0.53111474 Na 0 Fe 0.00218428 Mg 0 Al 0.10738722 B 0.00001973 Si 0.11942958 Gd 0.00000126 K 0 Th 0.00000177 Ca 0 U 0.00000049 Ti 0.00286515"},
             "illite_1": {'density': 2.670,
                          'formula': "H 0.1573698 O 0.55959445 Na 0.00085853 Fe 0.02579972 Mg 0.0017708 Al 0.07961133 B 0.00027032 Si 0.15261144 Gd 0.00000091 K 0.01881611 Th 0.00000139 Ca 0.00044771 U 0.00000039 Ti 0.00284709"},
             "illite_1b": {'density': 2.670,
                           'formula': "H 0.15734133 O 0.55911534 Na 0.00085838 Fe 0.02579506 Mg 0.00177048 Al 0.07959693 B 0.00082906 Si 0.15258383 Gd 0.00000091 K 0.0188127 Th 0.00000139 Ca 0.00044763 U 0.00000039 Ti 0.00284657"},
             "illite_2": {'density': 2.740,
                          'formula': "H 0.11310427 O 0.57532271 Na 0.00422046 Fe 0.01603736 Mg 0.00897712 Al 0.09101829 B 0.00028111 Si 0.16507807 Gd 0.00000047 K 0.02171448 Th 0.00000097 Ca 0.00237442 U 0.00000038 Ti 0.00186991"},
             "smectite": {'density': 1.980,
                          'formula': "H 0.410517 O 0.44789456 Na 0.00251317 Fe 0.00206912 Mg 0.00950333 Al 0.03854873 B 0.00002243 Si 0.08639271 Gd 0.00000077 K 0.00147776 Th 0.00000098 Ca 0.00057665 U 0.00000027 Ti 0.00048251"},
             #"chlorite": {'density': 2.710,
             #             'formula': "H 0.23211212 O 0.52231673 Na 0.0025815 Fe 0.04976488 Mg 0.01709284 Al 0.05530441 B 0.00007373 Si 0.10795162 Gd 0.00000108 K 0.00407675 Th 0.00000117 Ca 0.00824994 U 0.0000003 Ti 0.00047294"},
             # replacing chlorite with the chlorite from Herron and Matteson,
             # Nucl Geophys _7_, 383 (1993).
             "chlorite": {'density': 3.42,
                          'formula': "H 0.18722783 O 0.54018843 Na 0.00079736 Fe 0.06827334 Mg 0.03618167 Al 0.06522893 B 0.00003389 Si 0.09136656 Gd 0.00000058 K 0.0018754 Th 0.00000055 Ca 0.0032017 U 0.00000022 Ti 0.00505184 S  0.0005717"},
             "limestone":   {"density": 2.71,  "formula": "CaCO3"},
             "sandstone":   {"density": 2.648, "formula": "SiO2"},
             "dolomite":    {"density": 2.851, "formula": "CaCO3MgCO3"},
             "anhydrite":   {"density": 2.96,  "formula": "CaSO4"},
             "halite":      {"density": 2.17,  "formula": "NaCl"},
             "K-feldspar":  {"density": 2.56,  "formula": "KAlSi3O8"},
             "orthoclase":  {"density": 2.56,  "formula": "KAlSi3O8"},
             "plagioclase": {"density": 2.68,  "formula": "NaCaSi6Al2O16"},
             "siderite":    {"density": 3.96,  "formula": "FeCO3"},
             "pyrite":      {"density": 5.01,  "formula": "Fe2S"},
             "gypsum":      {"density": 2.3,   "formula": "CaSO4H4O2"},
             "water":       {"density": 0.9982071,   "formula": "H2O"},
            }
for key in MATERIALS:
    mat = MATERIALS[key]
    mat['comp'] = el.ElementalComposition(mat['formula'])
    mat['comp'].norm_fracs_to_one()


def get_random_seed():
    random_seed = random.randint(10001, 999999)
    while (random_seed % 2 == 0):
        random_seed = random.randint(10001, 999999)
    return random_seed


pct_tol = 1.0e-6
rho_w = MATERIALS['water']['density']
rho_q = MATERIALS['sandstone']['density']


def get_card(row, porosity=0.0, pct_mica=0.0, pct_smectite=20.0):
    rewt = 1.0 # re-weighting factor due to (possible) sandstone porosity
    v_w = float(porosity)/100.0
    name = "Shale mixture for %s_%d (%d mica, %d smectite)" % (row['well'],
                                                               row['sample'],
                                                               pct_mica,
                                                               pct_smectite)
    materials = []
    mass_fracs = []
    densities = []
    compositions = []
    for mat in ('sandstone', 'orthoclase', 'plagioclase',
                'limestone', 'dolomite', 'siderite',
                'pyrite', 'gypsum', 'kaolinite',
                'chlorite'):
        frac = row[mat] / 100.0  # wt frac
        if frac > 0:
            materials.append(mat)
            mass_fracs.append(frac)
            densities.append(MATERIALS[mat]['density'])
            compositions.append(MATERIALS[mat]['comp'])
    mica_frac = pct_mica / 100.0  # wt fraction
    smectite_frac = pct_smectite / 100.0  # wt fraction
    illite_mica_frac = row['illite_mica'] / 100.0  # wt frac
    mat_mica_frac = mica_frac*illite_mica_frac
    if mat_mica_frac > 0:
        materials.append('muscovite')
        mass_fracs.append(mat_mica_frac)
        densities.append(MATERIALS['muscovite']['density'])
        compositions.append(MATERIALS['muscovite']['comp'])
    illite_smectite_frac = row['illite_smectite'] / 100.0  # wt frac
    mat_smectite_frac = smectite_frac*illite_smectite_frac
    if mat_smectite_frac > 0:
        materials.append('smectite')
        mass_fracs.append(mat_smectite_frac)
        densities.append(MATERIALS['smectite']['density'])
        compositions.append(MATERIALS['smectite']['comp'])
    illite_frac = (illite_mica_frac*(1 - mica_frac)
                + illite_smectite_frac*(1 - smectite_frac))
    if illite_frac > 0:
        materials.append('illite_1')
        mass_fracs.append(illite_frac)
        densities.append(MATERIALS['illite_1']['density'])
        compositions.append(MATERIALS['illite_1']['comp'])
    # dry matrix weight percentages might not quite sum to 1
    norm = sum(mass_fracs)
    mass_fracs = [frac/norm for frac in mass_fracs]
    # take care of the sandstone porosity
    ss_frac = mass_fracs[materials.index('sandstone')]
    if ss_frac > 0 and v_w > 0:
        lam = (v_w/(1-v_w))*(rho_w/rho_q)*ss_frac
        rewt = 1.0/(1 + lam)
        materials.append('water')
        mass_fracs.append(lam)
        densities.append(MATERIALS['water']['density'])
        compositions.append(MATERIALS['water']['comp'])
        mass_fracs = rewt*np.array(mass_fracs)
        densities = np.array(densities)

    density = 1/sum(mass_fracs/densities)
    composition = el.add_compositions_by_mass_fracs(compositions, mass_fracs)
    card = el.get_material_card(name, density, composition, 3)
    return density, name, card


fp = open("ctn8tmpl")
deck_template = fp.read()
fp.close()
deck_template = PctTemplate(deck_template)

runfp = open("mcnprun", 'w')
runfp.write(submit_header)
runfp.write('\n')

mixdf = pd.read_csv('XRD.csv')
#mixdf = pd.read_csv('TESTXRD.csv')

filenum = 1
num_repeats = 10
smectite_pcts = (20,)
mica_pcts = (0,)
for idx, row in mixdf.iterrows():
    porosity = 20.0
    for pct_mica in mica_pcts:
        for pct_smectite in smectite_pcts:
            formation_density, formation, formation_card = get_card(row,
                                                                    porosity,
                                                                    pct_mica,
                                                                    pct_smectite)
            for repeat in range(num_repeats):
                d = {}
                d['date'] = str(datetime.date.today())
                filename = "s%05d" % filenum
                d['filename'] = "%sin" % filename
                d['formation'] = formation
                d['formation_card'] = formation_card
                d['formation_density'] = formation_density
                d['porosity'] = porosity
                d['pct_mica'] = pct_mica
                d['pct_smectite'] = pct_smectite
                d['rand_seed'] = get_random_seed()
                new_deck = deck_template.substitute(d)
                outfile = open('%sin' % filename, 'w')
                outfile.write(new_deck)
                outfile.close()
                runfp.write('Log = %s.log\n' % filename)
                runfp.write('Output = %s.out\n' % filename)
                runfp.write('Error = %s.err\n' % filename)
                runfp.write('Arguments = inp=%sin wwinp=ctn8ww ou=%sou ru=%sta\n' % (filename,
                                                                                    filename,
                                                                                    filename))
                runfp.write('transfer_input_files = %sin, ctn8ww\n' % filename)
                runfp.write('queue\n\n')
                filenum += 1

