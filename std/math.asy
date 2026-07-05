// Math Standard Library for Asylum

func min(a: byte, b: byte) {
    let i = 0;
    let found = 0;
    let res = 0;
    while (found != 1) {
        if (i == a) {
            res = a;
            found = 1;
        } else {
            if (i == b) {
                res = b;
                found = 1;
            }
        }
        i++;
    }
    return res;
}

func max(a: byte, b: byte) {
    let i = 255;
    let found = 0;
    let res = 0;
    while (found != 1) {
        if (i == a) {
            res = a;
            found = 1;
        } else {
            if (i == b) {
                res = b;
                found = 1;
            }
        }
        i--;
    }
    return res;
}

func mul(a: byte, b: byte) {
    let res = 0;
    let i = 0;
    while (i != b) {
        res += a;
        i++;
    }
    return res;
}

func div(a: byte, b: byte) {
    if (b == 0) { 
        return 255; 
    }
    
    let q = 0;
    let current_b = 0;
    let i = 0;
    let found = 0;
    
    while (found != 1) {
        if (i == a) {
            found = 1;
        } else {
            current_b++;
            if (current_b == b) {
                q++;
                current_b = 0;
            }
            i++;
        }
    }
    return q;
}

func mod(a: byte, b: byte) {
    if (b == 0) { 
        return 255; 
    }
    
    let q = 0;
    let current_b = 0;
    let i = 0;
    let found = 0;
    
    while (found != 1) {
        if (i == a) {
            found = 1;
        } else {
            current_b++;
            if (current_b == b) {
                q++;
                current_b = 0;
            }
            i++;
        }
    }
    return current_b;
}

func pow(base: byte, exp: byte) {
    if (exp == 0) { 
        return 1; 
    }
    let res = 1;
    let i = 0;
    while (i != exp) {
        res = mul(res, base);
        i++;
    }
    return res;
}

func abs(a: byte) {
    let i = 0;
    let found = 0;
    let is_neg = 0;
    while (found != 1) {
        if (i == a) {
            found = 1;
        } else {
            if (i == 128) {
                is_neg = 1;
                found = 1;
            }
        }
        i++;
    }
    
    if (is_neg == 1) {
        let res = 0;
        res -= a;
        return res;
    } else {
        return a;
    }
}
