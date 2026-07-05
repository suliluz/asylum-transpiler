let argc @ 0;
let sys_year @ 1;
let sys_month @ 2;
let sys_day @ 3;
let sys_hour @ 4;
let sys_minute @ 5;
let sys_second @ 6;
// argv starts at 7, but we can't easily access dynamically sized strings without pointers.

func print_digit(n: byte) {
    let zero = 48;
    zero += n;
    print(zero);
}

func print_num(n: byte) {
    let hundreds = 0;
    let tens = 0;
    let units = 0;
    
    let i = 0;
    while (i != n) {
        units++;
        if (units == 10) {
            units = 0;
            tens++;
            if (tens == 10) {
                tens = 0;
                hundreds++;
            }
        }
        i++;
    }
    
    if (hundreds != 0) {
        print_digit(hundreds);
        print_digit(tens);
        print_digit(units);
    } else {
        if (tens != 0) {
            print_digit(tens);
            print_digit(units);
        } else {
            print_digit(units);
        }
    }
}

