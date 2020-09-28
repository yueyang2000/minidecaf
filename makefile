ANTLR_JAR ?= /usr/local/lib/antlr-4.8-complete.jar

all:
	cd minidecaf && java -jar $(ANTLR_JAR) -Dlanguage=Python3 -visitor -o generated MiniDecaf.g4

clean:
	rm -rf minidecaf/generated