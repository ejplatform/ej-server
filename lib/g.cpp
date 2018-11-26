#include <bits/stdc++.h>
#define MAX 10000

using namespace std;

int c[MAX];

int main(){

	int a, j;
	char b[100], d[100], e[100], f[100];
	cin >> a;
	while(a != 0){
		j = 0;
		cin.getline (b, 100);
		d = reverse(b.begin(), b.end());
		for(int i = 0; i <= 0; i++){
			if (d[i] != " "){
				e[j];
				j++;
			}
		}
		f = reverse(e.begin(), e.end());
		if (f == e){
			if(d == b){
				cout << "Palindromo completo\n";
			}
			else{
				cout << "Frase palindromo\n";
			}
		}
		else{
			cout << "Nada\n"
		}
		a--;
	}

	return 0;
}

