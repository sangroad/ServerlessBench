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

all: $(PROG)

debug: CXXFLAGS=-Wall -g -DDEBUG -fsanitize=address
debug: LDFLAGS=-fsanitize=address
debug: $(PROG)

success: CXXFLAGS=-Wall -g -DDEBUG -fsanitize=address
success: $(SUC_PROG)

.cpp.o:
	$(CC) $(CXXFLAGS) $(INCLUDES) -c -o $@ $<

$(PROG): $(OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(OBJS) $(LDFLAGS) $(LIBS)

$(SUC_PROG): $(SUC_OBJS)
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $@ $(SUC_OBJS) $(LDFLAGS) $(SUC_LIBS)

clean:
	$(RM) *.o *~ $(PROG)
