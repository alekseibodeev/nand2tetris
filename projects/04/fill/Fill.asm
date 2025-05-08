// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

  @screen
  M = 0
  @SCREEN
  D = A

(LOOP)
  @KBD
  D = M
  @WHITE
  D;JEQ
  @BLACK
  0;JMP

(WHITE)
  @screen
  D = M
  @SCREEN
  A = D + A
  M = 0
  @screen
  D = M
  @LOOP
  D;JEQ
  @screen
  M = M - 1
  @LOOP
  0;JMP

(BLACK)
  @screen
  D = M
  @SCREEN
  A = D + A
  M = -1
  @screen
  D = M
  @8191
  D = D - A
  @LOOP
  D;JEQ
  @screen
  M = M + 1
  @LOOP
  0;JMP
