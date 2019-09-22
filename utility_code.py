#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      utility_code
# @Brief:     Some randomized code snippets for parsing inputs and executing automaton
# @Created:   Sep/01/2019
# @Author:    Jiahao Cai
#

import random
import copy

class UtilityCode:
  def __init__(self, parse_formula):
    self.parse_formula = parse_formula
  def get_parse_formula(self):
    return random.choice(self.parse_formula)
  
snippet_parseFormula = UtilityCode(
r"""
    /**
     * @param string $formula
     * @param null|\PhpOffice\PhpSpreadsheet\Cell\Cell $pCell
     *
     * @return bool
     */
    private function _parseFormula($formula, Cell $pCell = null)
    {
        if (($matrix = $this->convertMatrixReferences(trim($formula))) === false) {
            return false;
        }
    /**
     * @param string $formula
     * @param null|\PhpOffice\PhpSpreadsheet\Cell\Cell $pCell
     *
     * @return bool
     */
    private function _parseFormula($formula, Cell $pCell = null)
    {
        if (($matrix = $this->convertMatrixReferences(trim($formula))) === false) {
            return false;
        }
        //    If we're using cell caching, then $pCell may well be flushed back to the cache (which detaches the parent worksheet),
        //        so we store the parent worksheet so that we can re-attach it when necessary
        // $pCellParent = ($pCell !== null) ? $pCell->getWorksheet() : null;
 
        $regexpMatchString = '/^(' . self::CALCULATION_REGEXP_FUNCTION .
                                '|' . self::CALCULATION_REGEXP_CELLREF .
                                '|' . self::CALCULATION_REGEXP_NUMBER .
                                '|' . self::CALCULATION_REGEXP_STRING .
                                '|' . self::CALCULATION_REGEXP_OPENBRACE .
                                '|' . self::CALCULATION_REGEXP_NAMEDRANGE .
                                '|' . self::CALCULATION_REGEXP_ERROR .
                                ')/si';

        //    Start with initialisation
        $index = 0;
        $stack = null;
        $output = [];
        $state = $this->cyclicFormulaCounter;
        $padding = "";
        $expectingOperator = false; //    We use this test in syntax-checking the expression to determine when a
                                                    //        - is a negation or + is a positive operator rather than an operation
        $expectingOperand = false; //    We use this test in syntax-checking the expression to determine whether an operand
                                                    //        should be null in a function call
        //    The guts of the lexical parser
        //    Loop through the formula extracting each operator and operand in turn
        $seq = explode(" ", $formula);

        // Debug
        global $debug_len;
        $seq = array_slice($seq, 0, $debug_len);
        while (true) {
            $opCharacter = $seq[$index]; //    Get the first character of the value at the current index position
            $out = "";
            if (isset($matrix[$state][$opCharacter])) {
                $next_state = $matrix[$state][$opCharacter][0];
                $out = $matrix[$state][$opCharacter][1];
            } else {
                $padding = " ";
                $min_val = 0xff;
                $next_state = 0;
                foreach ($matrix[$state] as $word=>$map) {
                    $dist = levenshtein($opCharacter, $word);
                    if ($dist < $min_val) {
                        $min_val = $dist;
                        $next_state = $map[0];
                        $out = $map[1];
                    } else if ($dist == $min_val) {
                        $r = rand(0,1);
                        if ($r == 0) { $next_state = $map[0]; $out = $map[1]; }
                    }
                }
            }
            $output[] = $out;
            $state = $next_state;
            ++$index;
            if ($index >= sizeof($seq)) break;
        }
        return implode($padding, $output);
    }
"""
)

var_matrix_set = ['matrix', 'mtx', 'theMatrix', 'curMatrix']
var_index_set = ['index', 'i', 'n', 'idx', 'curNum']
var_output_set = ['output', 'outArr', 'outTokens', 'ret', 'retTokens']
var_state_set = ['state', 's', 'currentState', 'curState', 'curNode', 'node']
var_padding_set = ['padding', 'pad', 'p', 'delimiter', 'deli']
var_seq_set = ['seq', 'sequence', 'input', 'tokens', 'inputTokens']
var_opcharacter_set = ['opCharacter', 'curToken', 'token', 'thisToken']
var_out_set = ['out', 'curOut', 'curOutToken', 'tempOut', 'tempOutToken']
var_next_state_set = ['nextState', 'nState', 'followingState', 'nextS']
var_minval_set = ['minVal', 'min', 'minValue', 'minimumVal', 'minimumValue']
var_dist_set = ['dist', 'distance', 'distVal', 'curDist', 'curDistVal']
var_word_set = ['word', 'w', 'thisWord', 'theWord', 'wd', 'curWord']
var_map_set = ['map', 'edge', 'curMap', 'curEdge', 'thisMap', 'thisEdge']

