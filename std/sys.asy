let argc @ 10;
let sys_year @ 11;
let sys_month @ 12;
let sys_day @ 13;
let sys_hour @ 14;
let sys_minute @ 15;
let sys_second @ 16;
// argv starts at 17, but we can't easily access dynamically sized strings without pointers.

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

