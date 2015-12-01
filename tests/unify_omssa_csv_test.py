#!/usr/bin/env python3.4
# encoding: utf-8
'''

Test the unify_csv function for omssa engine

'''
import ursgal
import csv
import pickle
import os

R = ursgal.UController(
    profile = 'LTQ XL low res',
    params  = {
        'database': os.path.join(
            'data',
            'BSA.fasta'
        )
    },
    force  = False
)

scan_rt_lookup = pickle.load(
    open(
        os.path.join(
            'data',
            '_test_ursgal_lookup.pkl'
        )
        ,
        'rb'
    )
)

unify_csv_main = R.unodes['unify_csv_1_0_0']['class'].import_engine_as_python_function()

input_csv = os.path.join(
    'data',
    'omssa_2_1_9',
    'test_BSA1_omssa_2_1_9.csv'
)
output_csv = os.path.join(
    'data',
    'omssa_2_1_9',
    'test_BSA1_omssa_2_1_9_unified.csv'
)

unify_csv_main(
    input_file     = input_csv,
    output_file    = output_csv,
    scan_rt_lookup = scan_rt_lookup,
    params = {
        'aa_exception_dict' : {
            'U' : {
                'unimod_name' : 'Delta:S(-1)Se(1)',
                'original_aa' : 'C',
                'unimod_name_with_cam': 'SecCarbamidomethyl',
            },
        },
        'modifications' : [
            'M,opt,any,Oxidation',        # Met oxidation
            'C,fix,any,Carbamidomethyl',  # Carbamidomethylation
            '*,opt,Prot-N-term,Acetyl',    # N-Acteylation
            # '*,opt,any,Deamidated:18O(1)'  # test case for ':' in unimod, is Deamidated:18O(1), with heavy oxygen, but this fails right now!!!
            'R,opt,any,Label:13C(5)15N(1)', # we have to test SILAC!!!!
            'R,opt,any,Label:13C(6)15N(2)' # we have to test SILAC!!!!
        ],
        'label' : '',
        'decoy_tag': 'decoy_',
    },
    search_engine  = 'omssa_2_1_9',
)

ident_list = [ ]
for line_dict in csv.DictReader(open(output_csv, 'r')):
    ident_list.append( line_dict )
# print(ident_list)

def unify_omssa_test():
    for test_id, test_dict in enumerate(ident_list):
        yield unify_omssa, test_dict


def unify_omssa( test_dict ):
    assert 'uCalc m/z' in test_dict.keys()

    for key in [
            'Retention Time (s)',
            'Spectrum ID',
            'Modifications',
            'Spectrum Title'
        ]:
        test_value = test_dict[key]
        expected_value = test_dict['Expected {0}'.format(key)]
        if key == 'Retention Time (s)':
            test_value      = round(float(test_value), 4)
            expected_value  = round(float(expected_value), 4)

        assert test_value == expected_value


if __name__ == '__main__':
    print(__doc__)
    for test_id, test_dict in enumerate(ident_list):
        unify_omssa(test_dict)