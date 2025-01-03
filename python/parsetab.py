
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "ADD ASSIGN BEGIN COM COMMA DIV DO DOWNTO ELSE END ENDFOR ENDIF ENDWHILE EQ FOR FROM GEQ GT IF IS LBR LEQ LPAR LT MOD MUL NEQ NUM PID PROCEDURE PROGRAM RBR READ REPEAT RPAR SEMICOLON SUB T THEN TO UNTIL WHILE WRITEprogram_all : procedures mainprocedures : procedures PROCEDURE proc_head IS declarations BEGIN commands ENDprocedures : procedures PROCEDURE proc_head IS BEGIN commands ENDprocedures : emptymain : PROGRAM IS declarations BEGIN commands ENDmain : PROGRAM IS BEGIN commands ENDcommands : commands commandcommands : commandcommand : identifier ASSIGN expression SEMICOLONcommand : IF condition THEN commands ELSE commands ENDIFcommand : IF condition THEN commands ENDIFcommand : WHILE condition DO commands ENDWHILEcommand : REPEAT commands UNTIL condition SEMICOLONcommand : FOR PID FROM value TO value DO commands ENDFORcommand : FOR PID FROM value DOWNTO value DO commands ENDFORcommand : proc_callcommand : READ identifier SEMICOLONcommand : WRITE value SEMICOLONproc_head : PID LPAR args_decl RPARproc_call : PID LPAR args RPARdeclarations : declarations COMMA PIDdeclarations : declarations COMMA PID LBR NUM ':' NUM RBR declarations : PIDdeclarations :  PID LBR NUM ':' NUM RBRargs_decl : args_decl PIDargs_decl : args_decl T PIDargs_decl : PIDargs_decl : T PIDargs : args PIDargs : PIDexpression : valueexpression : value ADD valueexpression : value SUB valueexpression : value MUL valueexpression : value DIV valueexpression : value MOD valuecondition : value EQ valuecondition : value NEQ valuecondition : value GT valuecondition : value LT valuecondition : value GEQ valuecondition : value LEQ valuevalue : NUMvalue : identifieridentifier : PIDidentifier : PID LBR PID RBRidentifier : PID LBR NUM RBRempty :"
    
