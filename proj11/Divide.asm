@R2
M=0
@R0
D=M
@R3
M=D
(R1_LE_R3)
	@R1
	D=M
	@cursft
	M=D
	@nextsft
	M=D
	@two
	M=1
	@R3
	D=D-M
	@END_R1_LE_R3
	D; JGT
	(CURSFT_LE_R3)
		@nextsft
		D=M
		MD=D+M
		@END_CURSFT_LE_R3
		D; JLT // break if nextsft is negative
		@R3
		D=M-D
		@END_CURSFT_LE_R3
		D; JLT // break if R3 < nextsft
		@cursft
		D=M
		M=D+M
		@two
		D=M
		M=D+M
		@CURSFT_LE_R3
		0; JMP
	(END_CURSFT_LE_R3)
	@two
	D=M
	@R2
	M=M+D
	@cursft
	D=M
	@R3
	M=M-D
	@R1_LE_R3
	0; JMP
(END_R1_LE_R3)

(A_TICK_CLOSER_TO_DEATH)
@A_TICK_CLOSER_TO_DEATH
0; JMP