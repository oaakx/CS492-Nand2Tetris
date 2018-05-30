// bits[] = [49152, 12288, 3072, 768, 192, 48, 12, 3] at ram {17..24} {
	@3
	D=A
	@24
	M=D

	@12
	D=A
	@23
	M=D

	@48
	D=A
	@22
	M=D

	@192
	D=A
	@21
	M=D

	@768
	D=A
	@20
	M=D

	@3072
	D=A
	@19
	M=D

	@12288
	D=A
	@18
	M=D

	@24576
	D=A
	D=D+A
	@17
	M=D
// }

// row_offset = 0 at ram {R0} {
	@R0
	M=0
// }

// col_offset = 31 at ram {R1} {
	@31
	D=A
	@R1
	M=D
// }

// index = 0 at ram {R2} {
	@R2
	M=0
// }

// while (row_offset < 8192) {
	(LOOP)
	
	@8192
	D=A
	@R0
	D=M-D

	@END_LOOP
	D; JGE  // row_offset >= 8192
	

	// draw {
		// screen_addr = 16384 + row_offset + col_offset at ram {R3} {
			@16384
			D=A
			@R0
			D=D+M
			@R1
			D=D+M
			@R3
			M=D
		// }


		// curbits = bits[index] at reg {D} {
			@17
			D=A
			@R2
			A=D+M
			D=M
		// }

		// ram[screen_addr] = curbits {
			@R3
			A=M // load address from R3
			M=D
		// }
	// }


	// row_offset += 32 {
		@32
		D=A
		@R0
		M=M+D
	// }

	// index += 1 {
		@R2
		M=M+1
	// }


	// if (index >= 8) {
		@8
		D=A
		@R2
		D=M-D

		@END_IF
		D; JLT // index < 8

		// index = 0 {
			@R2
			M=0
		// }

		// col_offset -= 1 {
			@R1
			M=M-1
		// }

		(END_IF)
	// }

	@LOOP
	0; JMP
	(END_LOOP)

// }

// terminate
(INFINITE_LOOP)
@INFINITE_LOOP
0; JMP