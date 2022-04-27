CC=g++
CXXFLAGS=-Wall
INCLUDES=
LDFLAGS=
LIBS=-lyaml-cpp -pthread

SRCS=runWorkload.cpp
OBJS=$(SRCS:.cpp=.o)
PROG=run

SUC_LIBS=-lpthread
SUC_SRCS=runSuccessWorkload.cpp
SUC_OBJS=$(SUC_SRCS:.cpp=.o)
SUC_PROG=success_run

RAND_LIBS=-lyaml-cpp -pthread
RAND_SRCS=runRandWorkload.cpp
RAND_OBJS=$(RAND_SRCS:.cpp=.o)
RAND_PROG=rand_run

all: $(PROG)

debug: CXXFLAGS=-Wall -g -DDEBUG -fsanitize=address
debug: LDFLAGS=-fsanitize=address
debug: $(PROG)

success: CXXFLAGS=-Wall
success: $(SUC_PROG)

rand: CXXFLAGS=-Wall
rand: $(RAND_PROG)

.cpp.o:
	$(CC) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

$(PROG): $(OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(OBJS) $(LDFLAGS) $(LIBS)

$(SUC_PROG): $(SUC_OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(SUC_OBJS) $(LDFLAGS) $(SUC_LIBS)

$(RAND_PROG): $(RAND_OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(RAND_OBJS) $(LDFLAGS) $(RAND_LIBS)

clean:
	$(RM) *.o *~ $(PROG) $(SUC_PROG) $(RAND_PROG)
