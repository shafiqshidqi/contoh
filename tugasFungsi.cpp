#include <iostream> 
using namespace std;


int menu,x,y;
char balikmenu;
int faktorial (int);
int permutasi(int x, int y);
int kombinasi(int x, int y);

int main(){
    do{
        system("cls");
        cout << "=====================\n";
        cout << "|--------MENU-------|\n";
        cout << "| 1. Faktorial      |\n";
        cout << "| 2. Permutasi      |\n";
        cout << "| 3. Kombinasi      |\n";
        cout << "| 0. Exit           |\n";
        cout << "=====================\n";
        cout << "Pilih Menu: ";
        cin >> menu;
        cout << endl;

        switch(menu){
            case 1 :
                cout << "====faktorial====\n";
                cout << "input angka n: ";
                cin >> x;
                if(x > 0){
                    cout << "\nfaktorial dari " << x << " = " << faktorial(x) << endl;
                }else if(x < 0){
                    cout << "\ninput angka tidak boleh negatif";
                }else if(x == 0){
                    cout << "\nfaktorial dari 0 = 1" << endl;
                }
                break;
            case 2 :
                cout << "====permutasi====\n"<< endl;
                cout << "rumus: P = n! / (n - r)!\n" << endl;
                cout << "input nilai n: ";
                cin >> x;
                cout << "input niai r: ";
                cin >> y;
                if(x >= y){
                    cout << "\nhasil : " << endl << "P = " << permutasi(x,y) << endl;
                }else if(x <= y){
                    cout << "\nnilai n harus lebih besar dari nilai r";
                }
                break;
            case 3 :
                cout << "====kombinasi====\n"<< endl;
                cout << "rumus: P = n! / ((n - r)! r!)\n" << endl;
                cout << "input nilai n: ";
                cin >> x;
                cout << "input niai r: ";
                cin >> y;
                if(x >= y){
                    cout << "\nhasil : " << endl << "P = " << kombinasi(x,y) << endl;
                }else if(x <= y){
                    cout << "\nnilai n harus lebih besar dari nilai r";
                }
                break;
            case 0 :
                cout << "byee";
                exit(0);
                break;
            default :
                cout << "pilihan hanya dari 0-3!\n";
                break;
        }
        cout << "\n===============================" << endl;
        cout << "Kembali ke Menu Awal (y/n) : ";
        cin >> balikmenu;
    }while (balikmenu == 'y' || balikmenu == 'Y');
}


int faktorial (int n){
    if(n == 1)
        return(1);
    else
        return(n* faktorial (n-1));
}

int permutasi (int a, int b){
    int x,y;
    x = faktorial (a);
    y = faktorial (a-b);
    return(x / y);
}

int kombinasi (int a, int b){
    int x,y;
    x = faktorial (a);
    y = faktorial (a-b);
    return(x / (y * faktorial(b)));
}