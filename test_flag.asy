import "std/sys.asy";
func main() {
    let x = 10;
    let y = 0;
    let res = x / y;
    print("ERR: ");
    print_num(__err_flag);
    print("\n");
}
main();
