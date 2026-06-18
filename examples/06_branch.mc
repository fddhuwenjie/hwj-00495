// Example 6: Branch/Control Flow - demonstrates if-else and nested conditions
int max(int a, int b, int c) {
    int result;
    if (a > b) {
        if (a > c) {
            result = a;
        } else {
            result = c;
        }
    } else {
        if (b > c) {
            result = b;
        } else {
            result = c;
        }
    }
    return result;
}

void main() {
    int x = 10;
    int y = 20;
    int z = 15;
    int m = max(x, y, z);
    print(m);

    bool isPositive = m > 0;
    if (isPositive && m < 100) {
        print("Valid range");
    } else {
        print("Out of range");
    }

    int score = 85;
    string grade;
    if (score >= 90) {
        grade = "A";
    } else if (score >= 80) {
        grade = "B";
    } else if (score >= 70) {
        grade = "C";
    } else {
        grade = "F";
    }
    print(grade);
}
