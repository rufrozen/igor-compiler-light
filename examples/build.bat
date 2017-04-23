set PATH=C:\Programs\Python36;%PATH%

cd ..
python -m igor_compiler -t examples -s examples/schema.json examples/*.igor
pause