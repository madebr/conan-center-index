#include <iostream>

%%

ws      = [ \t]+;
alpha   = [A-Za-z];
dig     = [0-9];
name    = ((alpha)|(dig)|\$)((alpha)|(dig)|\_|\.|\-|\/|\$)*;
num1    = [-+]?(dig)+\.?([eE][-+]?((dig))+)?;
num2    = [-+]?(dig)*\.(dig)+([eE][-+]?(dig)+)?;
number  = (num1)|(num2);


ws          { /* skip blanks and tabs */ }

"/*"        {
    int c;

    while ((c = yyinput()) != 0)
        {
        if(c == '\n')
            ++mylineno;

        else if (c == '*')
            {
            if((c = yyinput()) == '/')
                break;
            else
                unput(c);
            }
        }
}

number      {std::cout << "number " << YYText() << '\n';}

"\n"        {mylineno++;}

name        {std::cout << "name " << YYText() << '\n';}

string      {std::cout << "string " << YYText() << '\n';}

%%

extern "C" {
    int yylex() {return 0;}
}

#include <stdio.h>

int main( int argc, const char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Need an argument\n");
        return 1;
    }
    return 0;
}