_lr_action_items = {'PROCEDURE':([0,2,3,59,82,],[-48,5,-4,-3,-2,]),'PROGRAM':([0,2,3,59,82,],[-48,6,-4,-3,-2,]),'$end':([1,4,42,61,],[0,-1,-6,-5,]),'PID':([5,9,10,11,13,16,17,18,19,20,21,22,23,25,26,27,28,30,31,32,34,35,36,38,39,40,43,44,51,53,54,58,60,65,66,67,68,69,70,71,72,73,74,77,78,79,80,84,85,86,87,88,89,90,97,102,103,111,112,113,114,115,116,119,123,124,125,126,127,128,129,],[8,14,14,17,29,29,-27,36,39,29,41,29,-8,49,49,29,52,-16,49,49,29,29,-25,60,-28,29,-7,49,29,75,77,29,-26,29,49,49,49,49,49,49,29,49,49,-30,102,-17,-18,-9,49,49,49,49,49,29,29,-29,-20,29,-11,-12,-13,49,49,29,-10,29,29,29,29,-14,-15,]),'IS':([6,7,37,],[9,10,-19,]),'LPAR':([8,29,],[11,54,]),'BEGIN':([9,10,12,14,15,41,117,122,],[13,16,20,-23,34,-21,-24,-22,]),'T':([11,17,18,36,39,60,],[19,-27,38,-25,-28,-26,]),'COMMA':([12,14,15,41,117,122,],[21,-23,21,-21,-24,-22,]),'IF':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[25,25,25,25,-8,25,-16,25,25,25,-7,25,25,25,25,-17,-18,-9,25,25,-20,25,-11,-12,-13,25,-10,25,25,25,25,-14,-15,]),'WHILE':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[26,26,26,26,-8,26,-16,26,26,26,-7,26,26,26,26,-17,-18,-9,26,26,-20,26,-11,-12,-13,26,-10,26,26,26,26,-14,-15,]),'REPEAT':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[27,27,27,27,-8,27,-16,27,27,27,-7,27,27,27,27,-17,-18,-9,27,27,-20,27,-11,-12,-13,27,-10,27,27,27,27,-14,-15,]),'FOR':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[28,28,28,28,-8,28,-16,28,28,28,-7,28,28,28,28,-17,-18,-9,28,28,-20,28,-11,-12,-13,28,-10,28,28,28,28,-14,-15,]),'READ':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[31,31,31,31,-8,31,-16,31,31,31,-7,31,31,31,31,-17,-18,-9,31,31,-20,31,-11,-12,-13,31,-10,31,31,31,31,-14,-15,]),'WRITE':([13,16,20,22,23,27,30,34,35,40,43,51,58,65,72,79,80,84,90,97,103,111,112,113,114,119,123,124,125,126,127,128,129,],[32,32,32,32,-8,32,-16,32,32,32,-7,32,32,32,32,-17,-18,-9,32,32,-20,32,-11,-12,-13,32,-10,32,32,32,32,-14,-15,]),'LBR':([14,29,41,49,],[33,53,62,53,]),'RPAR':([17,18,36,39,60,77,78,102,],[-27,37,-25,-28,-26,-30,103,-29,]),'END':([22,23,30,35,40,43,58,79,80,84,103,112,113,114,123,128,129,],[42,-8,-16,59,61,-7,82,-17,-18,-9,-20,-11,-12,-13,-10,-14,-15,]),'UNTIL':([23,30,43,51,79,80,84,103,112,113,114,123,128,129,],[-8,-16,-7,73,-17,-18,-9,-20,-11,-12,-13,-10,-14,-15,]),'ELSE':([23,30,43,79,80,84,90,103,112,113,114,123,128,129,],[-8,-16,-7,-17,-18,-9,111,-20,-11,-12,-13,-10,-14,-15,]),'ENDIF':([23,30,43,79,80,84,90,103,112,113,114,119,123,128,129,],[-8,-16,-7,-17,-18,-9,112,-20,-11,-12,-13,123,-10,-14,-15,]),'ENDWHILE':([23,30,43,79,80,84,97,103,112,113,114,123,128,129,],[-8,-16,-7,-17,-18,-9,113,-20,-11,-12,-13,-10,-14,-15,]),'ENDFOR':([23,30,43,79,80,84,103,112,113,114,123,126,127,128,129,],[-8,-16,-7,-17,-18,-9,-20,-11,-12,-13,-10,128,129,-14,-15,]),'ASSIGN':([24,29,100,101,],[44,-45,-46,-47,]),'NUM':([25,26,32,33,44,53,62,66,67,68,69,70,71,73,74,81,85,86,87,88,89,105,115,116,],[47,47,47,57,47,76,83,47,47,47,47,47,47,47,47,104,47,47,47,47,47,118,47,47,]),'THEN':([45,47,48,49,91,92,93,94,95,96,100,101,],[65,-43,-44,-45,-37,-38,-39,-40,-41,-42,-46,-47,]),'EQ':([46,47,48,49,100,101,],[66,-43,-44,-45,-46,-47,]),'NEQ':([46,47,48,49,100,101,],[67,-43,-44,-45,-46,-47,]),'GT':([46,47,48,49,100,101,],[68,-43,-44,-45,-46,-47,]),'LT':([46,47,48,49,100,101,],[69,-43,-44,-45,-46,-47,]),'GEQ':([46,47,48,49,100,101,],[70,-43,-44,-45,-46,-47,]),'LEQ':([46,47,48,49,100,101,],[71,-43,-44,-45,-46,-47,]),'SEMICOLON':([47,48,49,55,56,63,64,91,92,93,94,95,96,98,100,101,106,107,108,109,110,],[-43,-44,-45,79,80,84,-31,-37,-38,-39,-40,-41,-42,114,-46,-47,-32,-33,-34,-35,-36,]),'ADD':([47,48,49,64,100,101,],[-43,-44,-45,85,-46,-47,]),'SUB':([47,48,49,64,100,101,],[-43,-44,-45,86,-46,-47,]),'MUL':([47,48,49,64,100,101,],[-43,-44,-45,87,-46,-47,]),'DIV':([47,48,49,64,100,101,],[-43,-44,-45,88,-46,-47,]),'MOD':([47,48,49,64,100,101,],[-43,-44,-45,89,-46,-47,]),'DO':([47,48,49,50,91,92,93,94,95,96,100,101,120,121,],[-43,-44,-45,72,-37,-38,-39,-40,-41,-42,-46,-47,124,125,]),'TO':([47,48,49,99,100,101,],[-43,-44,-45,115,-46,-47,]),'DOWNTO':([47,48,49,99,100,101,],[-43,-44,-45,116,-46,-47,]),'FROM':([52,],[74,]),':':([57,83,],[81,105,]),'RBR':([75,76,104,118,],[100,101,117,122,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program_all':([0,],[1,]),'procedures':([0,],[2,]),'empty':([0,],[3,]),'main':([2,],[4,]),'proc_head':([5,],[7,]),'declarations':([9,10,],[12,15,]),'args_decl':([11,],[18,]),'commands':([13,16,20,27,34,65,72,111,124,125,],[22,35,40,51,58,90,97,119,126,127,]),'command':([13,16,20,22,27,34,35,40,51,58,65,72,90,97,111,119,124,125,126,127,],[23,23,23,43,23,23,43,43,43,43,23,23,43,43,23,43,23,23,43,43,]),'identifier':([13,16,20,22,25,26,27,31,32,34,35,40,44,51,58,65,66,67,68,69,70,71,72,73,74,85,86,87,88,89,90,97,111,115,116,119,124,125,126,127,],[24,24,24,24,48,48,24,55,48,24,24,24,48,24,24,24,48,48,48,48,48,48,24,48,48,48,48,48,48,48,24,24,24,48,48,24,24,24,24,24,]),'proc_call':([13,16,20,22,27,34,35,40,51,58,65,72,90,97,111,119,124,125,126,127,],[30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,]),'condition':([25,26,73,],[45,50,98,]),'value':([25,26,32,44,66,67,68,69,70,71,73,74,85,86,87,88,89,115,116,],[46,46,56,64,91,92,93,94,95,96,46,99,106,107,108,109,110,120,121,]),'expression':([44,],[63,]),'args':([54,],[78,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program_all","S'",1,None,None,None),
  ('program_all -> procedures main','program_all',2,'p_program_all','compiler.py',104),
  ('procedures -> procedures PROCEDURE proc_head IS declarations BEGIN commands END','procedures',8,'p_procedures_decl','compiler.py',110),
  ('procedures -> procedures PROCEDURE proc_head IS BEGIN commands END','procedures',7,'p_procedures_no_decl','compiler.py',114),
  ('procedures -> empty','procedures',1,'p_procedures_empty','compiler.py',119),
  ('main -> PROGRAM IS declarations BEGIN commands END','main',6,'p_main_decl','compiler.py',127),
  ('main -> PROGRAM IS BEGIN commands END','main',5,'p_main_no_decl','compiler.py',131),
  ('commands -> commands command','commands',2,'p_commands_commands','compiler.py',136),
  ('commands -> command','commands',1,'p_commands_end','compiler.py',141),
  ('command -> identifier ASSIGN expression SEMICOLON','command',4,'p_command_assign','compiler.py',148),
  ('command -> IF condition THEN commands ELSE commands ENDIF','command',7,'p_command_if_else','compiler.py',153),
  ('command -> IF condition THEN commands ENDIF','command',5,'p_command_if','compiler.py',157),
  ('command -> WHILE condition DO commands ENDWHILE','command',5,'p_command_while','compiler.py',161),
  ('command -> REPEAT commands UNTIL condition SEMICOLON','command',5,'p_command_repeat_until','compiler.py',165),
  ('command -> FOR PID FROM value TO value DO commands ENDFOR','command',9,'p_command_for_to','compiler.py',169),
  ('command -> FOR PID FROM value DOWNTO value DO commands ENDFOR','command',9,'p_command_for_downto','compiler.py',173),
  ('command -> proc_call','command',1,'p_command_proc_call','compiler.py',177),
  ('command -> READ identifier SEMICOLON','command',3,'p_command_read','compiler.py',181),
  ('command -> WRITE value SEMICOLON','command',3,'p_command_write','compiler.py',186),
  ('proc_head -> PID LPAR args_decl RPAR','proc_head',4,'p_proc_head','compiler.py',192),
  ('proc_call -> PID LPAR args RPAR','proc_call',4,'p_proc_call','compiler.py',197),
  ('declarations -> declarations COMMA PID','declarations',3,'p_declarations_decl_pid','compiler.py',202),
  ('declarations -> declarations COMMA PID LBR NUM : NUM RBR','declarations',8,'p_declarations_decl_tab','compiler.py',208),
  ('declarations -> PID','declarations',1,'p_declarations_pid','compiler.py',213),
  ('declarations -> PID LBR NUM : NUM RBR','declarations',6,'p_declarations_tab','compiler.py',219),
  ('args_decl -> args_decl PID','args_decl',2,'p_args_decl_ards_pid','compiler.py',229),
  ('args_decl -> args_decl T PID','args_decl',3,'p_args_decl_ards_tab','compiler.py',234),
  ('args_decl -> PID','args_decl',1,'p_args_decl_pid','compiler.py',239),
  ('args_decl -> T PID','args_decl',2,'p_args_decl_tab','compiler.py',245),
  ('args -> args PID','args',2,'p_args_args','compiler.py',252),
  ('args -> PID','args',1,'p_args_pid','compiler.py',257),
  ('expression -> value','expression',1,'p_expr_value','compiler.py',264),
  ('expression -> value ADD value','expression',3,'p_expr_add','compiler.py',268),
  ('expression -> value SUB value','expression',3,'p_expr_sub','compiler.py',272),
  ('expression -> value MUL value','expression',3,'p_expr_mul','compiler.py',276),
  ('expression -> value DIV value','expression',3,'p_expr_div','compiler.py',280),
  ('expression -> value MOD value','expression',3,'p_expr_mod','compiler.py',284),
  ('condition -> value EQ value','condition',3,'p_cond_eq','compiler.py',289),
  ('condition -> value NEQ value','condition',3,'p_cond_neq','compiler.py',293),
  ('condition -> value GT value','condition',3,'p_cond_gt','compiler.py',297),
  ('condition -> value LT value','condition',3,'p_cond_lt','compiler.py',301),
  ('condition -> value GEQ value','condition',3,'p_cond_geq','compiler.py',305),
  ('condition -> value LEQ value','condition',3,'p_cond_leq','compiler.py',309),
  ('value -> NUM','value',1,'p_value_num','compiler.py',314),
  ('value -> identifier','value',1,'p_value_id','compiler.py',318),
  ('identifier -> PID','identifier',1,'p_id_pid','compiler.py',323),
  ('identifier -> PID LBR PID RBR','identifier',4,'p_id_tab_pid','compiler.py',327),
  ('identifier -> PID LBR NUM RBR','identifier',4,'p_id_tab_num','compiler.py',331),
  ('empty -> <empty>','empty',0,'p_empty','compiler.py',336),
]
