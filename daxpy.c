#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define VECTOR_SIZE 10000
#define NUM_THREADS 8

float x[VECTOR_SIZE], y[VECTOR_SIZE], a = 2.0;

typedef struct {
    int start;
    int end;
} ThreadArgs;

void *daxpy_thread(void *arg) {
    ThreadArgs *data = (ThreadArgs *)arg;
    for (int i = data->start; i < data->end; ++i) {
        y[i] = a * x[i] + y[i];
    }
    pthread_exit(NULL);
}

int main() {
    pthread_t threads[NUM_THREADS];
    ThreadArgs threadData[NUM_THREADS];
    int chunk_size = VECTOR_SIZE / NUM_THREADS;

    // Initialize vectors
    for (int i = 0; i < VECTOR_SIZE; ++i) {
        x[i] = i * 2.0;
        y[i] = i * 3.0;
    }

    // Create threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        threadData[i].start = i * chunk_size;
        threadData[i].end = (i == NUM_THREADS - 1) ? VECTOR_SIZE : (i + 1) * chunk_size;
        pthread_create(&threads[i], NULL, daxpy_thread, &threadData[i]);
    }

    // Join threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    printf("Thread Computation complete.\n");
    return 0;
}
