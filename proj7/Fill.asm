// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// while (true) {
	(INFINITE_LOOP)

	// index = 16384 at reg {R0} {
		@16384
		D=A
		@R0
		M=D
	// }

	// bits = (key.down ? 65535 : 0) at reg {R1} {
		
		@24576
		D=M
		@IF
		D; JNE // key.down != 0

		// else {
			// bits = 0 {
				@R1
				M=0
			// }

			@END_IF
			0; JMP
		// }

		// if (key.down != 0) {
			(IF)
			
			// bits = 65535 {
				@32767
				D=A
				D=A+D
				D=D+1
				@R1
				M=D
			// }

			(END_IF)
		// }
		
	// }

	// while (index < 24576) {
		(LOOP)

		@24576
		D=A
		@R0
		D=M-D

		@END_LOOP
		D; JGE // index >= 24576

		// ram[index] = bits {
			@R1
			D=M
			@R0
			A=M
			M=D
		// }

		// index += 1 {
			@R0
			M=M+1
		// }

		@LOOP
		0; JMP
		(END_LOOP)
	// }

	@INFINITE_LOOP
	0; JMP
// }