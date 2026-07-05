#include <stdio.h>
#include <stdlib.h>
int main() {
    unsigned char* tape = calloc(1048576, 1);
    unsigned char* ptr = tape;
    ptr -= 1023;
    printf("ptr < tape ? %d\n", ptr < tape);
    if (ptr < tape) ptr += 1048576;
    printf("diff from tape: %ld\n", ptr - tape);
    return 0;
}