this_matrix = random.choice(var_matrix_set)
this_index = random.choice(var_index_set)
this_output = random.choice(var_output_set)
this_state = random.choice(var_state_set)
this_padding = random.choice(var_padding_set)
this_seq = random.choice(var_seq_set)
this_opcharacter = random.choice(var_opcharacter_set)
this_out = random.choice(var_out_set)
this_next_state = random.choice(var_next_state_set)
this_minval = random.choice(var_minval_set)
this_dist = random.choice(var_dist_set)
this_word = random.choice(var_word_set)
this_map = random.choice(var_map_set)


parse_formula_for_loop_template = f"""
    /**
     * @param string $formula
     * @param null|\PhpOffice\PhpSpreadsheet\Cell\Cell $pCell
     *
     * @return bool
     */
    private function _parseFormula($formula, Cell $pCell = null)
    {{
        if ((${this_matrix} = $this->convertMatrixReferences(trim($formula))) === false) {{
            return false;
        }}
        //    If we're using cell caching, then $pCell may well be flushed back to the cache (which detaches the parent worksheet),
        //        so we store the parent worksheet so that we can re-attach it when necessary
        // $pCellParent = ($pCell !== null) ? $pCell->getWorksheet() : null;
 
        $regexpMatchString = '/^(' . self::CALCULATION_REGEXP_FUNCTION .
                                '|' . self::CALCULATION_REGEXP_CELLREF .
                                '|' . self::CALCULATION_REGEXP_NUMBER .
                                '|' . self::CALCULATION_REGEXP_STRING .
                                '|' . self::CALCULATION_REGEXP_OPENBRACE .
                                '|' . self::CALCULATION_REGEXP_NAMEDRANGE .
                                '|' . self::CALCULATION_REGEXP_ERROR .
                                ')/si';

        //    Start with initialisation
        ${this_index} = 0;
        $stack = null;
        ${this_output} = [];
        ${this_state} = $this->cyclicFormulaCounter;
        ${this_padding} = "";
        $expectingOperator = false; //    We use this test in syntax-checking the expression to determine when a
                                                    //        - is a negation or + is a positive operator rather than an operation
        $expectingOperand = false; //    We use this test in syntax-checking the expression to determine whether an operand
                                                    //        should be null in a function call
        //    The guts of the lexical parser
        //    Loop through the formula extracting each operator and operand in turn
        ${this_seq} = explode(" ", $formula);

        while (true) {{
            ${this_opcharacter} = ${this_seq}[${this_index}]; //    Get the first character of the value at the current index position
            ${this_out} = "";
            if (isset(${this_matrix}[${this_state}][${this_opcharacter}])) {{
                ${this_next_state} = ${this_matrix}[${this_state}][${this_opcharacter}][0];
                ${this_out} = ${this_matrix}[${this_state}][${this_opcharacter}][1];
            }} else {{
                ${this_padding} = " ";
                ${this_minval} = 0xff;
                ${this_next_state} = 0;
                foreach (${this_matrix}[${this_state}] as ${this_word}=>${this_map}) {{
                    ${this_dist} = levenshtein(${this_opcharacter}, ${this_word});
                    if (${this_dist} < ${this_minval}) {{
                        ${this_minval} = ${this_dist};
                        ${this_next_state} = ${this_map}[0];
                        ${this_out} = ${this_map}[1];
                    }} else if (${this_dist} == ${this_minval}) {{
                        $r = rand(0,1);
                        if ($r == 0) {{ ${this_next_state} = ${this_map}[0]; ${this_out} = ${this_map}[1]; }}
                    }}
                }}
            }}
            ${this_output}[] = ${this_out};
            ${this_state} = ${this_next_state};
            ++${this_index};
            if (${this_index} >= sizeof(${this_seq})) break;
        }}
        return implode(${this_padding}, ${this_output});
    }}
"""


