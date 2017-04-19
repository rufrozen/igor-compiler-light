set PATH=C:\Programs\Python36;%PATH%

cd ..
python -m igor_compiler -i examples/schema.igor -t examples -s examples/schema.json
pause