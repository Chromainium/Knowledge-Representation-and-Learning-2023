# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 12:13:12 2023

@author: chels
"""
from sympy.core.symbol import Symbol
from sympy.logic.boolalg import And, Or, Not

class DimacsMapping:
    def __init__(self):
        self._symbol_to_variable = {}
        self._variable_to_symbol = {}
        self._total_variables = 0

    @property
    def total_variables(self):
        return self._total_variables

    def new_variable(self):
        self._total_variables += 1
        return self._total_variables

    def get_variable_for(self, symbol):
        result = self._symbol_to_variable.get(symbol)
        if result is None:
            result = self.new_variable()
            self._symbol_to_variable[symbol] = result
            self._variable_to_symbol[result] = symbol
        return result

    def get_symbol_for(self, variable):
        #returning literals as either themselves or "not"
        if variable < 0:
          variable *= -1
          return 'not ' + str(self._variable_to_symbol[variable])
        else:
          return self._variable_to_symbol[variable]

    def __str__(self) -> str:
        return str(self._variable_to_symbol)
    

class DimacsFormula:
    def __init__(self, mapping, clauses):
        self._mapping = mapping
        self._clauses = clauses

    @property
    def mapping(self):
        return self._mapping

    @property
    def clauses(self):
        return self._clauses

    def __str__(self):
        header = f"p wcnf {self._mapping.total_variables} {len(self._clauses)}"
        body = "\n".join(
            " ".join([str(literal) for literal in clause] + ["0"])
            for clause in self._clauses
        )

        return "\n".join([header, body])
    
    
def to_dimacs_formula(sympy_cnf, dimacs_mapping):
    dimacs_mapping = dimacs_mapping #DimacsMapping()
    dimacs_clauses = []
    
    def clause_to_dimacs(sympy_clause):
        assert type(sympy_clause) == Or
        dimacs_clause = []
        for sympy_literal in sympy_clause.args:
            if type(sympy_literal) == Not:
                sympy_symbol, polarity = sympy_literal.args[0], -1
            elif type(sympy_literal) == Symbol:
                sympy_symbol, polarity = sympy_literal, 1
            else:
                raise AssertionError("invalid cnf")
    
            dimacs_variable = dimacs_mapping.get_variable_for(sympy_symbol)
            dimacs_literal = dimacs_variable * polarity
            dimacs_clause.append(dimacs_literal)
            
        return dimacs_clause
      
    if type(sympy_cnf) == And:
        for sympy_clause in sympy_cnf.args:
            dimacs_clause = clause_to_dimacs(sympy_clause)
            dimacs_clauses.append(dimacs_clause)

    else:
        dimacs_clause = clause_to_dimacs(sympy_cnf)
        dimacs_clauses.append(dimacs_clause)

    return DimacsFormula(dimacs_mapping, dimacs_clauses)