CXX = g++
CXXFLAGS = -std=c++17 -Wall -O2 -pthread

# All your project sources
SRCS = main.cpp hashtable.cpp zset.cpp list.cpp heap.cpp thread_pool.cpp common.cpp
OBJS = $(SRCS:.cpp=.o)

# Output binary
TARGET = datastore

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
