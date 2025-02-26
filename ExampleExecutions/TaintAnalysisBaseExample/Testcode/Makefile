# Java compiler
JC = javac

# Source directory
SRCDIR = .

# Java source files
SOURCES = $(wildcard *.java)

# Class files
CLASSES = $(SOURCES:.java=.class)

# Default target
all: $(CLASSES)

# Compilation rule
%.class: %.java
	$(JC) $(SOURCES)

# Clean target
clean:
	rm -f testcode/*.class

# Run target
run: all
	java testcode.IndirectStringLeak 