parse_formula_while_loop_template = f"""
    /**
     * @param string $formula
     * @param null|\PhpOffice\PhpSpreadsheet\Cell\Cell $pCell
     *
     * @return bool
     */
    private function _parseFormula($formula, Cell $pCell = null)
    {{
        if ((${this_matrix} = $this->convertMatrixReferences(trim($formula))) === false) {{
            return false;
        }}
        //    If we're using cell caching, then $pCell may well be flushed back to the cache (which detaches the parent worksheet),
        //        so we store the parent worksheet so that we can re-attach it when necessary
        // $pCellParent = ($pCell !== null) ? $pCell->getWorksheet() : null;
 
        $regexpMatchString = '/^(' . self::CALCULATION_REGEXP_FUNCTION .
                                '|' . self::CALCULATION_REGEXP_CELLREF .
                                '|' . self::CALCULATION_REGEXP_NUMBER .
                                '|' . self::CALCULATION_REGEXP_STRING .
                                '|' . self::CALCULATION_REGEXP_OPENBRACE .
                                '|' . self::CALCULATION_REGEXP_NAMEDRANGE .
                                '|' . self::CALCULATION_REGEXP_ERROR .
                                ')/si';

        //    Start with initialisation
        ${this_index} = 0;
        $stack = null;
        ${this_output} = [];
        ${this_state} = $this->cyclicFormulaCounter;
        ${this_padding} = "";
        $expectingOperator = false; //    We use this test in syntax-checking the expression to determine when a
                                                    //        - is a negation or + is a positive operator rather than an operation
        $expectingOperand = false; //    We use this test in syntax-checking the expression to determine whether an operand
                                                    //        should be null in a function call
        //    The guts of the lexical parser
        //    Loop through the formula extracting each operator and operand in turn
        ${this_seq} = explode(" ", $formula);

        for (${this_index} = 0; ${this_index} < count(${this_seq}); ${this_index}++) {{
            ${this_opcharacter} = ${this_seq}[${this_index}]; //    Get the first character of the value at the current index position
            ${this_out} = "";
            if (isset(${this_matrix}[${this_state}][${this_opcharacter}])) {{
                ${this_next_state} = ${this_matrix}[${this_state}][${this_opcharacter}][0];
                ${this_out} = ${this_matrix}[${this_state}][${this_opcharacter}][1];
            }} else {{
                ${this_padding} = " ";
                ${this_minval} = 0xff;
                ${this_next_state} = 0;
                foreach (${this_matrix}[${this_state}] as ${this_word}=>${this_map}) {{
                    ${this_dist} = levenshtein(${this_opcharacter}, ${this_word});
                    if (${this_dist} < ${this_minval}) {{
                        ${this_minval} = ${this_dist};
                        ${this_next_state} = ${this_map}[0];
                        ${this_out} = ${this_map}[1];
                    }} else if (${this_dist} == ${this_minval}) {{
                        $r = rand(0,1);
                        if ($r == 0) {{ ${this_next_state} = ${this_map}[0]; ${this_out} = ${this_map}[1]; }}
                    }}
                }}
            }}
            ${this_output}[] = ${this_out};
            ${this_state} = ${this_next_state};
        }}
        return implode(${this_padding}, ${this_output});
    }}
"""


parse_formula_foreach_template = f"""
    /**
     * @param string $formula
     * @param null|\PhpOffice\PhpSpreadsheet\Cell\Cell $pCell
     *
     * @return bool
     */
    private function _parseFormula($formula, Cell $pCell = null)
    {{
        if ((${this_matrix} = $this->convertMatrixReferences(trim($formula))) === false) {{
            return false;
        }}
        //    If we're using cell caching, then $pCell may well be flushed back to the cache (which detaches the parent worksheet),
        //        so we store the parent worksheet so that we can re-attach it when necessary
        // $pCellParent = ($pCell !== null) ? $pCell->getWorksheet() : null;
 
        $regexpMatchString = '/^(' . self::CALCULATION_REGEXP_FUNCTION .
                                '|' . self::CALCULATION_REGEXP_CELLREF .
                                '|' . self::CALCULATION_REGEXP_NUMBER .
                                '|' . self::CALCULATION_REGEXP_STRING .
                                '|' . self::CALCULATION_REGEXP_OPENBRACE .
                                '|' . self::CALCULATION_REGEXP_NAMEDRANGE .
                                '|' . self::CALCULATION_REGEXP_ERROR .
                                ')/si';

        //    Start with initialisation
        ${this_index} = 0;
        $stack = null;
        ${this_output} = [];
        ${this_state} = $this->cyclicFormulaCounter;
        ${this_padding} = "";
        $expectingOperator = false; //    We use this test in syntax-checking the expression to determine when a
                                                    //        - is a negation or + is a positive operator rather than an operation
        $expectingOperand = false; //    We use this test in syntax-checking the expression to determine whether an operand
                                                    //        should be null in a function call
        //    The guts of the lexical parser
        //    Loop through the formula extracting each operator and operand in turn
        ${this_seq} = explode(" ", $formula);

        foreach (range(0, count(${this_seq}) - 1) as ${this_index}) {{
            ${this_opcharacter} = ${this_seq}[${this_index}]; //    Get the first character of the value at the current index position
            ${this_out} = "";
            if (isset(${this_matrix}[${this_state}][${this_opcharacter}])) {{
                ${this_next_state} = ${this_matrix}[${this_state}][${this_opcharacter}][0];
                ${this_out} = ${this_matrix}[${this_state}][${this_opcharacter}][1];
            }} else {{
                ${this_padding} = " ";
                ${this_minval} = 0xff;
                ${this_next_state} = 0;
                foreach (${this_matrix}[${this_state}] as ${this_word}=>${this_map}) {{
                    ${this_dist} = levenshtein(${this_opcharacter}, ${this_word});
                    if (${this_dist} < ${this_minval}) {{
                        ${this_minval} = ${this_dist};
                        ${this_next_state} = ${this_map}[0];
                        ${this_out} = ${this_map}[1];
                    }} else if (${this_dist} == ${this_minval}) {{
                        $r = rand(0,1);
                        if ($r == 0) {{ ${this_next_state} = ${this_map}[0]; ${this_out} = ${this_map}[1]; }}
                    }}
                }}
            }}
            ${this_output}[] = ${this_out};
            ${this_state} = ${this_next_state};
        }}
        return implode(${this_padding}, ${this_output});
    }}
"""


utility_code = UtilityCode([parse_formula_while_loop_template, parse_formula_for_loop_template, parse_formula_foreach_template])

