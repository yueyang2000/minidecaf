ANTLR_JAR ?= /usr/local/lib/antlr-4.8-complete.jar
all:
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 -visitor -o generated MiniDecaf.g4
compile:
	PYTHONPATH='.' python3 -m minidecaf input.c
run:
	spike --isa=RV32G /usr/local/bin/pk a.out
