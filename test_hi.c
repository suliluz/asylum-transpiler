#include <stdio.h>
#include <stdlib.h>
#define TAPE_SIZE 1048576

int main() {
    unsigned char* tape_start = calloc(TAPE_SIZE, sizeof(unsigned char));
    unsigned char* ptr = tape_start;

    ptr -= 1023; if (ptr < tape_start) ptr += TAPE_SIZE;
    *ptr = 1;

    ptr += 1023; if (ptr >= tape_start + TAPE_SIZE) ptr -= TAPE_SIZE;
    
    printf("val at 1023 offset: %d\n", *(tape_start + TAPE_SIZE - 1023));

    return 0;
}
