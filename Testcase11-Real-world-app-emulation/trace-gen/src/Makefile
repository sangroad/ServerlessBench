CC=g++
CXXFLAGS=-Wall
INCLUDES=
LDFLAGS=
LIBS=-lyaml-cpp

SRCS=runWorkload.cpp
OBJS=$(SRCS:.cpp=.o)
PROG=run

all: $(PROG)

debug: CXXFLAGS=-Wall -g -DDEBUG -fsanitize=address
debug: LDFLAGS=-fsanitize=address
debug: $(PROG)

.cpp.o:
	$(CC) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

$(PROG): $(OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(OBJS) $(LDFLAGS) $(LIBS)

clean:
	$(RM) *.o *~ $(PROG)
