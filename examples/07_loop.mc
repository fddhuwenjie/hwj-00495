// Example 7: Loops - demonstrates while, for loops and nested loops
int factorial(int n) {
    int result = 1;
    int i = 1;
    while (i <= n) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

int sum_range(int start, int end) {
    int sum = 0;
    for (int i = start; i <= end; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

void print_multiplication_table() {
    for (int i = 1; i <= 9; i = i + 1) {
        int row = 0;
        for (int j = 1; j <= i; j = j + 1) {
            row = i * j;
            print(row);
        }
    }
}

void main() {
    int fact5 = factorial(5);
    print(fact5);

    int sum10 = sum_range(1, 10);
    print(sum10);

    int count = 0;
    while (count < 3) {
        print(count);
        count = count + 1;
    }

    print_multiplication_table();
}
