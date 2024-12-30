%option noyywrap

%{
#include <stdio.h>
#include <stdlib.h>
#include "parser.hpp"
#define P 1234577

extern int yylex();
%}

%%

                    // ignore:
[ \t]  ;                //blanks
^#(.|\\\n)*\n ;         //comments

    //numbers
[[:digit:]]+ { 
    yylval = atoi(yytext); 
    return NUM; 
}
    //identifiers
[_a-z]+ {return PIDENTIFIER}

