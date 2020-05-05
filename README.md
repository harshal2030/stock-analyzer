# stock-analyzer

A software that compares NCDEX commodities on daily basis

### Installation for debugging and alters
make sure you install all dependencies
`pip install pandas`
`pip install matplotlib`
`pip install numpy`
`pip install tkcalendar`

and then run `python setup_stock.py` to run the program

### create executable
After installing all dependencies, you have install `pyinstaller` to create executables

and run `pyinstaller --hidden-import babel.numbers setup_stock.py`

TODO:-
- [ ] refactor code
- [x] Auto update data
- [x] Store offline data
- [x] Add extra information of graph in Header
- [ ] Use threads for responsivness 