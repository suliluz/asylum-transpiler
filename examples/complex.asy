// Complex Asylum Test
// Draws an ASCII pyramid and uses multiple features

let title: string[21] = "Asylum Pyramid!\n\n";
for (let i = 0; i != 21; i++) {
    print(title[i]);
}

let height = 10;
let row = 0;
let space_char = 32; // ' '
let star_char = 42;  // '*'
let hash_char = 35;  // '#'

while (row != height) {
    let spaces = height;
    spaces -= row;
    spaces--;
    
    // Print leading spaces
    for (let s = 0; s != spaces; s++) {
        print(space_char);
    }
    
    // Print alternating characters based on row parity (simulated by inner tracking)
    // Actually we can just alternate inside the loop
    let chars_to_print = row;
    chars_to_print += row;
    chars_to_print++; // 2*row + 1
    
    let toggle = 0; // 0 for star, 1 for hash
    
    for (let c = 0; c != chars_to_print; c++) {
        if (toggle == 0) {
            print(star_char);
            toggle = 1;
        } else {
            print(hash_char);
            toggle = 0;
        }
    }
    
    print(10); // '\n'
    row++;
}
